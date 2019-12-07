#!/usr/bin/env python
 
import configparser
import json
import os
import re
import requests
import sys
import queue
import threading
import time
from pkgxtra.gpsoauth import google

exitFlag = False
 
 
def getGoogleAccountTokenFromAuth():
 
    b64_key_7_3_29 = (b"AAAAgMom/1a/v0lblO2Ubrt60J2gcuXSljGFQXgcyZWveWLEwo6prwgi3"
                      b"iJIZdodyhKZQrNWp5nKJ3srRXcUW+F1BD3baEVGcmEgqaLZUNBjm057pK"
                      b"RI16kB0YppeGx5qIQ5QjKzsR8ETQbKLNWgRY0QRNVz34kMJR3P/LgHax/"
                      b"6rmf5AAAAAwEAAQ==")
 
    android_key_7_3_29 = google.key_from_b64(b64_key_7_3_29)
    encpass = google.signature(gmail, passw, android_key_7_3_29)
    payload = {'Email':gmail, 'EncryptedPasswd':encpass, 'app':client_pkg, 'client_sig':client_sig, 'parentAndroidId':devid}
    request = requests.post('https://android.clients.google.com/auth', data=payload)
    token = re.search('Token=(.*?)\n', request.text)
    
    if token:
       return token.group(1)
    else:
       quit(request.text)
 
 
def getGoogleDriveToken(token):
    payload = {'Token':token, 'app':pkg, 'client_sig':sig, 'device':devid, 'google_play_services_version':client_ver, 'service':'oauth2:https://www.googleapis.com/auth/drive.appdata https://www.googleapis.com/auth/drive.file', 'has_permission':'1'}
    request = requests.post('https://android.clients.google.com/auth', data=payload)
    token = re.search('Auth=(.*?)\n', request.text)
    if token:
       return token.group(1)
    else:
       quit(request.text)
 
