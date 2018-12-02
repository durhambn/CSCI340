#!/usr/bin/env python2.7
import os
from bs4 import BeautifulSoup
import requests
import urllib2
#import urllib.request
import re
import threading
from threading import Lock
import signal
import Queue
import heapq #by default this is a minheap, we will need to flip it
from collections import defaultdict

#CONFIG VARIABLES
MAX_CONNECTIONS = 300
MAX_THREADS = 3
MAX_RETRIES = 10

#GLOBAL VARIABLES
ACTIVE_THREADS = []
WORK_QUEUE = []
CURRENT_QUEUE_SIZE = 0
QUEUE_MUTEX = Lock()

LINKS_LIST = defaultdict(list)
RESULTS = []

#CONSTANTS 
QUIT = -1
GO = 0
UNSET = -1
SUCCESS = 0
FAILED = -1

## STOPLIGHT GOES ERWEREEEEREREREHH
msignal = QUIT  ##brakes on by default
##

# In order to sort our urls by something, we're creating this object
# the heapq function will run the __lt__ function to do its sorting therefor it's compatible
class PendingURL:
    url = "unset"
    currentdepth = UNSET
    maxdepth = UNSET
    threadID = UNSET

    def __init__(self, url, currentdepth, maxdepth, threadid):
        self.url = url
        self.currentdepth = currentdepth
        self.maxdepth = maxdepth
        self.threadid = threadid
    
    def __lt__(self, other):
        return self.currentdepth > other ## flipped to turn the minheap into a maxheap

def signal_handler(incomingsignal, frame):
    print('Signal Recieved, shutting down' + str(signal) + str(frame))
    global mSignal
    mSignal = QUIT
    sys.exit(0)

############################
#
# THREAD POOL CLASSES
#
### I was trying to put these in an object, but I can't figure out the scoping
### so that they can still access the parseURL method. Guess they stay here?

## Fire up the threads
def startAllThreads():
    global mSignal
    mSignal = GO
    count = 0
    while count is not MAX_THREADS:
        ACTIVE_THREADS.append(threading.Thread(target = workingThreadLooper, args = ()))
        ACTIVE_THREADS[-1].start()
        count += 1
                        
def stopAllThreads():
    global mSignal
    mSignal = QUIT
    for thread in ACTIVE_THREADS:
        thread.join()
    
def workingThreadLooper():
    global mSignal

    ##run until told not to
    while(mSignal is not QUIT):
        
        if (CURRENT_QUEUE_SIZE is not 0):
            myURL = heapq.heappop(WORK_QUEUE)         
            outcome = FAILED
            attempt = 0
            ## repeat attempts until something clicks
            while (outcome is not SUCCESS and attempt is not MAX_RETRIES):
                outcome = parseURL(myURL)
            if (outcome is not SUCCESS):
                print("html data from url " + myURL.url + " could not be retried after max retries")
       
    
#
# I've changed this to be using dummy values to make testing and whatnot far easier,
# It's just a bunch of hardcoded stuff, and it's just trying to get follow every link to the
# full depth every time. Our full functionanlity of having it only return links where
# the field is found can be cleanly built on top of this
#

def initialize():
    #signal.signal(signal.SIGINT, signal_handler)
    #signal.signal(signal.SIGTERM, signal_handler)
    
    site = ("http://compsci.cofc.edu/about/faculty-staff-listing/")
    print("Enter the target base URL... using - https://compsci.cofc.edu ")
    print("Enter the depth of links to be followed... using 1 ")
    depth = 2
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


# root recursive method, gets the ball rolling
def performSearch(url, maxdepth):
    print("starting search on site: " + url)

    baseurl = PendingURL(site,0,maxdepth,0)
    QUEUE_MUTEX.acquire();
    global CURRENT_QUEUE_SIZE
    CURRENT_QUEUE_SIZE += 1
    heapq.heappush(WORK_QUEUE,baseurl)
    QUEUE_MUTEX.release();
    
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


def parseURL(toParse):
    
    # this is where it will wait first for permission from the semaphore
    # to open a new connection
    # (just for debug) print("threadID: " + str(threadID) + " url: " + str(url) + ", currentdepth: " + str(currentdepth) + ", Requesting access to search critical section. ")

    connectionLimitingSemaphore.acquire()
    
    #print("threadID: " + str(threadID) + " url: " + str(url) + ", currentdepth: " + str(currentdepth) + ", Access granted from semaphore, parsing site. ")

    try:
        page = urllib2.urlopen(toParse.url).read()
    except Exception:
        print("Something broke when getting the url " + toParse.url + " - failed.")
        connectionLimitingSemaphore.release()
        return FAILED

    soup = BeautifulSoup(page,'html.parser')
    soup.prettify()

    connectionLimitingSemaphore.release()

    # grabs all links
    linksObject = soup.find_all('a', href= True)

    #Semaphore so only one thread can add to the list at a time
    searhingSemaphore.acquire()
    urlResults = []
    body = soup.get_text()
    addToResults = emailSearchRE(body) ## parses HTML for emails regex

    for i in range(len(addToResults)):        
        urlResults.append(toParse.threadID)
        urlResults.append(toParse.url)
        urlResults.append(addToResults[i])
        RESULTS.append(urlResults)

    searhingSemaphore.release()

    newIDscnt = toParse.threadID

    # QUEUES UP NEW URLS TO BE SEARCHED
    #
    # In this new version, the act of "doing" the work is separated from where it gets done
    # This loop finds every link that is to be explored, and adds it to the queue as needed
    #
    for link in linksObject:
        #print(link.get('href'))
        if(validateURL(toParse.url)):
            LINKS_LIST[toParse.threadID].append(link.get('href'))
            newIDscnt = newIDscnt + 1
            if (toParse.currentdepth+1 is not toParse.maxdepth):
                newURL = PendingURL(link.get('href'),toParse.currentdepth+1,toParse.maxdepth,newIDscnt)
                QUEUE_MUTEX.acquire();
                global CURRENT_QUEUE_SIZE
                CURRENT_QUEUE_SIZE += 1
                heapq.heappush(WORK_QUEUE,newURL)
                QUEUE_MUTEX.release();
        else:
            print("invalid url " + link + " detected, ignoring...")

    return SUCCESS


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

startAllThreads()
performSearch(site, depth)
stopAllThreads()

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
