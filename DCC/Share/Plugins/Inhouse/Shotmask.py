# -*- coding: utf-8 -*-
import sys
import os
from datetime import datetime

from maya.api import OpenMaya
from maya.api import OpenMayaUI
from maya.api import OpenMayaRender

from maya import cmds
from maya import mel

#
# Pre defines.
#
u"""
shotmask
"""
__author__ = 'Masahiro Ohmomo'
__version__ = '1.0.0'

_TYPE_IDS = (
    0x79999,
)


def maya_useNewAPI():
    pass


def getSceneName():
    fileFullPath = cmds.file(q=True, l=True)
    if isinstance(fileFullPath, list):
        fileFullPath = fileFullPath[0]
    sceneName = fileFullPath.split('/')[-1]
    sceneName, fileext = os.path.splitext(sceneName)
    return [sceneName, fileext]


def getFrameSize(frameContext, data):
    cameraPath = frameContext.getCurrentCameraPath()
    camera = OpenMaya.MFnCamera(cameraPath)
    cameraName = camera.name()
    focalLength = camera.focalLength
    focalLength = round(focalLength, 4)
    overscan = camera.overscan
    if data.overrideOverscanSize:
        overscan = 1.

    renderSizeX = float(cmds.getAttr('defaultResolution.w'))
    renderSizeY = float(cmds.getAttr('defaultResolution.h'))

    viewX, viewY, viewW, viewH = frameContext.getViewportDimensions()
    viewAspect = float(viewW) / float(viewH)
    renderAspect = renderSizeX / renderSizeY

    hCenter = viewW * .5
    vCenter = viewH * .5

    fontSize = data.fontSize

    # x = .0
    y = .0
    w = .0
    h = .0
    if viewAspect > renderAspect:
        h = vCenter / (vCenter / overscan)
        w = (h * 2. * renderAspect)
        y = 0
        # x = (viewW - w) / 2
    else:
        w = hCenter - (hCenter / overscan)
        h = (viewW / overscan) / renderAspect
        # x = 0
        y = (viewH - h) / 2

    screenLeft = w
    screenRight = viewW - w
    screenTop = viewH - y - fontSize
    screenBottom = y

    return {
        'screenLeft': screenLeft,
        'screenRight': screenRight,
        'screenTop': screenTop,
        'screenBottom': screenBottom,
        'hCenter': hCenter,
        'vCenter': vCenter,
        'cameraName': cameraName,
        'focalLength': focalLength
    }


