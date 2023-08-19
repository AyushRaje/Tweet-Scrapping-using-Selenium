from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd


#Extract Links from Worksheet
def ExtractLinks(filename,sheetname,linkcol)->list():
    tweet_urls=pd.read_excel(filename,sheet_name=sheetname,usecols=linkcol)
    tweet_urls=tweet_urls["Twitter Link"].to_list()
    return tweet_urls


#To log into a Twitter Account
def LoginDriver(username,password)->webdriver.Chrome():
    
    try:
        login_url="https://twitter.com/login"

        # If you don't want the chrome driver to run in background
        # Please uncomment the below two lines and add options inside the Chrome() function
        # options=webdriver.ChromeOptions()
        # options.add_argument("--headless")
        driver=webdriver.Chrome()
        driver.get(login_url)
        sleep(2)
        driver.find_element(By.XPATH,'//input').send_keys(username)
        sleep(1)
        driver.find_element(By.TAG_NAME,'input').send_keys(Keys.ENTER)
        WebDriverWait(driver,10).until(EC.presence_of_element_located((By.NAME,'password')))
        driver.find_element(By.NAME,'password').send_keys(password)
        sleep(1)
        driver.find_element(By.NAME,'password').send_keys(Keys.ENTER)
        sleep(3)

    except:
        driver=None
        print("Please Run Again")

    return driver    
        
#Scrape Twitter Data        
def scrape_tweet_data(link,driver)->dict():
    
        driver.get(link)
        
        sleep(3)
        #Collecting PageSource code
        soup=BeautifulSoup(driver.page_source,'lxml')

        #All the different divs containing the tweets
        All_tweets_div=soup.find_all('div',{"data-testid":"cellInnerDiv"})
        
        #Influencer Tweet
        influencer_tweet_div=BeautifulSoup(str(All_tweets_div[1]),'lxml')
        if influencer_tweet_div is not None:
            
            influencer_username=influencer_tweet_div.find('div',{"data-testid":"User-Name"})
            if influencer_username is not None:
                influencer_username=str(influencer_username.text).split('@')[1]
            else:
                influencer_username="NA"

            influencer_tweet_content=influencer_tweet_div.find('div',{"data-testid":"tweetText"})
            if influencer_tweet_content is not None:
                influencer_tweet_content=influencer_tweet_content.text
            else:
                influencer_tweet_content="Tweet Deleted"

            influencer_tweet_like=influencer_tweet_div.find('span',{"data-testid":"app-text-transition-container"})
            if influencer_tweet_like is not None:
                influencer_tweet_like=influencer_tweet_like.text
            else:
                influencer_tweet_like="NA"

            influencer_tweet_timestamp=influencer_tweet_div.find('time')
            if influencer_tweet_timestamp is not None:
                influencer_tweet_timestamp=influencer_tweet_timestamp.text
            else:
                influencer_tweet_timestamp="NA"            

        #Promoter Tweet
        promoter_tweet_div=BeautifulSoup(str(All_tweets_div[0]),'lxml')
        if promoter_tweet_div is not None:

            promoter_username=promoter_tweet_div.find('div',{"data-testid":"User-Name"})

            if promoter_username is not None:
                promoter_username=promoter_tweet_div.find('div',{"data-testid":"User-Name"}).find('a',{"tabindex":-1})
                promoter_username=str(promoter_username.text).split('@')[1]
            else:    
                promoter_username="NA"


            promoter_tweet_like=promoter_tweet_div.find('div',{"data-testid":"like"})
            if promoter_tweet_like is not None:
                promoter_tweet_like=promoter_tweet_like.text
            else:
                promoter_tweet_like="NA"

            promoter_tweet_content=promoter_tweet_div.find('div',{"data-testid":"tweetText"})
            if promoter_tweet_content is not None:
                promoter_tweet_content=promoter_tweet_content.text
            else:
                promoter_tweet_content="Tweet Deleted"

            promoter_tweet = driver.find_element(By.XPATH,"//article")
            promoter_tweet_url="NA"
            if promoter_tweet is not None:
                driver.execute_script("arguments[0].click();", promoter_tweet)
                sleep(2)
                promoter_tweet_url=driver.current_url
            if promoter_tweet_url==link:
                promoter_tweet_url="NA"

        #Converting Scraped data to Dict
        tweet_info_dict={'time_stamp':influencer_tweet_timestamp,
                        'influencer':"https://twitter.com/"+influencer_username ,
                        'promoter':"https://twitter.com/"+promoter_username,
                        'influencer_tweet':link,'promoter_tweet':promoter_tweet_url,
                        'influencer_tweet_likes':influencer_tweet_like,
                        'promoter_tweet_likes':promoter_tweet_like,
                        'influencer_tweet_text':influencer_tweet_content,
                        'promoter_tweet_text':promoter_tweet_content}

        for keys,value in tweet_info_dict.items():
            print(str(keys)+ " : "+ str(value))
        
        return tweet_info_dict

def ConvertToExcel(data):
    df=pd.DataFrame(data)
    df.to_excel('output.xlsx',sheet_name='output',index=False)




# Please change the username and password to your own twitter login credentials
username="your_username"
password="your_password"

#Change the parameters passed in this Function acc. to your input excel sheet
twitter_links=ExtractLinks('Input.xlsx','Sheet1','E')

driver=LoginDriver(username,password)

scraped_data=[]

for tweet_links in twitter_links[1:]:
    if driver:
        scraped_data.append(scrape_tweet_data(tweet_links,driver))

print(scraped_data)
ConvertToExcel(scraped_data)
