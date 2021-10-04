# -*- coding: utf-8 -*-
try:
    import sys
    import os
    import platform
    import getpass
except Exception as e:
    print(e.message)
    print(e.args)
    raise

from Qt.QtWidgets import *
from Qt.QtCore import *
from Qt.QtGui import *

sys.dont_write_bytecode = True


class toolDefine(object):
    kToolName = os.path.dirname(__file__).replace(os.sep, '/').split('/')[-1]


class userprefDefine(object):
    kSettingsFileName = 'windowPrefs.ini'


def getAppPath():
    appDataPath = os.environ.get('APPDATA', '')
    if platform.system() != 'Windows':
        username = getpass.getuser()
        appDataPath = '/Users/{}/Documents/APPDATA'.format(username)
    prefsPath = '/'.join([
        appDataPath,
        'SolaTools',
        toolDefine.kToolName
    ])
    try:
        if not os.path.exists(prefsPath):
            os.makedirs(prefsPath)
        return prefsPath
    except Exception as e:
        print(e.message)
        print(e.argsee)
        return ''


def getPath():
    userAppPath = getAppPath()
    if not userAppPath:
        return ''
    path = '/'.join([
        userAppPath,
        userprefDefine.kSettingsFileName
    ])
    return path


def getWindowPrefs():
    path = getPath()
    if not path:
        return
    settings = QSettings(
        path,
        QSettings.IniFormat
    )

    return settings
