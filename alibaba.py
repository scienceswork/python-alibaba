#! /usr/bin/env python
# coding:utf-8

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import urllib
import urllib2
import sys
import os
import re
import csv
import numpy as np

# 解决中文报错的问题
reload(sys)
sys.setdefaultencoding('utf-8')
# 打开一个火狐浏览器
driver = webdriver.Firefox()
# 睡眠3秒，防止浏览器还没打开就进行了其他操作
time.sleep(3)
# 化工商户页面的url
url = 'https://s.1688.com/company/company_search.htm?' \
      'keywords=%BB%AF%B9%A4&n=y&spm=a260k.635.1998096057.d1'
# 登录的url
login_url = 'https://login.taobao.com/member/login.jhtml'
# 跳转到登录页面
driver.get(login_url)
# 睡眠5秒，防止网速较差打不开网页就进行了其他操作
time.sleep(5)
# 找到账号登录框的DOM节点，并且在该节点内输入账号
driver.find_element_by_name("TPL_username").send_keys('这里是你的淘宝账号')
# 找到账号密码框的DOM节点，并且在该节点内输入密码
driver.find_element_by_name("TPL_password").send_keys('这里是你的淘宝密码')
# 找到账号登录框的提交按钮，并且点击提交
driver.find_element_by_name("TPL_password").send_keys(Keys.ENTER)
# 睡眠5秒，防止未登录就进行了其他操作
time.sleep(5)
# 跳转到化工商户页面的url
driver.get(url)
# 新建一个data.csv文件，并且将数据保存到csv中
csvfile = file('data.csv', 'web')
writer = csv.writer(csvfile)
# 写入标题，我们采集企业名称，主页，产品，联系人，电话和地址信息
writer.writerow((
    u'企业名称'.encode('gbk'),
    u'主页'.encode('gbk'),
    u'产品'.encode('gbk'),
    u'联系人'.encode('gbk'),
    u'电话'.encode('gbk'),
    u'地址'.encode('gbk')
))
# 构建agents防止反爬虫
user_agents = [
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
    'Opera/9.25 (Windows NT 5.1; U; en)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1;.NET CLR 1.1.4322; .NET CLR2.0.50727)',
    'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5(like Gecko) (Kubuntu)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
    'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
    "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ",
]
# 总共有100页，使用for循环采集
for page in xrange(1, 100):
    # 捕捉异常
    try:
        # 获取企业名称列表
        title = driver.find_elements_by_css_selector("a[class=list-item-title-text]")
        # 获取产品
        product = driver.find_elements_by_xpath("//div[@class=\"list-item-detail\"]/div[1]/div[1]/a[1]")
        # 打印长度，调试
        print len(title)
        # 定义正则匹配每条商户
        pattern = re.compile('<div class="contcat-desc".*?>(.*?)</div>', re.S)
        # 定义电话正则
        tel_pattern = re.compile('<dd>(.*?)</dd>', re.S)
        # 定义移动电话正则
        member_name_pattern = re.compile('<a.*?class="membername".*?>(.*?)</a>', re.S)
        # 定义地址正则
        address_pattern = re.compile('"address">(.*?)</dd>', re.S)
        for i in xrange(len(title)):
            # 获取标题的值
            title_value = title[i].get_attribute('title')
            # 获取跳转的url
            href_value = title[i].get_attribute('href') + 'page/contactinfo.htm'
            # 获取经营范围
            product_value = product[i].text
            # 随机选择agent进行访问
            agent = np.random.choice(user_agents)
            # 组建header头部
            headers = {'User-Agent': agent, 'Accept': '*/*', 'Referer': 'http://www.google.com'}
            # 使用urllib2进行Request
            request = urllib2.Request(href_value, headers=headers)
            # 访问链接
            response = urllib2.urlopen(request)
            # 获得网页源码
            html = response.read()
            # 进行信息匹配
            info = re.findall(pattern, html)
            try:
                info = info[0]
            except Exception, e:
                continue
            tel = re.findall(tel_pattern, info)
            try:
                tel = tel[0]
                tel = tel.strip()
                tel = tel.replace(' ', '-')
            except Exception, e:
                continue
            member_name = re.findall(member_name_pattern, html)
            try:
                member_name = member_name[0]
                member_name = member_name.strip()
            except Exception, e:
                continue
            address = re.findall(address_pattern, html)
            try:
                address = address[0]
                address = address.strip()
            except Exception, e:
                address = ''
            # 打印出信息，方便查看进度
            print 'tel:' + tel
            print 'member_name:' + member_name
            data = (
                title_value.encode('gbk', 'ignore'),
                title[i].get_attribute('href'),
                product_value.encode('gbk', 'ignore'),
                member_name,
                tel,
                address
            )
            writer.writerow(data)
        js = 'var q=document.documentElement.scrollTop=30000'
        driver.execute_script(js)
        time.sleep(1)
        page = driver.find_elements_by_css_selector("a[class=page-next]")
        page = page[0]
        page.click()
        time.sleep(2)
    except Exception, e:
        print 'error'
        continue
# 关闭csv
csvfile.close()
# 关闭模拟浏览器
driver.close()
