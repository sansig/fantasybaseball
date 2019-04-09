# coding: utf-8
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
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select
import logging
logging.basicConfig(level=logging.INFO)
import MySQLdb
today = date.today()
mytime = time
game_date = date.today()
year = str(game_date.year)
month = str(game_date.month)
day = str(game_date.day)
if len(str(month)) == 1:
    month = '0' + month

if len(str(day)) == 1:
    day = '0' + day

date_string = year + '-' + month + '-' +  day
db = MySQLdb.connect(host='mysql.michaelsansig.com', user='user_name', passwd='password', db='database')	#load games and data from database
cursor = db.cursor()
DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:16.0) Gecko/20121026 Firefox/16.0'
driver = webdriver.PhantomJS(executable_path='/home/zambartas/env/bin/phantomjs')
driver.set_window_size(2000,2000)

def numberfire_login(driver):
	driver.get('http://www.numberfire.com/account/login-yahoo?ref=page') 		#Yahoo
	try:
		driver.save_screenshot('numberfire_username_error' + date_string + '.png')
		driver.find_element_by_id('login-username').send_keys('')
		driver.find_element_by_id('login-signin').click()
		time.sleep(2)
	except:
		logging.error('Error loading url')
		driver.save_screenshot('numberfire_username_error' + date_string + '.png')
	try:
		driver.save_screenshot('numberfire_password_error' + date_string + '.png')
		driver.find_element_by_id('login-passwd').send_keys('')
		driver.find_element_by_id('login-signin').submit()
		time.sleep(2)
	except:
		logging.error('Error loading url')
		driver.save_screenshot('numberfire_password_error' + date_string + '.png')

#driver.save_screenshot('sdffsd' + date_string + '.png')

def numberfire_login_check(driver):
	try:
		driver.get('https://www.numberfire.com/nba/games/' + date_string)
		if driver.current_url <> 'https://www.numberfire.com/nba/games/' + date_string:
			time.sleep(10)
			driver.get('https://www.numberfire.com/nba/games/' + date_string)
			if driver.current_url <> 'https://www.numberfire.com/nba/games/' + date_string:
				driver.save_screenshot('numberfire_login_error_' + date_string + '.png')
	except:
		logging.critical('Could not load url, exiting')
		driver.close()
		driver.quit()
		sys.exit()
	print(driver.current_url)
	f = open('numberfire_nba_' + date_string + '.html', 'wb')
	f.write(driver.page_source.encode('utf-8'))
	f.close()
	driver.get('https://www.numberfire.com/nhl/games/' + date_string)
	print(driver.current_url)
	f = open('numberfire_nhl_' + date_string + '.html', 'wb')
	f.write(driver.page_source.encode('utf-8'))
	f.close()

def nf_nba(driver):
	logging.info('Searching Numberfire NBA')
	url = 'https://www.numberfire.com/nba/daily-fantasy/daily-basketball-projections'
	try:
		driver.get(url)
	except:
		logging.error('Error loading url')
	if driver.current_url != url:
		numberfire_login(driver)
		driver.get(url)
		if driver.current_url != url:
			logging.critical('Failure to load ' +  url)
			return
	try:
		lineups = driver.find_elements_by_xpath('//tbody[@id="projection-data"]//tr')
	except:
		logging.error('Numberfire data rows not found')
		return
	else:
		db.select_db('sansig_nba')
		for row in lineups:
			try:
				m = re.search('([\w\s\-\'\.]+) \(([\w]+)\, ([\w]+)\) ', row.text)
				player_info = row.text.replace(m.group(0),'').split(' ')
				player_name = m.group(1)
				name_split = player_name.split(' ')
				last_name = ' '.join(name_split[1:])
				first_name = name_split[0]
				player_pos = m.group(2)
				player_team = m.group(3)
			except:
				logging.error('Error with name position or team data')
				return
			try:
				player_opp = player_info[-11].replace('@','')
				player_mins = player_info[-10]
				player_pts = player_info[-3]
				player_salary = player_info[-2].replace('$','')
				player_value = player_info[-1]
			except:
				logging.error('Error with player_info: ' + player_info)
				return
			else:
				sql = 'INSERT INTO tbl_player_stats (`full_name` ,`first_name` ,`last_name` ,`pos` ,`team_abv` ,`opp_abv` ,`game_date` ,`nf_min` ,`nf_pts` ,`nf_value` ,`fd_salary`) VALUES (%s,   %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s)'
				sql_insert = (player_name, first_name, last_name, player_pos, player_team, player_opp, date_string, player_mins, player_pts, player_value, player_salary )
				print(sql_insert)
				try:
					cursor.execute(sql, sql_insert)
					db.commit()
				except:
					logging.error('Database insert error')

