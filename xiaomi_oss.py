from requests import get, post, head
import json
import re
from os import remove, rename, path, system, environ
import difflib
from datetime import date
GIT_OAUTH_TOKEN = environ['XFU']

HEADER = {'Authorization': f'token {environ["XFU"]}'}

def get_data_from_github(url):
    data = []
    last = head(url, headers=HEADER).links.get('last')
    if last:
        last = last.get('url').split('=')[-1]
        for i in range(1, int(last) + 1):
            for j in get(f"{url}&page={i}", headers=HEADER).json():
                data.append(j)
    else:
        data = get(url, headers=HEADER).json()
    return data


if path.exists("devices"):
    rename("devices", "old")

# get repos list
url = "https://api.github.com/repos/MiCode/Xiaomi_Kernel_OpenSource/branches?per_page=100"
req = get_data_from_github(url)
devices = re.findall(r"'[a-z]*-[a-z]*-oss'", str(req))
with open("new", "w+") as o:
    for branch in devices:
        device = str(branch).replace("'", '')
        o.write(device + '\n')

# compare
with open('old', 'r') as old, open('new', 'r') as new:
    diff = difflib.unified_diff(old.readlines(), new.readlines(), fromfile='old', tofile='new')
    changes = []
    for line in diff:
        if line.startswith('+'):
            changes.append(str(line))
new = ''.join(changes[1:]).replace("+", "")
with open('changes', 'w') as o:
    o.write(new)
rename("new", "devices")
remove("old")

# commit, push and send
today = str(date.today())
system("git add devices && "" \
       ""git commit -m \"sync: {0} [skip ci]\" --author='XiaomiFirmwareUpdater <xiaomifirmwareupdater@gmail.com>' && "" \
       ""git push -q https://{1}@github.com/XiaomiFirmwareUpdater/xiaomi-oss-tracker.git HEAD:master".format(today, GIT_OAUTH_TOKEN))

bottoken = environ['tg_bot_token']
tg_chat = environ['tg_chat']
tmp = open('changes', 'r').read().split('\n')[:-1]
for chat in ["@MIUIUpdatesTracker", tg_chat]:
  for line in tmp:
      message = "New kernel branch detected: *{0}* \n"\
                "Link: [Here](https://github.com/MiCode/Xiaomi_Kernel_OpenSource/tree/{0})".format(line)
      params = (
          ('chat_id', chat),
          ('text', message),
          ('parse_mode', "Markdown"),
          ('disable_web_page_preview', "yes")
      )
      url = "https://api.telegram.org/bot" + bottoken + "/sendMessage"
      req = post(url, params=params)
  
