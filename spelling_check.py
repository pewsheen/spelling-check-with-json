import re, os
import json
import time
import enchant
from enchant.checker import SpellChecker
from enchant.tokenize import EmailFilter, URLFilter
from fluentmail import *

# Global Settings #
pathList = ['D:\\word1.json', 
	'D:\\word2.json']

debugMode = False

def remove_HTML_tags(text):
	# Replace HTML tags with an empty string.
	result = re.sub("<.*?>", " ", text)
	return result

def remove_HTML_encode(text):
	# Replace HTML tags with an empty string.
	result = re.sub("&lt;", " ", text)
	return result

def remove_variable(text):
	# Replace HTML tags with an empty string.
	result = re.sub("(\$t\(.*?\))|(__.*?__)|(^--.*?--$)", " ", text)
	return result

def remove_han(text):
	result = text
	for n in re.findall(ur'[\u4e00-\u9fff]+',text):
		result = re.sub(n, " ", result)
	return result

def spellingCheck(jsonPath):
	inputTypo = {}

	input_file  = file(jsonPath, "r")
	inputWord = json.loads(input_file.read().decode("utf-8"))

	for key in inputWord :
		text = inputWord[key]
		# print 'TEXT: ' + text
		filterText = remove_variable(remove_HTML_tags(remove_HTML_encode(remove_han(text))))
		# print 'FILTERED: ' + filterText
		chkr.set_text(filterText)
		
		errList = []

		if debugMode:
			for err in chkr:
				# print (err.word)
				errList.append(err.word)

			if len(errList) > 0 :
				print 'TEXT: ' + text

				err_string = ''
				for item in errList:
					err_string += item + ' '
				print 'Typo: ' + err_string
				print '--------------------------------------------------'
		else:
			for err in chkr:
				errList.append(err.word)

			if len(errList) > 0 :
				inputTypo[key] = {}
				inputTypo[key]['typo'] = errList
				inputTypo[key]['text']  = text
	return inputTypo

def createTypoTable(inputTypo, filename):
	typoTable = ''
	if len(inputTypo) > 0 :
		typoTable = '\
			<h1>'+filename+' Typo<h1>\
			<table class="tg">\
				<tr>\
					<th class="tg">Key</th>\
					<th class="tg">String</th>\
				</tr>';

		for key in inputTypo:
			resultText = inputTypo[key]['text']
			for typo in inputTypo[key]['typo']:
				resultText = resultText.replace(typo, '<font color="red">'+typo+'</font>')
			
			typoTable += '\
			<tr class="tg">\
				<td class="tg">'+key+'</td>\
				<td class="tg">'+resultText+'</td>\
			</tr>'

		typoTable += '</table>'

	return typoTable

def sendMail(mailHTMLContent):
	mail = FluentMail('smtp.mail.com', 587, TLS)

	mail.credentials('key', 'secret')\
		.from_address('ME <ME@mail.com.tw>')\
		.to('YO <yo@mail.com.tw>')\
		.subject('Spelling Check Result')\
		.body(mailHTMLContent)\
		.as_html()\
		.send()

def runSpellingCheck(pathList):
	mailHTMLContent = ''
	mailHeader 		= ''
	mailTable 		= ''

	checkTime = time.strftime("%Y/%m/%d")

	mailHeader = '\
		<head>\
			<meta charset="UTF-8">\
		</head>\
		<h1>Spelling Check Result '+checkTime+'</h1>\
		<style type="text/css">\
			.tg  {border-collapse:collapse;border-spacing:0;}\
			.tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;}\
			.tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;}\
		</style>'

	for path in pathList:
		filename = os.path.basename(path)

		inputTypo = spellingCheck(path)

		mailHeader += '<h3> '+filename+' Typo: '+ str(len(inputTypo)) + '</h3>'
		mailTable  += createTypoTable(inputTypo, filename)

	mailHTMLContent = mailHeader + mailTable

	if(mailTable != ''):
		sendMail(mailHTMLContent)

'''
	MAIN
'''
chkr = SpellChecker("en_US",filters=[EmailFilter,URLFilter])

runSpellingCheck(pathList)