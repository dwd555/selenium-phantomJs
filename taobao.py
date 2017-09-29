from selenium import webdriver
from bs4 import BeautifulSoup
import threading
from threadpool import *
class Bedding(object):
    phantomjs_max = 1  ##同时开启phantomjs个数
    jiange = 0.00001  ##开启phantomjs间隔
    timeout = 20  ##设置phantomjs超时时间
    service_args = ['--load-images=no', '--disk-cache=yes']  ##参数设置
    def __init__(self):
        self.driver=webdriver.PhantomJS()
        self.driver.get("http://www.taobao.com")
        self.driver.set_window_size(1920,1080)
    def printContent(self):
        print(self.driver.page_source)

    def search(self):
        self.driver.find_element_by_id("q").send_keys("床上用品")
        self.driver.find_element_by_css_selector(".search-button>button").click()

    def findItem(self):
        soup=BeautifulSoup(self.driver.page_source,"html.parser")
        tags=soup.select(".pic-link.J_ClickStat.J_ItemPicA")
        urls=[]
        for i in tags:
            urls.append(i["href"])
        pool=ThreadPool(5)
        urlRequests=makeRequests(self.fetchData, urls)
        [pool.putRequest(req) for req in urlRequests]
        pool.wait()
        # print("结束")

    def fetchData(self,url):
        driver=webdriver.PhantomJS(service_args=self.service_args)
        if("http" not in url):
            url="http:"+url
        if "tmall" in url:
            return
        driver.get(url)
        print("currentUrl:  "+driver.current_url)
        # self.analyze(driver.page_source)
        driver.quit()

    def analyze(self,page):
        soup=BeautifulSoup(page,"html.parser")
        # title=soup.select("#detail .tb-detail-hd > h1")[0]
        print(title)


    def main(self):
        self.search()
        # self.printContent()
        self.findItem()
if __name__ == '__main__':
    Bedding().main()
    # driver = webdriver.PhantomJS()
    # driver.get("http://detail.tmall.com/item.htm?id=555752106004&ns=1&abbucket=12")
    # driver.set_window_size(1920, 1080)
    # print(driver.page_source)