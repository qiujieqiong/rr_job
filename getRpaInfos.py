#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import configparser
from subprocess import getstatusoutput as so
from pprint import pprint
import json

rr_url = 'https://rr.deepin.io/api/v1/review'
#curl https://rr.deepin.io/api/v1/review/317 -H Access-Token:B7jfaftY6sFMwEiIEjLkiJC3vZCH1z0W | jq ".result.rpa"

def getRpaInfo(section,name):
    config = configparser.ConfigParser()
    currentdir = os.getcwd()
    config.read(currentdir + '/rpa.info')
    info = config[section][name]
    return info

token = getRpaInfo('rpa', 'token')
headers = {"Access-Token":token}

def getRpaUrl():
    rpa_id = getRpaInfo('rpa', 'id')
    headers   = {"Access-Token":token}
    check_url = '/'.join((rr_url, rpa_id))
    url_info = requests.get(check_url, headers=headers)
    #外网
    rpa_url = url_info.json()['result']['rpa']
    #内网
    #rpa_url = rpa_url.replace('proposed.packages', 'pools.corp')
    return rpa_url

def getdatajson():
    rpa_url = getRpaUrl()
    json_url = rpa_url + '/checkupdate/data.json'
    url_info = requests.get(json_url, headers=headers)
    datajson = url_info.json()
    return datajson

def getRpaSourcePkgs():
    pkg_names = []
    datajson = getdatajson()
    for datas in datajson:
        pkg_names.append(datas['name'])
    return pkg_names

def getRpaDebPkgs():
    deb_names = [deb for data in getdatajson() for deb in list((data['deblist'].keys()))]
    return deb_names


def getRpaSourcePkgsVersion():
    datajson = getdatajson()
    pkg_version = {}
    for data in datajson:
        pkg_version[data['name']] = data['version']
    return pkg_version

def getRpaDebPkgsVersion():
    deb_names_version = {}
    datajson = getdatajson()
    for data in datajson:
        deblist = list(data['deblist'].keys())
        version = data['version']
        for deb in deblist:
            infos = '%s:%s' % (deb, version)
            deb_names_version[deb] = version
    return deb_names_version

def getDebPkgsVersion():
    pkgs_version = getRpaDebPkgsVersion()
    pkg_version_info = {}
    for pkg in pkgs_version:
        (s, o) = so('dpkg -s ' + pkg + ' |grep Version')
        if s == 0:
            (s, o) = so("dpkg -s " + pkg + " |grep Version |awk '{print $2}'")
            pkg_version_info[pkg] = o
    return pkg_version_info

class RpaDebs():
    def __init__(self):
        self.debs = getRpaDebPkgs()

    def version(self,name):
        version = [data['version'] for data in getdatajson() for key in list((data['deblist'].keys())) if key ==  name]
        return ''.join(version)

if __name__ == '__main__':
    rpadebs = RpaDebs()
    for deb in rpadebs.debs:
        print(deb,rpadebs.version(deb))
    
    
    