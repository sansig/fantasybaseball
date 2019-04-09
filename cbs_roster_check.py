# coding: utf-8
#Python script I created that checks my CBS baseball roster for any issues, including players without a game today, as well as checking 
#posted baseball lineups gathered by another script and loaded into the
#database for players who have been benched and are not playing today.

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
import MySQLdb
logging.basicConfig(level=logging.INFO)
import smtplib
from email.mime.text import MIMEText

import MySQLdb
import signal
userid = 'michael.sansig@gmail.com'	
password = ""

phantom_path = '/home/zambartas/env/bin/phantomjs'
db = MySQLdb.connect(host='', user='', passwd='', db='')	#load games and data from database
cursor = db.cursor()
sql = 'SELECT player_name, team, gt, pop, opp_team, batting_order, player_id FROM tbl_lineups WHERE game_date = CURDATE() and estimated <> 1 ORDER by team, batting_order'
logging.info(sql)
lineups = {}
cursor.execute(sql)
lineups = cursor.fetchall()
driver = webdriver.PhantomJS(executable_path='/home/zambartas/env/bin/phantomjs')
driver.set_window_size(2000,2000)
sql = "SELECT * FROM tbl_users INNER JOIN tbl_warning_settings ON tbl_users.user_id = tbl_warning_settings.user_id WHERE tbl_warning_settings.active = 1 AND tbl_users.active = 1 and fantasy_site LIKE 'CBS'"
logging.info(sql)
cursor.execute(sql)
for rs in cursor.fetchall():
	alert = ''
	i = 0
	warning = '';
	user_id = rs[0]
	email = rs[2]
	full_name = rs[3]
	text_address = rs[4]
	league_id = rs[7]
	remote_url = rs[9]
	team_nickname = rs[11]
	bench_warning = rs[12]
	start_warning = rs[13]
	no_game_warning = rs[14]
	postponed_warning = rs[15]
	unknown_warning = rs[16]
	warning_time = rs[17]
	email_warning = rs[18]
	text_warning = rs[19]
	minute = 60;
	thirty_minutes = 1800;
	hour = 3600;
	try:
		driver.get(remote_url)
		if driver.current_url != remote_url:
			driver.find_element_by_id('userid').send_keys('michael.sansig@gmail.com')
			driver.find_element_by_id('password').send_keys('')
			driver.find_element_by_id('password').submit()
	except:
		logging.error('Error with the phantom module')
		driver.close()
		driver.quit()
	else:
		logging.info('Searching for data...')
		try:
			batters = driver.find_elements_by_xpath('//table[@class="data data3 pinHeader borderTop"]//tr')
			logging.info(len(batters))
			pitchers = driver.find_elements_by_xpath('//table[@class="data pinHeader"]//tr')
			logging.info(len(pitchers))
			for player in batters:
				try:
					inner_data = player.get_attribute('innerHTML')
					m = re.search('playerpage/([\d]+)', inner_data)
					player_id = m.group(1)
					ds = player.text.split(' | ')
					pi = ds[0].split(' ')
					player_current_slot = pi[0]
					player_eligible = pi[-1]
					player_name = ds[0].replace(' ' + pi[-1],'')
					logging.info(player_name)
					player_name = player_name.replace(pi[0] + ' ','')
					data = ds[1].split(' ')
					team_info = data[0].split('\n')
					player_team = team_info[0]
					try:
						m = re.search('([\d\:]+[apm]+)', data[1])
						game_time = m.group(1)
					except:
						game_time = ''
					player_found = 0
					team_found = 0
					i += 1
					try:
						player_opp = team_info[1]
					except:
						logging.info('No Game')
						if no_game_warning == 1 and i < 11:
							sql = "SELECT * FROM tbl_warnings WHERE user_id = " + str(user_id) + " AND league_id = " + str(league_id) + " AND player_id = '" + str(player_id) + "' AND date = CURDATE()"
							print(sql)
							cursor.execute(sql)
							if cursor.rowcount < 1:
								player_status = player_current_slot + ' -> No game '
								alert += player_name + ' ' + player_status + '\n'
								sql = 'INSERT INTO tbl_warnings (user_id, player_id, league_id, player_status, date) VALUES (%s, %s, %s, %s, CURDATE())'
								sql_insert = (user_id, player_id, league_id, 3)
								cursor.execute(sql, sql_insert)
								db.commit()
					else:
						for x in lineups:
							if x[1] == player_team:
								team_found = 1
								if x[0] == player_name:
									player_found = 1
									logging.info(x[0] + ' found')
						if i < 11:
							if player_found == 1:
								player_status = player_current_slot + ' -> Starting ' + game_time
							elif team_found == 1:
								if bench_warning == 1:
									sql = "SELECT * FROM tbl_warnings WHERE user_id = " + user_id + " AND league_id = " + league_id + " AND player_id = '" + player_id + "' AND date = CURDATE()"
									print(sql)
									cursor.execute(sql)
									if cursor.rowcount < 1:
										player_status = player_current_slot + ' -> Benched ' + game_time
										alert += player_name + ' ' + player_status + '\n'
										sql = 'INSERT INTO tbl_warnings (user_id, player_id, league_id, player_status, date) VALUES (%s, %s, %s, %s, CURDATE())'
										sql_insert = (user_id, player_id, league_id, 1)
										cursor.execute(sql, sql_insert)
										db.commit()
							else:
								player_status = str(i) + ' -> Lineups not posted yet ' + game_time
						else:
							if player_found == 1:
								if start_warning == 1:
									sql = "SELECT * FROM tbl_warnings WHERE user_id = " + str(user_id) + " AND league_id = " + str(league_id) + " AND player_id = '" + str(player_id) + "' AND date = CURDATE()"
									print(sql)
									cursor.execute(sql)
									if cursor.rowcount < 1:
										player_status = player_eligible + ' -> Starting ' + game_time
										alert += player_name + ' ' + player_status + '\n'
										sql = 'INSERT INTO tbl_warnings (user_id, player_id, league_id, player_status, date) VALUES (%s, %s, %s, %s, CURDATE())'
										sql_insert = (user_id, player_id, league_id, 2)
										cursor.execute(sql, sql_insert)
										db.commit()
							elif team_found == 1:
								player_status = str(i) + ' -> Benched ' + game_time
							else:
								player_status = str(i) + ' -> Lineups not posted yet ' + game_time

				except:
					exc_type, exc_obj, tb = sys.exc_info()
					f = tb.tb_frame
					lineno = tb.tb_lineno
					filename = f.f_code.co_filename
					linecache.checkcache(filename)
					line = linecache.getline(filename, lineno, f.f_globals)
					#driver.save_screenshot('fanduel_error.png')
					print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
					continue
	
		except:
			print('Error')
			exc_type, exc_obj, tb = sys.exc_info()
			f = tb.tb_frame
			lineno = tb.tb_lineno
			filename = f.f_code.co_filename
			linecache.checkcache(filename)
			line = linecache.getline(filename, lineno, f.f_globals)
			#driver.save_screenshot('fanduel_error.png')
			print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
	print(alert)
	print(email_warning)
	if email_warning == 1 and alert <> '':
		msg = MIMEText(alert)
		msg['Subject'] = 'Diamond King Club roster alert'
		msg['From'] = email_from
		msg['To'] = email
		s = smtplib.SMTP('localhost')
		s.sendmail(email_from, email, msg.as_string())
		s.quit()
logging.info('Completed')
driver.close()
driver.quit()
