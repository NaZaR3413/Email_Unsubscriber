import requests
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from unsub_emails import main as unsub_emails_main
from quickstart import get_credentials
from selenium import webdriver
import time
import os  # Needed for checking the existence of token.json

# testing
def open_links_safari(links):
    driver = webdriver.Safari()
    for link in links:
        driver.get(link)
        # Add any additional logic needed to interact with the page
        time.sleep(5)  # Adjust as necessary
    driver.quit()
    
# validate credentials 
creds = get_credentials()

unsubscribe_links = unsub_emails_main(creds)
 
# Check for token.json for successful login
if 'token.json':
    print("\033[92mLogin Successful\033[0m")
else:
    print("Authentication Failed")
    