def nf_mlb(driver):
	logging.info('Searching Numberfire MLB')
	url = 'https://www.numberfire.com/mlb/daily-fantasy/daily-baseball-projections'
	try:
		driver.get(url)
	except:
		logging.error('Error loading url')
	if driver.current_url != url:
		numberfire_login(driver)
		driver.get(url)
		if driver.current_url != url:
			logging.critical('Failure to load ' +  url)
			return
	try:
		lineups = driver.find_elements_by_xpath('//tbody[@id="projection-data"]//tr')
	except:
		logging.error('Numberfire data rows not found')
		return
	else:
		db.select_db('rokanigg')
		for row in lineups:
			try:
				m = re.search('([\w\s\-\'\.]+) \(([\w\d]+)\, ([\w]+)\)\s?([\w]+)?\n', row.text)
				player_info = row.text.replace(m.group(0),'').split(' ')
				game_info = player_info[0].split('\n')
				player_opp = game_info[0].replace('@','')
				player_name = m.group(1)
				name_split = player_name.split(' ')
				last_name = ' '.join(name_split[1:])
				first_name = name_split[0]
				player_pos = m.group(2)
				player_team = m.group(3)
				player_opp = player_info[-11].replace('@','')
				player_pts = player_info[-3]
				player_salary = player_info[-2].replace('$','')
				player_value = player_info[-1]
			except:
				logging.error('Problem with numberfire batter values')
				exc_type, exc_obj, tb = sys.exc_info()
				f = tb.tb_frame
				lineno = tb.tb_lineno
				filename = f.f_code.co_filename
				linecache.checkcache(filename)
				line = linecache.getline(filename, lineno, f.f_globals)
				#driver.save_screenshot('fanduel_error.png')
				print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
				continue
			else:
				sql = 'INSERT INTO tbl_player_stats (`full_name` ,`first_name` ,`last_name` ,`pos` ,`team_abv` ,`opp_abv` ,`game_date` ,`nf_pts` ,`nf_value` ,`fd_salary`) VALUES (%s,   %s, %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s)'
				sql_insert = (player_name, first_name, last_name, player_pos, player_team, player_opp, date_string, player_pts, player_value, player_salary )
				print(sql_insert)
				try:
					cursor.execute(sql, sql_insert)
					db.commit()
				except:
					logging.error('Database insert error')
	url = 'https://www.numberfire.com/mlb/daily-fantasy/daily-baseball-projections/pitchers'
	try:
		driver.get(url)
	except:
		logging.error('Error loading url')
	if driver.current_url != url:
		driver.get(url)
		if driver.current_url != url:
			logging.critical('Failure to load ' +  url)
			return
	try:
		lineups = driver.find_elements_by_xpath('//tbody[@id="projection-data"]//tr')
	except:
		logging.error('Numberfire data rows not found')
		return
	else:
		for row in lineups:
			try:
				m = re.search('([\w\s\-\'\.]+) \((?:([\w\d]+)\, )?([\w]+)\)\s?([\w]+)?\n', row.text)
				player_info = row.text.replace(m.group(0),'').split(' ')
				game_info = player_info[0].split('\n')
				player_opp = game_info[0].replace('@','')
				player_name = m.group(1)
				if player_name == 'Chris Ryan Young':
					player_name = 'Chris Young'
				name_split = player_name.split(' ')
				last_name = ' '.join(name_split[1:])
				first_name = name_split[0]
				player_pos = 'P'
				player_team = m.group(3)
				player_opp = player_info[-11].replace('@','')
				player_pts = player_info[-3]
				player_salary = player_info[-2].replace('$','')
				player_value = player_info[-1]
			except:
				logging.error('Problem with numberfire pitcher values')
				exc_type, exc_obj, tb = sys.exc_info()
				f = tb.tb_frame
				lineno = tb.tb_lineno
				filename = f.f_code.co_filename
				linecache.checkcache(filename)
				line = linecache.getline(filename, lineno, f.f_globals)
				#driver.save_screenshot('fanduel_error.png')
				print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
				continue
			else:
				sql = 'INSERT INTO tbl_player_stats (`full_name` ,`first_name` ,`last_name` ,`pos` ,`team_abv` ,`opp_abv` ,`game_date` ,`nf_pts` ,`nf_value` ,`fd_salary`) VALUES (%s,   %s, %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s)'
				sql_insert = (player_name, first_name, last_name, player_pos, player_team, player_opp, date_string, player_pts, player_value, player_salary )
				print(sql_insert)
				try:
					cursor.execute(sql, sql_insert)
					db.commit()
				except:
					logging.error('Database insert error')