class ShotmaskNode(OpenMayaUI.MPxLocatorNode):
    pluginName = 'shotmaskShape'
    nodeId = OpenMaya.MTypeId(_TYPE_IDS[0])
    drawDbClassification = "drawdb/geometry/shotmaskNode"
    drawRegistrantId = "ShotmaskNodePlugin"

    def __init__(self):
        OpenMayaUI.MPxLocatorNode.__init__(self)

    def compute(self, plug, dataBlock):
        return

    def draw(self, view, path, style, status):
        return

    def drawLast(self):
        return True

    # override
    def excludeAsLocator(self):
        return False

    def isBounded(self):
        return True

    def boundingBox(self):
        corner1 = OpenMaya.MPoint(-1000000, -1000000, -1000000)
        corner2 = OpenMaya.MPoint(1000000, 1000000, 1000000)
        return OpenMaya.MBoundingBox(corner1, corner2)

    @classmethod
    def nodeCreator(cls):
        return cls()

    @classmethod
    def nodeInitializer(cls):
        fnNumeric = OpenMaya.MFnNumericAttribute()
        stringAttr = OpenMaya.MFnTypedAttribute()

        cls.overrideOverscanSize = fnNumeric.create(
            'overrideOverscanSize',
            'oos',
            OpenMaya.MFnNumericData.kBoolean,
            True
        )
        fnNumeric.writable = True
        fnNumeric.readable = False
        fnNumeric.storable = True
        fnNumeric.hidden = False
        fnNumeric.keyable = False
        cls.addAttribute(cls.overrideOverscanSize)

        cls.fontSize = fnNumeric.create(
            "fontSize",
            "fs",
            OpenMaya.MFnNumericData.kInt,
            20
        )
        fnNumeric.writable = True
        fnNumeric.storable = True
        fnNumeric.hidden = False
        fnNumeric.keyable = False
        cls.addAttribute(cls.fontSize)

        stringData = OpenMaya.MFnStringData()
        consolasObject = stringData.create("Consolas")
        cls.fontFamily = stringAttr.create(
            "fontFamily",
            "fn",
            OpenMaya.MFnData.kString,
            consolasObject
        )
        stringAttr.writable = True
        stringAttr.storable = True
        stringAttr.keyable = True
        cls.addAttribute(cls.fontFamily)

        cls.fontColor = fnNumeric.createColor('fontColor', 'fc')
        fnNumeric.default = (1., 1., 1.)
        fnNumeric.writable = True
        fnNumeric.readable = False
        fnNumeric.storable = False
        cls.addAttribute(cls.fontColor)

        cls.fontColorAlpha = fnNumeric.create(
            'fontColorAlpha',
            'fca',
            OpenMaya.MFnNumericData.kDouble,
            1.
        )
        fnNumeric.writable = True
        fnNumeric.readable = False
        fnNumeric.storable = False
        cls.addAttribute(cls.fontColorAlpha)

        cls.backplateColor = fnNumeric.createColor('backplateColor', 'bc')
        fnNumeric.default = (.0, .0, .0)
        fnNumeric.writable = True
        fnNumeric.readable = False
        fnNumeric.storable = False
        cls.addAttribute(cls.backplateColor)

        cls.borderColorAlpha = fnNumeric.create(
            'borderColorAlpha',
            'bca',
            OpenMaya.MFnNumericData.kDouble,
            .5
        )
        fnNumeric.writable = True
        fnNumeric.readable = False
        fnNumeric.storable = False
        cls.addAttribute(cls.borderColorAlpha)

        stringData = OpenMaya.MFnStringData().create('')
        cls.assetName = stringAttr.create(
            "assetName",
            "an",
            OpenMaya.MFnData.kString,
            stringData
        )
        stringAttr.writable = True
        stringAttr.storable = True
        stringAttr.keyable = True
        stringAttr.readable = False
        stringAttr.hidden = False
        stringAttr.keyable = True
        cls.addAttribute(cls.assetName)

        stringData = OpenMaya.MFnStringData().create('')
        cls.overscanSize = stringAttr.create(
            "overscanSize",
            "oss",
            OpenMaya.MFnData.kString,
            stringData
        )
        stringAttr.writable = True
        stringAttr.storable = True
        stringAttr.keyable = True
        stringAttr.readable = False
        stringAttr.hidden = False
        stringAttr.keyable = True
        cls.addAttribute(cls.overscanSize)

        stringData = OpenMaya.MFnStringData().create('')
        cls.cameraShakeType = stringAttr.create(
            "cameraShakeType",
            "ust",
            OpenMaya.MFnData.kString,
            stringData
        )
        stringAttr.writable = True
        stringAttr.storable = True
        stringAttr.keyable = True
        stringAttr.readable = False
        stringAttr.hidden = False
        stringAttr.keyable = True
        cls.addAttribute(cls.cameraShakeType)


#
# Viewport 2.0 override
#
class shotmaskData(OpenMaya.MUserData):
    def __init__(self):
        OpenMaya.MUserData.__init__(self, False)

        self.fColor = OpenMaya.MColor()
        self.fSoleLineList = OpenMaya.MPointArray()
        self.fSoleTriangleList = OpenMaya.MPointArray()
        self.rHeelLineList = OpenMaya.MPointArray()
        self.rHeelTriangleList = OpenMaya.MPointArray()


