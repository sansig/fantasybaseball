# coding: utf-8
#Loads fanduel contests in the database with missing data and attempts to add or correct that data, or delete the contest listing from the database if there was an error

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
import logging
logging.basicConfig(level=logging.WARNING)

import MySQLdb
import signal
userid = 'michael.sansig@gmail.com'
password = ""

def check_404(contest_id, driver):
	if len(contest_id) == 0:
		logging.warning('No contest id supplied - exiting')
		return False
	try:
		no = driver.find_element_by_xpath('//p[@class="status"]')
	except:
		logging.warning('404 message not found')
		return False
	if no.get_attribute('innerHTML') == '404 NOT FOUND':	#contest didn't fill so it was cancelled
		sql = "DELETE FROM tbl_fanduel_contests  WHERE contest_id = '" + contest_id + "'"
		sql_data = (contest_id)
		print(sql)
		db = MySQLdb.connect(host='', user='', passwd='', db='')	#load games and data from database
		cursor = db.cursor()
		try:
			cursor.execute(sql)
		except:
			logging.error('Could not run delete query on ' + contest_id)
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			#driver.save_screenshot('fanduel_error.png')
			logging.critical('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
			return False
		else:
			db.commit()
			print('Contest '+contest_id+' was updated')
			return(True)
		finally:
			cursor.close()

def check_upcoming(contest_id, driver):
	if len(contest_id) == 0:
		logging.warning('No contest id supplied - exiting')
		return False
	try:
		minutes = driver.find_element_by_xpath('//span[@class="digits minutes"]')
		hours = driver.find_element_by_xpath('//span[@class="digits hours"]').get_attribute('innerHTML')
		st = driver.find_element_by_xpath('//div[@class="start-time data-chunk-name"]').get_attribute('innerHTML')
	except:
		logging.warning('Time elements were not found')
		return False
	m = re.search('([\d]+)\:([\d]+)([apm]+)', st)
	game_hours = int(m.group(1))
	game_minutes = m.group(2)
	game_apm = m.group(3)
	if game_apm == 'pm' and game_hours < 12:
		game_hours += 12
	start_time = str(game_hours) + ':' + str(game_minutes)
	logging.info(start_time)
	if int(hours) < 24:
		td = date.today()
		td = td.strftime('%Y-%m-%d')
		sql = "UPDATE tbl_fanduel_contests SET `contest_date` = %s, `start_time` = %s  WHERE contest_id = %s"
		logging.info(sql)
		sql_data = (td, start_time, contest_id)
		db = MySQLdb.connect(host='', user='', passwd='', db='')	#load games and data from database
		cursor = db.cursor()
		try:
			cursor.execute(sql, sql_data)
		except:
			logging.error('Could not run update query on ' + contest_id)
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			#driver.save_screenshot('fanduel_error.png')
			logging.critical('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
			return False
		else:
			db.commit()
			print('Contest '+contest_id+' was updated')
			return(True)
		finally:
			cursor.close()


def fd_post_info(contest_id):
	if len(contest_id) == 0:
		logging.critical('No contest id supplied - exiting')
		return
	contest = contest_id.split('-')
	if len(contest) < 2:
		logging.critical('Invalid contest id format')
		return
	url = "https://www.fanduel.com/games/" + contest[0] + "/contests/" + contest_id + "/entries/448970418/scoring"
	logging.info('Checking contest id ' + contest_id)
	try:
		driver = webdriver.PhantomJS(executable_path='/home/zambartas/env/bin/phantomjs')
		driver.set_window_size(2000,2000)
		driver.get(url)
		if driver.current_url != url:
			logging.info(driver.current_url)
			logging.error('Requested URL failed to load ' + url)
			return
		logging.info('Browser loaded ' + url)
	except:
		logging.error('Error with the phantom module')
		driver.close()
		driver.quit()
	else:
		logging.info('Searching for data...')
		try:
			entry_fee = driver.find_element_by_xpath('//dl[@class="entry-detail contest-entry-fee"]').text
			m = re.search('\$([\d\.\,]+)', entry_fee)
			entry_fee = m.group(1)
			logging.debug('Entry fee: ' + entry_fee)
		except:
			logging.info('Entry fee not located')
			if check_404(contest_id, driver):
				logging.info('Contest was deleted')
			elif check_upcoming(contest_id, driver):
				logging.info('Contest is upcoming, database updated')
			else:
				logging.warning('Unknown problem with current contest ' + contest_id + '\nSaving source code as /home/zambartas/fanduel_errors/fanduel_error' +  contest_id + '.html')
				f = open('/home/zambartas/fanduel_errors/fanduel_error' +  contest_id + '.html', 'w+')
				f.write(driver.page_source.encode('utf-8'))
				f.close()
		try:
			logging.info('Searching for entries...')
			entry_count = driver.find_element_by_xpath('//dl[@class="entry-detail contest-position"]').get_attribute('innerHTML')
			m = re.search('/ ([\d]+)', entry_count)
			total_entries = m.group(1)
			logging.info('Total entries: ' + total_entries)
		except:
			logging.error('Could not find total entry count')
			return
		try:
			logging.info('Searching for sport...')
			data = driver.find_element_by_xpath('//i[@data-sport-icon]')
			data = re.search('data-sport-icon="([\w]+)"', data.get_attribute('outerHTML'))
			sport = data.group(1)
			logging.info('Sport type: ' + sport)
		except:
			logging.info('Could not find sport')
		try:
			logging.info('Searching for title...')
			contest_title = driver.find_element_by_xpath('//div[@class="contest-name"]').text
			m = re.search('([\$\w\d\s\.\-\#\(\)\/\%]+)', contest_title)
			contest_title = m.group(1)
			logging.info('Contest title: ' + contest_title)
		except:
			logging.error('Could not find contest_title')
			return
		try:
			scores = driver.find_element_by_xpath('//span[@class="camel-number"]')	#Finds the first score element
			high_score = scores.get_attribute('innerHTML').replace('<em>', '') #Line 58?
			high_score = high_score.replace('</em>', '')
			logging.info('High score: ' + high_score)
		except:
			logging.error('Could not find high score')
			return
		try:
			last = driver.find_element_by_xpath('//button[@class="button text tiny"]')	#get link for last paid position
			try:
				last.click()
			except:
				logging.info('One page maybe')
			time.sleep(1)
			last_place = driver.find_elements_by_xpath('//li[@class="live-leaderboard-entry in-the-money"]')
			scores = driver.find_elements_by_xpath('//span[@class="camel-number"]')	#Finds the first score element
			last_paid_score = scores[len(last_place)-1].text
			logging.info('Last paid score fee: ' + last_paid_score)
		except:
			last_paid_score = '-1'
			return
		try:
			db = MySQLdb.connect(host='', user='', passwd='', db='')	#load games and data from database
			cursor = db.cursor()
		except:
			logging.error('Couldn\'t connect to database')
			return
		try:
			sql = "UPDATE tbl_fanduel_contests SET `contest_title` = %s, `high_score` = %s , `last_paid_score` = %s , `contest_max_entries` = %s, `contest_entry_fee` = %s WHERE contest_id = '" +  contest_id + "'"
			sql_data = (contest_title, high_score, last_paid_score, total_entries, entry_fee)
			logging.info(sql_data)
			print('Contest '+contest_id+' was updated')
			cursor.execute(sql, sql_data)
			db.commit()
		except:
			logging.error('Database error occurred on update, could not update details on ' + contest_id)
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			#driver.save_screenshot('fanduel_error.png')
			logging.critical('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
			return
		finally:
			cursor.close()
			db.close()
	finally:
		driver.close()
		driver.quit()	


db = MySQLdb.connect(host='', user='', passwd='', db='')	#load games and data from database
cursor = db.cursor(MySQLdb.cursors.DictCursor)
td = date.today()
td = td.strftime('%Y-%m-%d')
sql = "SELECT * FROM  `tbl_fanduel_contests` WHERE `high_score` = 0 AND contest_date < CURDATE() and contest_id <> '' ORDER BY contest_date DESC"
print(sql)
cursor.execute(sql)
contest_ids = {}
for row in cursor.fetchall():
	contest_ids[row['contest_id']] = row['contest_id']

cursor.close()
db.close()
for row in contest_ids:
	fd_post_info(row)
