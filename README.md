WhatsApp Google Drive Extractor
===============================

Allows WhatsApp users on Android to extract their backed up WhatsApp data
from Google Drive.


Prerequisites
-------------

 1. [Python 3][PYTHON]
 2. Android device with WhatsApp installed and the Google Drive backup
    feature enabled.
 3. The device's Android ID (if you want to reduce the risk of being logged
    out of Google). Run `adb shell settings get secure android_id` or Search Google Play for "device id" for plenty of apps
    that can reveal this information.
 4. Google account login credentials (username and password). Create and use an App password when using 2-factor authentication: https://myaccount.google.com/apppasswords


Instructions
------------

 1. Extract `WhatsApp-GD-Extractor-master.zip`.
 2. Install dependencies: Run `python3 -m pip install -r requirements.txt`
    from your command console. Make sure gpsoauth is the latest version.
 3. Edit the `[auth]` section in `settings.cfg`.
 4. Run `python3 WhatsAppGDExtract.py` from your command console.
 5. Read the usage examples that are displayed.
 6. Run any of the examples.

If downloading is interrupted, the files that were received successfully
won't be re-downloaded when running the tool one more time. After
downloading, you may verify the integrity of the downloaded files using
`md5sum --check md5sum.txt` on Linux or [md5summer][MD5SUMMER] on Windows.


Troubleshooting
---------------

 1. Check that you have the required imports installed: `python3 -m pip
    install gpsoauth`
 2. If you have `Error:Need Browser`, go to this url to solve the issue:
    https://accounts.google.com/b/0/DisplayUnlockCaptcha


Credits
-------

Author: TripCode

Contributors: DrDeath1122 from XDA for the multi-threading backbone part,
YuriCosta for reverse engineering the new restore system


[MD5SUMMER]: http://md5summer.org/
[PYTHON]: https://www.python.org/downloads/
