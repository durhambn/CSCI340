#!/usr/bin/env python2.7
import os
from bs4 import BeautifulSoup
import requests
import urllib2
import re
import threading
import signal

#CONFIG VARIABLES
MAX_CONNECTIONS = 5

# using dummy values to make testing and whatnot far easier, also just having it go to max depth for now
# I've expanded the functionality of this method to just have it get everything we need
# the implication is that things like max_connections could be user input, or maybe not
# the initialize function just handles it all
def initialize():
    site = ("https://compsci.cofc.edu")
    print("Enter the target base URL... using - https://compsci.cofc.edu ")
    print("Enter the depth of links to be followed... using 1 ")
    depth = ("1")
    type(site)
    type(depth)
    return site, depth, MAX_CONNECTIONS

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
    return parseURL(url,0,maxdepth)

# method used to parse a given url link, recursively calling itself on any
# subordinate urls found
# returns address (link) and the address/number found
# truly 100% recursive, calls back to it's parent, and to it's parent's parent
# each parent's output is built upon by its child's output, incrementally
# until a full links object is returned by the root method

def parseURL(url, currentdepth, maxdepth):
    if(currentdepth >= maxdepth):
        print("url: " + url + ", max depth reached, returning...")
        return
    else:
        # this is where it will wait first for permission from the semaphore
        # to open a new connection
        print("url: " + url + ", currentdepth: " + str(currentdepth) + ", Requesting access to search critical section.")
        
        connectionLimitingSemaphore.acquire()
        
        print("url: " + url + ", currentdepth: " + str(currentdepth) + ", Access granted from semaphore, parsing site.")
        page = urllib2.urlopen(url).read()
        
        soup = BeautifulSoup(page,'lxml')
        soup.prettify()        

        for link in soup.find_all('a'):
            print(link.get('href'))
            
        connectionLimitingSemaphore.release()

        return link['href']
        

def writeLinks(linksList, outfile):
    print("attempting to write links to outfile: " + outfile)
    print("...not yet implemented.")

#gets user input and stores in vaiables

site, depth, maxconnections = initialize()
print("Website to search: " + site)
print("Depth of search: " + depth)
print("Max simulataneous connections: " + str(maxconnections))

connectionLimitingSemaphore = threading.BoundedSemaphore(maxconnections)

# recurse through all links, gathering the link object, using the provided signal handler
linksList = performSearch(site, depth)

# write the link object to the output file
writeLinks(linksList, outfile.txt)

"""
threads = []
for i in range(len(links)):
    threads.append(threading.Thread(target = threadTask, args = (links[i])))
    threads[-1].start()
for t in threads:
    t.join()
"""
