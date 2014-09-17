#!/usr/bin/python
# -*- coding: utf-8 -*-
import ConfigParser
import pprint
import urllib2
import urllib
import json
import sys
import os
import time
import codecs
import dropbox
import webbrowser
from datetime import datetime
import logging
import __main__ as main

configFileName = ''
cfg = None
db_app_key = ''
db_app_secret = ''
db_access_token = ''
localpath = os.path.dirname(os.path.abspath(__file__))
filecount = 0
filesize = 0
errcount = 0
db_client = dropbox.client
drive_service = None
dbpath = '/Camera Uploads'
curdbpath = '/Camera Uploads'
picfolder = localpath + '/camera'
curlpath = picfolder


def main():
	doGreeting()
	doLocalSetup()
	checkConfig()
	checkAuth()
	listFiles(dbpath)

def doGreeting():
	sys.stderr.write("\x1b[2J\x1b[H")
	greetingStr = ''
	greetingStr += '\nDropbox Camera Folder Downloader'
	greetingStr += '\n'
	greetingStr += '\nA simple but reasonable robust Python script to download phone photos synced to Dropbox.'
	greetingStr += '\nFor full details see http://freelancewebdev.github.com/DropboxCameraDownloader'
	greetingStr += '\n'  
	greetingStr += '\nCopyright (C) ' + str(datetime.now().year) + '  Joe Molloy (info[at]hyper-typer.com)'
	greetingStr += '\nThis program comes with ABSOLUTELY NO WARRANTY.'
	greetingStr += '\nThis is free software, licensed under the GPL V3'
	greetingStr += '\nand you are welcome to redistribute it'
	greetingStr += '\n'
	print greetingStr
	answer = raw_input('greeting')

def doLocalSetup():
	global logFileName, configFileName
	logFileName = os.path.basename(__file__) +'.log'
	
	logging.basicConfig(filename=logFileName,level=logging.DEBUG)
	logging.info('Logging set up')
	configFileName = os.path.basename(__file__) + '.cfg'
	if not os.path.isdir(picfolder):
		try:
			os.mkdir(picfolder,0777)
		except IOError as e:
			print 'Failed to create photos folder. Exiting'
			logging.critical('Failed to make pics folder. Exiting.' + e.message)
			sys.exit()
	os.chmod(picfolder,0777)
	print 'System setup complete.  Ready to start!'
	logging.info('Local setup completed successfully')

def checkConfig():
	global cfg, db_app_key, db_app_secret, db_access_token
	print '\nChecking configuration data...'
	logging.info('Checking config data')
	cfg = ConfigParser.ConfigParser()
	try:
		cfg.read(localpath + '/' + configFileName)
		logging.info('Config file loaded')
	except:
		logging.debug('Initial attempt to read config file failed')
		try:
			os.chmod(localpath + '/' + configFileName,0777)
			cfg.read(localpath + '/' + configFileName)
			logging.debug('Config file loaded after changing permissions')
		except error as e:
			logging.critical('Reading config file failed. ' + e.strerror)
			print 'There was a problem reading the config file'
			print 'Please ensure you have renamed'
			print '\'' + configFileName + '_sample\' to \'' + configFileName + '\''
			print 'and added your own values as appropriate'
			sys.exit()
	try:
		db_app_key = cfg.get('dropbox','db-app-key')
	except:
		print 'No Dropbox application key set in config file'
		sys.exit()
	try:
		db_app_secret = cfg.get('dropbox','db-app-secret')
	except:
		print 'No Dropbox application secret set in config file'
		sys.exit()
	try:
		db_access_token = cfg.get('dropbox','db-access-token')
	except:
		pass		
	print 'Config values set'

def checkAuth():
	global db_client, db_access_token
	if(db_access_token == ''):
		print '\nNeed to authenticate with Dropbox'
		db_client = db_auth()
	else:
		print '\nWe have already authenticated with Dropbox, creating client...'
		db_client = getDBClient()

