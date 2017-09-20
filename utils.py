#!/usr/bin/env python3
# -*- coding: utf-8 -*-



import gi

gi.require_version('Wnck', '3.0')
from gi.repository import Wnck
import dbus
from time import sleep
from subprocess import getoutput, getstatusoutput
import threading
import pandas as pd
from getRpaInfos import *


def convertToHtml(result, title):
    d = {}
    index = 0
    for t in title:
        d[t] = result[index]
        index = index + 1
    df = pd.DataFrame(d)
    df = df[title]
    h = df.to_html(index=False)
    return h


def getAllWindowsPid():
    try:
        screen = Wnck.Screen.get_default()
        screen.force_update()
        return [win.get_pid() for win in screen.get_windows()]
    finally:
        screen = None
        Wnck.shutdown()


class Window:
    def __init__(self, pid):
        self.pid = pid

    def close(self):
        print('close window: %s' % self.pid)
        screen = Wnck.Screen.get_default()
        screen.force_update()
        for win in screen.get_windows():
            if self.pid == win.get_pid():
                win.close(1)
        screen = None
        Wnck.shutdown()

    def getAllWindows(self):
        try:
            screen = Wnck.Screen.get_default()
            screen.force_update()
            return [win for win in screen.get_windows()]
        finally:
            screen = None
            Wnck.shutdown()

    def getAllWindowsName(self):
        try:
            screen = Wnck.Screen.get_default()
            screen.force_update()
            return [win.get_name() for win in screen.get_windows()]
        finally:
            screen = None
            Wnck.shutdown()

    def getAllWindowsPid(self):
        try:
            screen = Wnck.Screen.get_default()
            screen.force_update()
            return [win.get_pid() for win in screen.get_windows()]
        finally:
            screen = None
            Wnck.shutdown()


install_cmd = 'sudo DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true apt-get -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" -y install '
remove_cmd = 'sudo DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true apt-get -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" -y install '


def getTrayIcons():
    dbusDir = 'com.deepin.dde.TrayManager'
    dbusObj = '/com/deepin/dde/TrayManager'
    ifc = 'com.deepin.dde.TrayManager'
    trayicons = 'TrayIcons'
    session_bus = dbus.SessionBus()
    session_obj = session_bus.get_object(dbusDir, dbusObj)
    property_obj = dbus.Interface(session_obj, dbus_interface=dbus.PROPERTIES_IFACE)
    dbus_array = property_obj.Get(ifc, trayicons)
    icons = [str(icon) for icon in dbus_array]
    return icons


def getpids():
    pscmd = 'ps -eo pid --no-headers'
    pids = getoutput(pscmd).split('\n')
    return pids


class Pkgs:
    def __init__(self, pkgname):
        self.pkgname = pkgname
        self.installed_status = ''
        self.opened_status = ''
        self.removed_status = ''
        self.desktop_path = ''
        self.exec_str = ''
        self.oldversion = ''
        self.newversion = ''

    def getRpadebs(self):
        return getRpaDebPkgs()

    def dbusifc(self):
        dbusDir = 'com.deepin.lastore'
        dbusObj = '/com/deepin/lastore'
        ifc = 'com.deepin.lastore.Manager'
        system_bus = dbus.SystemBus()
        system_obj = system_bus.get_object(dbusDir, dbusObj)
        system_if = dbus.Interface(system_obj, dbus_interface=ifc)
        return system_if

    def desktop_name(self):
        desktop_path = self.dbusifc().PackageDesktopPath(self.pkgname)
        if desktop_path == '':
            return
        return desktop_path

    def exec_name(self):
        desktop_path = self.desktop_name()
        if desktop_path is None:
            return
        else:
            o = getoutput('cat ' + desktop_path.replace(' ', '\ ') + '|grep Exec= |head -1')
            start = o.find('=') + 1
            end = o.rfind('%') - 1 if o.find('%') != -1 else len(o)
            return o[start:end]

    def isExisted(self):
        return self.dbusifc().PackageExists(self.pkgname)

    def version(self):
        if self.isExisted():
            return getoutput("apt-cache policy " + self.pkgname + " |grep Installed |awk '{print $2}'")
        else:
            return 'not installed'

    def rrversion(self):
        datajson = getdatajson()
        for data in datajson:
            deblist = list(data['deblist'].keys())
            version = data['version']
            for deb in deblist:
                if self.pkgname == deb:
                    return version

    def install(self):
        s, o = getstatusoutput(install_cmd + self.pkgname)
        return s, o

    def remove(self):
        s, o = getstatusoutput(remove_cmd + self.pkgname)
        return s, o

    def run(self):
        t = threading.Thread(target=lambda: getoutput(self.exec_name()))
        t.setDaemon(True)
        t.start()

    def killps(self, pid):
        print('kill %s' % pid)
        getoutput('sudo kill -9 %s' % pid)


if __name__ == '__main__':
    rpadebs = RpaDebs()
    pkgs = [Pkgs(pkg) for pkg in rpadebs.debs]
    for pkg in pkgs:
        print(pkg.pkgname, pkg.version())
