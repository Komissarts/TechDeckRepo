import maya.cmds as cmds
from pymel.core.other import AbcExport
import os
import re

def BrowseFolder():
    global filePath
    filePath = cmds.fileDialog2(fileMode = 3, caption = "Select Folder")[0]
    print(filePath)
    if filePath is not None:
        cmds.textField(filePathTF, text = filePath, edit = True)

def saveAsset():
    global assetMode, filePath, objName, assetCategory
    obj = cmds.textField(objName, query = True, text = True)
    path = os.path.join(filePath, "scenes", "wip", "assets", assetMode, obj)
    publishPath = os.path.join(filePath, "scenes", "publish", "assets", assetMode, obj)
    verNo = "" #HOLD BIGGEST VERSION NUMBER IN STRING "v.001"
    verNoInt = 0 #verNo IN INT FORMAT
    
    #CHECK WIP DIRECTORY EXIST, IF NOT CREATE DIRECTORY
    if os.path.isdir(path) == False:
        os.mkdir(path)
        os.mkdir(os.path.join(path, "model"))
        if assetMode == "setPiece":
            os.mkdir(os.path.join(path, "surfacing"))
        if assetMode == "prop":
            os.mkdir(os.path.join(path, "surfacing"))
            os.mkdir(os.path.join(path, "rig"))
        if assetMode == "character":
            os.mkdir(os.path.join(path, "surfacing"))
            os.mkdir(os.path.join(path, "rig"))
            os.mkdir(os.path.join(path, "anim"))
        
        verNo = str(1).zfill(3)
        
    else:
        #SET dirList TO DIRECTORY
        if assetCategory == "model" or assetCategory == "rig" or assetCategory == "anim":
            dirList = os.listdir(os.path.join(path, assetCategory))
        elif assetCategory == "surface":
            dirList = os.listdir(os.path.join(path, "surfacing"))
        if not dirList: #CHECK dirList ALREADY EXIST, IF NOT SET VERSION NUMBER TO 0
            verNoInt = 0
        else:
            verNoInt = int(re.search('.v(.+?).mb', dirList[-1]).group(1))
        
        verNo = str(verNoInt + 1).zfill(3)
    
    #SET publishPath
    if assetMode == "set":
        publishPath = os.path.join(publishPath, "model")
    elif assetCategory == "surface":
        publishPath = os.path.join(publishPath, "surfacing")
    else:
        publishPath = os.path.join(publishPath, assetCategory, "source")
    
    #CHECK publishPath EXIST
    if os.path.isdir(publishPath) == True:
        dirList = os.listdir(publishPath)
        print(dirList)
        tempInt = int(re.search('.v(.+?).mb', dirList[-1]).group(1))
        if (tempInt > verNoInt): #CHECK PUBLISH VARIANT HAVE A BIGGER VERSION NUMBER
            verNoInt = tempInt
            verNo = str(verNoInt + 1).zfill(3)
            
    fileName = obj + "_" + assetCategory + ".v" + verNo
    if assetCategory == "model" or assetCategory == "anim" or assetCategory == "rig":
        path = os.path.join(path, assetCategory)
    else:
        path = os.path.join(path, "surfacing")
    #SAVING PROCESS
    cmds.file(rename = os.path.join(path, fileName + ".mb"))
    cmds.file(save = True, type = "mayaBinary")
    changeWarnMsg("File save as " + fileName + ".mb")

