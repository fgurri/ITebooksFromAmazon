'''
Web scraping of kindle books from Amazon
Here is the detailed process:
	1) first access to get number of pages to link
	2) for each page, download page and
		2.1) convert html to a tree using lxml library
		2.2) access to elements identified by unique class in html tag
		2.3) access to the other elements by manually seeking its position in rows, tags, etc
		2.4) we stop the process 10 seconds in each iteration to avoid being blocked
	3) save stored array of dictionaries to a csv 'results.csv' in current folder
General considerations:
	- Python 3.6.5 used
	- libraries unidecode, requests, lxml and cssselect needed
	- User-agent set to Mozilla/5
	- csv is ";" separated, single access needed, be sure to close it while running this script
	- for 163 pages (April 2018), script runs for about 20 minutes
	- title and author names are unidecoded to avoid problems with some language specific characters
'''
import requests
import urllib.request
from urllib.request import Request, urlopen
import lxml.html
import csv
from time import sleep
from unidecode import unidecode

q = Request ('https://www.amazon.es/s/ref=lp_1335562031_pg_2?rh=n%3A818936031%2Cn%3A%21818938031%2Cn%3A827231031%2Cn%3A1335562031&page=1&ie=UTF8&qid=1522334970')
#setting user agent to avoid being blocked
q.add_header('User-agent', 'Mozilla/5.0')
#first acces, just to calculate number of pages
html = urllib.request.urlopen(q).read()
tree = lxml.html.fromstring(html)
#get total pages
totalpages = tree.cssselect('span.pagnDisabled')[0].text_content()
print (totalpages)
#initialize array to store results
results = []

#loop through all pages
#totalpages = '1'
for k in range(1, int(totalpages)+1):
	print(' ------------------------- downloading page ' + str(k) + ' of ' + totalpages + ' ------------------------- ')
	#dynamically contruct the url using the atribute pages
	q = Request ('https://www.amazon.es/s/ref=lp_1335562031_pg_2?rh=n%3A818936031%2Cn%3A%21818938031%2Cn%3A827231031%2Cn%3A1335562031&page=' + str(k) + '&ie=UTF8&qid=1522334970')
	#setting user agent to avoid being blocked
	q.add_header('User-agent', 'Mozilla/5.0')
	html = urllib.request.urlopen(q).read()
	# html = urllib.request.urlopen('https://www.amazon.es/s/ref=lp_1335562031_pg_2?rh=n%3A818936031%2Cn%3A%21818938031%2Cn%3A827231031%2Cn%3A1335562031&page=' + str(k) + '&ie=UTF8&qid=1522334970').read()
	tree = lxml.html.fromstring(html)
	#get list of results
	elements = tree.cssselect('ul.s-result-list > li.s-result-item')

	for e in elements:
		#get title
		title = e.cssselect('h2.s-access-title')[0].text_content() 
		print (title)
		#get prize
		prize = e.cssselect('span.s-price')[0].text_content()
		#format "EUR NNN", we discard the text
		prize = prize[4:]
		print (prize)
		#get stars
		l_stars = e.cssselect('span.a-icon-alt')
		if not l_stars:
			#no ratings yet
			stars = 'NA'
			rates = 0
		else:
			stars = l_stars[0].text_content()
			#format is "NN de un maximo de 5", we get the substring till first blank
			stars = stars.split(' ', 1)[0]
			#get quantity rates
			rates = e.cssselect('div.a-span5')[0].cssselect('a.a-link-normal')
			if rates: 
				rates = rates[0].text_content()
			else:
				rates = 0
			print(rates)
		print (stars)
		#get rows content for fetching
		#we need to manually select rows because not all elements have unique class or id to filter for
		l_rows = e.cssselect('div.a-row')
		#get publish date
		date = l_rows[1].cssselect('span.a-size-small')
		if date:
			date = date[0].text_content()
		else:
			date = 'NA'
		print(date)
		#get authors
		l_author = l_rows[3].cssselect('span.a-size-small')
		author = ''
		#first element is "de ", so we discard it
		if l_author:
			l_author.pop(0)
		for a in l_author:
			author = author + a.text_content()
		#author = author[3:]
		print(author)
		#unidecode to avoid problems with some language specific characters
		title = unidecode(str(title))
		author = unidecode(str(author))
		#add dictionary to result
		results.append({'title': title, 'prize': prize, 'ratings': rates, 'stars': stars, 'publish_date': date, 'authors':author})
	#delay to avoid being blocked	
	sleep(10)
	
#create csv and insert all dictionary rows
with open('ITebooksFromAmazon.csv', 'w', newline='') as csvfile:
	fieldnames = ['title', 'prize', 'ratings', 'stars', 'publish_date', 'authors']
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=";")
	writer.writeheader()
	for row in results:
		writer.writerow(row)