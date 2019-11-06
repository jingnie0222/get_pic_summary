#!/usr/bin/python3
# -*-codig=utf8-*-
import base64
import json

from pyppeteer import launch
import asyncio
from urllib.parse import quote
import DataFile
import datetime
import os
import time
import requests
from io import BytesIO
from PIL import Image
import random
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import smtplib



wordlist = DataFile.read_file_into_list("vr_1")
#requests.adapters.DEFAULT_RETRIES = 5


async def action_get_page_content(page):
    content = await page.evaluate('document.documentElement.outerHTML', force_expr=True)
    return content
    
async def action_is_element_exist(page, selector):
    #返回文档中与指定选择器或选择器组匹配的第一个 html元素Element。 如果找不到匹配项，则返回null
    el = await page.querySelector(selector);
    return el
  
async def action_get_result_loc(page):
    #print("=======")
    result_loc_list = await page.evaluate('''() => {
                        //classid黑名单,50000000占位符，50023801/50023901/50024901相关推荐，30010081中部hint，21312001关系图谱，11005401搜狗问问提问,
                        //30010058/30010059/30010048官网结构化/'30010156',30010155,'30010092',30010154,30010056医疗/30010173知乎结构化
                        //30010186,30010187/ 30010098/30010007/30000907百度经验,30010163/30010097/30010100百科,11002601微信,30010208/30010171知乎,30000402宝宝树,300802百度文库,
                        //30010085学术, 30000202/30010125搜狗知识,30010170知乎聚合,30010106手机结构化,11002501微信聚合,30000610大众点评,30000501新闻聚合
                        //30000201作业帮,30010154百姓健康网,30010111英文聚合,11018201微博聚合,30010029汽车，'30001408','30001414'，30001412/30001409/30001410/'30010054/30001405/30001503/30001401/30001403/30001507视频，
                        //30002402/30002401贴吧,30010035豆瓣,30010139医疗聚合,30010096搜狗指南
                        classidBlackArr = ['50000000','50023801','50023901','30010081','21312001','11005401','50024901',\
                                            '30010058','30010059','30010048','30010156','30010092','30010173','30010210',\
                                            '30010186','30010163','30010155','30010187','30010097','11002601','30010208',\
                                            '30000402','300802','30010085','30000202','30010098','30010170','30010106',\
                                            '11002501','30000610','30010007','30000501','30010125','30000201','30010154',\
                                            '30010111','11018201','30010029','30010153','30010056','30001408','30001414',\
                                            '30010054','30010100','30001405','30001503','30001401','30001403','30002402',\
                                            '30001507','30001410','30001409','30001412','30010035','30002401','30010171',\
                                            '30010139','30001402','30010219','30010209','30010026','30010211','30010215',\
                                            '30010213','30000907','30010055','30010096'];
                        //tplid黑名单
	                    tplidBlackArr = [];
                        //聚合结果vrid
                        clusterVridArr = ['30000202','30010125','30000501','30002401'];
                        //结构化结果vrid
                        structVridArr = ['11002501','11002601','11008601','11008701','11008801','11008901','11009501','30000101','30000201','30000202',\
                                        '30000302','30000402','30000501','30000601','30000602','30000604','30000610','30000907','30000909','30001401',\
                                        '30001402','30001403','30001405','30001408','30001410','30001430','30001431','30001501','30002401','30002402',\
                                        '30010000','30010007','30010010','30010020','30010021','30010026','30010033','30010035','30010048','30010055',\
                                        '30010056','30010058','30010059','30010068','30010070','30010072','30010073','30010081','30010085','30010086',\
                                        '30010087','30010092','30010096','30010097','30010098','30010100','30010103','30010106','30010107','30010108',\
                                        '30010109','30010111','30010119','30010120','30010125','30010134','30010136','30010139','30010153','30010154',\
                                        '30010155','30010156','300802', '30010173','30010165','30010054','30001407','30001409','30001412','30001414',\
                                        '30001430','30001431','30001502','30001503','30001505','30001507','30010029','30010048','30010053',\
                                        '30010170','30010171','30001411','30010208','30010209'];
	                    tplidVridHeights= [];
	                    let dbgs = document.getElementsByClassName('sogou-debug-title');
	                    let index_dbg = -1; 
                        
	                    for(var dbg of dbgs){
	                        index_dbg = index_dbg + 1;
	                        if (index_dbg >= dbgs.length){
	                            break;
	                        }
                            let res_type = "";
	                        let innerContent = dbg.innerHTML;
                            
                            //去掉debuginfo里的Header，否则下面的split会报错
                            if (innerContent.indexOf('tplid') < 0){  
                                continue;
                            }
                            
                            let tplid = innerContent.split("tplid: ")[1].split(" classid:")[0];
	                        let vrid  = innerContent.split("classid: ")[1].trim()
	                        if (classidBlackArr.includes(vrid) || tplidBlackArr.includes(tplid)){
	                            continue;
	                        }
                            
                            if (vrid.indexOf('2') == 0 || vrid.indexOf('4') == 0 || vrid.indexOf('7') == 0 || (vrid.indexOf('1') == 0 && structVridArr.indexOf(vrid) < 0)){
                                continue;
                            }
	                        if (innerContent.indexOf('tplid: undefined classid: undefined')> -1 || (vrid == "" && tplid == "") || (vrid == "" && (tplid == "50" || \
	                        tplid == "51" || tplid == "54")) || (vrid == "undefined" && tplid == "356") || (vrid == "30010187" && tplid == "61")){
	                            res_type = "normal";
	                        }
                            if (structVridArr.includes(vrid)){
                                res_type = "struct";
                            }
                            if (clusterVridArr.includes(vrid)){
                                res_type = "cluster";
                            }

	                        let sizeLocStart = dbgs[index_dbg].getBoundingClientRect();
	                        if(dbgs[index_dbg+1] ==undefined){
		                        let next_pate = document.getElementById('ajax_next_page')
		                        if (next_pate == null){
	                                continue;		 
		                        }
                                sizeLocEnd = next_pate.getBoundingClientRect();
	                        }else{
                                sizeLocEnd = dbgs[index_dbg+1].getBoundingClientRect();
                            }
                            //如果是新闻聚合，去掉底部APP推荐，其高度为72
                            if(vrid=='30000501' || vrid == '30000202' || vrid == '30010139'){
                                height = sizeLocEnd.y - sizeLocStart.y - 72;
                            }else{
	                            height = sizeLocEnd.y - sizeLocStart.y;
                            }
	                        tplidVridHeight={
		                        x:0,
		                        y:sizeLocStart.y + 37,  //去掉debuginfo部分
		                        width:sizeLocStart.width,
		                        height:height - 37,    //去掉debuginfo部分
		                        vrid:vrid,
		                        tplid:tplid,
                                res_type:res_type
	                        }
	                    // console.log(tplidVridHeight)
	                    tplidVridHeights.push(tplidVridHeight)
	                    }
	                    return(tplidVridHeights)    
                    }''')
    #print(result_loc_list)
    return result_loc_list


