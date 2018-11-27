
# coding: utf-8

# In[1]:


facebook_id = ''
facebook_psw = ''


# In[2]:


from selenium import webdriver
import requests
import json
import time
import facebook
import urllib3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException,NoSuchElementException
from selenium.webdriver.chrome.options import Options
import csv
import pickle
from bs4 import BeautifulSoup


# In[3]:


def fetch(url):
    time.sleep(0.4)
    response=requests.get(url=url)
    if response.status_code != 200:  #回傳200代表正常
        print('Invalid url:', response.url)
        return None
    else:
        return response


# In[4]:


def bs4soup(driver):
    html = driver.page_source
    soup = BeautifulSoup(html, "lxml")
    return soup


# In[5]:


def webdriver_crawl(driver, xpath):
    try:
        content = driver.find_element_by_xpath(xpath).text
        return content
    except NoSuchElementException:
        return "?"
    time.sleep(0.4)


# In[6]:


def crawl_country(soup):
    p_tags = soup.findAll('div', class_ ='clearfix _h71')
    current = "?"
    hometown = "?"
    for p_tag in p_tags:
        contents = p_tag.findNext('ul', class_ = 'uiList fbProfileEditExperiences _4kg _4ks')
        for content in contents:
            try:
                prefix = content.find('div', class_ = 'fsm fwn fcg').text
                if prefix == '現居城市':
                    current = content.find('span', class_ = '_2iel _50f7').text
                elif prefix == '家鄉':
                    hometown = content.find('span', class_ = '_2iel _50f7').text
            except:
                pass
    return current, hometown


# In[7]:


def crawl_work_education(soup):
    p_tags = soup.findAll('div', class_ ='clearfix _h71')
    work = []
    education = []
    for p_tag in p_tags:
        contents = p_tag.findNext('ul', class_ = 'uiList fbProfileEditExperiences _4kg _4ks')
        for content in contents:
            if p_tag.text == '工作經歷':
                try:
                    work.append(content.find('div', class_ = '_2lzr _50f5 _50f7').text)
                except:
                    pass
            elif p_tag.text == '學歷':
                try:
                    education.append(content.find('div', class_ = '_2lzr _50f5 _50f7').text)
                except:
                    pass
    if work == []:
        work = "?"
    if education == []:
        education = "?"
    return work, education


# In[8]:


def get_age_star(birthday):
    age = '?'
    star_sign = '?'
    if birthday == '?':
        return age, star_sign
    if '年' in birthday:
        year = int(birthday.split('年')[0])
        month = int(birthday.split('年')[1].split('月')[0])
        date = int(birthday.split('年')[1].split('月')[1].split('日')[0])
        age = 2018 - year
        star_sign = "?"
        return age, star_sign
    else:
        month = int(birthday.split('月')[0])
        date = int(birthday.split('月')[1].split('日')[0])
        star_sign = "?"
        return age, star_sign


# In[9]:


def crawl_relationship(soup):
    p_tags = soup.findAll('div', class_ ='clearfix _h71')
    relationship = '?'
    for p_tag in p_tags:
        contents = p_tag.findNext('ul', class_ = 'uiList fbProfileEditExperiences _4kg _4ks')
        for content in contents:
            if p_tag.text == '感情狀況':
                relationship = content.text
    if relationship == '沒有感情狀況資訊可顯示':
        relationship = '無'
    return relationship


# In[10]:


def crawl_basic_info(soup):
    p_tags = soup.findAll('div', class_ ='clearfix _h71')
    birthday = '?'
    gender = '?'
    blood = '?'
    sex_orientation = '?'
    language = '?'
    religion = '?'

    for p_tag in p_tags:
        #contents = p_tag.findNext('ul', class_ = 'uiList fbProfileEditExperiences _4kg _4ks')
        if p_tag.text == '基本資料':
            contents = p_tag.findAllNext('div', class_ = '_4bl7 _3xdi _52ju')
            for content in contents:
                if content.text == '生日':
                    birthday = content.findNext('div', class_ = '_4bl7 _pt5').text
                elif content.text == '性別':
                    gender = content.findNext('div', class_ = '_4bl7 _pt5').text
                elif content.text == '血型':
                    blood = content.findNext('div', class_ = '_4bl7 _pt5').text
                elif content.text == '戀愛性向':
                    sex_orientation = content.findNext('div', class_ = '_4bl7 _pt5').text
                elif content.text == '語言':
                    language = content.findNext('div', class_ = '_4bl7 _pt5').text
                elif content.text == '宗教信仰':
                    religion = content.findNext('div', class_ = '_4bl7 _pt5').text
    return birthday, gender, blood, sex_orientation, language, religion


