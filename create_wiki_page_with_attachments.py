#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#        Copyright (c) IRAP CNRS
#        Odile Coeur-Joly, Toulouse, France
#
"""
This part tests Redmine server access.
"""

# To disable Insecure Request Warnings, in case of requests={'verify': False} is used
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
This part replaces the wiki text in the TEMPLATE pages.
"""
# Dialog boxes to get the test parameters
import easygui

testname = easygui.enterbox("Test directory ? (copy/paste from D:\DRE_TESTS\PROTO)", default="20200226_135406__DACBIAS-10_DACFBCK-11_pix-10_fast")
if testname is None or len(str(testname)) == 0:
    easygui.msgbox('The program will end. Please restart and enter a test name')
    exit()

config = easygui.enterbox("Configuration number ?", default="071")
operator = easygui.choicebox(msg = "Operator's name", title = "Hello", 
                             choices = ['Bernard','Christophe','David','Laurent','Odile','Wilfried','Yann'], preselect=4)

easygui.msgbox('Test directory = ' + testname + '\n' + 
               'Configuration number = ' + config + '\n' + 
               'Operator name = ' + str(operator))

# 1. Connect to the dummy site bitnami (OCJ)
from redminelib import Redmine
redmine = Redmine('http://127.0.0.1:82/redmine', key = '5dea73303c7b0899ea3af513df628382043375f5', requests={'verify': False})

# 1. Get the Prototype_DACs_test_campaign_TEMPLATE wiki page text
wiki_page = redmine.wiki_page.get('Prototype_DACs_test_campaign_TEMPLATE', project_id='test_ocj')    
text_template = wiki_page.text

# 2. Replace the wiki text
header = "|_.Date |_.Test Reference |_.Configuration |_.Operator |_.Test Purpose |_.Results"

strDate = testname[6:8] + str("/") + testname[4:6] + str("/") + testname[0:4]
text_template = text_template.replace('TEST_DATE', strDate)
text_template = text_template.replace('TEST_NAME', testname)
text_template = text_template.replace('TEST_CONFIG_ID', config)
text_template = text_template.replace('OPERATOR', operator)

#print("text_template\n", text_template)
#print("text_template\n", text_template.replace('\r', ''))

# Get the Text of the DAC current DAC campaign page
wiki_page = redmine.wiki_page.get('Prototype_DACs_test_campaign', project_id='test_ocj')    
text_dac_campaign = wiki_page.text

# Replace the wiki text
text_dac_campaign = text_dac_campaign.replace(header, text_template)

#print("text_dac_campaign AFTER\n", text_dac_campaign)

"""
This part tests howto update the text of a Redmine Wiki page
"""
redmine.wiki_page.update(
                        'Prototype_DACs_test_campaign',
                        project_id='test_ocj',
                        title='Prototype_DACs_test_campaign',
                        text=text_dac_campaign
                        )
print("Page DAC campaign updated...")

"""
This part tests howto create a DAC Test report wiki page, with attachment files
"""
# 1. Get the Text of the DAC_Test_Report_TEMPLATE Wiki page
wiki_page = redmine.wiki_page.get('DACs_test_report_TEMPLATE', project_id='test_ocj')    
text_template = wiki_page.text

# Replace the wiki text
title = testname[0:15] + "  " + testname[17:38] + " " + testname[39:]
text_template = text_template.replace('TEST_REPORT_TITLE', title)
text_template = text_template.replace('TEST_NAME', testname)
text_template = text_template.replace('TEST_CONFIG_ID', config)

# 2. Find all the attachment files on disk
import os.path
normpath = os.path.normpath("D:/DRE_TESTS/PROTO")
savepath = os.path.join(normpath, testname, "PLOTS")

filelist = os.listdir(savepath)
uploadlist = []

# Each attachment must be a dict
index = 0
for fi in filelist:
    uploadict = {}
    uploadict['path'] = os.path.join(savepath, fi)
    uploadict['filename'] = fi
    uploadict['description'] = "desc"
    uploadlist.append(uploadict)

redmine.wiki_page.create(
                        project_id='test_ocj',
                        title=testname,
                        text=text_template,
                        parent_title='03 Tests',
                        comments='no comment',
                        uploads=uploadlist
                        )

print("Page Test Report created...")