def pil_base64(image_path):
    """
		image->base64	"""
    image = Image.open(image_path)
    img_buffer = BytesIO()
    image.save(img_buffer, format='PNG')
    byte_data = img_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str

def get_title(text_size):
    #print(text_size)
    if len(text_size) == 1:
        return text_size[0]
    elif len(text_size) == 2:
        return text_size[0]

    res = [[] for i in range(10)]
    counter = 0
    ac_rete = 10
    for i in range(len(text_size)):
        if i == 0:
            distance_left = 0
            distance_right = abs(text_size[i] - text_size[i + 1])
            res[counter].append(text_size[i])
        elif i == len(text_size) - 1:
            distance_left = abs(text_size[i] - text_size[i - 1])
            distance_right = 0
            res[counter].append(text_size[i])
        else:
            distance_left = abs(text_size[i] - text_size[i - 1])
            distance_right = abs(text_size[i] - text_size[i + 1])

            # if distance_left > 2* ac_rete and distance_right > 2 * ac_rete:
            #     ac_rete = abs(text_size[i] - text_size[i - 1])
            #     continue
            # else:
            #     ac_rete = abs(text_size[i] - text_size[i - 1])

            if distance_left > distance_right:
                counter += 1
                res[counter].append(text_size[i])
            else:
                res[counter].append(text_size[i])
    #print(res)

    return res


