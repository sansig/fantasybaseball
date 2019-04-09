# coding: utf-8
#Fanduel contest scraper. 
#This page runs all day pulling new contests as they're posted on fanduel.com
import time
import os
import sys
import re
import linecache
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys
from datetime import date
import random
import signal

import MySQLdb
db = MySQLdb.connect(host='', user='', passwd='', db='')
cursor = db.cursor(MySQLdb.cursors.DictCursor)

driver = webdriver.PhantomJS(executable_path='/home/micsan58/env/bin/phantomjs')

driver.set_window_size(2000,2000)
driver.get("https://www.fanduel.com/games")
userid = 'michael.sansig@gmail.com'
password = ""

driver.find_element_by_id("email").send_keys(userid)
driver.find_element_by_id('password').send_keys(password)

try:
	driver.find_element_by_name("login").click()
except:
	driver.save_screenshot('login_error_post.png')

game_date = date.today()


def fd_add_contests(sport_name):
	accepted_contests = ('Tournaments', '50/50s &amp; Multipliers')
	event_type = driver.find_elements_by_xpath('//span[@class="contest-type-label"]')
	for events in event_type:
		event_type_name = events.get_attribute('innerHTML')
		print('T: ' + event_type_name)
		if event_type_name in accepted_contests:
			print('Found' + event_type_name)
			events.click()
			time.sleep(1)
			contests = driver.find_elements_by_xpath('//tr[@class="contest-list-item featured-contest updated"|@class="contest-list-item featured-contest"]')
			print(len(contests))
			for id in contests:
				inner_data = id.get_attribute('innerHTML')
				contest_date = date.today()
				#print(id).get_attribute('innerHTML')
				contest_id = id.get_attribute('id').replace('contest_','')
				try:
					m = re.search('contest-name-text">([\$\w\d\s\.\-\#\/\(\)\%]+)', inner_data)
					contest_title = m.group(1)
					print(contest_id)
				except:
					continue
				try:
					m = re.search('size">([\d]+)</span', inner_data)
					contest_max_entries = m.group(1)
					print(contest_max_entries)
				except:
					continue
				
				try:
					m = re.search('Guaranteed">([\w]+)', inner_data)
					contest_guaranteed = m.group(1)
					print(contest_guaranteed)
					guaranteed = '1'
				except:
					guaranteed = ''
				try:
					m = re.search('Entry">([\w]+)</abbr', inner_data)
					contest_multi_entries = m.group(1)
					print(contest_multi_entries)
					multi_entry = '1'
				except:
					multi_entry = ''
				
				m = re.search('fee\">\$([\d\.\,]+)', inner_data)
				contest_entry_fee = m.group(1)
				print(contest_entry_fee)
				
				m = re.search('datetime="([\d]+)\-([\d]+)\-([\d]+)[A-Z]([\d]+)\:([\d]+)\:([\d]+)([\w])">', inner_data)
				contest_year = m.group(1)
				contest_month = m.group(2)
				contest_day = m.group(3)
				contest_hour = m.group(4)
				contest_minutes = m.group(5)
				contest_time_zone = m.group(7)
				m = re.search('([\d\:]+[apm]+)</time>', inner_data)
				start_time = m.group(1)
				print(start_time)
				#sql_fanduel = "INSERT INTO tbl_fanduel (`contest_id` ,`contest_title` ,`multi_entry` ,`guaranteed` ,`contest_type` ,`contest_sport` ,`contest_max_entries` ,`contest_entry_fee` ,`contest_date`,`start_time` ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
				sql_fanduel = "INSERT INTO tbl_fanduel_contests (`contest_id` ,`contest_title` ,`multi_entry` ,`guaranteed` ,`contest_type`  ,`contest_sport` ,`contest_max_entries` ,`contest_entry_fee`,`contest_date`,`start_time`) VALUES ('" + contest_id + "','"+ contest_title +"','"+ multi_entry +"','"+ guaranteed +"','"+ event_type_name +"','"+ sport_name +"','"+ contest_max_entries +"','"+ contest_entry_fee +"','"+ str(contest_date) +"','"+ start_time +"')"
				print(sql_fanduel)
				sql_data = (contest_id, sport_name, contest_date)
				try:
					cursor.execute(sql_fanduel)
					db.commit()
				except:
					print('DB error')
			#end for
		#end if
	#end for
	print(sport_name + ' completed')
#end def


accepted_sports = ('NBA', 'MLB', 'NHL')
sport_links = driver.find_elements_by_xpath('//a[@ng-click="onSelect({ sport: sport })"]')
for e in range(1, len(sport_links)):
	m = re.search('sport-label">([\w]+)</span>', sport_links[e].get_attribute('innerHTML'))
	try:
		sport_name = m.group(1)
	except:
		print('Some error')
		continue
	print(sport_name)
	if sport_name in accepted_sports:
		try:
			sport_links[e].click()
		except:
			print("Couldn't click element")
		else:
			fd_add_contests(sport_name)

cursor.close()
db.close()
driver.quit()