def publishAsset():
    global assetMode, filePath, objName, assetCategory
    obj = cmds.textField(objName , query = True, text = True)
    path = os.path.join(filePath, "scenes", "publish", "assets", assetMode, obj)
    wipPath = os.path.join(filePath, "scenes", "wip", "assets", assetMode, obj)
    verNo = ""
    #CREATE PUBLISH DIRECTORY IF NOT EXIST
    if os.path.isdir(path) == False:
        os.mkdir(path)
        
        os.mkdir(os.path.join(path, "model"))

        if assetMode == "prop" or assetMode == "setPiece" or assetMode == "character":
            os.mkdir(os.path.join(path, "model", "cache"))
            os.mkdir(os.path.join(path, "model", "cache", "abc"))
            os.mkdir(os.path.join(path, "model", "cache", "fbx"))
            os.mkdir(os.path.join(path, "model", "cache", "obj"))
            os.mkdir(os.path.join(path, "model", "cache", "usd"))
            os.mkdir(os.path.join(path, "model", "source"))
            
            os.mkdir(os.path.join(path, "surfacing"))
            os.mkdir(os.path.join(path, "surfacing", "material"))
            os.mkdir(os.path.join(path, "surfacing", "source"))
            os.mkdir(os.path.join(path, "surfacing", "textures"))
            
            if assetMode == "prop" or assetMode == "character":
                os.mkdir(os.path.join(path, "rig"))
                os.mkdir(os.path.join(path, "rig", "source"))
                
                if assetMode == "character":
                    os.mkdir(os.path.join(path, "anim"))
                    
        if assetMode == "set":
            os.mkdir(os.path.join(path, "cache"))
            os.mkdir(os.path.join(path, "cache", "abc"))
            os.mkdir(os.path.join(path, "cache", "fbx"))
            os.mkdir(os.path.join(path, "cache", "obj"))
            os.mkdir(os.path.join(path, "cache", "usd"))
            
    #CHECK VERSION NUMBER FROM WIP DIRECTORY
    dirList = []
    if os.path.isdir(wipPath):
        if assetCategory == "model" or assetCategory == "rig" or assetCategory == "anim":
            dirList = os.listdir(os.path.join(wipPath, assetCategory))
        elif assetCategory == "surface":
            dirList = os.listdir(os.path.join(wipPath, "surfacing"))
    if not dirList or os.path.isdir(wipPath) == False:
        verNoInt = 0
    else:
        verNoInt = int(re.search('.v(.+?).mb', dirList[-1]).group(1))
        
    verNo = str(verNoInt + 1).zfill(3)
    
    fileName = ""
    
    if assetMode == "set":
        fileName = obj + "_model.v" + verNo + ".mb"
        cmds.file(rename = os.path.join(path, assetCategory, fileName))
        cmds.file(save = True, type = "mayaBinary") #Export MB File
        cmds.FBXExport('-file', os.path.join(path, "cache", "fbx", obj + "_model_fbx.v" + verNo + ".fbx")) #Export FBX
        command = "-frameRange 1 120 -dataFormat ogawa -file \"" + os.path.join(path, "cache", "abc", obj + "_model_alembic.v" + verNo + ".abc").replace("\\", "/") + "\""
        cmds.AbcExport(jobArg = command)
    
    elif assetCategory == "model":
        fileName = obj + "_model.v" + verNo + ".mb"
        cmds.file(rename = os.path.join(path, assetCategory, "source", fileName))
        cmds.file(save = True, type = "mayaBinary") #Export MB File
        cmds.FBXExport('-file', os.path.join(path, assetCategory, "cache", "fbx", obj + "_model_fbx.v" + verNo + ".fbx")) #Export FBX
        command = "-frameRange 1 120 -dataFormat ogawa -file \"" + os.path.join(path, assetCategory, "cache", "abc", obj + "_model_alembic.v" + verNo + ".abc").replace("\\", "/") + "\""
        cmds.AbcExport(jobArg = command) #Export ABC
        
    elif assetCategory == "rig":
        fileName = obj + "_rig.v" + verNo + ".mb"
        cmds.file(rename = os.path.join(path, assetCategory, "source", fileName))
        cmds.file(save = True, type = "mayaBinary")
        
    elif assetCategory == "surface":
        fileName = obj + "_surface.v" + verNo + ".mb"
        cmds.file(rename = os.path.join(path, "surfacing", "source", fileName))
        cmds.file(save = True, type = "mayaBinary")
    #CREATE ANOTHER VERSION IN WIP FOLDERS
    saveAsset()
        
    changeWarnMsg("File save as " + fileName)

