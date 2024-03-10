import requests
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from unsub_emails import main as unsub_emails_main
from quickstart import get_credentials
from selenium import webdriver
import time
import os  # Needed for checking the existence of token.json

def main():
    # validate credentials 
    creds = get_credentials()
    
    #switch variable for while
    state = 0
    layout_menu()
    while(state != 4):
        state = input("Please enter an option: ")
        state = int(state)
        
        match state:
            case 1: # unsub
                unsubscribe_links = unsub_emails_main(creds)
                print("unsub success")
                layout_menu()
            case 2: # label 
                print("label success")
            case 3: #print menu
                layout_menu()
            case 4: # quit 
                break
            case _: # default 
                print("Please enter a valid option.")

    
    # Check for token.json for successful login
    if 'token.json':
        print("\033[92mLogin Successful\033[0m")
    else:
        print("Authentication Failed")
    
def layout_menu(): #displayed menu for all available options. Top line highlighted in green
    print("\033[92mPlease select a number from the options below:\033[0m")
    print("Unsubscribe from emails: \t1")
    print("Manage labels: \t\t\t2")
    print("Print menu: \t\t\t3")
    print("Quit: \t\t\t\t4")
    
if __name__ == "__main__": #start at main()
    main()