class shotmaskDrawOverride(OpenMayaRender.MPxDrawOverride):
    @staticmethod
    def creator(obj):
        return shotmaskDrawOverride(obj)

    @staticmethod
    def draw(context, data):
        portWidth, portHeight = context.getRenderTargetSize()
        return

    def __init__(self, obj):
        OpenMayaRender.MPxDrawOverride.__init__(
            self,
            obj,
            shotmaskDrawOverride.draw
        )

    def isBounded(self, objPath, cameraPath):
        return False

    def boundingBox(self, objPath, cameraPath):
        corner1 = OpenMaya.MPoint(-1000000, -1000000, -1000000)
        corner2 = OpenMaya.MPoint(1000000, 1000000, 1000000)
        return OpenMaya.MBoundingBox(corner1, corner2)

    def disableInternalBoundingBoxDraw():
        return True

    def supportedDrawAPIs(self):
        return OpenMayaRender.MRenderer.kOpenGL | OpenMayaRender.MRenderer.kDirectX11 | OpenMayaRender.MRenderer.kOpenGLCoreProfile

    def prepareForDraw(self, objPath, cameraPath, frameContext, data):
        if not isinstance(data, shotmaskData):
            data = shotmaskData()

        obj = objPath.node()
        mfnDagNode = OpenMaya.MFnDagNode(obj)

        data.fontSize = mfnDagNode.findPlug(
            "fontSize",
            False
        ).asInt()
        data.fontFamily = mfnDagNode.findPlug(
            "fontFamily",
            False
        ).asString()
        data.overrideOverscanSize = mfnDagNode.findPlug(
            "overrideOverscanSize",
            False
        ).asShort()
        data.fontColor = mfnDagNode.findPlug(
            "fontColor",
            False
        )
        data.fontColorAlpha = mfnDagNode.findPlug(
            "fontColorAlpha",
            False
        ).asDouble()
        data.backplateColor = mfnDagNode.findPlug(
            "backplateColor",
            False
        )
        data.borderColorAlpha = mfnDagNode.findPlug(
            "borderColorAlpha",
            False
        ).asDouble()

        data.assetName = mfnDagNode.findPlug(
            "assetName",
            False
        ).asString()

        data.overscanSize = mfnDagNode.findPlug(
            "overscanSize",
            False
        ).asString()

        data.cameraShakeType = mfnDagNode.findPlug(
            "cameraShakeType",
            False
        ).asString()

        self.startFrame = int(cmds.playbackOptions(q=True, min=True))
        self.endFrame = int(cmds.playbackOptions(q=True, max=True))

        return data

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, objPath, drawManager, frameContext, data):
        locatordata = data
        if not isinstance(locatordata, shotmaskData):
            return

        uiDrawManagerNode = objPath.node()
        if uiDrawManagerNode.isNull():
            return

        fontSize = data.fontSize

        shotmaskInfo = getFrameSize(frameContext, data)
        screenLeft = shotmaskInfo.get('screenLeft', 0.0)
        screenRight = shotmaskInfo.get('screenRight', 50.0)
        screenTop = shotmaskInfo.get('screenTop', 0.0)
        screenBottom = shotmaskInfo.get('screenBottom', 50.0)
        hCenter = shotmaskInfo.get('hCenter', 25.0)
        # vCenter = shotmaskInfo.get('vCenter', 25.0)
        cameraName = shotmaskInfo.get('cameraName', 'camera')
        focalLength = shotmaskInfo.get('focalLength', 0.0)

        self.currentFrame = int(cmds.currentTime(q=True))
        self.currentFrame = str(self.currentFrame).zfill(4)

        timeCode = '{} {}-{}'.format(
            self.currentFrame,
            str(self.startFrame).zfill(4),
            str(self.endFrame).zfill(4)
        )

        drawManager.beginDrawable()
        drawManager.setColor(locatordata.fColor)
        drawManager.setDepthPriority(10)

        # Draw backplate.
        backplateColor = cmds.getAttr(locatordata.backplateColor)[0]
        backplateColor = (
            backplateColor[0],
            backplateColor[1],
            backplateColor[2],
            data.borderColorAlpha
        )
        backplateColor = OpenMaya.MColor(backplateColor)

        # Start Draw text.
        fontColor = cmds.getAttr(locatordata.fontColor)[0]
        fontColor = (
            fontColor[0],
            fontColor[1],
            fontColor[2],
            data.fontColorAlpha
        )
        backplateColor = OpenMaya.MColor(fontColor)
        textColor = OpenMaya.MColor(fontColor)

        drawManager.setColor(textColor)
        drawManager.setFontName(data.fontFamily)
        drawManager.setFontSize(fontSize)
        drawManager.setDepthPriority(1)
        drawManager.setFontIncline(
            OpenMayaRender.MUIDrawManager.kInclineNormal
        )
        drawManager.setFontWeight(
            OpenMayaRender.MUIDrawManager.kWeightBold
        )

        # Draw CameraName.
        drawManager.text2d(
            OpenMaya.MPoint(screenLeft, screenTop),
            ' {} '.format(cameraName),
            alignment=OpenMayaRender.MUIDrawManager.kLeft,
            backgroundSize=None,
            backgroundColor=OpenMaya.MColor(
                (.0, .0, .0, data.borderColorAlpha)
            ),
            dynamic=False
        )

        # Draw Scene.
        drawManager.text2d(
            OpenMaya.MPoint(hCenter, screenTop),
            ' {} '.format(getSceneName()[0]),
            alignment=OpenMayaRender.MUIDrawManager.kCenter,
            backgroundSize=None,
            backgroundColor=OpenMaya.MColor(
                (.0, .0, .0, data.borderColorAlpha)
            ),
            dynamic=False
        )

        # Draw Date.
        today = datetime.now().strftime("%Y/%m/%d")
        drawManager.text2d(
            OpenMaya.MPoint(screenRight, screenTop),
            ' {} '.format(today),
            alignment=OpenMayaRender.MUIDrawManager.kRight,
            backgroundSize=None,
            backgroundColor=OpenMaya.MColor(
                (.0, .0, .0, data.borderColorAlpha)
            ),
            dynamic=False
        )

        # Draw Camera Lens.
        drawManager.text2d(
            OpenMaya.MPoint(screenLeft, screenBottom),
            ' {}mm '.format(focalLength),
            alignment=OpenMayaRender.MUIDrawManager.kLeft,
            backgroundSize=None,
            backgroundColor=OpenMaya.MColor(
                (.0, .0, .0, data.borderColorAlpha)
            ),
            dynamic=False
        )

        # Draw BG Asset.
        drawManager.text2d(
            OpenMaya.MPoint(hCenter / 4., screenBottom),
            data.assetName,
            alignment=OpenMayaRender.MUIDrawManager.kLeft,
            backgroundSize=None,
            backgroundColor=OpenMaya.MColor(
                (.0, .0, .0, data.borderColorAlpha)
            ),
            dynamic=False
        )

        # Draw Timecode.
        drawManager.text2d(
            OpenMaya.MPoint(hCenter, screenBottom),
            ' {} '.format(timeCode),
            alignment=OpenMayaRender.MUIDrawManager.kCenter,
            backgroundSize=None,
            backgroundColor=OpenMaya.MColor(
                (.0, .0, .0, data.borderColorAlpha)
            ),
            dynamic=False
        )

        # Draw overscan size.
        drawManager.text2d(
            OpenMaya.MPoint(screenRight / 1.6, screenBottom),
            data.overscanSize,
            alignment=OpenMayaRender.MUIDrawManager.kLeft,
            backgroundSize=None,
            backgroundColor=OpenMaya.MColor(
                (.0, .0, .0, data.borderColorAlpha)
            ),
            dynamic=False
        )

        # Draw camera shake type.
        drawManager.text2d(
            OpenMaya.MPoint(screenRight / 1.4, screenBottom),
            data.cameraShakeType,
            alignment=OpenMayaRender.MUIDrawManager.kLeft,
            backgroundSize=None,
            backgroundColor=OpenMaya.MColor(
                (.0, .0, .0, data.borderColorAlpha)
            ),
            dynamic=False
        )

        # Draw User
        # if data.isUserLabel:
        userName = os.environ.get('user')
        drawManager.text2d(
            OpenMaya.MPoint(screenRight, screenBottom),
            ' {} '.format(userName),
            alignment=OpenMayaRender.MUIDrawManager.kRight,
            backgroundSize=None,
            backgroundColor=OpenMaya.MColor(
                (.0, .0, .0, data.borderColorAlpha)
            ),
            dynamic=False
        )

        drawManager.endDrawable()


