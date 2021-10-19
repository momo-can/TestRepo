# -*- coding: utf-8 -*-
import sys
import platform
import webbrowser
# from pprint import pprint

from maya.api import OpenMaya
from maya import cmds

sys.dont_write_bytecode = True

platformSystem = platform.system()


def openHelp():
    apps = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

    if platformSystem in ['Darwin', 'Linux']:
        apps = 'open -a /Applications/Google\ Chrome.app %s'

    url = 'https://docs.google.com/document/d/1_Uynzl04RldMn_CpQXQFnXDP3MKQnfLc3rxGMdQBWB8/edit?usp=sharing'
    webbrowser.get(apps).open(url)


def getReferenceNamespace():
    it = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kReference)
    refNodes = OpenMaya.MObjectArray()
    while not it.isDone():
        refNodes.append(it.thisNode())
        it.next()

    fnReference = OpenMaya.MFnReference()
    namespaceList = []
    for i, ref in enumerate(refNodes):
        fnReference.setObject(ref)
        if fnReference.isShared:
            continue
        name = fnReference.name()
        try:
            namespace = fnReference.associatedNamespace(shortName=False)
            namespaceList.append({
                'name': name,
                'namespace': namespace
            })
        except Exception:
            print(name)
    return namespaceList


def editReferenceName(userInputs=[]):
    it = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kReference)
    refNodes = OpenMaya.MObjectArray()
    while not it.isDone():
        refNodes.append(it.thisNode())
        it.next()

    tempInputs = {}
    for userInput in userInputs:
        name = userInput.get('name', '')
        namespace = userInput.get('namespace', '')
        edit = userInput.get('edit', None)
        tempInputs[name] = {
            'namespace': namespace,
            'edit': edit
        }

    fnReference = OpenMaya.MFnReference()
    for i, ref in enumerate(refNodes):
        fnReference.setObject(ref)
        if fnReference.isShared:
            continue

        try:
            nodename = fnReference.name()
            oldname = fnReference.associatedNamespace(shortName=False)
            if not cmds.objExists(nodename):
                continue

            filepath = cmds.referenceQuery(nodename, f=True)

            renameInfo = tempInputs.get(nodename, None)
            if not renameInfo:
                continue

            newname = renameInfo.get('edit', None)
            if not newname:
                continue
            print('> Found "{}"'.format(nodename))

            cmds.file(
                filepath,
                e=True,
                namespace=newname
            )

            editRN = '{}RN'.format(newname)
            fnReference.setName(editRN)
            print('{} >>> {}'.format(oldname, newname))
        except Exception:
            pass