def  isvalid(image, type, vrid):
    #print("1" + str(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())))
    pic64 = pil_base64(image)
    line = {"realname": "kgm", "pic": pic64}
    headers = {"Content-type": "application/x-www-form-urlencoded;charset=UTF-16LE", 'Connection': 'close'}
    resp = requests.post("http://10.134.120.30:8888/ocr-api", data=line, headers=headers)
    #print(resp.text)
    #print("2" + str(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())))
    s = json.loads(resp.text)
    resp.close()
    sum_line = len(s["res"]) - 1
    pic_flag = int(s["res"][sum_line][0]["picFlag"])
    index = 0
    text_size = []
    title = 1
    #print("=============")
    while (index < sum_line):
        text_size.append(float(s["res"][index]["text_size"]))
        index += 1
    #print(image, text_size)

    max = 0
    index = 0
    i = 0
    # while (i < sum_line - 2):
    #     if (abs(text_size[i] - text_size[i+1]) > max):
    #         max = abs(text_size[i] - text_size[i+1])
    #         index = i
    #     i += 1
    # title = index + 1
    new_text_size = get_title(text_size)
    if text_size.__len__() == 1 or text_size.__len__() == 2:
        return "标题摘要过少"
    elif text_size.__len__() == 3:
        return ""
    # new_len = 0
    # for item in new_text_size:
    #     new_len += item.__len__()
    title = new_text_size[0].__len__()
    res = ""
    if(title > 2):
        res += "title大于两行&&"
    if((title == 2 and len(s["res"][index]["text"]) < 3 )):
        res += "title最后一行少于3个字&&"
#summary_len   摘要行数，-1是去掉来源
    summary_len = sum_line - title - 1
    #summary_len = new_len - title - 1
    if(type == "normal" or type == "struct"):
        if pic_flag == 0:
            if summary_len > 3:
                res += "无图摘要大于3行&&"
        else :
            if summary_len > 4:
                res += "有图摘要大于4行&&"
        if(len(s["res"][sum_line-2]["text"]) < 3 ):
            res += "摘要最后一行少于3个字&&"
    elif(type == "cluster"):
        return ""
    print(image, text_size, new_text_size, title, pic_flag)
    #print(res)
    return res

def mail_res(dirPath, _usr, _pwd, _to):
    mailContent = ""
    fread = open(dirPath, 'r', encoding='utf-8')
    for text in fread.readlines():
        textlist = text.split('\t')
        _query = textlist[0]
        _dimention = textlist[2]
        _link = """<a href=\"10.138.25.204/summaryCheck/""" + textlist[1] + """\">查看现场</a>"""
        _wrongtext = textlist[4]
        _num = textlist[3]
        mailContent = mailContent + """
            <tr>
                <td align="center">""" + _query + """</td>
                <td align="center">""" + _num + """</td>
                <td align="center">""" + _dimention + """</td>
                <td align="center">""" + _wrongtext + """</td>
                <td align="center">""" + _link + """</td>
            </tr>"""
    fread.close()
    _html = """\
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=gbk" />
    <body>
    <div id="container">
    <p><strong>截断异常用例如下:</strong></p>
    <div id="content">
    <table width="80%" border="2" bordercolor="black" cellspacing="0" cellpadding="0">
    <tr>
    <td align="center" width="20"><strong>用例名称</strong></td>
    <td align="center" width="10"><strong>结果位置</strong></td>
    <td align="center" width="10"><strong>分辨率</strong></td>
    <td align="center" width="80"><strong>错误信息</strong></td>
    <td align="center" width="10"><strong>错误现场</strong></td>
    </tr>""" + mailContent + """
    </table>
    </div>
    </div>
    </body>
    </html>
    """
    msg = email.mime.multipart.MIMEMultipart()
    _context = MIMEText(_html, _subtype='html', _charset='gbk')
    msg['Subject'] = "网页summary结果截断监控"
    msg['From'] = _usr
    msg['To'] = ','.join(_to)
    msg.attach(_context)
    s = smtplib.SMTP()
    s.connect("mail.sogou-inc.com")
    s.login(_usr, _pwd)
    s.sendmail(_usr, _to, msg.as_string())
    s.quit()


