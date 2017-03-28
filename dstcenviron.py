import csv
import requests
from lxml import html
import re

filepath = 'dstc_env_word.csv'
writer=csv.writer(open(filepath,'ab')) #ab = append binary file

url = 'http://www.dtsc.ca.gov/InformationResources/Glossary_of_Environmental_Terms.cfm'

for i in range(0,1):
	response = requests.get(url)# headers=headers,cookies=cookies
	
	tree = html.fromstring(response.content) #parse the html response content
	
	for j in range(462752,462754):
		env_word_value = tree.xpath('//*[@id="cs_control_'+str(j)+'"]/div/span/p[*]/strong/text()') #retrieve environmental words using XPath
		if not env_word_value:
			env_word_value=['empty']
		env_word = [word.encode('utf-8').strip() for word in env_word_value] #convert into UTF-8 encoding and removing blanks,spaces, etc
		writer.writerow(env_word)		#store into csv

#sample Xpath values from HTML page
# //*[@id="cs_control_462752"]/div/span/p[4]/strong
# //*[@id="cs_control_462752"]/div/span/p[5]/strong

# //*[@id="cs_control_462752"]/div/span/p[69]/strong

# //*[@id="cs_control_462753"]/div/span/p[9]/strong

# //*[@id="cs_control_462753"]/div/span/p[170]/strong