def rg_nba(driver):
	logging.info('Searching Rotogrinders NBA')
	db.select_db('sansig_nba')
	driver.get('https://rotogrinders.com/projected-stats/nba?site=fanduel')
	rotogrind = driver.find_elements_by_xpath('//table[@id="proj-stats"]//tr')
	for row in rotogrind:
		try:
			logging.info(len(rotogrind) + 'Rows found')
			m = re.search('([\w\s\-\.\']+) ([A-Z]{1,2}) ', row.text)
			player_info = row.text.replace(m.group(0),'').split(' ')
			player_name = m.group(1)
			name_split = player_name.split(' ')
			last_name = ' '.join(name_split[1:])
			first_name = name_split[1]
			player_pos = m.group(2)
			player_opp = player_info[1]
			player_salary = player_info[2].replace('$','')
			player_salary = float(player_salary.replace('K',''))*1000
			player_floor = player_info[4]
			player_ceil = player_info[5]
			player_pts = player_info[6]
			player_value = player_info[7]
		except:
			logging.error('Problem with rotogrinders nba values')
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			#driver.save_screenshot('fanduel_error.png')
			print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
			continue
		else:
			#sql = 'INSERT INTO tbl_player_stats (`full_name` ,`first_name` ,`last_name` ,`pos` ,`team_abv` ,`opp_abv` ,`game_date` ,`rg_pts` ,`rg_pts` ,`rg_value` ,`rg_pts`) VALUES (%s,   %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s);
			sql = 'UPDATE tbl_player_stats SET rg_pts = %s, rg_floor = %s, rg_ceiling = %s, rg_value = %s WHERE full_name = %s AND game_date = %s'
			sql_update = (player_pts, player_floor, player_ceil , player_value, player_name, date_string)
			print(sql_update)
			cursor.execute(sql, sql_update)
			db.commit()
	