def saveSequence():
    global sequenceMode, seqTF, shotTF
    seq = cmds.textField(seqTF, query = True, text = True)
    shot = cmds.textField(shotTF, query = True, text = True)
    
    path = os.path.join(filePath, "scenes", "wip", "sequence", seq, seq + "_" + shot)
    publishPath = os.path.join(filePath, "scenes", "publish", "sequence", seq, seq + "_" + shot, sequenceMode, "source")
    verNoInt = 0
    verNo = ""
    
    if os.path.isdir(os.path.join(path, sequenceMode)) == False:
        if os.path.isdir(os.path.join(filePath, "scenes", "wip", "sequence", seq)) == False:
            os.mkdir(os.path.join(filePath, "scenes", "wip", "sequence", seq))
        if os.path.isdir(path) == False:
            os.mkdir(path)
        if os.path.isdir(os.path.join(path, sequenceMode)) == False:
            os.mkdir(os.path.join(path, sequenceMode))
    
    else:
        dirList = os.listdir(os.path.join(path, sequenceMode))
        if not dirList:
            verNoInt = 0
        else:
            verNoInt = int(re.search('.v(.+?).mb', dirList[-1]).group(1))
    
    if os.path.isdir(publishPath) == True:
        dirList = os.listdir(publishPath)
        tempInt = int(re.search('.v(.+?).mb', dirList[-1]).group(1))
        if (tempInt > verNoInt): #CHECK PUBLISH VARIANT HAVE A BIGGER VERSION NUMBER
            verNoInt = tempInt
            
    verNo = str(verNoInt + 1).zfill(3)
             
    fileName = seq + "_" + shot + "_" + sequenceMode + ".v" + verNo + ".mb"
    cmds.file(rename = os.path.join(path, sequenceMode, fileName))
    cmds.file(save = True, type = "mayaBinary")
    changeWarnMsg("File save as " + fileName)
    
    

def publishSequence():
    global sequenceMode, seqTF, shotTF
    seq = cmds.textField(seqTF, query = True, text = True)
    shot = cmds.textField(shotTF, query = True, text = True)
    
    path = os.path.join(filePath, "scenes", "publish", "sequence", seq, seq + "_" + shot)
    wipPath = os.path.join(filePath, "scenes", "wip", "sequence", seq, seq + "_" + shot, sequenceMode)
    verNoInt = 0
    verNo = ""
    
    if os.path.isdir(os.path.join(path, sequenceMode)) == False:
        if os.path.isdir(os.path.join(filePath, "scenes", "publish", "sequence", seq)) == False:
            os.mkdir(os.path.join(filePath, "scenes", "publish", "sequence", seq))
        if os.path.isdir(path) == False:
            os.mkdir(path)
        if os.path.isdir(os.path.join(path, sequenceMode)) == False:
            os.mkdir(os.path.join(path, sequenceMode))
            os.mkdir(os.path.join(path, sequenceMode, "cache"))
            os.mkdir(os.path.join(path, sequenceMode, "cache", "abc"))
            os.mkdir(os.path.join(path, sequenceMode, "cache", "fbx"))
            os.mkdir(os.path.join(path, sequenceMode, "cache", "obj"))
            os.mkdir(os.path.join(path, sequenceMode, "cache", "usd"))
            os.mkdir(os.path.join(path, sequenceMode, "source"))
            if sequenceMode == "light":
                os.mkdir(os.path.join(path, sequenceMode, "renders"))
                
    else:
        dirList = os.listdir(os.path.join(path, sequenceMode, "source"))
        if not dirList:
            verNoInt = 0
        else:
            verNoInt = int(re.search('.v(.+?).mb', dirList[-1]).group(1))
    
    if os.path.isdir(wipPath) == True:
        dirList = os.listdir(wipPath)
        tempInt = int(re.search('.v(.+?).mb', dirList[-1]).group(1))
        if (tempInt > verNoInt): #CHECK WIP VARIANT HAVE A BIGGER VERSION NUMBER
            verNoInt = tempInt
    
    verNo = str(verNoInt + 1).zfill(3)
    
    fileName = seq + "_" + shot + "_" + sequenceMode + ".v" + verNo + ".mb"
    cmds.file(rename = os.path.join(path, sequenceMode, "source", fileName))
    cmds.file(save = True, type = "mayaBinary")
    cmds.FBXExport('-file', os.path.join(path, sequenceMode, "cache", "fbx", seq + "_" + shot + "_" + sequenceMode + "_" + "fbx.v" + verNo + ".fbx")) #Export FBX
    command = "-frameRange 1 120 -dataFormat ogawa -file \"" + os.path.join(path, sequenceMode, "cache", "abc", seq + "_" + shot + "_" + sequenceMode + "_" + "alembic.v" + verNo + ".abc").replace("\\", "/") + "\""
    cmds.AbcExport(jobArg = command)
    
    saveSequence()
    
    changeWarnMsg("File save as " + fileName)
    
