#!/usr/bin/env python2.7
import os
from bs4 import BeautifulSoup
import requests
import urllib2
import re
import threading




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
    #response = urllib2.urlopen(url)
    #pageSource = response.read()

    html = requests.get(url).text
    pageSource = BeautifulSoup(html, "html.parser")
    pageSource.prettify()
    #print(pageSource)
    return pageSource

#pass in source code and find all the links on the website
#return list of all the links in source code
def getLinks(sourcecode):
    list = []
    #links = sourcecode.find_all('a')
    #finalLinks = set()
    for link in sourcecode.find_all('a', href=True):
        list.append(link['href'])
        #finalLinks.add(link.attrs['href'])
    return list


#This will call all the methods that each thread needs to do
#and return a tuplet of (link, address or amount)
def threadTask(url):
    searchSite(url)
    #links = getLinks(callSite(url))
    #print("links found at url: " + links)



#method used to seach website for getInput
#return address (link) and the address/number found
def searchSite(num, search, url):
    print("searching this site: " + url)
    sourceCode = callSite(url)
    #print(sourceCode)
    #soup = BeautifulSoup(sourceCode, 'html.parser')
    text = sourceCode.get_text()
    #text = text.split()
    #1 is email address and 2 is phone number
    if(num == 1):
        if search in text:
            print(url + " : " + search)
        else:
            print(url + " : " + search + " not found")
    elif(num ==2):
        if search in text:
            print(url + " : " + search)
        else:
            print(url + " : " + search + " not found")



#pass in info found and make output file
#with link and stuff found
#def makeTable():



#gets user input and stores in vaiables
site, num, search = getInput()
print("Website to search: " + site)
print("Type of search: " + str(num))
print("Searching for: " + search)
# get the source code of the main site
pageSource = callSite(site)
#print(pageSource)
#get all the links from the main site
links = getLinks(pageSource)
#print(links)
'''
for i in range(len(links)):
    str(i) = threading.Thread(target = threadTask, args = (links[i]), name = str(i))
for i in range(len(links)):
    str(i).start()
for i in range(len(links)):
    str(i).join()
'''
searchSite(num, search, site)

threads = []
for i in range(len(links)):
    threads.append(threading.Thread(target = threadTask, args = (links[i])))
    threads[-1].start()
for t in threads:
    t.join()
'''
executor = concurrent.futures.ProcessPoolExecutor(10)
futures = [executor.submit(threadTask, item) for item in links]
concurrent.futures.wait(futures)
'''
#implement threads for each link on main page?
#thread will call getLinks to find links on new pageSource
#will call search site to seach for user address
