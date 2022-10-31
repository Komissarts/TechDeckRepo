import maya.cmds as mc
import os.path
import ntpath
import json

#GITHUB LINK
#https://github.com/Komissarts/TechDeckRepo

#ASSUMPTION 1: ARTISTS CREATING SHADERS INCREMENT VERSION NUMBERS
    #i.e. PublishShaders() Only Increments Packaged Shader Files, not the individual Shaders Themselves

#ProjectDir = mc.workspace(q=True, rd=True) #Gets Relative file path for PROJECT - not scene or model


#Gets Relative File path of model 
SceneDir = str(mc.file(q=True, exn=True))
if(SceneDir.find("surfacing") != -1):
    isCurrentlyInLighting = False
elif(SceneDir.find("light") != -1):
    isCurrentlyInLighting = True







#print("SceneDirArray[-1]: "+ SceneDirArray[-1])
#ShaderPUB_Dir.replace(SceneDirArray[-1], 'test')
#ShaderPUB_Dir = '/'.join(SceneDirArray)

#print("New ShaderPUB_Dir: "+ ShaderPUB_Dir)

#String DirectoryValues for different Folders
#ShaderWIP_Dir = ProjectDir + "Scenes/wip/tst/surfacing"


if(isCurrentlyInLighting == False):
    ShaderPUB_Dir = SceneDir.replace("wip", "publish")
    #print(ShaderPUB_Dir)
    
elif(isCurrentlyInLighting == True):
    #LightPUB_Dir = SceneDir.replace("model/source", "surfacing")
    print("test")

    
ShaderDirArray=[]
for i in ShaderPUB_Dir.split('/'):
    #print(str(i))
    ShaderDirArray.append(i)
FileNameArray=[]
for i in ShaderDirArray[-1].split('.'):
    FileNameArray.append(i)
BaseSurfacingName = FileNameArray[0] + ".v"
#print(BaseSurfacingName)

ShaderDirArray.remove(ShaderDirArray[-1])

#print (str(ShaderDirArray))




ShaderPUB_Dir = '/'.join(ShaderDirArray) + "/" 

#print("New ShaderPUB_Dir: "+ ShaderPUB_Dir)

def PublishShaders():
    #mc.select(cl = True)
    selected = mc.ls(selection = True)
    ShadersToExport = []
    MeshDataToExport = []
    MeshMaterials={}
    
    if(len(selected) == 0):
        print("No Meshes Selected - Exporting All Shaders")
        selected = mc.ls(mat = True)
        
        for i in range(len(selected)):
            
            print(mc.listAttr(selected[i],iu=True))
        
        mc.select(selected)
        print("Shaders Exported: "+str(selected))
    else:
        print("Meshes Selected: Exporting Shaders")
        
        if(not mc.listRelatives(selected[0], s=True)):
            print("Selected Group or Transform, using children")
            selected = mc.listRelatives(selected[0], c=True)
        
        for i in range(len(selected)):
            selectedMesh = mc.listRelatives(selected[i], shapes=True)[0]
            selectedMeshShading = mc.listConnections(selectedMesh, type="shadingEngine")[0]
            selectedMat = mc.listConnections(selectedMeshShading + ".surfaceShader")[0]
            
            MeshMaterials[selectedMesh] = {"AttachedMaterial": selectedMat }
            
            ShadersToExport.append(selectedMat)
            #Add mesh name/data and attached material to a json file
        mc.select(ShadersToExport)
        print("Shaders Exported: "+str(ShadersToExport))
        
    fileIncrementer = 1
    while os.path.exists(ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".mb"):
        fileIncrementer  += 1    
        
    # Writing to .json File
    json_object = json.dumps(MeshMaterials, indent = 4)
    with open(ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".json", "w") as outfile:
        outfile.write(json_object)

    
    mc.file(ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".mb", force=True, op="v=0;", typ="mayaBinary", pr=True, es=True)
    print ("To Directory: " + ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".mb")
    mc.select(cl = True)

def ImportLatestShaders():
    selected = mc.ls(selection = True)
    
    for i in range(len(selected)):
        modelReference= mc.referenceQuery(selected[i], filename=True)
        surfaceReference = modelReference.replace("model/source", "surfacing")
        
        print(surfaceReference)