async def main():
    wd_idx = 1
    viewport720 = {
        "width": 360,
        "height": 720,
        "deviceScaleFactor": 2,
        "isMobile": True,
        "hasTouch": True,
        "isLandscape": False
    }
    viewport1080 = {
        "width": 360,
        "height": 640,
        "deviceScaleFactor": 3,
        "isMobile": True,
        "hasTouch": True,
        "isLandscape": False
    }
    viewport750 = {
        "width": 375,
        "height": 667,
        "deviceScaleFactor": 2,
        "isMobile": True,
        "hasTouch": True,
        "isLandscape": False
    }
    viewport1242 = {
        "width": 414,
        "height": 736,
        "deviceScaleFactor": 3,
        "isMobile": True,
        "hasTouch": True,
        "isLandscape": False
    }
    with open("wrongAns", 'w', encoding='utf-8') as f:
        for word in wordlist:
            #word = "一品蹄督"
            #print(time.asctime(time.localtime(time.time())))
            try:
                print("start process %dth word" % wd_idx)
                #uaIosplus = "ozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"
                #uaIos = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36"
                #uaAndroid = "Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36"

                dimensions = [720, 750, 1080, 1242]
                #dimensions = [1080]
                #browser = await launch({"args": ["--no-sandbox", '--disable-setuid-sandbox', "--user-agent=\
                #                        'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36'"]})
                for d in dimensions:
                    browser = await launch({"args": ["--no-sandbox", '--disable-setuid-sandbox', "--user-agent=\
                                                            'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.23 Mobile Safari/537.36'"]})
                    page = await browser.newPage()
                    await page.setViewport(locals()['viewport' + str(d)])
                    url = "http://wap.sogou.com.inner/web/searchList.jsp?dbg=on&screenWidth=" + str(d) + "&keyword=" + quote(word)
                    await page.goto(url)
                    await asyncio.sleep(1)
                    loc_list = await action_get_result_loc(page)
                    for index, loc in enumerate(loc_list):
                        if not loc['res_type']:
                            print(word, loc)
                        path = "pic/" + word + '_' + str(index) + '_' + str(d) + '.png'
                        await page.screenshot({"path": path, "clip": {'x': loc['x'], 'y': loc['y'], 'width': loc['width'],'height': loc['height']}})
                        #print("3" + str(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())))
                        res = isvalid(path, loc['res_type'], loc['vrid'])
                        if(res != ""):
                            f.write(str(word) + '\t' + str(path) + '\t'+ str(d) + '\t' + str(index) + '\t' + str(res)[:-2] + '\n')
                        #print("4" + str(time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())))
                    #await page.waitFor(3000)
                    await page.close()
                    #time.sleep(1)
                    await browser.close()
                    #time.sleep(1)
                    #await browser.close()
                    #time.sleep(3)
                #await browser.close()
                wd_idx = wd_idx + 1
            except Exception as err:
                print(err)
                wd_idx = wd_idx + 1
                continue
    f.close()
        

if __name__ == '__main__':
    print((time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())))
    asyncio.get_event_loop().run_until_complete(main())
    usr = "qa_svnreader"
    pwd = "xyz"
    to = ['xyz']
    mail_res("wrongAns", usr, pwd, to)
    print((time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())))