# In[11]:


def retrieve_all_information(driver,profile_url):
    all_result=[]
    """
    中文姓名、英文姓名、FB帳號、ig帳號、居住地區、來自地區、地址、工作、學歷(畢業國中、高中、大學、研究所)、性別、血型、性向、語言、宗教、生日、年齡、星座、gmail、手機號碼、父母名字、感情狀態
    """
    
    #========== 中文姓名 ==========
    xpath = "/html/body/div[1]/div[3]/div[1]/div/div[2]/div[2]/div[1]/div/div[1]/div/div[3]/div/div[1]/div/div/h1/span[1]/a"
    all_result.append(webdriver_crawl(driver, xpath))

    #========== 英文姓名 ==========
    xpath = "/html/body/div[1]/div[3]/div[1]/div/div[2]/div[2]/div[1]/div/div[1]/div/div[3]/div/div[1]/div/div/h1/span[1]/a/span"
    all_result.append(webdriver_crawl(driver, xpath))
    
    #========== FB帳號 ==========
    all_result.append(profile_url)
    
    #========== IG帳號 ==========
    all_result.append("?")
    
    
    #-------------------
    #|   他住過的地方   |
    #-------------------
    driver.get(profile_url+"&sk=about&section=living&")
    soup = bs4soup(driver)
    
    #========== 現居城市，家鄉 ==========
    current_living, hometown = crawl_country(soup)
    all_result.append(current_living)
    all_result.append(hometown)
    
    #========== 地址 ==========
    all_result.append("?")
    
    
    #-------------------
    #|  學歷與工作經歷  |
    #-------------------
    driver.get(profile_url+"&sk=about&section=education&")
    soup = bs4soup(driver)
    
    #========== 工作、學歷(畢業國中、高中、大學、研究所) ==========
    work, education = crawl_work_education(soup)
    all_result.append(work)
    all_result.append(education)
    
    
    #-------------------
    #|  聯絡和基本資料  |
    #-------------------
    driver.get(profile_url+"&sk=about&section=contact-info")
    soup = bs4soup(driver)
    #========== 性別，血型，性向，語言，宗教，生日 ==========
    birthday, gender, blood, sex_orientation, language, religion = crawl_basic_info(soup)
    all_result.append(gender)
    all_result.append(blood)
    all_result.append(sex_orientation)
    all_result.append(language)
    all_result.append(religion)
    all_result.append(birthday)
    
    #========== 年齡，星座 ==========
    age, star_sign = get_age_star(birthday)
    all_result.append(age)
    all_result.append(star_sign)
    
    #========== gmail ==========
    all_result.append("?")
    
    #========== 手機號碼 ==========
    all_result.append("?")
    
    #========== 父親名字 ==========
    all_result.append("?")
    
    #========== 母親名字 ==========
    all_result.append("?")
    

    #-------------------
    #|  家人和感情狀況  |
    #-------------------
    driver.get(profile_url+"&sk=about&section=relationship&")
    soup = bs4soup(driver)
    
    #========== 感情狀態 ==========
    relationship = crawl_relationship(soup)
    all_result.append(relationship)
    
    return all_result


# In[14]:


#token="EAALbnTifIKMBADeC06vX50ZA26BiJuHgo6b4IuEQwFFfiKRkaTIx7yIevwf38J3VWZC1Qrh5pvQmeDgQTlZCzgeuUSvelKZAtGdPQY4By7Dh4tb9DonC8mmTYorloyZBHuLl6iwng2fFBxZBh55FDnSEPNL3ArZBOMZCGAKaLJ0ZBahivZBbuXcgBtZAyqlQTbVlOMZD"
token="EAAex8H67oRIBANEqewmuYfcvxQsmadG7YZC21p7BJwY20pK1MlyyQLQdgjpYOwe6FnGVrdcXh0hmxZCb4JiWl1XiujcY0Abx4yFzHdw2h5bnsAH8gpWEzIE5FJGo2QmJ7s1XDLZAIHAhS52cePkdwQdM1xUDgRXyhys3gW0nHInejSJIkrwL6HUdtlZAi0fVZC2L4Ji1y7gZDZD"
graph = facebook.GraphAPI(access_token = token)

options = webdriver.FirefoxOptions()

firefox_profile = webdriver.FirefoxProfile()#設定讀圖模式
firefox_profile.set_preference('permissions.default.image', 2)#不讀圖片
firefox_profile.set_preference('dom.ipc.plugins.enabled.libflashplayer.so', 'false')#不讀圖片，不讀flash driver

driver = webdriver.Firefox(executable_path=r'C:\\Program Files\Mozilla Firefox\geckodriver.exe', options=options,firefox_profile=firefox_profile)
LOGIN_URL = 'https://www.facebook.com/login.php?login_attempt=1&lwv=111'

driver.get(LOGIN_URL)

# wait for the login page to load
wait=WebDriverWait(driver, 10)
wait.until(ec.visibility_of_element_located((By.ID, "email")))

driver.find_element_by_id('email').send_keys(facebook_id)
driver.find_element_by_id('pass').send_keys(facebook_psw)
driver.find_element_by_id('loginbutton').click()

start_url = r"https://www.facebook.com/profile.php?id=100002703513934"
driver.get(start_url)
my_all_information = retrieve_all_information(driver, start_url)
print(my_all_information)

#friends start
time.sleep(0.4)
driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[1]/div/div[2]/div[2]/div[1]/div/div[1]/div/div[3]/div/div[2]/div[2]/ul/li[3]/a").click()
#$$$This line is a little bit weired, it will crash in some case!!

flag=True
uls_beforeScroll =len(driver.find_elements_by_xpath("//div[@id='pagelet_timeline_app_collection_1155995189:2356318349:2']/ul"))

while(flag):#會抓到社團和粉絲專頁
    driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    time.sleep(4)
    uls_afterScroll = len(driver.find_elements_by_xpath("//div[contains(@id,'pagelet_timeline_app_collection_')]/ul"))
    if(uls_afterScroll == uls_beforeScroll):
        flag = False
    else:
        uls_beforeScroll = uls_afterScroll

name=""

names = driver.find_elements_by_xpath("//div[@class='fsl fwb fcb']")
overall_friends_url=[]
for name in names:
    print(name.find_element_by_tag_name("a").text)
    overall_friends_url.append(name.find_element_by_tag_name("a").get_attribute('href'))
#friends end

all_friends_information=[]
for index in range(0,len(overall_friends_url)
    driver.get(overall_friends_url[index])
    my_all_information=[]
    my_all_information=retrieve_all_information(driver,overall_friends_url[index])
    all_friends_information.append(my_all_information)
    #print(my_all_information)
    
with open("facebook_dataset.csv",'w',newline='',encoding='utf8') as csvfile:
    writer=csv.writer(csvfile)
    writer.writerow(['id','中文名字','英文名字','FB URL','ig URL','現居地區','來自地區','地址','工作','學歷','性別','血型','性向','語言','宗教','生日','年齡','星座','gmail','手機號碼','父親名字','母親名字','感情狀態'])
    counter=1
    current_row=[]
    current_row.append(counter)
    current_row.extend(my_all_information)
    writer.writerow(current_row)
    #start the friends
    for i in range(0,len(all_friends_information)):
        for j in range(0,len(all_friends_information[i])):
            all_friends_information[i][j].encode('utf8').decode('utf8')
        writer.writerow(all_friends_information[i])
        
# pickle a variable to a file
file = open('all_friends_url.pickle', 'wb')
pickle.dump(overall_friends_url, file)
file.close()

