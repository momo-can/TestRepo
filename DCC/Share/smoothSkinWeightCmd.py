# -*- coding: utf-8 -*-
import re
from maya import OpenMaya
from maya import OpenMayaAnim
from maya import OpenMayaMPx
from maya import cmds

kPluginCmdName = "smoothSkinWeight"
kValueFlag = "-v"
kValueLongFlag = "-value"


class SmoothSkinWeightCmd(OpenMayaMPx.MPxCommand):
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

        self.dagPath = OpenMaya.MDagPath()
        self.component = OpenMaya.MObject()
        self.fnSkin = None
        self.infDags = OpenMaya.MDagPathArray()
        self.maintainMaxInfluences = True
        self.maxInfluences = 4
        self.indecies = None

        self.value = 0.5

        self.oldWeights = OpenMaya.MDoubleArray()
        self.infIndices = None
        self.mitVtx = None
        self.indecies = []

        self.error_is = False

        self.skinCluster = ''
        self.obj = ''
        self.mitVex = ''

    def isUndoable(self):
        return True

    def getVertsIndecies(self):
        if not self.component.isNull():
            # There were components selected
            self.indecies = OpenMaya.MIntArray(self.mitVtx.count(), 0)
            i = 0
            while not self.mitVtx.isDone():
                self.indecies[i] = self.mitVtx.index()
                i += 1
                self.mitVtx.next()

    def doIt(self, args):
        # Create selection list.
        sel_list = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(sel_list)

        # Create dagPath.
        sel_list.getDagPath(0, self.dagPath)

        # Create component.
        sel_list.getDagPath(0, self.dagPath, self.component)

        if self.component.apiType() != OpenMaya.MFn.kMeshVertComponent:
            OpenMaya.MGlobal.displayError('Please select verticies.')
            self.error_is = True
            return

        # currentNode is MObject to your mesh
        self.mitVtx = OpenMaya.MItMeshVertex(self.dagPath, self.component)

        # get skincluster from shape
        # get dag path for selection
        try:
            sel_list.getDagPath(0, self.dagPath, self.component)
            self.dagPath.extendToShape()
        except:
            self.error_is = True
            return

        # get skincluster from shape
        itSkin = OpenMaya.MItDependencyGraph(
            self.dagPath.node(),
            OpenMaya.MFn.kSkinClusterFilter,
            OpenMaya.MItDependencyGraph.kUpstream,
            OpenMaya.MItDependencyGraph.kBreadthFirst,
            OpenMaya.MItDependencyGraph.kPlugLevel
        )

        skcMObj = None
        while not itSkin.isDone():
            skcMObj = itSkin.currentItem()
            self.fnSkin = OpenMayaAnim.MFnSkinCluster(skcMObj)

            # cast current MObj to MFnDependencyNode to get attribute value
            mFnDependSkinCluster = OpenMaya.MFnDependencyNode(skcMObj)

            # get if maintain max influences is checked
            maintainMaxInfMPlug = mFnDependSkinCluster.findPlug(
                'maintainMaxInfluences')
            self.maintainMaxInfluences = maintainMaxInfMPlug.asBool()

            # get number of max influences to maintain
            maxInfMPlug = mFnDependSkinCluster.findPlug('maxInfluences')
            self.maxInfluences = maxInfMPlug.asInt()
            break

        # Get inf dags.
        self.fnSkin.influenceObjects(self.infDags)

        # Create verts indecies.
        self.getVertsIndecies()

        # parse flags
        argData = OpenMaya.MArgDatabase(self.syntax(), args)

        # -value
        if argData.isFlagSet(kValueFlag):
            self.value = argData.flagArgumentDouble(kValueFlag, 0)

        # do the actual work
        self.redoIt()

    def undoIt(self):
        if self.error_is:
            pass
        else:
            # Restore oldWeights.
            self.fnSkin.setWeights(
                self.dagPath,
                self.component,
                self.infIndices,
                self.oldWeights,
                False
            )

    def redoIt(self):
        mitVtx = self.mitVtx

        # Pre difines.
        infCount = OpenMaya.MScriptUtil()
        int = infCount.asUintPtr()

        # Check tweek.
        if not self.fnSkin:
            OpenMaya.MGlobal.displayError("skinCluster was not found.")
            self.error_is = True
            return

        # Catch current vertecies.
        vtx_count = self.indecies.length()
        # Cache old weight.
        self.fnSkin.getWeights(
            self.dagPath, self.component, self.oldWeights, int)
        inf_count = OpenMaya.MScriptUtil.getUint(int)
        newWeights = []
        start_id = 0
        slice_id = inf_count

        hold_map = {}
        for x in xrange(self.infDags.length()):
            inf_path = self.infDags[x].fullPathName()
            hold_val = cmds.getAttr('%s.liw' % inf_path)
            hold_map[x] = hold_val

        for vtx_id in self.indecies:
            # Set iterator index
            util = OpenMaya.MScriptUtil()
            util.createFromInt(0)
            prev_ptr = util.asIntPtr()
            self.mitVtx.setIndex(vtx_id, prev_ptr)

            # Current weight.
            currentWeight = self.oldWeights[start_id:slice_id]

            # Get connected vertices
            vertices = OpenMaya.MIntArray()
            self.mitVtx.getConnectedVertices(vertices)
            cntVtxCount = vertices.length()

            # Get near weights.
            components = OpenMaya.MFnSingleIndexedComponent().create(
                OpenMaya.MFn.kMeshVertComponent)
            OpenMaya.MFnSingleIndexedComponent(components).addElements(
                vertices)
            nearWeights = OpenMaya.MDoubleArray()
            self.fnSkin.getWeights(
                self.dagPath, components, nearWeights, int)

            # Calc average.
            w_count = nearWeights.length()
            weight_template = []
            total_weight = 0.0
            free_inf = 0
            for i in range(inf_count):
                current_id = i
                calc_value = 0.0

                res = 0.0
                if hold_map.get(i) is True:
                    res = currentWeight[i]
                    free_inf += 1
                else:
                    for v in range(cntVtxCount):
                        if v > 0:
                            current_id += inf_count
                        calc_value += ((nearWeights[current_id] / cntVtxCount) * self.value) + (currentWeight[i] / cntVtxCount) * (1. - self.value)
                    res = calc_value

                weight_template.append(res)
                total_weight += res

            # Normalize.
            normal_weight = []

            free_inf = inf_count-free_inf
            if free_inf == 0:
                free_inf = inf_count

            norm_sum = 0.0
            for i in range(len(weight_template)):
                hold_is = hold_map.get(i)
                if not hold_is:
                    norm_sum += weight_template[i]

            over_weight = total_weight-1.0

            if over_weight != 0.0:
                for i in range(len(weight_template)):
                    hold_is = hold_map.get(i)
                    v = weight_template[i]
                    if not hold_is and v > 0.0:
                        precision = v/norm_sum
                        normal_weight.append(v - over_weight * precision)
                    else:
                        normal_weight.append(v)
            else:
                normal_weight = weight_template

            newWeights = newWeights+normal_weight

            start_id += inf_count
            slice_id += inf_count

        # Reset variable infIndices
        infIndices_util = OpenMaya.MScriptUtil()
        infIndices_util.createFromList(range(0, inf_count), inf_count)
        infIndices_iPtr = infIndices_util.asIntPtr()
        self.infIndices = OpenMaya.MIntArray(infIndices_iPtr, inf_count)

        # newWeights
        newWeight_util = OpenMaya.MScriptUtil()
        newWeight_util.createFromList(newWeights, self.oldWeights.length())
        newWeight_dPtr = newWeight_util.asDoublePtr()
        resWeights = OpenMaya.MDoubleArray(
            newWeight_dPtr, self.oldWeights.length())
        self.fnSkin.setWeights(
            self.dagPath, self.component,
            self.infIndices, resWeights, False, self.oldWeights)


# Creator
def cmdCreator():
    # Create the command
    return OpenMayaMPx.asMPxPtr(SmoothSkinWeightCmd())


# Syntax creator
def syntaxCreator():
    syntax = OpenMaya.MSyntax()
    syntax.addFlag(kValueFlag, kValueLongFlag, OpenMaya.MSyntax.kDouble)
    return syntax


# Initialize the script plug-in
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Nuternativ", "1.0", "Any")
    try:
        mplugin.registerCommand(kPluginCmdName, cmdCreator, syntaxCreator)
    except Exception, e:
        OpenMaya.MGlobal.displayError(
            'Failed to register command:  %s\n%s' % (kPluginCmdName, e))


# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(kPluginCmdName)
    except Exception, e:
        OpenMaya.MGlobal.displayError(
            'Failed to de-register command:  %s\n%s' % (kPluginCmdName, e))
