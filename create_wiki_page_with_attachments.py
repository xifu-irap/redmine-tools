#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#        Copyright (c) IRAP CNRS
#        Odile Coeur-Joly, Toulouse, France
#
"""
Setup Redmine server access.
"""
# To disable Insecure Request Warnings, in case of requests={'verify': False} is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
Launches a basic GUI to get user inputs.
"""
import easygui

API_key = easygui.enterbox("KEY ? (copy/paste from My Account on the Redmine site")

testname = easygui.enterbox("Test directory ? (copy/paste from D:\DRE_TESTS\PROTO)", default="20200226_135406__DACBIAS-10_DACFBCK-11_pix-10_fast")
if testname is None or len(str(testname)) == 0:
    easygui.msgbox('The program will end. Please restart and enter a test name')
    exit()

config = easygui.enterbox("Configuration number ?", default="071")
operator = easygui.choicebox(msg = "Operator's name", title = "Hello Operator", 
                             choices = ['Bernard','Christophe','David','Laurent','Odile','Wilfried','Yann'], preselect=3)

easygui.msgbox('Test directory = ' + testname + '\n' + 
               'Configuration number = ' + config + '\n' + 
               'Operator name = ' + str(operator))

"""
Redmine access to Redmine servers : please update the "key" parameter with your private access API key.
"""
# a. = Connect to the dummy site bitnami (OCJ)
# a. redmine = Redmine('http://127.0.0.1:83/redmine', key = 'KEY', requests={'verify': False})
# b. = Connect to the xifu-redmine site
# b. redmine = Redmine('https://xifu-redmine.irap.omp.eu', key = API_key, requests={'verify': False})

from redminelib import Redmine
redmine = Redmine('https://xifu-redmine.irap.omp.eu', key = API_key, requests={'verify': False})

# 1.1. Get the Prototype_DACs_test_campaign_TEMPLATE wiki page text
wiki_page = redmine.wiki_page.get('Prototype_DACs_test_campaign_TEMPLATE', project_id='DRE')    
text_template = wiki_page.text

# 1.2. Create a header line with the user input values
header = "|_.Date |_.Test Reference |_.Configuration |_.Operator |_.Test Purposes |_.Results"

strDate = testname[6:8] + str("/") + testname[4:6] + str("/") + testname[0:4]
text_template = text_template.replace('TEST_DATE', strDate)
text_template = text_template.replace('TEST_NAME', testname)
text_template = text_template.replace('TEST_CONFIG_ID', config)
text_template = text_template.replace('OPERATOR', operator)

# 1.3. Get the Text of the current DAC test campaign page and replace the first lines
wiki_page = redmine.wiki_page.get('Prototype_DACs_test_campaign', project_id='DRE')    
text_dac_campaign = wiki_page.text
text_dac_campaign = text_dac_campaign.replace(header, text_template)

"""
This part updates the text of an existing Redmine Wiki page
"""
redmine.wiki_page.update(
                        'Prototype_DACs_test_campaign',
                        project_id='DRE',
                        title='Prototype_DACs_test_campaign',
                        text=text_dac_campaign
                        )
print("1. Page Prototype DACs test campaign updated...")

# 2.1. Get the Text of the DAC_Test_Report_TEMPLATE Wiki page
wiki_page = redmine.wiki_page.get('DACs_test_report_TEMPLATE', project_id='DRE')    
text_template = wiki_page.text

# 2.2 Replace the wiki text with the user input values
table_split = testname.split('_')
hour = table_split[0] + '_' + table_split[1]
dacs = table_split[3] + '_' + table_split[4]
pixel = table_split[5].split('-')[0] + 'el'
pixel_num = table_split[5].split('-')[1]
title = hour + ' ' + dacs + ' ' + pixel + ' ' + pixel_num

text_template = text_template.replace('TEST_REPORT_TITLE', title)
text_template = text_template.replace('TEST_NAME', testname)
text_template = text_template.replace('TEST_CONFIG_ID', config)

# 2.3 Find all the attachment files on disk
import os.path
normpath = os.path.normpath("D:/DRE_TESTS/PROTO")
savepath = os.path.join(normpath, testname, "PLOTS")

filelist = os.listdir(savepath)

# 2.4 Fill a dict with all attachments
uploadlist = []
index = 0
for fi in filelist:
    uploadict = {}
    uploadict['path'] = os.path.join(savepath, fi)
    uploadict['filename'] = fi
    uploadict['description'] = "desc"
    uploadlist.append(uploadict)

"""
This part creates a new Wiki page, with attachment files
"""
redmine.wiki_page.create(
                        project_id='DRE',
                        title=testname,
                        text=text_template,
                        parent_title='Prototype DACs test campaign',
                        comments='no comment',
                        uploads=uploadlist
                        )

print("2. Page DAC test report created...")
print("Done !")
