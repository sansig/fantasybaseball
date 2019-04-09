# coding: utf-8
#Fanduel contest data and entry detail
#This script loads contests and pulls entry data, overall score, rankings, and players selected
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

logging.basicConfig(level=logging.ERROR)

import MySQLdb
import signal
userid = 'michael.sansig@gmail.com'
password = ""

pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]	#clean up hanging phantom instances
for pid in pids:
  try:
   process = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
   if 'phantom' in process:
    print('Hanging process ' + pid + ' will be terminated')
    os.kill(int(pid), signal.SIGKILL) #or signal.SIGKILL 
    print('Hanging process ' + pid + ' has been terminated')
  except IOError: # proc has already terminated
   continue
   
phantom_path = '/home/zambartas/env/bin/phantomjs'

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
		db = MySQLdb.connect(host='', user='', passwd='', db='')
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
		db = MySQLdb.connect(host='', user='', passwd='', db='')
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


def fd_post_details(contest_id, game_date):
	if len(contest_id) == 0:
		logging.critical('No contest id supplied - exiting')
		return
	if len(contest_id.split('-')) != 2:
		logging.critical('Invalid contest id format')
		return
	else:
		contest = contest_id.split('-')
	if len(str(game_date)) == 0:
		logging.critical('No contest date supplied - exiting')
		return
	if len(str(game_date).split('-')) != 3:
		logging.critical('Invalid contest id format')
		return
	else:
		contest_date = str(game_date).split('-')
	url = "https://www.fanduel.com/games/" + contest[0] + "/contests/" + contest_id + "/entries/467130919/scoring"
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
		return
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
			logging.info('Contest title: ' + contest_title)
		except:
			logging.error('Could not find contest_title')
			return
		try:
			scores = driver.find_element_by_xpath('//span[@class="camel-number"]').text	#Finds the first score element
		except:
			logging.error('Could not find high score')
			return
		last_paid_score = 0
		high_score = 0
		try:
			db = MySQLdb.connect(host='', user='', passwd='', db='')
			cursor = db.cursor(MySQLdb.cursors.DictCursor)
		except:
			logging.critical('Couldn\'t connect to database')
			return
		try:
			total_pages = int(driver.find_element_by_xpath('//input[@class="paging-input ng-pristine ng-untouched ng-valid ng-valid-min ng-valid-max"]').get_attribute('max'))
		except:
			logging.error('Could not find total page count')
			return
		for pages in range(1,11):
			logging.info("Reading page " + str(pages) + " details")
			driver.execute_script("scroll(2500,0);")	#scroll up
			try:
				entry_links = driver.find_elements_by_xpath('//div[@class="live-leaderboard-entry-link"]')
				entry_details = driver.find_elements_by_xpath('//div[@class="live-leaderboard-entry-details"]')
			except:
				logging.critical('No entries found, problem with contest')
				return
			f=11
			if len(entry_links) < 11:
				f = len(entry_links)
			for i in range(0,f):
				try:
					logging.info("Reading page " + str(pages) + " entry " + str(i) + " details")
					entry_links[i].click()
					entry_data = entry_details[i].text.split('\n')
					m = re.search('([\d]+)', entry_data[0])
					rank = m.group(0)
					user_name = entry_data[1]
					winnings = entry_data[2].replace('$','')
					periods_left = entry_data[3]
					score = entry_data[4]
				except:
					exc_type, exc_obj, tb = sys.exc_info()
					f = tb.tb_frame
					lineno = tb.tb_lineno
					filename = f.f_code.co_filename
					linecache.checkcache(filename)
					line = linecache.getline(filename, lineno, f.f_globals)
					#driver.save_screenshot('fanduel_error.png')
					print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
					try:
						logging.info('Could not find entry links, scrolling up and trying again')
						entry_links = driver.find_elements_by_xpath('//div[@class="live-leaderboard-entry-link"]')	#Entry links lost, try to scrape them again
						time.sleep(1)
						driver.execute_script("scroll(2500,0);")	#scroll up
						entry_links[i].click()
					except:
						logging.critical('Could not pull entry details')
						driver.quit()
						return
				try:
					type = ''
					link = driver.current_url
					m = re.search('entry=([\d]+)', driver.current_url)
					entry_id = m.group(1)
					percentile = (float(total_entries)-float(rank)+1)/(float(total_entries))
					sql_fanduel = "INSERT INTO tbl_fanduel (`entry_id` ,`contest_id` ,`user_name` ,`sport` ,`game_date` ,`contest_title` ,`score` ,`rank` ,`total_entries` ,`entry_fee` ,`winnings` ,`link`, `type`, `percentile`) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
					sql_data = (entry_id, contest_id, user_name, sport, str(game_date), contest_title, score, rank, str(total_entries), entry_fee, winnings, link, type, percentile)
				except:
					exc_type, exc_obj, tb = sys.exc_info()
					f = tb.tb_frame
					lineno = tb.tb_lineno
					filename = f.f_code.co_filename
					linecache.checkcache(filename)
					line = linecache.getline(filename, lineno, f.f_globals)
					#driver.save_screenshot('fanduel_error.png')
					print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
					logging.critical('Problem forming query - missing data')
					logging.critical(sql_fanduel)
					return
				else:
					try:
						if db.open == 0:
							try:
								cursor.close()
								db = MySQLdb.connect(host='', user='', passwd='', db='')
								cursor = db.cursor(MySQLdb.cursors.DictCursor)
							except:
								logging.error('Could not connect to database')
								return
						try:
							cursor.execute(sql_fanduel, sql_data)
							db.commit()
						except:
							logging.warning("Couldn't insert row")
					except:
						exc_type, exc_obj, tb = sys.exc_info()
						f = tb.tb_frame
						lineno = tb.tb_lineno
						filename = f.f_code.co_filename
						linecache.checkcache(filename)
						line = linecache.getline(filename, lineno, f.f_globals)
						#driver.save_screenshot('fanduel_error.png')
						print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))	
						logging.error('Problem running update query')
						continue
				try:
					entry_links[i].click()
					lineup = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, u'//div[@class="live-comparison-entry active"]')))
					logging.info("Searching roster details")
					lineup = driver.find_elements_by_xpath('//li[@class="lineup__slot lineup__slot--has-player"]')
					player_names = driver.find_elements_by_xpath('//img[@class="player-image__image"|@class="player-image__image hidden"]')	#need alternate xpath for players with no image
					player_names = driver.find_elements_by_xpath('//img[@class="player-image__image"]')
					print(len(player_names))
					player_teams = driver.find_elements_by_xpath('//span[@class="live-fixture__team-code live-fixture__team-code--player-team"]')
					opp_teams = driver.find_elements_by_xpath('//span[@class="live-fixture__team-code"]')
					print(len(player_teams))
					player_positions = driver.find_elements_by_xpath('//span[@class="lineup__player-position"]')
					print(len(player_positions))
					print(user_name)
					player_salaries = driver.find_elements_by_xpath('//dl[@class="definition lineup__player-salary"]')
					player_ownership = driver.find_elements_by_xpath('//dl[@class="definition lineup__player-ppo"]')
					player_scores = driver.find_elements_by_xpath('//dl[@class="definition lineup__player-score"]')
					print(len(player_names))
					for n in range(9,len(player_names)):	#Only need the other roster here
						s = lineup[n].text.split('\n')
						if sport == 'mlb':	#MLB has starting lineup info listed with batting order as first item
							z = 1
						else:
							z = 0
						pos_and_name = s[z]
						print(pos_and_name)
						pos = pos_and_name.split(' ')
						player_position = pos[0]
						try:
							player_name = pos[1] + ' ' + pos[2] #Fix this later
						except:
							logging.error('There was a problem with separating the player name from: ' + lineup[n].text)
						game_info = s[z+1].split(' ')
						road_team = game_info[0]
						road_score = game_info[1]
						home_team = game_info[2]
						home_score = game_info[3]
						#game_status = s[z+2]
						player_salary = s[z+3].replace(',','')
						player_salary = player_salary.replace('$','')
						#salary = s[z+4]
						pct_owned = float(s[z+5].replace('%', ''))/100
						#owned = s[z+6]
						player_score = s[z+7]
						#m = re.search('position">([\w]+)</span>',player.get_attribute('innerHTML'))
						#position = m.group(1)
						player_team = player_teams[n].text
						if player_team == home_team:
							location = 'home'
							pt_dx = int(home_score) - int(road_score)
							opp_team = road_team
						if player_team == road_team:
							location = 'road'
							pt_dx = int(road_score) - int(home_score)
							opp_team = home_team
						logging.info(player_team)
						#player_name = player_names[n].get_attribute('alt').replace("'","''")
						#player_position = player_positions[n].get_attribute('innerHTML')
						#m = re.search('\$([\d\,]+)', player_salaries[n*2].get_attribute('innerHTML').replace(',',''))
						#player_salary = m.group(1)
						#m = re.search('([\d\.]+)\%', player_ownership[(n-9)*2].get_attribute('innerHTML').replace(',',''))
						#pct_owned = str(float(m.group(1))/100)
						#m = re.search('([\d\.]+)</dd>', player_scores[n].get_attribute('innerHTML').replace(',',''))
						#pts = m.group(1)
						#print(player_position + ': ' + player_name + ' ' + player_team)
						#sql = "INSERT INTO tbl_fanduel_rosters (`entry_id` ,`contest_id`,`sport`, `position`, `player_name`, `team`, `salary`, `pct_owned`, `pts`, `team_pt_dx`, `location`) VALUES ('" + entry_id + "' , '" + sport + "' , '" + player_position + "' , '" + player_name + "' , '" + player_team + "' , '" + player_salary + "' , '" + pct_owned + "' , '" + player_score + "' , '" + pt_dx + "' , '" + location + "')"
						try:
							sql = "INSERT INTO tbl_fanduel_rosters (`entry_id`,`contest_id` ,`sport`, `position`, `player_name`, `team`, `salary`, `pct_owned`, `pts`, `team_pt_dx`, `location`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
							sql_data = (entry_id, contest_id, sport, player_position, player_name, player_team, player_salary, pct_owned, player_score, pt_dx, location)
						except:
							exc_type, exc_obj, tb = sys.exc_info()
							f = tb.tb_frame
							lineno = tb.tb_lineno
							filename = f.f_code.co_filename
							linecache.checkcache(filename)
							line = linecache.getline(filename, lineno, f.f_globals)
							#driver.save_screenshot('fanduel_error.png')
							print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))	
							logging.error('Couldn\'t form query')
						logging.info(sql)
						#print(sql)
						try:				
							if db.open == 0:
								try:
									cursor.close()
									db = MySQLdb.connect(host='', user='', passwd='', db='')
									cursor = db.cursor(MySQLdb.cursors.DictCursor)
								except:
									logging.error('Could not connect to database')
								else:
									cursor.execute(sql, sql_data)
									db.commit()
							else:
								cursor.execute(sql, sql_data)
								db.commit()
						except:
							logging.error('Couldn\'t execute update query')
							logging.error(sql_data)
						driver.execute_script("scroll(2500,0);")	#scroll up
					#end lineup detail loop
				except:
					exc_type, exc_obj, tb = sys.exc_info()
					f = tb.tb_frame
					lineno = tb.tb_lineno
					filename = f.f_code.co_filename
					linecache.checkcache(filename)
					line = linecache.getline(filename, lineno, f.f_globals)
					#driver.save_screenshot('fanduel_error.png')
					print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
					logging.error('Couldn\'t find lineup data')
				#end try
			try:
				next_page = driver.find_element_by_xpath('//button[@class="paging-control button tiny text page-next"]')
				next_page.click()
			except:
				logging.info('End of contest ' + contest_id)
			#end entry loop
		#end page deail loop
	finally:
		driver.close()
		driver.quit()
		print('Completed')
#end def

db = MySQLdb.connect(host='', user='', passwd='', db='')	#load games and data from database
cursor = db.cursor(MySQLdb.cursors.DictCursor)
td = date.today()
td = td.strftime('%Y-%m-%d')
sql = "SELECT * FROM  `v_fanduel_entry_count` WHERE `v_fanduel_entry_count`.`missing_entries` > 1 AND entries < 99 AND contest_date < CURDATE()  order by entries asc"

cursor.execute(sql)
contest_ids = {}
for row in cursor.fetchall():
	contest_ids[row['contest_id']] = row['contest_date']

cursor.close()
db.close()
for row in sorted(contest_ids):
	fd_post_details(row, contest_ids[row])
	
driver.close()
driver.quit()