def changeAssetMode(item): #WHEN ASSETMODE IN OPTIONMENU CHANGED
    global assetMode
    global assetCategoryOM
    global modelBtn, surfaceBtn, rigBtn, animBtn
    
    assetMode = item
    # REMOVE OPTIONS IN ASSETCATEGORY
    if cmds.menuItem(surfaceBtn, exists=True):
        cmds.deleteUI(surfaceBtn)
    if cmds.menuItem(rigBtn, exists=True):
        cmds.deleteUI(rigBtn)
    if cmds.menuItem(animBtn, exists=True):
        cmds.deleteUI(animBtn)
    #ADD OPTIONS BASED ON ASSETMODE
    if assetMode == "setPiece":
        surfaceBtn = cmds.menuItem(label = "surface", parent = assetCategoryOM)
    if assetMode == "prop":
        surfaceBtn = cmds.menuItem(label = "surface", parent = assetCategoryOM)
        rigBtn = cmds.menuItem(label = "rig", parent = assetCategoryOM)
    if assetMode == "character":
        surfaceBtn = cmds.menuItem(label = "surface", parent = assetCategoryOM)
        rigBtn = cmds.menuItem(label = "rig", parent = assetCategoryOM)
        animBtn = cmds.menuItem(label = "anim", parent = assetCategoryOM)
    
    checkFolderExist()
        
def changeAssetCategory(item):
    global assetCategory
    assetCategory = item

def changeSequenceMode(item):
    global sequenceMode
    sequenceMode = item
    checkFolderExistSeq()
    
def checkFolderExist():
    global objName, objMsg
    global assetMode
    
    obj = cmds.textField(objName, query = True, text = True) #URL TEXTFIELD
    path = os.path.join(filePath, "scenes", "wip", "assets", assetMode, obj) #CHECK OBJ ASSETMODE EXIST

    if os.path.exists(path):
        cmds.text(objMsg, label = "Folder Exist", edit = True)
    else:
        cmds.text(objMsg, label = "Folder Does Not Exist", edit = True)

def checkFolderExistSeq():
    global seqMsg, sequenceMode, seqTF, shotTF
    
    seq = cmds.textField(seqTF, query = True, text = True)
    shot = cmds.textField(shotTF, query = True, text = True)
    path = os.path.join(filePath, "scenes", "wip", "sequence", seq, seq + "_" + shot, sequenceMode)
    
    if os.path.exists(path):
        cmds.text(seqMsg, label = "Folder Exist", edit = True)
    else:
        cmds.text(seqMsg, label = "Folder Does Not Exist", edit = True)
        
