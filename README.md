### CSCI340 FINAL PROJECT: Site Searching Spider ###

Python Searching Website Spider/Crawler created by Brandi Durham and John Quinn

For our final project, we wanted to create a python program that allows a user to input a web 
url and a search input and have our program give back all occurences of the search input on the 
website. We plan to use python to write the script, and have it initially where the user can 
input an email address to search for on the site. Our program will seach a certain depth of pages on the website.
In the future, we would like to have it where the user can choose which option they would like to 
search for: email address, phone number, or name. 
At this time the user can search for an email address, phone number, or get a list of all emails on the site.   
For the users benefit, we also collected every link that is on the site and stored in a seperate outfile.txt.

### DEPENDENCIES ###

developed with python 2.7 and on ubuntu 16.04 LTS

pip install requests
            beautifulsoup4

### TECHNICAL OVERVIEW ###

This software utilizes three advanced features as specified in our assignment documentation:

    Multithreading - urls are parsed simultaneously, utilizing a user-defined depth. Each
        parsing instance of the Crawler will create new instances up to this defined depth.

    Semaphores - due to the possibility of hundreds of parsing instances attempting to run
        simultaneously, there will be a critical section imposed on code which launches new
        instances, which will be regulated by a semaphore. Requests for new instances will
        be sent to this section of code. Depth numbers exceeding the specified depth will not be
        honored. Requests for URLS outside the specified target will not be honored.

    Signal Handlers - it's possible that selected urls will fail to resolve, with the likelihood
        of this occurring becoming significant when analyzing large websites. As a result, the
	application will respond to error signals from the parsing threads, and retry the
	parse operations as appropriate


  
  

  
