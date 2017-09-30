#爬淘宝信息
#Author:Joshua
#date:2017/09/30
#version:1.0
from selenium import webdriver
from bs4 import BeautifulSoup
from threadpool import *
import re,json,os
import logging
logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='myapp.log',
                filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
class Bedding(object):
    phantomjs_max = 10  ##同时开启phantomjs个数
    pageCount=0 #总页数
    service_args = ['--load-images=no', '--disk-cache=yes']  ##参数设置，禁止图片加载
    dataList=[] #存放数据的列表
    def __init__(self):
        self.driver=webdriver.PhantomJS()
        self.driver.get("http://www.taobao.com")
        self.driver.set_window_size(1920,1080)

    def search(self):#进入首页搜索关键字
        self.driver.find_element_by_id("q").send_keys("床上用品")
        self.driver.find_element_by_css_selector(".search-button>button").click()

    def loop(self):#循环点击下一页
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        self.pageCount=int(re.findall(r"\d+",soup.select(".total")[0].text)[0])
        # self.pageCount=1 #测试数据
        logging.info("总页数：%d" % self.pageCount)
        for i in range(self.pageCount):
            self.findItem()
            self.driver.find_element_by_css_selector("a.J_Ajax.num.icon-tag").click()

    def findItem(self):#查找所有商品
        soup=BeautifulSoup(self.driver.page_source,"html.parser")
        tags=soup.select(".pic-link.J_ClickStat.J_ItemPicA")
        urls=[]
        for i in tags:
            urls.append(i["href"])
        pool=ThreadPool(self.phantomjs_max)
        urlRequests=makeRequests(self.fetchData, urls)
        [pool.putRequest(req) for req in urlRequests]
        pool.wait()
        # print("结束")

    def fetchData(self,url):#追踪链接
        driver=webdriver.PhantomJS(service_args=self.service_args)
        if("http" not in url):
            url="http:"+url
        if "tmall" in url:  #过滤天猫
            return
        driver.get(url)
        currentUrl=driver.current_url
        if "tmall" in currentUrl:
            return
        self.analyze(driver.page_source,currentUrl)
        driver.quit()

    def analyze(self,page,currentUrl):#解析追踪链接的网页
        soup=BeautifulSoup(page,"html.parser")
        title=soup.select("#detail  h3")[0].text
        price=soup.select("#J_StrPrice .tb-rmb-num")[0].text
        attributes=soup.select("#attributes li")
        details={}
        details["title"]=title.replace("\n","").strip()
        details["price"]=price
        details["url"]=currentUrl
        for i in attributes:
            attr=i.text.split(":")
            details[attr[0]]=attr[1]
        self.dataList.append(details)
        logging.debug(details)

    def writeData(self):#将数据以json格式写入文件
        logging.debug("写入中")
        with open(os.path.abspath(".")+"\\taobao.log","a")as f:
            f.write(json.dumps(self.dataList))

    def main(self):
        self.search()
        self.loop()
        self.driver.quit()
        self.writeData()
        logging.info("finish")
if __name__ == '__main__':
    Bedding().main()
