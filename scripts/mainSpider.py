#!/usr/bin/env python2.7
import os
from bs4 import BeautifulSoup
import requests
import urllib2
import re
import threading
import signal
from collections import defaultdict

#CONFIG VARIABLES
MAX_CONNECTIONS = 500

#GLOBAL VARIABLES
ACTIVE_THREADS = []
LINKS_LIST = defaultdict(list)

# This is a signal handler class, registered to the signals as defined below in it's constructor
# It's currently not used. Apparently signal handlers must always be accessed from the main thread
class SignalHandler:
    def __init__(self):
        signal.signal(signal.SIGINT, self.shutdown_threads)
        signal.signal(signal.SIGTERM, self.shutdown_threads)

    def shutdown_threads(self, signum, frame):
        print("Shutdown signal received, not yet implemented...")
            
# 
# I've changed this to be using dummy values to make testing and whatnot far easier,
# It's just a bunch of hardcoded stuff, and it's just trying to get every link to the
# full depth every time. Our full functionanlity of having it only return links where
# the field is found can be cleanly built on top of this
#

def initialize():
    site = ("https://compsci.cofc.edu")
    print("Enter the target base URL... using - https://compsci.cofc.edu ")
    print("Enter the depth of links to be followed... using 1 ")
    depth = (1)
    type(site)
    type(depth)
    return site, depth, MAX_CONNECTIONS

# big complicated regex function taken from django that just makes sure it's a valid url
#
# returns: true or false
def validateURL(url):
    if url is None:
        return False
    
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://n
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return re.match(regex,url) is not None

"""    
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
"""

#This will call all the methods that each thread needs to do
#and return a tuplet of (link, address or amount)
def threadTask(url):
    searchSite(url)
    #links = getLinks(callSite(url))
    #print("links found at url: " + links)

# root recursive method, gets the ball rolling
def performSearch(url, maxdepth):
    print("starting search on site: " + url)   
    ACTIVE_THREADS.append(threading.Thread(target = parseURL, args = (url,0,maxdepth,0)))
    ACTIVE_THREADS[-1].daemon=True
    ACTIVE_THREADS[-1].start()
    return 

# method used to parse a given url link, recursively calling itself on any
# subordinate urls found
# returns address (link) and the address/number found
# truly 100% recursive, calls back to it's parent, and to it's parent's parent
# each parent's output is built upon by its child's output, incrementally
# until a full links object is returned by the root method

def parseURL(url, currentdepth, maxdepth, threadID):
    if(currentdepth >= maxdepth):
        print("url: " + str(url) + ", max depth reached, returning...")
        return
    else:
        # this is where it will wait first for permission from the semaphore
        # to open a new connection
        # print("threadID: " + str(threadID) + " url: " + str(url) + ", currentdepth: " + str(currentdepth) + ", Requesting access to search critical section. ")
        
        connectionLimitingSemaphore.acquire()
        
        print("threadID: " + str(threadID) + " url: " + str(url) + ", currentdepth: " + str(currentdepth) + ", Access granted from semaphore, parsing site. ")
        page = urllib2.urlopen(url).read()
        
        soup = BeautifulSoup(page,'lxml')
        soup.prettify()
        
        connectionLimitingSemaphore.release()

        linksObject = soup.find_all('a')
        
        threads = []
        newIDscnt = threadID
        
        for link in linksObject:            
            print(link.get('href'))
            if(validateURL(url)):
                LINKS_LIST[threadID].append(link.get('href'))
                newIDscnt = newIDscnt + 1
                threads.append(threading.Thread(target = parseURL, args = (link.get('href'),currentdepth+1,maxdepth,threadID)))
                threads[-1].daemon=True
                threads[-1].start()
            else:
                print("invalid url " + link.get('href') + " detected, ignoring...")

        for t in threads:
            t.join()

def writeLinks(linksList, outfile):
    print("attempting to write links to outfile: " + outfile)
    print("...not yet implemented.")

#gets user input and stores in vaiables

site, depth, maxconnections = initialize()
print("Website to search: " + site)
print("Depth of search: " + str(depth))
print("Max simulataneous connections: " + str(maxconnections))

connectionLimitingSemaphore = threading.BoundedSemaphore(maxconnections)

# recurse through all links, gathering the link object, using the provided signal handler
performSearch(site, depth)

ACTIVE_THREADS[0].join()

print("Final returned list.")

# returned full list
for threadID in LINKS_LIST:
    for entry in LINKS_LIST[threadID]:
        print(entry)

# write the link object to the output file
writeLinks(LINKS_LIST, "outfile.txt")