def rg_mlb(driver):
	logging.info('Searching Rotogrinders MLB')
	db.select_db('rokanigg')
	driver.get('https://rotogrinders.com/projected-stats/mlb?site=fanduel')
	rotogrind = driver.find_elements_by_xpath('//div[@class="player"]')
	for row in rotogrind:
		try:
			m = re.search('([\w\s\-\.\']+) ([A-Z1-3]{1,2}) ', row.text)
			player_info = row.text.replace(m.group(0),'').split(' ')
			player_name = m.group(1)
			name_split = player_name.split(' ')
			last_name = ' '.join(name_split[1:])
			first_name = name_split[1]
			player_pos = m.group(2)
			player_opp = player_info[-4]
			player_salary = player_info[-3].replace('$','')
			player_salary = float(player_salary.replace('K',''))*1000
			player_pts = player_info[-2]
			player_value = player_info[-1]
		except:
			logging.error('Problem with rotogrinders mlb values')
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			#driver.save_screenshot('fanduel_error.png')
			print('EXCEPTION IN ({}, LINE {} "{}"): {} - {}'.format(filename, lineno, line.strip(),exc_type, exc_obj))
			continue
		else:
			#sql = 'INSERT INTO tbl_player_stats (`full_name` ,`first_name` ,`last_name` ,`pos` ,`team_abv` ,`opp_abv` ,`game_date` ,`rg_pts` ,`rg_pts` ,`rg_value` ,`rg_pts`) VALUES (%s,   %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s);
			sql = 'UPDATE tbl_player_stats SET rg_pts = %s, rg_value = %s WHERE full_name = %s AND game_date = %s'
			sql_update = (player_pts, player_value, player_name, date_string)
			print(sql_update)
			cursor.execute(sql, sql_update)
			db.commit()

	driver.get('https://rotogrinders.com/projected-stats/mlb-pitcher?site=fanduel')
	rotogrind = driver.find_elements_by_xpath('//table[@id="proj-stats"]//tr')
	for row in rotogrind:
		try:
			m = re.search('([\w\s\-\.\']+) ([A-Z1-3]{1,2}) ', row.text)
			player_info = row.text.replace(m.group(0),'').split(' ')
			player_name = m.group(1)
			name_split = player_name.split(' ')
			last_name = ' '.join(name_split[1:])
			first_name = name_split[1]
			player_pos = m.group(2)
			player_opp = player_info[-4]
			player_salary = player_info[-3].replace('$','')
			player_salary = float(player_salary.replace('K',''))*1000
			player_pts = player_info[-2]
			player_value = player_info[-1]
		except:
			logging.error('Problem with rotogrinders mlb values')
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			#driver.save_screenshot('fanduel_error.png')
			print('EXCEPTION IN ({}, LINE {} "{}"): {} - {}'.format(filename, lineno, line.strip(),exc_type, exc_obj))
			continue
		else:
			#sql = 'INSERT INTO tbl_player_stats (`full_name` ,`first_name` ,`last_name` ,`pos` ,`team_abv` ,`opp_abv` ,`game_date` ,`rg_pts` ,`rg_pts` ,`rg_value` ,`rg_pts`) VALUES (%s,   %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s);
			sql = 'UPDATE tbl_player_stats SET rg_pts = %s, rg_value = %s WHERE full_name = %s AND game_date = %s'
			sql_update = (player_pts, player_value, player_name, date_string)
			print(sql_update)
			cursor.execute(sql, sql_update)
			db.commit()


def old_rg_nba(driver):
	logging.info('Searching Rotogrinders NBA')
	db.select_db('sansig_nba')
	driver.get('https://rotogrinders.com/projected-stats/nba?site=fanduel')
	rotogrind = driver.find_elements_by_xpath('//table[@id="proj-stats"]//tr')
	for row in rotogrind:
		try:
			logging.info(len(rotogrind) + 'Rows found')
			m = re.search('([\w\s\-\.\']+) ([A-Z]{1,2}) ', row.text)
			player_info = row.text.replace(m.group(0),'').split(' ')
			player_name = m.group(1)
			name_split = player_name.split(' ')
			last_name = ' '.join(name_split[1:])
			first_name = name_split[1]
			player_pos = m.group(2)
			player_opp = player_info[1]
			player_salary = player_info[2].replace('$','')
			player_salary = float(player_salary.replace('K',''))*1000
			player_floor = player_info[4]
			player_ceil = player_info[5]
			player_pts = player_info[6]
			player_value = player_info[7]
		except:
			logging.error('Problem with rotogrinders nba values')
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			#driver.save_screenshot('fanduel_error.png')
			print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
			continue
		else:
			#sql = 'INSERT INTO tbl_player_stats (`full_name` ,`first_name` ,`last_name` ,`pos` ,`team_abv` ,`opp_abv` ,`game_date` ,`rg_pts` ,`rg_pts` ,`rg_value` ,`rg_pts`) VALUES (%s,   %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s);
			sql = 'UPDATE tbl_player_stats SET rg_pts = %s, rg_floor = %s, rg_ceiling = %s, rg_value = %s WHERE full_name = %s AND game_date = %s'
			sql_update = (player_pts, player_floor, player_ceil , player_value, player_name, date_string)
			print(sql_update)
			cursor.execute(sql, sql_update)
			db.commit()
	

