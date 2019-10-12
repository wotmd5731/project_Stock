# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from selenium import webdriver
#from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.wait import WebDriverWait

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
driver = webdriver.Chrome("C:\\Users\\J\\Downloads\\chromedriver.exe")

#
#driver.get('https://google.com')
#
#driver.implicitly_wait(3)

#inele = driver.find_element_by_xpath("""//*[@id="tsf"]/div[2]/div[1]/div[1]/div/div[2]/input""")
#inele.send_keys("investing 배당캘린더")
#inele.submit()

#%%
driver.get('https://kr.investing.com/dividends-calendar/')

#driver.implicitly_wait(3)
try:
    element = WebDriverWait(driver, 10).until(
            lambda x: x.find_element_by_xpath("""//*[@id="PromoteSignUpPopUp"]/div[2]/i"""))
    driver.find_element_by_xpath("""//*[@id="PromoteSignUpPopUp"]/div[2]/i""").click()
    
except TimeoutException:
    print("time out")
    

driver.find_element_by_xpath("""//*[@id="timeFrame_nextWeek"]""").click()
#%%
rows = driver.find_elements_by_xpath("""//*[@id="dividendsCalendarData"]/tbody/*""")
for row in rows:
    
    try : 
        country = row.find_element_by_xpath('td/span').get_attribute('title')
        if country == '미국':
            data = row.text.split()
            data[-9] = data[-9].strip('()')
            print(data[-9:])
    except:
       pass
   
#//*[@id="dividendsCalendarData"]/tbody/tr[2]/td[1]/span
#//*[@id="dividendsCalendarData"]/tbody/*/*/span
#//*[@id="dividendsCalendarData"]/tbody/tr
#
#b0 = aa.text
#b1 = b0.split('\n')


#%%

aa = driver.find_elements_by_xpath("""//*[@id="dividendsCalendarData"]/tbody/tr""")
