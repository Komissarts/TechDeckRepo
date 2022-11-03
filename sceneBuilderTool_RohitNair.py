import maya.cmds as cmds
import os
import re
import ntpath
import posixpath

#Get Relative File path of directories
SceneDir = str(cmds.file(q=True, exn=True))
AssetsDir = SceneDir[:SceneDir.rfind("sequence")] + "assets"
SetDir = AssetsDir + "/set/"
CamDir = AssetsDir + "/camera/"
CharDir = AssetsDir + "/character/"
PropDir = AssetsDir + "/prop/"

#Check if Windows OS
if(os.name == 'nt'):
    isWindows = True
else:
    isWindows = False

def buildScene(): #Detects what scene the user is in and imports relevant assets
    if(SceneDir.find("animation") != -1):
        print('Building Animation')
        importSetAssets()
        importCamAssets()
        importCharAssets()
        importPropAssets()
    elif(SceneDir.find("layout") != -1):
        print('Building Layout')
        importSetAssets()
        importCharAssets()
        importPropAssets()
    elif(SceneDir.find("light") != -1):
        print('Building Lighting')
        importSetAssets()
        importCamAssets()
    else:
        print('Scene Not Identified. Please open an animation, layout or lighting scene.')

def importSetAssets():
    ModelDir = None
    verNumber = ''
    verNumberInt = 0
    verIncrementer = 1
    modelName = ''

    #Goes into correct directories and finds the models to be imported
    for filename in os.listdir(SetDir):
        if "DS_Store" not in filename:
            ModelDir = SetDir + filename + '/model/'
            for model in os.listdir(ModelDir):
                # Version control to determine latest model version and import it
                if "DS_Store" not in model and "cache" not in model and "source" not in model:
                    verNumber = model[-4:-3]
                    verNumberInt = int(verNumber)
                    modelName = model[0:-8]
                    while os.path.exists(modelName + '.v00' + str(verIncrementer) + '.mb'):
                        verIncrementer += 1
                    importVersion = verIncrementer - 1                    
                    latestVersion = ModelDir + modelName + '.v00' + str(verIncrementer) + '.mb'
                    print(latestVersion)
                    cmds.file(latestVersion, r=True, force=True, typ="mayaBinary", pr=True)

def importCamAssets():
    ModelDir = None
    verNumber = ''
    verNumberInt = 0
    verIncrementer = 1
    modelName = ''

    for filename in os.listdir(CamDir):
        if "DS_Store" not in filename:
            ModelDir = CamDir + filename + '/model/'
            for model in os.listdir(ModelDir):
                if "DS_Store" not in model and "cache" not in model and "source" not in model:
                    verNumber = model[-4:-3]
                    verNumberInt = int(verNumber)
                    modelName = model[0:-8]
                    while os.path.exists(modelName + '.v00' + str(verIncrementer) + '.mb'):
                        verIncrementer += 1
                    importVersion = verIncrementer - 1                    
                    latestVersion = ModelDir + modelName + '.v00' + str(verIncrementer) + '.mb'
                    print(latestVersion)
                    cmds.file(latestVersion, r=True, force=True, typ="mayaBinary", pr=True)                    

def importCharAssets():
    ModelDir = None
    verNumber = ''
    verNumberInt = 0
    verIncrementer = 1
    modelName = ''

    for filename in os.listdir(CharDir):
        if "DS_Store" not in filename:
            ModelDir = CharDir + filename + '/model/'
            for model in os.listdir(ModelDir):
                if "DS_Store" not in model and "cache" not in model and "source" not in model:
                    verNumber = model[-4:-3]
                    verNumberInt = int(verNumber)
                    modelName = model[0:-8]
                    while os.path.exists(modelName + '.v00' + str(verIncrementer) + '.mb'):
                        verIncrementer += 1
                    importVersion = verIncrementer - 1                    
                    latestVersion = ModelDir + modelName + '.v00' + str(verIncrementer) + '.mb'
                    print(latestVersion)
                    cmds.file(latestVersion, r=True, force=True, typ="mayaBinary", pr=True)

def importPropAssets():
    ModelDir = None
    verNumber = ''
    verNumberInt = 0
    verIncrementer = 1
    modelName = ''

    for filename in os.listdir(PropDir):
        if "DS_Store" not in filename:
            ModelDir = PropDir + filename + '/model/source/'
            for model in os.listdir(ModelDir):
                if "DS_Store" not in model and "cache" not in model and "source" not in model:
                    verNumber = model[-4:-3]
                    verNumberInt = int(verNumber)
                    modelName = model[0:-8]
                    while os.path.exists(modelName + '.v00' + str(verIncrementer) + '.mb'):
                        verIncrementer += 1
                    importVersion = verIncrementer - 1                    
                    latestVersion = ModelDir + modelName + '.v00' + str(verIncrementer) + '.mb'
                    print(latestVersion)
                    cmds.file(latestVersion, r=True, force=True, typ="mayaBinary", pr=True)


#GUI
#Create Window
if cmds.window('Scene_Builder', exists = True):
    cmds.deleteUI('Scene_Builder')
cmds.window('Scene_Builder', resizeToFitChildren = True)
cmds.columnLayout(adjustableColumn = True, cal = "center", w=200)
cmds.separator(h=10)
cmds.text('Scene Directory')
cmds.separator(h=10)
cmds.textField(tx = SceneDir)
cmds.separator(h=20)

#Build Scene Section
cmds.button(label='Build Current Scene', command='buildScene()')
cmds.separator(h=20)

cmds.showWindow('Scene_Builder')