def old_rg_mlb(driver):
	logging.info('Searching Rotogrinders MLB')
	db.select_db('rokanigg')
	driver.get('https://rotogrinders.com/projected-stats/mlb?site=fanduel')
	rotogrind = driver.find_elements_by_xpath('//table[@id="proj-stats"]//tr')
	for row in rotogrind:
		try:
			m = re.search('([\w\s\-\.\']+) ([A-Z1-3]{1,2}) ', row.text)
			player_info = row.text.replace(m.group(0),'').split(' ')
			player_name = m.group(1)
			name_split = player_name.split(' ')
			last_name = ' '.join(name_split[1:])
			first_name = name_split[1]
			player_pos = m.group(2)
			player_opp = player_info[-4]
			player_salary = player_info[-3].replace('$','')
			player_salary = float(player_salary.replace('K',''))*1000
			player_pts = player_info[-2]
			player_value = player_info[-1]
		except:
			logging.error('Problem with rotogrinders mlb values')
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			#driver.save_screenshot('fanduel_error.png')
			print('EXCEPTION IN ({}, LINE {} "{}"): {} - {}'.format(filename, lineno, line.strip(),exc_type, exc_obj))
			continue
		else:
			#sql = 'INSERT INTO tbl_player_stats (`full_name` ,`first_name` ,`last_name` ,`pos` ,`team_abv` ,`opp_abv` ,`game_date` ,`rg_pts` ,`rg_pts` ,`rg_value` ,`rg_pts`) VALUES (%s,   %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s);
			sql = 'UPDATE tbl_player_stats SET rg_pts = %s, rg_value = %s WHERE full_name = %s AND game_date = %s'
			sql_update = (player_pts, player_value, player_name, date_string)
			print(sql_update)
			cursor.execute(sql, sql_update)
			db.commit()

	driver.get('https://rotogrinders.com/projected-stats/mlb-pitcher?site=fanduel')
	rotogrind = driver.find_elements_by_xpath('//table[@id="proj-stats"]//tr')
	for row in rotogrind:
		try:
			m = re.search('([\w\s\-\.\']+) ([A-Z1-3]{1,2}) ', row.text)
			player_info = row.text.replace(m.group(0),'').split(' ')
			player_name = m.group(1)
			name_split = player_name.split(' ')
			last_name = ' '.join(name_split[1:])
			first_name = name_split[1]
			player_pos = m.group(2)
			player_opp = player_info[-4]
			player_salary = player_info[-3].replace('$','')
			player_salary = float(player_salary.replace('K',''))*1000
			player_pts = player_info[-2]
			player_value = player_info[-1]
		except:
			logging.error('Problem with rotogrinders mlb values')
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			#driver.save_screenshot('fanduel_error.png')
			print('EXCEPTION IN ({}, LINE {} "{}"): {} - {}'.format(filename, lineno, line.strip(),exc_type, exc_obj))
			continue
		else:
			#sql = 'INSERT INTO tbl_player_stats (`full_name` ,`first_name` ,`last_name` ,`pos` ,`team_abv` ,`opp_abv` ,`game_date` ,`rg_pts` ,`rg_pts` ,`rg_value` ,`rg_pts`) VALUES (%s,   %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s);
			sql = 'UPDATE tbl_player_stats SET rg_pts = %s, rg_value = %s WHERE full_name = %s AND game_date = %s'
			sql_update = (player_pts, player_value, player_name, date_string)
			print(sql_update)
			cursor.execute(sql, sql_update)
			db.commit()


nf_nba(driver)
nf_mlb(driver)
rg_nba(driver)
rg_mlb(driver)
cursor.close()
db.close()
driver.close()
print('Completed')