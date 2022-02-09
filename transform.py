#-
# Copyright 2015 Autodesk, Inc. All rights reserved.
# 
# Use of this software is subject to the terms of the Autodesk
# license agreement provided at the time of installation or download,
# or which otherwise accompanies this software in either electronic
# or hard copy form.
#+

# This plug-in implements an example custom transform that
# can be used to perform a rocking motion around the X axix.
# Geometry of any rotation can be made a child of this transform
# to demonstrate the effect.
# The plug-in contains two pieces:
# 1. The custom transform node -- NodeClass
# 2. The custom transformation matrix -- MatrixClass
# These classes are used together in order to implement the
# rocking motion.  Note that the rock attribute is stored outside
# of the regular transform attributes.

# Usage:
# import maya.cmds
# maya.cmds.loadPlugin("rockingTransform.py")
# maya.cmds.file(f=True,new=True)
# maya.cmds.polyPlane()
# maya.cmds.select("pPlane1",r=True)
# maya.cmds.rotate(-15,-15,-15,r=True,ws=True)
# maya.cmds.createNode("spRockingTransform")
# maya.cmds.parent("pPlane1","spRockingTransform1")
# maya.cmds.setAttr("spRockingTransform1.rockx",55)
#

import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import math
import sys

kRockingTransformPluginName = "spRockingTransform"
kRockingTransformNodeName = "spRockingTransformNode"
# 0x00000000 ～ 0x0007ffff
plugin_node_ids = (
    OpenMaya.MTypeId(0x00090001),
    OpenMaya.MTypeId(0x00090002),
)

# keep track of instances of MatrixClass to get around script limitation
# with proxy classes of base pointers that actually point to derived
# classes
kTrackingDictionary = {}


class MatrixClass(OpenMayaMPx.MPxTransformationMatrix):
    def __init__(self):
        OpenMayaMPx.MPxTransformationMatrix.__init__(self)
        kTrackingDictionary[OpenMayaMPx.asHashable(self)] = self
        self.rockXValue = 0.0

    def __del__(self):
        del kTrackingDictionary[OpenMayaMPx.asHashable(self)]

    def setRockInX(self,rockingValue):
        self.rockXValue = rockingValue

    def getRockInX(self):
        return self.rockXValue

    def asMatrix(self,percent=None):
        """
        Find the new matrix and return it
        """
        if percent == None:
            matrix = OpenMayaMPx.MPxTransformationMatrix.asMatrix(self)
            tm = OpenMaya.MTransformationMatrix(matrix)
            quat = self.rotation()
            rockingValue = self.getRockInX()
            newTheta = math.radians( rockingValue )
            quat.setToXAxis( newTheta )
            tm.addRotationQuaternion( quat.x, quat.y, quat.z, quat.w, OpenMaya.MSpace.kTransform )
            return tm.asMatrix()
        else:
            m = OpenMayaMPx.MPxTransformationMatrix(self)
            #
            trans = m.translation()
            rotatePivotTrans = m.rotatePivot()
            scalePivotTrans = m.scalePivotTranslation()
            trans = trans * percent
            rotatePivotTrans = rotatePivotTrans * percent
            scalePivotTrans = scalePivotTrans * percent
            m.translateTo(trans)
            m.setRotatePivot( rotatePivotTrans )
            m.setScalePivotTranslation( scalePivotTrans )
            #
            quat = self.rotation()
            rockingValue = self.getRockInX()
            newTheta = math.radians( rockingValue )

            quat.setToXAxis( newTheta )
            m.rotateBy( quat )
            eulerRotate = m.eulerRotation()
            m.rotateTo( eulerRotate * percent, OpenMaya.MSpace.kTransform )
            #
            s = self.scale( OpenMaya.MSpace.kTransform )
            s.x = 1.0 + ( s.x - 1.0 ) * percent
            s.y = 1.0 + ( s.y - 1.0 ) * percent
            s.z = 1.0 + ( s.z - 1.0 ) * percent
            m.scaleTo( s, OpenMaya.MSpace.kTransform )
            #
            return m.asMatrix()


class NodeClass(OpenMayaMPx.MPxTransform):
    aRockInX = OpenMaya.MObject()

    def __init__(self, transform=None):
        if transform is None:
            OpenMayaMPx.MPxTransform.__init__(self)
        else:
            OpenMayaMPx.MPxTransform.__init__(self, transform)
        self.rockXValue = 0.0

    def createTransformationMatrix(self):
        return OpenMayaMPx.asMPxPtr(MatrixClass())

    def className(self):
        return kRockingTransformNodeName

    def compute(self, plug, data):
        if plug.isNull():
            return OpenMayaMPx.MPxTransform.compute(plug, data)

        if ( (plug == self.matrix)
        or   (plug == self.inverseMatrix)
        or   (plug == self.worldMatrix)
        or   (plug == self.worldInverseMatrix)
        or   (plug == self.parentMatrix)
        or   (plug == self.parentInverseMatrix) ):

            try:
                rockInXData = data.inputValue( self.aRockInX )

                # Update our new internal "rock in x" value
                rockInX = rockInXData.asDouble()

                # Update the custom transformation matrix to the
                # right rock value.
                ltm = self.getRockingTransformationMatrix()
                if ltm is not None:
                    ltm.setRockInX(rockInX)
            except Exception as ex:
                print('rockingTransform Compute error: {}'.format(str(ex)))

        return OpenMayaMPx.MPxTransform.compute(self, plug, data)

    def validateAndSetValue(self, plug, handle, context):
        if not plug.isNull():
            if plug == self.aRockInX:
                block = self._forceCache(context)
                blockHandle = block.outputValue(plug)

                # Update our new rock in x value
                rockInX = handle.asDouble()
                blockHandle.setDouble(rockInX)

                # Update the custom transformation matrix to the
                # right value.
                ltm = self.getRockingTransformationMatrix()
                if ltm is not None:
                    ltm.setRockInX(rockInX)

                blockHandle.setClean()

                # Mark the matrix as dirty so that DG information
                # will update.
                self._dirtyMatrix()

        OpenMayaMPx.MPxTransform.validateAndSetValue(self, plug, handle, context)

    def getRockingTransformationMatrix(self):
        baseXform = self.transformationMatrixPtr()
        return kTrackingDictionary[OpenMayaMPx.asHashable(baseXform)]

    @classmethod
    def nodeCreator(cls):
        return OpenMayaMPx.asMPxPtr(cls())

    @classmethod
    def nodeInitializer(cls):
        numFn = OpenMaya.MFnNumericAttribute()

        cls.aRockInX = numFn.create(
            "RockInX",
            "rockx",
            OpenMaya.MFnNumericData.kDouble,
            0.0
        )

        numFn.setKeyable(True)
        numFn.setAffectsWorldSpace(True)

        cls.addAttribute(cls.aRockInX)
        cls.mustCallValidateAndSet(cls.aRockInX)
        return

    @classmethod
    def matrixCreator(cls):
        return OpenMayaMPx.asMPxPtr(cls())


# create/initialize node and matrix
# initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)

    try:
        mplugin.registerTransform(
            kRockingTransformPluginName,
            plugin_node_ids[0],
            NodeClass.nodeCreator,
            NodeClass.nodeInitializer,
            NodeClass.matrixCreator,
            plugin_node_ids[1]
        )
    except:
        sys.stderr.write("Failed to register transform: {}\n".format(kRockingTransformPluginName))
        raise


# uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)

    try:
        mplugin.deregisterNode(plugin_node_ids[0])
    except:
        sys.stderr.write("Failed to unregister node: {}\n".format(kRockingTransformPluginName))
        raise