from selenium import webdriver
from scrapy.selector import Selector

browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver')

browser.get('https://item.taobao.com/item.htm?spm=a219r.lm874.14.1.31385b62pIqpP9&id=566087651247&ns=1&abbucket=14')
#print(browser.page_source)
t_selector = Selector(text=browser.page_source)
print(t_selector.css('#J_PromoPriceNum::text').extract())

#下拉滚动
for i in range(3):
    browser.execute_script("window.scrollTo(0,document.body.scrollHeight);var lenOfPage = document.body.scrollHeight; return lenOfPage;")

#设置不加载图片
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
chrome_opt.add_experimental_option('prefs',prefs)
browser = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver',chrome_options=chrome_opt)
browser.get()

browser.quit()