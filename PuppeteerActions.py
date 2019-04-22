from pyppeteer import launch
import asyncio,json
from urllib.parse import urlparse
import DataFile
import UserAgent
import time
import traceback
#pyppeteer的检查actions

#阻止加载图片
async def ignore_images(request):
    if(request.resourceType == 'image'):
        await request.abort()
    else:
        await request.continue_()
        
async def set_ignore_images(page):
    await page.setRequestInterception(True)
    page.on('request', lambda request: asyncio.ensure_future(ignore_images(request)))
    
#action区，这部分功能是和具体业务逻辑不相干的操作，例如检查某个元素是否存在。
async def action_get_page_content(page):
    content = await page.evaluate('document.documentElement.outerHTML', force_expr=True)
    return content
    
#根据 selector 返回元素是否可见
async def action_is_element_visible_by_selector(page, selector):
    #先检查元素在不在，不在直接返回false
    check_exist = await action_is_element_exist(page, selector)
    if(not check_exist):
        return False
    el = await page.querySelector(selector)
    return await action_is_element_visible(page, el)
    
async def action_is_element_visible(page, el):
    dn = await page.evaluate('(element) => element.style.display', el)
    if(dn == "none" or dn == "hidden"):
        return False
    else:
        return True
    
async def action_get_elements_content(page, div_selector_to_get, exclude_hidden = False):
    result_arr = []
    elements = await page.querySelectorAll(div_selector_to_get)
    for element in elements:
        is_visible = True
        if(exclude_hidden):
            is_visible = await action_is_element_visible(page, element)
        if(not is_visible):
            continue
        el_content = await page.evaluate('(element) => element.textContent', element)
        result_arr.append(el_content)
    return result_arr
    
#返回数据的详细版，不仅给出内部textContent也给出外部html
async def action_get_elements_detail_content(page, div_selector_to_get, exclude_hidden = False):
    result_arr = []
    elements = await page.querySelectorAll(div_selector_to_get)
    for element in elements:
        is_visible = True
        if(exclude_hidden):
            is_visible = await action_is_element_visible(page, element)
        if(not is_visible):
            continue
        el_content = await page.evaluate('(element) => element.textContent', element)
        inner_html = await page.evaluate('(element) => element.innerHTML', element)
        result_arr.append({"content" : el_content, "html" : inner_html})
    return result_arr
    
#获取正文中 符合 div_selector_to_get 而且包含 content_must_contain 的元素，如果没有则返回 None
async def action_get_container_element(page, div_selector_to_get, content_must_contain):
    elements = await page.querySelectorAll(div_selector_to_get)
    for element in elements:
        el_content = await page.evaluate('(element) => element.textContent', element)
        if(content_must_contain in el_content):
            return element
    return None

#检查元素是否存在
async def action_is_element_exist(page, selector):
    el = await page.querySelector(selector);
    if(el is None):
        return False
    else:
        return True

#获取 selector 选择的元素中的attr属性
async def action_get_element_attr(page, selector, attr):
    element = await page.querySelector(selector)
    if(element is None):
        return None
    data = await page.evaluate('(element) => element.' + attr, element)
    return data
    
async def action_get_elements_attr(page, selector, attr, to_string = False):
    result_arr = []
    elements = await page.querySelectorAll(selector)
    for element in elements:
        #先检查一下是否有这个属性
        data = await page.evaluate('(element) => element.' + attr, element)
        if(to_string and not (data is None)): #如果是要求toString则进行修正
            data = await page.evaluate('(element) => element.' + attr + ".toString()", element)
        result_arr.append(data)
    return result_arr
    
        
async def action_get_content(page, div_selector_to_get):
    check_exist = await action_is_element_exist(page, div_selector_to_get)
    if(not check_exist):
        return ""
    element = await page.querySelector(div_selector_to_get)
    return await page.evaluate('(element) => element.textContent', element)

#删除所有的selector指向元素    
async def action_remove_all_element(page, div_selector_to_remove):
    await page.evaluate('''(sel) => {
        var elements = document.querySelectorAll(sel);
        for(var i=0; i< elements.length; i++){
            elements[i].parentNode.removeChild(elements[i]);
        }
    }''', div_selector_to_remove)
    return True
    
#combo区，检查业务不相关但元素相关的操作，例如检查某个vrid是否存在等
async def combo_pc_get_vrid(page, vrid):
    vrid = str(vrid)
    result_divs = await page.querySelectorAll(".results>div")
    #print (len(result_divs))
    for i in range(1,len(result_divs)):
        seek_name = ".results>div:nth-of-type(" + str(i) + ") a[id*='" + str(vrid) + "']"
        check_exist = await action_is_element_exist(page, seek_name)
        if(check_exist):
            return ".results>div:nth-of-type(" + str(i) + ")"
    print ("".join(["vrid ", vrid, " not exits."]))
    return None
    
async def combo_wap_get_vrid(page, vrid):
    vrid = str(vrid)
    result_divs = await page.querySelectorAll(".results>div")
    #print (len(result_divs))
    check_exist = False
    for i in range(1,len(result_divs)):
        seek_name = ".results>div:nth-of-type(" + str(i) + ") a[id*='" + str(vrid) + "']"
        check_exist = await action_is_element_exist(page, seek_name)
        if(check_exist):
            return ".results>div:nth-of-type(" + str(i) + ")"
    if(not check_exist): #貌似不存在，查找非results下面的一层
        seek_name = ".results div[id*='sogou_vr_" + str(vrid) + "']"
        check_exist = await action_is_element_exist(page, seek_name)
        if(check_exist):
            return seek_name
    print ("".join(["vrid ", vrid, " not exits."]))
    return None
    
#load页面并返回结果
async def _action_combo_get_page_content(url, cookies_dir = 'data/cookies/'):
    try:
        #解析url属于那个domain
        parsed_uri = urlparse(url)
        cookies_file = "".join([cookies_dir, parsed_uri.netloc, "cookie"])
        my_cookie_file = DataFile.read_file_intostr(cookies_file)
        browser = await launch({"executablePath": "chromium-browser", "args": ["--no-sandbox"]})
        page = await browser.newPage()
        #读取cookies
        if(len(my_cookie_file) > 0):
            my_cookie_object = json.loads(my_cookie_file)
            print ("".join(["Load ", str(len(my_cookie_object)), " cookie item(s)."]))
            for row in my_cookie_object:
                await page.setCookie(row)        
        #设置UA
        ua_box = UserAgent.UserAgentBox()
        await page.setUserAgent(ua_box.wap_normal_user)
        await page.goto(url)
        new_cookie = await page.cookies()
        json_cookie = json.dumps(new_cookie)
        res = await action_get_page_content(page)
        DataFile.write_full_file(cookies_file, json_cookie)
        await browser.close()
        return res
    except Exception as e:
        traceback.print_exc()
        return ""

#WAP版把页面content点出连接标签
def action_change_wap_url(content):
    return content.replace("./uID=", "http://m.sogou.com/uID=")
     
def action_combo_get_page_content(url, sleep_time = 1, cookies_dir = 'data/cookies/'):
    res = asyncio.get_event_loop().run_until_complete(_action_combo_get_page_content(url, cookies_dir))
    time.sleep(sleep_time)
    return res