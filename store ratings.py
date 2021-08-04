import time
import requests
import csv
import csv
from bs4 import BeautifulSoup

#Read the CSV file to get store addresses
with open("CT Store Addresses.csv") as csvfile:
    reader = csv.reader(csvfile, delimiter=",", quotechar='"')
    # next(reader, None)  # skip the headers
    csv_data = [row for row in reader]

#Declare a method to get the store rating
def getstore(link):
    try:
        r = requests.get(link)
    except:
        print("Something went bad, trying again in 5s")
        time.sleep(5)
        getstore(link)
    return r

outputFile = open("store ratings.csv", "w")
storeIndex = 0
Retries = 0
#Write the column headers
outputFile.write("Store Number,Google Rating\n")
#Iterate through the stores
for i in csv_data:
    if (storeIndex > 0):
        #Applying some half-assed URL encoding since we know there aren't any special characters in our data
        link = "https://www.google.com/search?q=canadian+tire+" + (i[1] + ' ' + i[2] + ' ' + i[7]).replace(" ", "+")
        try:
            r = getstore(link)
        #Getting the rating failed. Let's give the user the bad news!
        except:
            Retries = Retries + 1
            print("Something went bad getting " + link + ". " + str(storeIndex) + " failures so far.")
            if Retries < 10:
                print("Trying again in 5s")
                # Let's wait a bit in case the error was a temporary network issue
                time.sleep(5)
                r = getstore(link)
            else:
                print("Sorry! I give up!")
                break

        #Let's crawl Google's DOM and try to find the CSS classes used for the ratings
        data = r.text
        soup = BeautifulSoup(data, 'html.parser')
        span = soup.find('span', {'class': 'oqSTJd'})
        #Note that if Google changes their DOM/CSS classes this script will fail
        #If we don't find the first class, let's try an alternate
        if span is None:
            span = soup.find('span', {'class': 'Aq14fc'})
        #If we couldn't find the alternate then we should log the error
        if span is None:
            print('ERROR with ' + i[0], link)
            outputFile.write(i[0] + "," + "ERROR!" + "\n")
        #Success! Let's write that rating
        else:
            print(str(storeIndex) + " - " + i[0] + "," + span.text, link)
            outputFile.write(i[0] + "," + span.text + "\n")
    storeIndex = storeIndex + 1
    #Let's go easy on Google's servers and wait a bit before the next call
    time.sleep(0.25)
outputFile.close()

