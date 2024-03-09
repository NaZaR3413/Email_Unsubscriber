from googleapiclient.discovery import build
from quickstart import get_credentials  # Importing from quickstart.py
from bs4 import BeautifulSoup
import re
import base64
import email
from googleapiclient import errors
import utility
# import unsub_selenium
# from unsub_selenium import open_unsubscribe_links_in_safari
from selenium import webdriver
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
    Opens unsubscribe links from a list of emails in Safari using Selenium.
    """
    if not link:
        print("No unsubscribe links to open.")
        return

    driver = webdriver.Safari()
    driver.execute_script("window.open('{}');".format(link))
    print("link opened successfully")
    time.sleep(10)  # Time for the user to interact with the pages
    driver.quit()

def main(creds):
    emails = []
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
                
                utility.insert_email(emails, name, False, link) 
                count += 1
                print("\033[92mCounter: \033[0m" + str(count))

    print("emails list")
    utility.print_emails(emails)
    
# go through list, see if user wants to activate "is_clicked for any email"
    for email in emails:
        var = input("is clicked?: ")
        if(var == "yes"):
            # change is clicked to true
            utility.update_clicked_status(emails, email.name, True)
        
    # open links for any "is clicked" emails
    for email in emails:
        if email.is_clicked == True:
            open_unsubscribe_links_in_safari(email.link)
            
            
if __name__ == "__main__":
    main()