def rawGoogleDriveRequest(bearer, url):
    headers = {'Authorization': 'Bearer '+bearer, 'User-Agent': 'WhatsApp/2.19.291 Android/5.1.1 Device/samsung-SM-N950W', 'Content-Type': 'application/json; charset=UTF-8', 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'}
    request = requests.get(url, headers=headers)
    return request.text
    
def gDriveFileMapRequest(bearer, nextPageToken):
    header = {'Authorization': 'Bearer ' + bearer, 'User-Agent': 'WhatsApp/2.19.291 Android/5.1.1 Device/samsung-SM-N950W', 'Content-Type': 'application/json; charset=UTF-8', 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'}
    url = "https://backup.googleapis.com/v1/clients/wa/backups/{}/files?pageToken={}&pageSize=5000".format(celnumbr, nextPageToken)
    request = requests.get(url, headers=header)
    return request.text
 
def downloadFileGoogleDrive(bearer, url, local):
    if not os.path.exists(os.path.dirname(local)):
        os.makedirs(os.path.dirname(local))
    if os.path.isfile(local):
        os.remove(local)
    headers = {'Authorization': 'Bearer '+bearer}
    request = requests.get(url, headers=headers, stream=True)
    request.raw.decode_content = True
    if request.status_code == 200:
        with open(local, 'wb') as asset:
            for chunk in request.iter_content(1024):
                asset.write(chunk)
    print('Downloaded: "'+local+'".')
 
def gDriveFileMap(nextPageToken):
    global bearer
    data = gDriveFileMapRequest(bearer, nextPageToken)
    jres = json.loads(data)
    
    incomplete_backup_marker = False
    description_url = 'https://backup.googleapis.com/v1/clients/wa/backups/'+celnumbr

    description = rawGoogleDriveRequest(bearer, description_url)
    if not('files' in jres):
        quit('Unable to locate google drive file map for: '+pkg)
        
    try:
        if 'invisible' in description['title']:
            for p in result['properties']:
                if (p['key'] == 'incomplete_backup_marker') and (p['value'] == 'true'):
                    incomplete_backup_marker = True                   
    except:
        pass
    if len(jres) == 0:
        if incomplete_backup_marker:
            quit(pkg + ' has an incomplete backup, it may be corrupted!\nMake sure the backup is ok and try again')
        else:
            quit(pkg + ' has no backup filemap, make sure the backup is ok')
    files = jres['files']
    if 'nextPageToken' in jres.keys():
     descriptionOnThisPage, filesOnThisPage = gDriveFileMap(jres['nextPageToken'])
     description += descriptionOnThisPage
     files += filesOnThisPage
    return description, files
 
def getConfigs():
    global gmail, passw, devid, pkg, sig, client_pkg, client_sig, client_ver, celnumbr
    config = configparser.RawConfigParser()
    try:
        config.read('settings.cfg')
        gmail = config.get('auth', 'gmail')
        passw = config.get('auth', 'passw')
        devid = config.get('auth', 'devid')
        celnumbr = config.get('auth', 'celnumbr')
        pkg = config.get('app', 'pkg')
        sig = config.get('app', 'sig')
        client_pkg = config.get('client', 'pkg')
        client_sig = config.get('client', 'sig')
        client_ver = config.get('client', 'ver')
    except(configparser.NoSectionError, configparser.NoOptionError):
        quit('The "settings.cfg" file is missing or corrupt!')
 
def jsonPrint(data):
    print(json.dumps(json.loads(data), indent=4, sort_keys=True))
 
def createSettingsFile():
    with open('settings.cfg', 'w') as cfg:
        cfg.write('[auth]\ngmail = alias@gmail.com\npassw = yourpassword\ndevid = 0000000000000000\ncelnumbr = BACKUPPHONENUMBER\n\n[app]\npkg = com.whatsapp\nsig = 38a0f7d505fe18fec64fbf343ecaaaf310dbd799\n\n[client]\npkg = com.google.android.gms\nsig = 38918a453d07199354f8b19af05ec6562ced5788\nver = 9877000')
 
def getSingleFile(data, asset):
    data = json.loads(data)
    for entries in data:
        if entries['f'] == asset:
            return entries['f'], entries['m'], entries['r'], entries['s']

class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print ('Initiated: ' + self.name)
        process_data(self.name, self.q)
        print ('Terminated: ' + self.name)

def process_data(threadName, q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            queueLock.release()
            getMultipleFilesThread(data['bearer'], data['entries_r'], data['local'], threadName, data['progress'], data['max'])
        else:
            queueLock.release()
        time.sleep(1)

def getMultipleFilesThread(bearer, entries_r, local, threadName, progress, max):
        url = entries_r
        folder_t = os.path.dirname(local)
        if not os.path.exists(folder_t):
            try:
                os.makedirs(folder_t)
            #Other thead was trying to create the same 'folder'
            except (FileExistsError):
                pass
                
        if os.path.isfile(local):
            os.remove(local)
        headers = {'Authorization': 'Bearer '+bearer, 'User-Agent': 'WhatsApp/2.19.291 Android/5.1.1 Device/samsung-SM-N950W', 'Content-Type': 'application/json; charset=UTF-8', 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'}
        request = requests.get(url, headers=headers, stream=True)
        request.raw.decode_content = True
        if request.status_code == 200:
            with open(local, 'wb') as asset:
                for chunk in request.iter_content(1024):
                    asset.write(chunk)
        print(threadName + '=> Downloaded: "'+local+'".\nPogress: {:3.5f}%'.format(progress*100/max))


queueLock = threading.Lock()
workQueue = queue.Queue(9999999)
 
def getMultipleFiles(data, folder):
    threadList = ["Thread-1", "Thread-2", "Thread-3", "Thread-4", "Thread-5", "Thread-6", "Thread-7", "Thread-8", "Thread-9", "Thread-10", "Thread-11", "Thread-12", "Thread-13", "Thread-14", "Thread-15", "Thread-16", "Thread-17", "Thread-18", "Thread-19", "Thread-20"]
    threads = []
    threadID = 1
    global exitFlag
    for tName in threadList:
        thread = myThread(threadID, tName, workQueue)
        thread.start()
        threads.append(thread)
        threadID += 1
        
    progress = 1
    max = len(data)
    url_file = 'https://backup.googleapis.com/v1/'
    queueLock.acquire()
    
    for entries in data:
        name = entries['name']
        local = folder+os.path.sep+name.split('files/')[1].replace("/", os.path.sep)
        if os.path.isfile(local) and 'database' not in local.lower():
            print('Skipped: "'+local+'".')
        else:
            workQueue.put({'bearer':bearer, 'entries_r':url_file+name+'?alt=media', 'local':local, 'progress':progress, 'max':max})
            progress += 1
    queueLock.release()
    while not workQueue.empty():
        pass
    exitFlag = True
    for t in threads:
        t.join()
    print ("File List Downloaded")
 
def runMain(mode, asset, bID):
    global bearer
    global exitFlag
   
    if os.path.isfile('settings.cfg') == False:
        createSettingsFile()
    getConfigs()
    bearer = getGoogleDriveToken(getGoogleAccountTokenFromAuth())
    description, files = gDriveFileMap("")
    if mode == 'info':
        print(description)
    elif mode == 'list':
        for i, drive in enumerate(files):
            if len(files) > 1:
                print("Backup: "+str(i))
            print('/'.join(drive['name'].split('/')[5:]))
            
    elif mode == 'sync':
        exitFlag = False
        folder = 'WhatsApp'
        getMultipleFiles(files, folder)
 
def main():
    args = len(sys.argv)
    if  args < 2 or str(sys.argv[1]) == '-help' or str(sys.argv[1]) == 'help':
        print('\nUsage: '+str(sys.argv[0])+' -help|-vers|-info|-list|-sync|-pull file [backupID]\n\nExamples:\n')
        print('python '+str(sys.argv[0])+' -help (this help screen)')
        print('python '+str(sys.argv[0])+' -vers (version information)')
        print('python '+str(sys.argv[0])+' -info (google drive app settings)')
        print('python '+str(sys.argv[0])+' -list (list all availabe files)')
        print('python '+str(sys.argv[0])+' -sync (sync all files locally)')
    elif str(sys.argv[1]) == '-info' or str(sys.argv[1]) == 'info':
        runMain('info', 'settings', 0)
    elif str(sys.argv[1]) == '-list' or str(sys.argv[1]) == 'list':
        runMain('list', 'all', 0)
    elif str(sys.argv[1]) == '-sync' or str(sys.argv[1]) == 'sync':
        runMain('sync', 'all', 0)
    elif str(sys.argv[1]) == '-vers' or str(sys.argv[1]) == 'vers':
        print('\nWhatsAppGDExtract Version 1.1 Copyright (C) 2016 by TripCode\n')
    elif args < 3:
        quit('\nUsage: python '+str(sys.argv[0])+' -help|-vers|-info|-list|-sync|-pull file [backupID]\n')
    else:
        quit('\nUsage: python '+str(sys.argv[0])+' -help|-vers|-info|-list|-sync|-pull file [backupID]\n')
 
if __name__ == "__main__":
    main()
    
