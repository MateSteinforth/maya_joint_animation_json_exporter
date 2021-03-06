from maya import cmds
import maya.OpenMaya as om
import math
import json
import os

def saveSelectedJointsToJsonFile(startTime, endTime, filename = "joints"):

     objects = cmds.ls(selection=True, type="joint", dag=True, long=True)
     joints = {}
     timeRange = range(startTime,endTime+1,1)

     for obj in objects:

         jointDict = {}
         shortName = obj.split("|")[-1]
         isRoot = False
         if "_ROOT_" in shortName:
             isRoot = True

         print cmds.listAttr(r=True)

         for frame in timeRange:
             if isRoot:
                jointDict[frame] = _getFrameDictForRootJoint(obj,frame)
             else:
                jointDict[frame] = _getFrameDict(obj,frame)

         joints[shortName] = jointDict

     jsonObject = json.dumps(joints)
     _saveJson(jsonObject, filename)

#non root joints should pass values from object space
def _getFrameDict(obj, frame):

    rotOrder = cmds.getAttr('%s.rotateOrder'%obj)

    jointMat = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(cmds.getAttr('%s.matrix'%obj, time=frame), jointMat)
    jointTMat = om.MTransformationMatrix(jointMat)

    eulerRot = jointTMat.eulerRotation()
    eulerRot.reorderIt(rotOrder)
    translation = jointTMat.getTranslation(om.MSpace.kTransform)
    angles = [math.degrees(angle) for angle in (eulerRot.x, eulerRot.y, eulerRot.z)]

    frameDict = {}

    frameDict['tx'] = "%.8f" % translation.x
    frameDict['ty'] = "%.8f" % translation.y
    frameDict['tz'] = "%.8f" % translation.z
    frameDict['rx'] = "%.8f" % (angles[0])
    frameDict['ry'] = "%.8f" % (angles[1])
    frameDict['rz'] = "%.8f" % (angles[2])
    return frameDict

#root joints pass values from world space
def _getFrameDictForRootJoint(obj,frame):

    #get world matrix for root joint
    rootJointWMat = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(cmds.getAttr('%s.worldMatrix'%obj, time=frame), rootJointWMat)
    jointWorldMat = om.MTransformationMatrix(rootJointWMat)

    #read rotation in world space
    rotOrder = cmds.getAttr('%s.rotateOrder'%obj)
    eulerRot = jointWorldMat.eulerRotation()
    eulerRot.reorderIt(rotOrder)
    translation = jointWorldMat.getTranslation(om.MSpace.kWorld)

    angles = [math.degrees(angle) for angle in (eulerRot.x, eulerRot.y, eulerRot.z)]

    frameDict = {}

    frameDict['tx'] = "%.8f" % translation.x
    frameDict['ty'] = "%.8f" % translation.y
    frameDict['tz'] = "%.8f" % translation.z
    frameDict['rx'] = "%.8f" % (angles[0])
    frameDict['ry'] = "%.8f" % (angles[1])
    frameDict['rz'] = "%.8f" % (angles[2])

    print "--------------"
    print obj
    print frame
    print "--------------"
    print translation.x
    print translation.y
    print translation.z
    print angles
    print frameDict
    print "              "

    return frameDict

def _saveJson(jsonObject, filename):
    if ".json" not in filename:
        filename += ".json"

    completeName = os.path.join(os.path.expanduser('~'))
    completeName += "/" + filename;

    with open(completeName, "w") as jsonFile:
        json.dump(jsonObject, jsonFile, indent=2)

    print "Finished writing data to {0}".format(completeName)
