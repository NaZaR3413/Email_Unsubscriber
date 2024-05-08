Program to mass unsubscribe from gmail emails. We are not liable for anything related to how this program is used.
This program only contains code for gmail

key notes:
- Google API needed, the credentials posted on this project are not valid. Replace with your own.
    - The imports should still be the same for the google API, but in the event that google undates how they do it, you will need to 
        adjust the imporst at the top of the applicable files as needed.
- Functionality to add/remove labels, and mass move emails not included. Simple setup is still here in main,
    but our own code for that is included in the official project.
- 

Instructions:
In the terminal: Python main.py 
## the above instruction will open a tab that will confirm your gmail account. If valid, it will progress. 

NOTE: The program will go through and scan for every email that contains an unsubscribe link. After the scan is finished, 
    it will present them to you one by one, where you will have to enter "yes" if that is an email provider you want to unsubscribe from. Anything else 
    will indicate that you want to keep recieving emails from that provider.

NOTE: In the unsub_emails.py file, on line 16 in the heading of the search_emails function, you will see a "max_results = 6". This 6
    is the max number of different emails with an unsubscribe link that the program will look for, adjust accordingly.
    In the same file, there is a headless and non headless method, headless meaning no browswer will be opened when the program 
    goes through and unsubscribes. This prevents mass browswers from opening, however if you wanted the browsers to open for whatever 
    reason, comment out line 191-200, and uncomment 190. 

NOTE: utility.py contains the algorithms we used to manage our email lists. No adjustment is needed for the program to work.