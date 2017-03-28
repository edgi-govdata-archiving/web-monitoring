import csv
import requests
from lxml import html
import re

filepath = 'wiki_env.csv'
writer=csv.writer(open(filepath,'ab'))  #ab = append binary file

url = 'https://en.wikipedia.org/wiki/Glossary_of_environmental_science'

for i in range(0,1):
	response = requests.get(url)# headers=headers,cookies=cookies
	
	tree = html.fromstring(response.content) #parse the html response content

	for j in range(1,27):
		env_word_value = tree.xpath('//*[@id="mw-content-text"]/ul['+str(j)+']/li[*]/b/a/text()')  #retrieve environmental words using XPath
		if not env_word_value:
			env_word_value=['empty']
		env_word = [word.encode('utf-8').strip() for word in env_word_value] #convert into UTF-8 encoding and removing blanks,spaces, etc
		writer.writerow(env_word)				#store into csv
	
#sample Xpath expressions		
	# //*[@id="mw-content-text"]/ul[1]/li[1]/b/a
	# //*[@id="mw-content-text"]/ul[1]/li[2]/b/a
	# //*[@id="mw-content-text"]/ul[2]/li[2]/b/a
	# //*[@id="mw-content-text"]/ul[26]/li/b/a