############################################ PSEDUDOCODE STARTS ############################################
######Go Through every file version in Shader Published Directory until find largest version num (most recent)
#    HighestVerNum = 0
#    VerIterator = 0
#    for file in ShaderPUB_Dir:
#        if(fileVerNum > VerIterator ):
#            HighestVerNum = VerIterator
#            VerIterator ++
#
#    mc.file(import ShaderPUB_Dir + "/tst_Surfacing_v"+str(HighestVerNum)+".mb") #Import most recent Shader Ver
#    
#    
######Go through every shader in the project file, check if there are duplicate named shaders
######Add the lower version number to OutdatedShaders List, add newest version number to NewShaders List
#     #Import shader & material connection data through .JSON file
######Delete All shaders in OutdatedShaders
#    outdatedShaders = []
#    newShaders = []
#    for shader in currentScene:
#        if(duplicate of same shader):
#            outdatedShaders.append(shader v < highestVerNum)
#            newShaders.append(Shader_VhighestNumber)
#        
#        mc.delete(outdatedShaders)
#    
######Allows the user to select specific objects/meshes to reapply the shaders to
######Otherwise, the new matching shaders will be applied to everything in the scene
#    selected = mc.ls(selection = True)
#    MeshesToReshade = []
#    if(len(selected) == 0):
#        print("No Meshes Selected - Reapplying All Recent Shaders")
#        selected = mc.ls(type = 'geometryShape')
#        
##########For every Object, compare it's name with the shader names from the newShaders List
##########If the Names Match - Apply shader to mesh
#        for object in selected:
#            
#        
#    else:
#        for i in range(len(selected)):
#############Same as above, but filtered by user selected meshes and models
#            selectedMesh = mc.listRelatives(selected[i], shapes=True)[0]
#            selectedMeshShading = mc.listConnections(selectedMesh, type="shadingEngine")[0]
#            
#            for shader in newShaders:
#                mc.addAttribute(selectedMeshShading)
#############selectedMat = mc.listConnections(selectedMeshShading + ".surfaceShader")[0]
#            
#            ShadersToExport.append(selectedMat)
#            mc.select(selectedMat, tgl = True)
############################################ PSEDUDOCODE END ############################################
    
    print("ImportLighting")




def ApplyCustomShaders():
    ShaderVer = mc.intField(LightingVerInput, q = True, value = True)

############################################ PSEDUDOCODE STARTS ############################################
#####Loop through versions in Shader Published Folder until Desired Shader Ver is found
#    for file in ShaderPUB_Dir:
#        if(fileVerNum == ShaderVer):
#            print("Shader Version Found!")
#            mc.file(import ShaderPUB_Dir + "/tst_Surfacing_v"+str(ShaderVer)+".mb") #Import most recent Shader Ver
#        else:
#            print("Shader Version Not Found!")
#
######Exact Same Code as ImportLatestShaders() but instead of incrementing the value to find highest one,
######Increment Value until LightingVer (from input text field) is found    
#            
############################################ PSEDUDOCODE END ############################################
    
    print("ApplyLighting")
    

def ReloadLighting():
    #¯\_(ツ)_/¯# Placeholder Function
    print("ReloadLighting")






### Yucky Gui Stuff ###
if mc.window('Shader_Publishing', exists = True):
    mc.deleteUI('Shader_Publishing')
mc.window('Shader_Publishing', resizeToFitChildren = True)
mc.columnLayout(adjustableColumn = True, cal = "center", w=300)
mc.separator(h=10)
mc.text('SceneDirectory')
mc.separator(h=10)
mc.textField(tx = SceneDir)

### Shader Exporting Functions ###
mc.separator(h=10)
mc.text('Surfacing: Select Objects to Publish')
mc.separator(h=10)
mc.button(label = 'Export Shaders to Publish', command = 'PublishShaders()', en = not isCurrentlyInLighting) #Temp Bool Inverter

### Shader Importing Functions ###
mc.separator(h=30)
mc.text('Lighting: Select Objects to Re-Apply Materials')
mc.separator(h=10)
mc.button(label = 'Import Latest Shaders', command = 'ImportLatestShaders()', en = isCurrentlyInLighting)
mc.separator(h=10)

mc.gridLayout(ch=20,cw=150, nrc=[3,2], autoGrow= True)

mc.text('Enter Version Number:')
ShaderVerInput = mc.intField(width = 50, v=0, en = isCurrentlyInLighting)

mc.separator(h=10)
mc.separator(h=10)

mc.button(label = 'Reload Shaders', command = 'ReloadLighting()', en = isCurrentlyInLighting)
mc.button(label = 'Apply Custom Shaders', command = 'ApplyCustomShaders()', en = isCurrentlyInLighting)

mc.separator(h=10)
mc.separator(h=10)

mc.showWindow('Shader_Publishing')