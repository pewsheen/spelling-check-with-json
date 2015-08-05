import re
import json
import time
import enchant
from enchant.checker import SpellChecker
from enchant.tokenize import EmailFilter, URLFilter
from fluentmail import FluentMail

# Global Settings #
jsWordPath 		= 'D:\\js.json'

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

# d = enchant.Dict("en_US")
chkr = SpellChecker("en_US",filters=[EmailFilter,URLFilter])

jsWord = {}
jsTypo = {}

'''
	js.json
'''
print '\n------------- mup -------------\n'
input_mup_file  = file(jsWordPath, "r")
jsWord = json.loads(input_mup_file.read().decode("utf-8"))

for key in jsWord :
	text = jsWord[key]
	text = text.encode('ascii','ignore')
	# print 'TEXT: ' + text
	filterText = remove_variable(remove_HTML_tags(remove_HTML_encode(text)))
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
			jsTypo[text] = {}
			jsTypo[text]['typo'] = errList
			jsTypo[text]['key']  = key

'''
	Compose mail
'''

mailHTMLContent = ''
mailHeader 		= '';
typoTable 	= '';
mailTranslationTable = '';

checkTime = time.strftime("%Y/%m/%d");

mailHeader = '\
	<h1>Spelling Check Result '+checkTime+'</h1>\
	<h3> Typo: '+ str(len(jsTypo)) + '</h3>';

''' typoTable '''
typoTable = '\
	<h1>MUP Typo<h1>\
	<style type="text/css">\
		.tg  {border-collapse:collapse;border-spacing:0;}\
		.tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;}\
		.tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;}\
	</style>\
	<table class="tg">\
		<tr>\
			<th class="tg">Key</th>\
			<th class="tg">String</th>\
		</tr>';

for text in jsTypo :
	resultText = text
	for typo in jsTypo[text]['typo']:
		resultText = resultText.replace(typo, '<font color="red">'+typo+'</font>')
	
	typoTable += '\
	<tr class="tg">\
		<td class="tg">'+jsTypo[text]['key']+'</td>\
		<td class="tg">'+resultText+'</td>\
	</tr>';

typoTable += '</table>';

'''
	Send mail
'''

mailHTMLContent = mailHeader + typoTable

mail = FluentMail('smtp.server.com', 587, TLS)

mail.credentials('name', 'pass')\
	.from_address('name <your@mail.com>')\
	.to('rv <rcv@mail.com>')\
	.subject('Spelling Check Result')\
	.body(mailHTMLContent)\
	.as_html()\
	.send()