def _registerNode(mPlugin, cls, nodeType):
    if not nodeType:
        return
    try:
        mPlugin.registerNode(
            cls.pluginName,
            cls.nodeId,
            cls.nodeCreator,
            cls.nodeInitializer,
            nodeType,
            cls.drawDbClassification
        )
    except Exception as e:
        sys.stderr.write('Failed to register node: ' + cls.pluginName)
        print(e.message)
        print(e.args)
        raise


def _registerDraw(mdrawRegister, cls, drawOrverride):
    try:
        mdrawRegister.registerDrawOverrideCreator(
            cls.drawDbClassification,
            cls.drawRegistrantId,
            drawOrverride.creator
        )
    except Exception as e:
        sys.stderr.write("Failed to register override")
        print(e.message)
        print(e.args)
        raise


def _deregisterNode(mPlugin, cls):
    try:
        mPlugin.deregisterNode(cls.nodeId)
    except Exception as e:
        sys.stderr.write('Failed to deregister node: ' + cls.pluginName)
        print(e.message)
        print(e.args)
        raise


def _deregisterDraw(mdrawRegister, cls):
    try:
        mdrawRegister.deregisterDrawOverrideCreator(
            cls.drawDbClassification,
            cls.drawRegistrantId
        )
    except Exception as e:
        sys.stderr.write("Failed to register override")
        print(e.message)
        print(e.args)
        raise


