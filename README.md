# WhatsApp Google Drive Extractor
Allows WhatsApp users on Android to extract their backed up WhatsApp data from Google Drive.  

###### BRANCH UPDATES:
v1.0 - Initial release.  
v1.1 - Added Python 3 support.


###### PREREQUISITES:
 1. O/S: Windows Vista, Windows 7, Windows 8, Windows 10, Mac OS X or Linux  
 2. Python 2.x or 3.x - If not installed: https://www.python.org/downloads/  
 3. Android device with WhatsApp installed and the Google Drive backup feature enabled  
 4. Google services device id (if you want to reduce the risk of being logged out of Google)  
     Search Google Play for "device id" for plenty of apps that can reveal this information  
 5. Google account login credentials (username and password)
 6. Generate an App Password if your Google account has 2-factor-authentication.
     App passwords are generated at https://security.google.com/settings/security/apppasswords.


###### INSTRUCTIONS:
 1. Extract "WhatsApp-GD-Extractor-master.zip".  
 2. Install dependencies (`pip install -r requirements.txt`)
 3. Copy `auth.cfg.example` to `auth.cfg`. Fill in your Google credentials in the file.
 4. Run python WhatsAppGDExtract.py from your command console.  
 5. Read the usage examples that are displayed.  
 6. Run any of the examples.  
 

###### TROUBLESHOOTING:
 1. Check you have the required imports installed (configparser and requests).  
     I.E.: `pip install -r requirements.txt`  
 2. If you have 2-factor-authentication enabled, make sure you use an App Password instead of your Google passsword.

###### CREDITS:
 AUTHOR: TripCode  
