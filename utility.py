import bisect
import re
# List Node
class EmailInfo:
    def __init__(self, name, count, is_clicked, link):
        self.name = str(name) if isinstance(name, re.Match) else name
        self.count = count
        self.is_clicked = is_clicked
        self.link = link

    # for alphabetical order purposes
    def __lt__(self, other):
        return self.name < other.name

# adjust inputted name into proper format
def get_proper_name(name):
  # If 'name' is a match object, extract the matched string
  if isinstance(name, re.Match):
      name = name.group()

  # Now 'name' is a string, and you can use the 'find' method
  beginning = name.find('<', name.find('<') + 1) + 2
  end = name.find('>', beginning)
  return name[beginning:end]

# Insert function. Checks if email is in list, count++ if it is.
# Adds new email if not in list
def insert_email(emails, name, _is_checked, link):
  # verify emails is a string, name and count are int, ischecked bool
  # this should be done in a try/catch before calling the method to 
  #ensure smooth running

  # edit name to proper format ** changed over to unsub emails portion
  _name = get_proper_name(name)

  # add relevant info to an email node
  # NOTE: count should default to 1 as we do not know if the name already exists or not
  # NOTE: _is_checked should also be defaulted to false, same reasons.
  _count = 1

  email_info = EmailInfo(_name, _count, _is_checked, link)

  # If list is empty, add email to list 
  if not emails:
    emails.append(email_info)
    return

  #iterate through emails list, add new email if not found.
  # Position contains location of email if it exists, -1 if it does not
  position = find_email_node_position(emails, email_info)
  if position == -1: # If email is not found, add it to the list
    bisect.insort(emails, email_info)
  else: # If found, increment count
    emails[position].count += 1


# Function to find a position of node in the emails list 
# bisect_left uses a binary search with O(logn) complexity, if i did it right
def find_email_node_position(emails, email_info):
  # Assign position of email to i
  i = bisect.bisect_left(emails, email_info)
  if i != len(emails) and emails[i].name == email_info.name:
    return i
  else:
    return -1

# Don't think it will be necessary, but method to find position 
# of a name in an emails list
def find_email_name_position(emails, _name):
  low, high = 0, len(emails) - 1

  while low <= high:
      mid = (low + high) // 2
      mid_name = emails[mid].name

      if mid_name < _name:
          low = mid + 1
      elif mid_name > _name:
          high = mid - 1
      elif mid_name == _name:
          return mid  # Found the position

  return -1  # Name not found


# Function to print list of all emails in email list
def print_emails(emails):
    for email in emails:
      print(email.name, email.count, email.is_clicked)

# Function to form a list of all true "is_clicked" nodes and return them
def get_clicked_emails(emails):
  # iterates over each email in emails list, returns everything that 
  # is_clicked 
  return [email for email in emails if email.is_clicked]

# If we ever wanted to sort our list by count 
def sort_emails_by_count(emails):
  emails.sort(key=lambda email: email.count)

# Sortng back to alphabetically 
def sort_emails_alphabetically(emails):
  emails.sort(key=lambda email: email.name)

# Sorting based off of is_clicked
def sort_emails_by_clicked(emails):
  emails.sort(key=lambda email: email.is_clicked, reverse=True)

# Update is_clicked when needed
def update_clicked_status(emails, _name, _status):
  # status being a bool, name a string, emails the initial list
  
  # find the position of the email using defined sorting algorithm
  pos = find_email_name_position(emails, _name)
  
  # veriy it is found. update status if it is
  if(pos != -1):
    emails[pos].is_clicked = _status
  else:
    print("Update_clicked_status ERROR: update name not found") # print an error if name not in list