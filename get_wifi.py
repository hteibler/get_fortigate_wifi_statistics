#!/usr/bin/python3

# (C) 2022 by Herbert the ScriptKiddy ;-)
# and without any warranty from Fortinet

import os
import sys
import requests
import json
from datetime import datetime
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

WIFI_CLIENTS = "/api/v2/monitor/wifi/client"
WIFI_AP = "/api/v2/monitor/wifi/managed_ap"
NOW_EPOCH = int(datetime.now().timestamp())
NOW_LONG = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#######################  global parameters to change - begin
# list of FortiGates

# you have 2 option with the ACCESS_TOKEN
#  1 put it dirctly in the json
#  2 reference it to an environment variable : variable defined after "@"
#
# you can use then localy a "set_env.sh"
# execute: # source ./set_env.sh

# FGs = {
#    "Name":"<fg name>","URL","<full url >","ACCESS_TOKEN":"< token or @env>",,"VDOM":"<vdom",
#    "Name":"<fg name>","URL","<full url >","ACCESS_TOKEN":"< token or @env>",,"VDOM":"<vdom",
#    "Name":"<fg name>","URL","<full url >","ACCESS_TOKEN":"< token or @env>",,"VDOM":"<vdom"
#   }
#

FGs = [
    {"Name":"HTFG80E","URL":"https://192.168.0.1:11443","ACCESS_TOKEN":"@FG80E","VDOM":"root"}
    ]



# List of values to display with "friendly name" : "<json-key>"
# seperate neseted json keys with  "|"
# find struct in list of nested json : use search @key:value

# WIFI-CLIENT-VALUES  
WCLV = {
    "ip":"ip",
  #  "MAC":"mac",
    "hostname":"hostname",
    "SNR-V":"health|snr|value",
    "SNR-S":"health|snr|severity",
    "strength-V":"health|signal_strength|value",
    "strength-S":"health|signal_strength|severity",
    "band":"health|band|value",
    "on AP name":"wtp_name",
    "on AP ID":"wtp_id",
    "mimo":"mimo"
    }

# WIFI-AP-VALUES
WAPV = {
    "Name":"name",
    "status":"status",
    "Version":"os_version",
    "SSID-R1":"ssid|@radio:1|list",
    "R1-Clients":"radio|@radio_id:1|health|client_count|value",
    "R2-Clients":"radio|@radio_id:2|health|client_count|value",
    "R3-Clients":"radio|@radio_id:3|health|client_count|value",
    "R1-Bytes_RX":"radio|@radio_id:1|bytes_rx"
}

# output seperator  eg: "\t" or "," or ";"  used for CSV
SEP = ";"
# which time format
NOW_USED = NOW_LONG
# include time
INCLUDE_DATE = True
# include headerline in output
INCLUDE_HEADER_LINE = True # False
# include FortiGate name in output
INCLUDE_FG_NAME = True

#######################  global parameters to change -  end

def apiGet(url,ACCESS_TOKEN):
    if ACCESS_TOKEN[0] == "@":
        env=ACCESS_TOKEN[1:]
        if env in os.environ:
            ACCESS_TOKEN = os.getenv(ACCESS_TOKEN[1:]).replace('\r', '')
        else:
            print(80*"=")
            print("Error: Missing ACCESS_TOKEN in Environ")
            sys.exit(1)
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    results = requests.get(url,headers=headers, verify=False)
    res=json.loads(results.text)
    res=res["results"]
    return res

def createline(source,cols,name):
    line = ""
    if INCLUDE_DATE: line += NOW_USED + SEP
    if INCLUDE_FG_NAME: line += name + SEP
    for name,field in cols.items():
        try:
            c = field.count("|")
            if c == 0:
                line += source[field]
                line += SEP
                continue
            f = field.split("|")
            s = source
            for sf in f:
                if sf[0] == "@":
                    x=sf.find(":")
                    key=sf[1:x]
                    value=sf[x+1:]
                    for si in s:
                        for ik,iv in si.items():
                            if (ik == key) and (str(iv)==value):
                                s=si
                                continue
                else:
                    s = s[sf]
            line += str(s)
            line += SEP
        except Exception as e:
            #print(e)
            line += SEP
            pass
    return line

def printHeadLine(cols):
    line = ""
    if INCLUDE_DATE: line += "Date" + SEP
    if INCLUDE_FG_NAME: line += "Name" + SEP
    for name,field in cols.items():
        line += name + SEP
    print(line)

def printITEMs(api,cols):
    for FG in FGs:
        url = f'{FG["URL"]}{api}?vdom={FG["VDOM"]}'
        items=apiGet(url,FG["ACCESS_TOKEN"])
        for item in items:
            print(createline(item,cols,FG["Name"]))

### main ------------------------------------------------------------------

arg = sys.argv[1:]
if arg == []:
    print("what do you want to do:")
    print("-------------------------------")
    print("c: list client statistic")
    print("a: list AP statistic")
    print("------------------------------")
    print("and add >file.csv")
    print(".")
    print("e.g.:     ./get_wifi.py a >ap.csv")
    sys.exit(0)

arg = sys.argv[1]

if arg == "c":
    if INCLUDE_HEADER_LINE: printHeadLine(WCLV)
    printITEMs(WIFI_CLIENTS,WCLV)

if arg == "a":
    if INCLUDE_HEADER_LINE: printHeadLine(WAPV)
    printITEMs(WIFI_AP,WAPV)
