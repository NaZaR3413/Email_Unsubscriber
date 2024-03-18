from googleapiclient.discovery import build
from quickstart import get_credentials  # Importing from quickstart.py
from bs4 import BeautifulSoup
import requests
import re
import base64
import email
from googleapiclient import errors
import utility
# import unsub_selenium
# from unsub_selenium import open_unsubscribe_links_in_safari
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def search_emails(service, query, max_results=6):
    try:
        messages = []
        request = service.users().messages().list(userId='me', q=query, maxResults=500)
        response = request.execute()

        while request is not None and len(messages) < max_results:
            messages.extend(response.get('messages', []))
            request = service.users().messages().list_next(previous_request=request, previous_response=response)
            if request:
                response = request.execute()

        return messages[:max_results]
    except Exception as error:
        print(f"An error occurred: {error}")
        return []

def get_email_details(service, message_id):
    try:
        message = service.users().messages().get(userId='me', id=message_id, format='metadata').execute()
        headers = message.get('payload', {}).get('headers', [])

        details = {
            'From': next(header['value'] for header in headers if header['name'] == 'From'),
            'Subject': next(header['value'] for header in headers if header['name'] == 'Subject'),
            'Date': next(header['value'] for header in headers if header['name'] == 'Date')
        }

        return details
    except Exception as error:
        print(f"An error occurred: {error}")
        return None

def get_mime_message(service, user_id, msg_id):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
        msg_raw = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
        mime_msg = email.message_from_bytes(msg_raw)
        return mime_msg
    except errors.HttpError as error:
        print(f'An error occurred: {error}')

def find_unsubscribe_link(mime_msg):
    if mime_msg.is_multipart():
        for part in mime_msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if "text/html" in content_type and "attachment" not in content_disposition:
                html = part.get_payload(decode=True).decode()
                soup = BeautifulSoup(html, 'html.parser')
                for link in soup.find_all('a', href=True):
                    if 'unsubscribe' in link.text.lower():
                        return link['href']
    else:
        if "text/html" in mime_msg.get_content_type():
            html = mime_msg.get_payload(decode=True).decode()
            soup = BeautifulSoup(html, 'html.parser')
            for link in soup.find_all('a', href=True):
                if 'unsubscribe' in link.text.lower():
                    return link['href']
    return None

def extract_emails_from_content(email_content):
    # Regular expression pattern to find emails within < >
    pattern = r'<([^>]+)>'
    # Find all instances of the pattern in the email content
    found_emails = re.findall(pattern, email_content)
    # Return the list of found emails
    return found_emails

def open_unsubscribe_links_in_safari(link):
    """
    Opens unsubscribe links from a list of emails in Google using Selenium.
    opens with browswer 
    """
    if not link:
        print("No unsubscribe links to open.")
        return

    driver = webdriver.Chrome()
    driver.execute_script("window.open('{}');".format(link))
    print("link opened successfully")
    time.sleep(10)  # Time for the user to interact with the pages
    driver.quit()
        
        
def open_link_without_browswer(link):
    """
    Opens unsubscribe links in Chrome in headless mode using Selenium.
    """
    if not link:
        print("No unsubscribe links to open.")
        return 0
    
    # Set up Chrome options for headless execution
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")  # Optional, recommended for Windows
    options.add_argument('--log-level=3')  # This should suppress most of the informational messages


    # Initialize the Chrome driver with options
    driver = webdriver.Chrome(options=options)

    try:
        # open browserless window, give time to open and print if successful
        driver.execute_script("window.open('{}');".format(link))
        print("Link opened successfully")
        time.sleep(5)  # Time for the page to process if needed
        
        # confirm any activity
        if "success" in driver.current_url: # if success is in the current page url
            print("action appears to be succesful based on current url")
            driver.quit()
            return 1
        elif "unsubscribed" in driver.page_source or "Unsubscribed" in driver.page_source or "UNSUBSCRIBED" in driver.page_source: # if unsubscribe is found anywhere in the page itself
            print("action appers to be successful based on page contents")
            driver.quit()
            return 1
        else: # no clear indication found, requires user input 
            print("No clear success indicator found")
            driver.quit()
            return -1
            
    finally:
        driver.quit()

def main(creds):
    emails = [] # total list of emails 
    success_list = [] # list of all successful unsubscriptions
    unsucessful_list = [] # list of all unsucessful unsubscriptions
    
    service = build('gmail', 'v1', credentials=creds)

    query = 'unsubscribe'
    messages = search_emails(service, query)

    count = 0

    if not messages:
        print("No emails found.")
        return

    print("Emails containing 'unsubscribe':")
    for message in messages:
        details = get_email_details(service, message['id'])
        name = re.search(r'<(.*?)>', details.get('From', ''))
        str(name)
        if details:
            mime_msg = get_mime_message(service, 'me', message['id'])
            if mime_msg:
                link = find_unsubscribe_link(mime_msg)
                str(link)
                                
                utility.insert_email(emails, name, False, link) 
                count += 1
                print("\033[92mCounter: \033[0m" + str(count))

    print("emails list")
    utility.print_emails(emails)
    
# go through list, see if user wants to activate "is_clicked for any email"
    for email in emails:
        print("\nfor " + email.name)
        var = input("is clicked?: ")
        if(var == "yes"):
            # change is clicked to true
            utility.update_clicked_status(emails, email.name, True)
        
    # open links for any "is clicked" emails
    for email in emails:
        if email.is_clicked == True:
            print("\ncurrent email: " + email.name)
            #open_unsubscribe_links_in_safari(email.link)
            link_verifier = open_link_without_browswer(email.link)
            
            if link_verifier == 1: # add to success list if successful unsubscription 
                utility.insert_email(success_list, email.name, email.is_clicked, email.link)
            elif link_verifier == -1: # add to unsuccessful list of unsucessful unsubscription
                utility.insert_email(unsucessful_list, email.name, email.is_clicked, email.link)
            elif link_verifier == 0: # no link case
                print("ERROR: No link available")
            else:
                print("ERROR: unexpected return: open_link_without_browser")
                
            
            
if __name__ == "__main__":
    main()
