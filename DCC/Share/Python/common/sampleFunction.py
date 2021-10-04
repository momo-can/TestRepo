# -*- coding:utf-8 -*-
import sys
import os
import subprocess

from maya import cmds

sys.dont_write_bytecode = True


def getRendererParameters():
    def getParams(name='', plugs={}):
        params = {}
        for k in plugs.keys():
            p = plugs.get(k, '')
            value = cmds.getAttr('{}.{}'.format(name, p))
            params[k] = value
        return params

    r = 'defaultRenderGlobals'
    renderer = cmds.getAttr('{}.currentRenderer'.format(r))
    attributes = {
        'defaultRenderGlobals': {
            'output': 'imageFilePrefix',
            'start': 'startFrame',
            'end': 'endFrame'
        },
        'vraySettings': {
            'output': 'fileNamePrefix'
        }
    }

    params = {}
    plugs = attributes.get(r, {})
    if plugs:
        params = getParams(name=r, plugs=plugs)

    if renderer in ['vray']:
        r = 'vraySettings'

    plugs = attributes.get(r, {})
    if plugs:
        params.update(getParams(name=r, plugs=plugs))
    return params


def getUsername():
    username = os.environ.get('username')
    if not username:
        username = 'Staff'
    return username


def getFileParameters():
    result = {}
    path = cmds.file(q=True, sn=True)
    if not path:
        return result
    basename = os.path.basename(path)
    filename, fileext = os.path.splitext(basename)
    result = {'filename': filename}
    return result


def getDeadlineParameters():
    result = {}
    path = os.environ.get('DEADLINE_PATH')
    if not path:
        return result
    apps = '/'.join([path, 'deadlinecommand.exe'])
    apps = apps.replace(os.sep, '/')
    pools = subprocess.check_output([apps, '-Pools'], shell=True)
    groups = subprocess.check_output([apps, '-Groups'], shell=True)
    pools = pools.split('\r\n')
    pools.remove('')
    groups = groups.split('\r\n')
    groups.remove('')
    result = {
        'pools': pools,
        'groups': groups
    }
    return result