def db_auth():
	global cfg, db_access_token
	print 'Authenticating with Dropbox'
	flow = dropbox.client.DropboxOAuth2FlowNoRedirect(db_app_key, db_app_secret)
	authorize_url = flow.start()
	authorize_url = authorize_url.replace('%27','')
	print '1. About to launch your browser at ' + authorize_url
	print '2. Click "Allow" (you might have to log in first)'
	print '3. Copy the authorization code.'
	time.sleep(5)
	print 'Opening...'
	webbrowser.open(authorize_url,new=1)
	code = raw_input("\nEnter the authorization code here: ").strip()
	db_access_token, user_id = flow.finish(code)
	cfg.set('dropbox','db-access-token',db_access_token)
	cfgfile = os.fdopen(os.open(localpath + '/' + configFileName,os.O_WRONLY|os.O_CREAT,0664),'w')
	cfg.write(cfgfile)
	cfgfile.close()
	dbclient = dropbox.client.DropboxClient(db_access_token)
	return dbclient

def getDBClient():
	dbclient = dropbox.client.DropboxClient(db_access_token)
	return dbclient	

def listFiles(path):
	global filecount, dbpath, curdbpath, curlpath
	try:
		folder_metadata = db_client.metadata(curdbpath)
	except Exception as e:
		logging.debug('Error retreiving Dropbox folder list. ' + e.strerror)
		time.sleep(30)
		listFiles(path)
	print 'Checking for files in \'' + path + '\' on Dropbox'
	logging.info('Checking for files in \'' + path +'\' on Dropbox')
	subfiles = [d['path'] for d in folder_metadata['contents'] if d['is_dir'] == False]
	if(len(subfiles) > 0):
		for f in subfiles:
			try:
				filename = dbdownload(f)
				print 'Saved ' + filename
				filecount += 1
			except:
				time.sleep(30)
				filename = dbdownload(f)
				print 'Saved ' + filename
				filecount += 1
	else:
		print 'No files found.'
	print 'Checking for directories in \'' + path + '\' on Dropbox'
	subdirs = [d['path'] for d in folder_metadata['contents'] if d['is_dir'] == True]
	if(len(subdirs) > 0):
		for d in subdirs:
			print 'Looking at the \'' + d + '\' folder'
			curlpath = os.path.join(picfolder,d.split('/')[-1])
			try:
				os.mkDir(curlpath, 0777)
			except Exception as e:
				print 'Failed to create nested folder ' + d.split('/')[-1] + '. Exiting.'
				logging.critical('Failed to create nested folder ' + d)
				sys.exit(1)
			curdbpath = d
			try:
				listFiles(curdbpath)
			except:
				print 'Trying again in 30 seconds...'
				time.sleep(30)
				listFiles(curdbpath)
	else:
		print 'No directories found in \'' + path + '\' on Dropbox'
	curdbpath = curdbpath.rsplit('/', 1)[0] 
	if(curdbpath == ''):
		curdbpath = '/'
	print 'Moving back up to ' + curdbpath + ' on Dropbox'

def dbdownload(filepath):
	global filesize
	filename = os.path.basename(filepath)
	try:
		f, metadata = db_client.get_file_and_metadata(filepath)
		print 'Downloading ' + filename
		logging.info('Downloading ' + filename)
	except Exception as e:
		print filename + ' not found'
		logging.debug(filename + ' not found: ' + e.message)
		return False
	try:
		out = open(picfolder + '/' + filename, 'wb')
		out.write(f.read())
		out.close()
		print filename + ' downloaded'
		logging.debug(filename + ' downloaded')
		filesize = filesize + os.path.getsize(picfolder + '/' + filename)
		return filename
	except Exception as e:
		try:
			print 'Problem reading file. Trying again in 30 seconds'
			time.sleep(30)
			dbdownload(filepath)
		except:
			print 'Problem saving ' + filename + ' ' + e.message
			logging.debug('Problem saving ' + filename + ' ' + e.strerror)
			return False

def finish():
	print 'Closing log file...'
	if(filecount != 1):
		print str(filecount) + ' files uploaded (' + sizeof_fmt(filesize) + ')'
	else:
		print str(filecount) + ' file uploaded (' + sizeof_fmt(filesize) + ')'

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


if __name__ == '__main__':
	main()