import os
#from bs4 import BeautifulSoup
import urllib2
import re



#method used to get input from user
#return user choice: email or phone number
#the address or number to seach
def getInput():
    site = raw_input("Enter the URL you'd like to search: ")
    type(site)
    print("1: Email Address")
    print("2: Phone Number")
    num = input("Which would you like to find? ")
    type(num)
    #print num
    if(num == 1):
        search = raw_input("Enter the email address you'd like to search for: ")
        type(search)
        #print search
        return site, num, search
    elif(num ==2):
        search = raw_input("Enter the phone number you'd like to seach for: ")
        type(search)
        #print search
        return site, num, search
    else:
        #print ("Not a valid number ... exiting")
        sys.exit("Not a valid number ... exiting")




#method used to get the source code from the
#website entered by user
#return source code
def callSite(url):
    response = urllib2.urlopen(url)
    pageSource = response.read()
    print(pageSource)
    return pageSource

#pass in source code and find all the links on the website
#return list of all the links in source code
def getLinks(sourcecode):
    links = []




#method used to seach website for getInput
#return address (link) and the address/number found
def searchSite():



#pass in info found and make output file
#with link and stuff found
def makeTable():



#gets user input and stores in vaiables
site, num, search = getInput()
print("Website to search: " + site)
print("Type of search: " + str(num))
print("Searching for: " + search)
# get the source code of the main site
pageSource = callSite(site)
#get all the links from the main site
links = getLinks(pageSource)