def changeWarnMsg(string):
    cmds.text(warnMsg, label = string, edit = True)
    
def SavePublishWindow():
    global filePathTF
    global objName
    global objMsg
    global assetMode
    global warnMsg
    global filePath
    global assetCategory
    global assetCategoryOM
    global assetCategoryMI
    global sequenceMode, seqMsg, seqTF, shotTF
    global modelBtn, surfaceBtn, rigBtn, animBtn
    
    assetMode = "setPiece"
    assetCategory = "model"
    sequenceMode = "layout"
    
    filePath = ""
    
    if cmds.window('SavePublishWindow', exists = True):
        cmds.deleteUI('SavePublishWindow')
    
    cmds.window(width = 100)
    cmds.window('SavePublishWindow', resizeToFitChildren = True)
    
    cmds.columnLayout(adjustableColumn = True)
    
    cmds.text(label = "Project File Directory:",  align = "left")
    filePathTF = cmds.textField(text = r"D:\Uni stuff\Tech Dir of 3D Anim\TechDeckRepo\Assessment2_GroupX\Assessment2_GroupX")
    cmds.button(label = "Browse Folder", align = "center", command = "BrowseFolder()")
    
    cmds.separator(h = 10)
    cmds.text(label = "Folder Name", align = "center")
    objName = cmds.textField(changeCommand = "checkFolderExist()")
    currentFileName = os.path.basename(cmds.file(query = True, sceneName = True))
    if "_" in currentFileName:
        cmds.textField(objName, edit = True, text = re.search('(.+?)_', currentFileName).group(1))
        
    objMsg = cmds.text(label = "", align = "center")
    
    cmds.separator(h = 20)
    
    cmds.text(label = "Asset Department Selection")
    cmds.optionMenu(changeCommand = changeAssetMode)
    cmds.menuItem(label = "setPiece")
    cmds.menuItem(label = "set")
    cmds.menuItem(label = "prop")
    cmds.menuItem(label = "character")
    
    assetCategoryOM = cmds.optionMenu(changeCommand = changeAssetCategory)
    modelBtn = cmds.menuItem(label = "model", parent = assetCategoryOM)
    surfaceBtn = cmds.menuItem(label = "surface", parent = assetCategoryOM)
    rigBtn = cmds.menuItem(label = "rig", parent = assetCategoryOM)
    animBtn = cmds.menuItem(label = "anim", parent = assetCategoryOM)
    
    cmds.deleteUI(rigBtn, animBtn)

    
    cmds.separator(h=10)
    cmds.button(label = "Save", align = "center", command = "saveAsset()")
    cmds.button(label = "Publish", align = "center", command = "publishAsset()")
    
    cmds.separator(h = 20)
    
    cmds.text("Sequence Number")
    seqTF = cmds.textField(changeCommand = "checkFolderExistSeq()")
    cmds.text("Shot Number")
    shotTF = cmds.textField(changeCommand = "checkFolderExistSeq()")
    if "_" in currentFileName:
        cmds.textField(seqTF, edit = True, text = re.search('(.+?)_', currentFileName).group(1))
        cmds.textField(shotTF, edit = True, text = re.search('_(.+?)_', currentFileName).group(1))
    seqMsg = cmds.text(label = "", align = "center")
    
    cmds.columnLayout(adjustableColumn = True)
    cmds.separator(h = 10)
    cmds.text(label = "Sequence Department Selection")
    cmds.optionMenu(changeCommand = changeSequenceMode)
    cmds.menuItem(label = "layout")
    cmds.menuItem(label = "animation")
    cmds.menuItem(label = "light")
    
    cmds.separator(h=10)
    cmds.button(label = "Save", align = "center", command = "saveSequence()")
    cmds.button(label = "Publish", align = "center", command = "publishSequence()")
    cmds.separator(h = 20)
    warnMsg = cmds.text(label = "", align = "center")

    cmds.showWindow('SavePublishWindow')
SavePublishWindow()