def initializePlugin(mobject):
    mPlugin = OpenMaya.MFnPlugin(mobject, __author__, __version__, 'Any')
    nodeType = OpenMaya.MPxNode.kLocatorNode
    mdrawRegister = OpenMayaRender.MDrawRegistry

    _registerNode(mPlugin, ShotmaskNode, nodeType)
    _registerDraw(mdrawRegister, ShotmaskNode, shotmaskDrawOverride)


def uninitializePlugin(mobject):
    mPlugin = OpenMaya.MFnPlugin(mobject)
    mdrawRegister = OpenMayaRender.MDrawRegistry

    _deregisterNode(mPlugin, ShotmaskNode)
    _deregisterDraw(mdrawRegister, ShotmaskNode)


#
# AEshotmaskShapeTemplate.mel
#
if not cmds.about(batch=True):
    mel.eval('''
    refreshEditorTemplates;
    global proc AEshotmaskShape_setFont(string $attrName) {
        string $fontFamily = `fontDialog`;
        string $temp[];
        tokenize $fontFamily "|" $temp;
        textFieldGrp -e -tx $temp[0] "shotmaskShapeFontFamilyField";
        setAttr $attrName -type "string" $temp[0];
    }

    global proc AEshotmaskShape_fontFamilyWidgetProc(string $attrName) {
        rowColumnLayout -nc 2;
        $fontFamily = `getAttr $attrName`;
        textFieldGrp
             -ed 0
             -l "Font Family"
             -tx $fontFamily
             "shotmaskShapeFontFamilyField";
        button -l "..." -c ("AEshotmaskShape_setFont(\\""+$attrName+"\\")");
    }

    global proc AEshotmaskShape_updateFontFamilyWidgetProc(string $attrName) {
    }

    global proc AEshotmaskShape_fontColorWidgetProc(string $attrName) {
        $value = `getAttr $attrName`;
        rowColumnLayout -nc 2;
        floatFieldGrp
            -numberOfFields 3
            -label "Font Color"
            -en1 0 -en2 0 -en3 0
            -v1 $value[0] -v2 $value[1] -v3 $value[2]
            -cw4 145 51 51 51
            -cc ("AEshotmaskShape_setColorValue(\\"fontColorFields\\", \\"" + $attrName + "\\")")
            "fontColorFields";
        button -l "..." -c ("getColor(\\"fontColorFields\\",\\"" + $attrName + "\\")");
    }

    global proc AEshotmaskShape_updatefontColorWidgetProc(string $attrName) {
        $value = `getAttr $attrName`;
        floatFieldGrp
            -e
            -v1 $value[0]
            -v2 $value[1]
            -v3 $value[2]
            "fontColorFields";
    }

    proc AEshotmaskShape_changeFontSize(string $attrName) {
        $fontSize = `intFieldGrp -q -v1 "shotmaskShapeFontSizeField"`;
        setAttr $attrName $fontSize;
    }

    global proc AEshotmaskShape_fontSizeWidgetProc(string $attrName) {
        columnLayout -adj 1;
        intFieldGrp
            -l "Font size"
            -v1 20
            -cc ("AEshotmaskShape_changeFontSize(\\""+$attrName+"\\")")
            "shotmaskShapeFontSizeField";
    }

    global proc AEshotmaskShape_updateFontSizeWidgetProc(string $attrName) {
        $value = `getAttr $attrName`;
        intFieldGrp -e -v1 $value "shotmaskShapeFontSizeField";
    }

    global proc AEshotmaskShape_backplateColorWidgetProc(string $attrName) {
        $value = `getAttr $attrName`;
        rowColumnLayout -nc 2;
        floatFieldGrp
            -numberOfFields 3
            -label "Backplate Color"
            -en1 0 -en2 0 -en3 0
            -v1 $value[0] -v2 $value[1] -v3 $value[2]
            -cw4 145 51 51 51
            -cc ("AEshotmaskShape_setColorValue(\\"backplateColorFields\\", \\"" + $attrName + "\\")")
            "backplateColorFields";
        button -l "..." -c ("getColor(\\"backplateColorFields\\",\\"" + $attrName + "\\")");
    }

    global proc AEshotmaskShape_updatebackplateColorWidgetProc(string $attrName) {
        $value = `getAttr $attrName`;
        floatFieldGrp
            -e
            -v1 $value[0]
            -v2 $value[1]
            -v3 $value[2]
            "backplateColorFields";
    }

    global proc AEshotmaskShape_setColorValue(string $name, string $attrName) {
        $v = `floatFieldGrp -q -v $name`;
        if($v[0]<.0){$v[0]=.0;}
        if($v[0]>1.){$v[0]=1.;}
        if($v[1]<.0){$v[1]=.0;}
        if($v[1]>1.){$v[1]=1.;}
        if($v[2]<.0){$v[2]=.0;}
        if($v[2]>1.){$v[2]=1.;}
        floatFieldGrp -e -v1 $v[0] -v2 $v[1] -v3 $v[2] $name;
        setAttr $attrName $v[0] $v[1] $v[2];
    }

    global proc getColor(string $name, string $attrName) {
        string $colorPicker = "try:\\n";
        $colorPicker +=	"\\tfrom PySide.QtGui import *\\n";
        $colorPicker +=	"\\tfrom PySide.QtCore import *\\n";
        $colorPicker +=	"except:\\n";
        $colorPicker +=	"\\tfrom PySide2.QtWidgets import *\\n";
        $colorPicker +=	"\\tfrom PySide2.QtCore import *\\n";
        $colorPicker +=	"\\tfrom PySide2.QtGui import *\\n";

        $colorPicker +=	"def getColor():\\n";
        $colorPicker +=	"\\tcolor = QColorDialog.getColor(Qt.green) or []\\n";
        $colorPicker +=	"\\tif not color:\\n";
        $colorPicker +=	"\\t\\treturn [.0, .0, .0, 1.]\\n";
        $colorPicker += "\\tcolor = color.getRgbF()\\n";
        $colorPicker +=	"\\treturn [color[0], color[1], color[2], color[3]]\\n";
        python $colorPicker;
        $color = `python "getColor()"`;
        floatFieldGrp -e -v1 $color[0] -v2 $color[1] -v3 $color[2] $name;
        setAttr ($attrName) $color[0] $color[1] $color[2];
    }

    global proc AEshotmaskShape_fontAlphaWidgetProc(string $attrName) {
        $value = `getAttr $attrName`;
        columnLayout -adj 1;
        floatFieldGrp
            -numberOfFields 1
            -label "Font Alpha"
            -v1 $value
            -cc ("setAlpha(\\"fontAlphaFields\\",\\"" + $attrName + "\\")")
            "fontAlphaFields";
    }

    global proc AEshotmaskShape_updateFontAlphaWidgetProc(string $attrName) {
        $value = `getAttr $attrName`;
        floatFieldGrp -e -v1 $value "fontAlphaFields";
    }

    global proc AEshotmaskShape_backplateAlphaWidgetProc(string $attrName) {
        $value = `getAttr $attrName`;
        columnLayout -adj 1;
        floatFieldGrp
        -numberOfFields 1
        -label "Backplate Alpha"
        -v1 $value
        -cc ("setAlpha(\\"backplateColorAlphaFields\\",\\"" + $attrName + "\\")")
        "backplateColorAlphaFields";
    }

    global proc AEshotmaskShape_updatebackplateAlphaWidgetProc(string $attrName) {
        $value = `getAttr $attrName`;
        floatFieldGrp -e -v1 $value "backplateColorAlphaFields";
    }

    global proc setAlpha(string $name, string $attrName) {
        $v = `floatFieldGrp -q -v1 $name`;
        if($v < .0){$v = .0;}
        if($v > 1.){$v = 1.;}
        floatFieldGrp -e -v1 $v $name;
        setAttr $attrName $v;
    }

    global proc AEshotmaskShapeTemplate(string $nodeName) {
        editorTemplate -beginScrollLayout;
            editorTemplate
                -beginLayout (uiRes("m_AElocatorTemplate.kLocatorAttributes"))
                -collapse 0;
                AElocatorCommon $nodeName;
            editorTemplate -endLayout;
            AElocatorInclude $nodeName;
        editorTemplate -addExtraControls;
        editorTemplate -beginLayout "Viewport 2.0 Parameters";
        editorTemplate -callCustom "AEshotmaskShape_fontSizeWidgetProc" "AEshotmaskShape_updateFontSizeWidgetProc" "fontSize";
        editorTemplate -callCustom "AEshotmaskShape_fontFamilyWidgetProc" "AEshotmaskShape_updateFontFamilyWidgetProc" "fontFamily";
        editorTemplate -callCustom "AEshotmaskShape_fontColorWidgetProc" "AEshotmaskShape_updatefontColorWidgetProc" "fontColor";
        editorTemplate -callCustom "AEshotmaskShape_fontAlphaWidgetProc" "AEshotmaskShape_updateFontAlphaWidgetProc" "fontColorAlpha";
        editorTemplate -callCustom "AEshotmaskShape_backplateColorWidgetProc" "AEshotmaskShape_updatebackplateColorWidgetProc" "backplateColor";
        editorTemplate -callCustom "AEshotmaskShape_backplateAlphaWidgetProc" "AEshotmaskShape_updatebackplateAlphaWidgetProc" "borderColorAlpha";
        editorTemplate -endLayout;
        editorTemplate -endScrollLayout;
    }
    updateAE AEshotmaskShapeTemplate;
    ''')
