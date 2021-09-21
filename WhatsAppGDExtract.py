#!/usr/bin/env python3

"""
usage: python3 {} help|info|list|sync

    help    Show this help.
    info    Show WhatsApp backups.
    list    Show WhatsApp backup files.
    sync    Download all WhatsApp backups.
"""

from base64 import b64decode
from getpass import getpass
from multiprocessing.pool import ThreadPool
from textwrap import dedent
import configparser
import gpsoauth
import hashlib
import json
import os
import requests
import sys

def human_size(size):
    for s in ["B", "kiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"]:
        if abs(size) < 1024:
            break
        size = int(size / 1024)
    return "{}{}".format(size, s)

def have_file(file, size, md5):
    """
    Determine whether the named file's contents have the given size and hash.
    """
    if not os.path.exists(file) or size != os.path.getsize(file):
        return False

    digest = hashlib.md5()
    with open(file, "br") as input:
        while True:
            b = input.read(8 * 1024)
            if not b:
                break
            digest.update(b)

    return md5 == digest.digest()

def download_file(file, stream):
    """
    Download a file from the given stream.
    """
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, "bw") as dest:
        for chunk in stream.iter_content(chunk_size=None):
            dest.write(chunk)

class WaBackup:
    """
    Provide access to WhatsApp backups stored in Google drive.
    """
    def __init__(self, gmail, password, android_id):
        token = gpsoauth.perform_master_login(gmail, password, android_id)
        if "Token" not in token:
            quit(token)
        self.auth = gpsoauth.perform_oauth(
            gmail,
            token["Token"],
            android_id,
            "oauth2:https://www.googleapis.com/auth/drive.appdata",
            "com.whatsapp",
            "38a0f7d505fe18fec64fbf343ecaaaf310dbd799",
        )

    def get(self, path, params=None, **kwargs):
        try:
            response = requests.get(
                "https://backup.googleapis.com/v1/{}".format(path),
                headers={"Authorization": "Bearer {}".format(self.auth["Auth"])},
                params=params,
                **kwargs,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            print ("\n\nHttp Error:",errh)
        except requests.exceptions.ConnectionError as errc:
            print ("\n\nError Connecting:",errc)
        except requests.exceptions.Timeout as errt:
            print ("\n\nTimeout Error:",errt)
        except requests.exceptions.RequestException as err:
            print ("\n\nOOps: Something Else",err)
        return response

    def get_page(self, path, page_token=None):
        return self.get(
            path,
            None if page_token is None else {"pageToken": page_token},
        ).json()

    def list_path(self, path):
        last_component = path.split("/")[-1]
        page_token = None
        while True:
            page = self.get_page(path, page_token)
            for item in page[last_component]:
                yield item
            if "nextPageToken" not in page:
                break
            page_token = page["nextPageToken"]

    def backups(self):
        return self.list_path("clients/wa/backups")

    def backup_files(self, backup):
        return self.list_path("{}/files".format(backup["name"]))

    def fetch(self, file):
        name = os.path.sep.join(file["name"].split("/")[3:])
        md5Hash = b64decode(file["md5Hash"], validate=True)
        if not have_file(name, int(file["sizeBytes"]), md5Hash):
            download_file(
                name,
                self.get(file["name"].replace("%", "%25").replace("+", "%2B"), {"alt": "media"}, stream=True)
            )

        return name, int(file["sizeBytes"]), md5Hash

    def fetch_all(self, backup, cksums):
        num_files = 0
        total_size = 0
        with ThreadPool(10) as pool:
            downloads = pool.imap_unordered(
                lambda file: self.fetch(file),
                self.backup_files(backup)
            )
            for name, size, md5Hash in downloads:
                num_files += 1
                total_size += size
                print(
                    "\rProgress: {:7.3f}% {:60}".format(
                        100 * total_size / int(backup["sizeBytes"]),
                        os.path.basename(name)[-60:]
                    ),
                    end="",
                    flush=True,
                )

                cksums.write("{md5Hash} *{name}\n".format(
                    name=name,
                    md5Hash=md5Hash.hex(),
                ))

        print("\n{} files ({})".format(num_files, human_size(total_size)))


def getConfigs():
    config = configparser.ConfigParser()
    try:
        config.read('settings.cfg')
        gmail = config.get('auth', 'gmail')
        password = config.get("auth", "password", fallback="")
        if not password:
            try:
                password = getpass("Enter your password for {}: ".format(gmail))
            except KeyboardInterrupt:
                quit('\nCancelled!')
        android_id = config.get("auth", "android_id")
        return {
            "android_id": android_id,
            "gmail": gmail,
            "password": password,
        }
    except (configparser.NoSectionError, configparser.NoOptionError):
        quit('The "settings.cfg" file is missing or corrupt!')

def createSettingsFile():
    with open('settings.cfg', 'w') as cfg:
        cfg.write(dedent("""
            [auth]
            gmail = alias@gmail.com
            # Optional. The account password or app password when using 2FA.
            # You will be prompted if omitted.
            password = yourpassword
            # The result of "adb shell settings get secure android_id".
            android_id = 0000000000000000
            """).lstrip())

def backup_info(backup):
    metadata = json.loads(backup["metadata"])
    for size in "backupSize", "chatdbSize", "mediaSize", "videoSize":
        metadata[size] = human_size(int(metadata[size]))
    return dedent("""
        Backup {name} ({backupSize}):
            WhatsApp version: {versionOfAppWhenBackup}
            Password protected: {passwordProtectedBackupEnabled}
            Messages: {numOfMessages} ({chatdbSize})
            Media files: {numOfMediaFiles} ({mediaSize})
            Photos: {numOfPhotos}
            Videos: included={includeVideosInBackup} ({videoSize})
        """.format(
            name=backup["name"].split("/")[-1],
            **metadata
        )
    )

def main(args):
    if len(args) != 2 or args[1] not in ("info", "list", "sync"):
        quit(__doc__.format(args[0]))

    if not os.path.isfile('settings.cfg'):
        createSettingsFile()
    wa_backup = WaBackup(**getConfigs())
    backups = wa_backup.backups()

    if args[1] == "info":
        for backup in backups:
            print(backup_info(backup))

    elif args[1] == "list":
        num_files = 0
        total_size = 0
        for backup in backups:
            for file in wa_backup.backup_files(backup):
                num_files += 1
                total_size += int(file["sizeBytes"])
                print(os.path.sep.join(file["name"].split("/")[3:]))
        print("{} files ({})".format(num_files, human_size(total_size)))

    elif args[1] == "sync":
        with open("md5sum.txt", "w", encoding="utf-8", buffering=1) as cksums:
            for backup in backups:
                try:
                    print("Backup {} ({}):".format(
                        backup["name"],
                        human_size(int(backup["sizeBytes"])),
                    ))
                    wa_backup.fetch_all(backup, cksums)
                except:
                    print("Corrupted/Incomplete Backup!");
                    continue

if __name__ == "__main__":
    main(sys.argv)
