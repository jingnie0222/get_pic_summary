#!/usr/bin/python3
# -*-codig=utf8-*-

from pyppeteer import launch
import asyncio
from urllib.parse import quote
import DataFile
import datetime
import os
import time
import random

wordlist = DataFile.read_file_into_list("./vr_1")


async def action_get_page_content(page):
    content = await page.evaluate('document.documentElement.outerHTML', force_expr=True)
    return content
    
async def action_is_element_exist(page, selector):
    #返回文档中与指定选择器或选择器组匹配的第一个 html元素Element。 如果找不到匹配项，则返回null
    el = await page.querySelector(selector);
    return el
  
async def action_get_result_loc(page):
    result_loc_list=await page.evaluate('''() => {
                        //classid黑名单,50000000占位符，50023801/50023901/50024901相关推荐，30010081中部hint，21312001关系图谱，11005401搜狗问问提问
	                    classidBlackArr = ['50000000','50023801','50023901','30010081','21312001','11005401', '50024901'];
	                    //tplid黑名单
	                    tplidBlackArr = [];
                        //聚合结果vrid
                        clusterVridArr = [];
                        //结构化结果vrid
                        structVridArr = ['11002501','11002601','11008601','11008701','11008801','11008901','11009501','30000101','30000201','30000202',\
                                        '30000302','30000402','30000501','30000601','30000602','30000604','30000610','30000907','30000909','30001401',\
                                        '30001402','30001403','30001405','30001408','30001410','30001430','30001431','30001501','30002401','30002402',\
                                        '30010000','30010007','30010010','30010020','30010021','30010026','30010033','30010035','30010048','30010055',\
                                        '30010056','30010058','30010059','30010068','30010070','30010072','30010073','30010081','30010085','30010086',\
                                        '30010087','30010092','30010096','30010097','30010098','30010100','30010103','30010106','30010107','30010108',\
                                        '30010109','30010111','30010119','30010120','30010125','30010134','30010136','30010139','30010153','30010154',\
                                        '30010155','30010156','300802', '30010173'];
    
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
	                        if (innerContent.indexOf('tplid: undefined classid: undefined')> -1 || (vrid == "" && tplid == "")){
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

	                        height = sizeLocEnd.y - sizeLocStart.y 
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

    
    
async def main():

    wd_idx = 1
    for word in wordlist: 
    
        try:     
            print("start process %dth word" % wd_idx)

            browser = await launch({"executablePath": "chromium-browser", "args": ["--no-sandbox"]})
            page = await browser.newPage()
            await page.setViewport({"width": 800, "height": 1080})

            url = "http://wap.sogou.com.inner/web/searchList.jsp?dbg=on&keyword=" + quote(word)
            print(url)
            await page.goto(url)
            
            loc_list = await action_get_result_loc(page)
           
            for index, loc in enumerate(loc_list):
                if not loc['res_type']:
                    print(loc)
                await page.screenshot({"path": "./" + word + '_' + str(index) + '.png', \
                "clip":{'x':loc['x'], 'y':loc['y'], 'width':loc['width'], 'height':loc['height']}})           

            #截图
            #await page.setViewport({"width": 400, "height": 1080})
            #await page.screenshot({"path": "./" + word + ".png", "fullPage": "True"})
                  
            wd_idx = wd_idx + 1
            time.sleep(0.5)
            await browser.close()
            time.sleep(3)
        
        except Exception as err:  
            print(err)
            wd_idx = wd_idx + 1
            continue
        

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
