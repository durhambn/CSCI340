#!/usr/bin/env python2.7
import os
from bs4 import BeautifulSoup
import requests
import urllib2
#import urllib.request
import re
import threading
import signal
from collections import defaultdict


#CONFIG VARIABLES
MAX_CONNECTIONS = 300

#GLOBAL VARIABLES
ACTIVE_THREADS = []
LINKS_LIST = defaultdict(list)
RESULTS = []

# This is a signal handler class, registered to the signals as defined below in it's constructor
# It's currently not used. Apparently signal handlers must always be accessed from the main thread
# so that is what this is about
class SignalHandler:
    def __init__(self):
        signal.signal(signal.SIGINT, self.shutdown_threads)
        signal.signal(signal.SIGTERM, self.shutdown_threads)

    def shutdown_threads(self, signum, frame):
        print("Shutdown signal received, not yet implemented...")

#
# I've changed this to be using dummy values to make testing and whatnot far easier,
# It's just a bunch of hardcoded stuff, and it's just trying to get follow every link to the
# full depth every time. Our full functionanlity of having it only return links where
# the field is found can be cleanly built on top of this
#

def initialize():
    site = ("http://compsci.cofc.edu/about/faculty-staff-listing/")
    print("Enter the target base URL... using - https://compsci.cofc.edu ")
    print("Enter the depth of links to be followed... using 1 ")
    depth = 1
    type(site)
    type(depth)
    return site, depth, MAX_CONNECTIONS
    print("1: Email Address")
    print("2: Phone Number")
    print("3: All emails")
    num = input("Which would you like to find? ")
    type(num)
    #print num
    if(num == 1):
        search = raw_input("Enter the email address you'd like to search for: ")
        type(search)
        #print search
        return site, depth, MAX_CONNECTIONS, num, search
    elif(num ==2):
        search = raw_input("Enter the phone number you'd like to seach for: ")
        type(search)
        #print search
        return site, depth, MAX_CONNECTIONS, num, search
    elif(num ==3):
        print("Searching all emails")
        search = "email"
        return site, depth, MAX_CONNECTIONS, num, search
    else:
        #print ("Not a valid number ... exiting")
        sys.exit("Not a valid number ... exiting")

#
# big complicated regex function taken from django that just makes sure it's a valid url
# I emailed Munsell about whether or not it's okay for us to use it, we can find another way to
# validate the URL's if needed. This one just werks(TM)
#
# returns: true or false
#

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

# root recursive method, gets the ball rolling
def performSearch(url, maxdepth):
    print("starting search on site: " + url)
    parseURL(url,0,maxdepth,0);
    return


def emailSearchRE(html):
    #print(html)
    emails = re.findall(r'[\w\.-]+@[\w\.-]+',html)
    '''
    for i in emails:
        print (i)
        '''
    return emails

#
# The big "does stuffs" method, which parses a given url link, recursively calling itself on any
# subordinate urls found. The multithreading magic happens in the way this method recursively functions:
# each URL it finds and deems to be valid will spawn a thread to follow that url, calling another instance
# of this same function. At the end of the method, the thread will wait ala thread.join() on each of its
# child threads.
#
# In this manner, the spider threads tend to explode outwards, with each parent waiting on it's respective
# children. This is opposed to the main thread managing all children
#


def parseURL(url, currentdepth, maxdepth, threadID):

    # this is that key recursive "stopping" statement, which stops this thing from running forever
    if(currentdepth >= maxdepth):
        #print("url: " + str(url) + ", max depth reached, returning...")
        return
    else:
        # this is where it will wait first for permission from the semaphore
        # to open a new connection

        # (just for debug) print("threadID: " + str(threadID) + " url: " + str(url) + ", currentdepth: " + str(currentdepth) + ", Requesting access to search critical section. ")

        connectionLimitingSemaphore.acquire()

        #print("threadID: " + str(threadID) + " url: " + str(url) + ", currentdepth: " + str(currentdepth) + ", Access granted from semaphore, parsing site. ")

        ## this is the only part of this program that actually causes the network call. Arguably the critical section could be limited to this one line
        page = urllib2.urlopen(url).read()

        #changed to html.parser because xlml didn't work for me
        #html.parser is standard
        soup = BeautifulSoup(page,'html.parser')
        soup.prettify()

        connectionLimitingSemaphore.release()

        # grabs all links
        #linksObject = soup.find_all('a')
        linksObject = soup.find_all('a', href= True)


        #Semaphore so only one thread can add to the list at a time
        searhingSemaphore.acquire()
        urlResults = []
        body = soup.get_text()
        addToResults = emailSearchRE(body)

        for i in range(len(addToResults)):
            urlResults.append(threadID)
            urlResults.append(url)
            urlResults.append(addToResults[i])
            RESULTS.append(urlResults)

        searhingSemaphore.release()

        threads = []
        newIDscnt = threadID

        # as mentioned above, this is where the concurrency kicks in. the parent creates a thread for every valid link it finds
        # because this would spawn over a hundred threads easily on one major page alone, this is why that network call limiter is so important
        # try playing with the semaphore and you'll notice your computer does NOT like all those network calls. websites might ban you too :)
        for link in linksObject:
            #print(link.get('href'))
            if(validateURL(url)):
                LINKS_LIST[threadID].append(link.get('href'))
                newIDscnt = newIDscnt + 1
                threads.append(threading.Thread(target = parseURL, args = (link.get('href'),currentdepth+1,maxdepth,newIDscnt)))
                threads[-1].daemon=True
                threads[-1].start()
            else:
                print("invalid url " + link + " detected, ignoring...")

        for t in threads:
            t.join()


def writeLinks(linksList, outfile):
    file =open(outfile, "w")
    for threadID in LINKS_LIST:
        print(threadID)
        file.write("At Depth: " + str(threadID) + "\n")
        for entry in LINKS_LIST[threadID]:
            file.write(str(entry) + " \n ")
    #file.write(linksList)
    print("Writing links to outfile: " + outfile)
    #print("...not yet implemented.")
    file.close()

def writeResults(results, outfile):
    file2 = open(outfile, "w")
    i = 0
    print("len of results: " + str(len(results)))
    while(i< (len(results)-3)):
        string = (str(results[i]) +" " +  str(results[i+1]) + " " +  str(results[i+2]) + "\n")
        file2.write(string)
        i=i+3
    file2.close()

#############################################################################3
#
#  WHERE THE MAGIC HAPPENS
#
############

#gets user input and stores in vaiables
#add num and search
site, depth, maxconnections= initialize()
print("Website to search: " + site)
print("Depth of search: " + str(depth))
print("Max simulataneous connections: " + str(maxconnections))
print

connectionLimitingSemaphore = threading.BoundedSemaphore(maxconnections)
searhingSemaphore = threading.BoundedSemaphore(1)

# recurse through all links, gathering the link object, using the provided signal handler
ACTIVE_THREADS.append(threading.Thread(target = performSearch, args = (site,depth)))
ACTIVE_THREADS[-1].daemon=True
ACTIVE_THREADS[-1].start()

performSearch(site, depth)
ACTIVE_THREADS[0].join()

print("Final returned list.")

# returned full list
#for threadID in LINKS_LIST:
    #for entry in LINKS_LIST[threadID]:
        #print(entry)
if(len(RESULTS) ==0):
    print("There were no emails found at depth " + str(depth))
else:
    writeResults(RESULTS, "results.txt")
    #print(RESULTS)
# write the link object to the output file

writeLinks(LINKS_LIST, "outfile.txt")
