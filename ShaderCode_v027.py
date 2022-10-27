import maya.cmds as mc
import os
import ntpath
import json
import posixpath
import mtoa

#Gets Relative File path of model 
SceneDir = str(mc.file(q=True, exn=True))

#Boolean flip flop to check if user is in surfacing or lighting scene
#or mabye theyre a little lost and in neither
UserSeemsToBeALittleLost = False
if(SceneDir.find("surfacing") != -1):
    isCurrentlyInLighting = False
elif(SceneDir.find("light") != -1):
    isCurrentlyInLighting = True
else:
    UserSeemsToBeALittleLost = True

#test to check difference between linux and windows system
#beats me, since maya seems to be using linux
#forward slashes (/), even if its running in a windows computer
#so i guess it should be fine?
# ¯\_( ツ )_/¯
if(os.name == 'nt'):
    isRunningWindows = True
else:
    isRunningWindows = False

#If the user is currently in a surfacing scene, they will only need
#access to that model's published folder, which is a simple word replace
#Getting access to the version number and file name is a bit more involved
if(isCurrentlyInLighting == False):
    ShaderPUB_Dir = SceneDir.replace("wip", "publish")
    ShaderDirArray=[]
    for i in ShaderPUB_Dir.split('/'):
        ShaderDirArray.append(i)
    FileNameArray=[]
    for i in ShaderDirArray[-1].split('.'):
        FileNameArray.append(i)
    BaseSurfacingName = FileNameArray[0] + ".v"
    ShaderDirArray.remove(ShaderDirArray[-1])
    ShaderPUB_Dir = '/'.join(ShaderDirArray) + "/" 

#We can't use the same trick in lighting scenes, the above directory splitting
#and appending needs to be done for each object in the scene.
elif(isCurrentlyInLighting == True):
    print("Currently In A Lighting Scene") #(⌐▨_▨)


def PublishShaders():
    selected = mc.ls(selection = True) #start off by using whatever the user has selected 
    ShadersToExport = []
    MeshDataToExport = []
    MeshMaterials={} #JSON Dict array
    
    if(len(selected) == 0):
        print("No Meshes Selected - Exporting All Shaders")
        #im banking a lot on the naming convention being consistent ●﹏●
        selected = mc.ls('mRef_*')
        mc.select(selected)
        
    else:
        print("Meshes Selected: Exporting Shaders")
    #backup check in case the user selects a transform group
    #grabs the groups children objects instead
    if(not mc.listRelatives(selected[0], s=True)):
        print("Selected Group or Transform, using children")
        selected = mc.listRelatives(selected[0], c=True)
    #For every selected object, access its mesh shading and attached material.
    for i in range(len(selected)):
        selectedMesh = mc.listRelatives(selected[i], shapes=True)[0]
        selectedMeshShading = mc.listConnections(selectedMesh, type="shadingEngine")[0]
        selectedMat = mc.listConnections(selectedMeshShading + ".surfaceShader")[0]
        
        #adds the mesh and its material to a JSON Dict
        #Use a colon for some sneaky splitting later on
        MeshMaterials[selectedMesh +":"+ selectedMat] = {"AttachedMaterial": selectedMat }
        #Adds the materials to a list for exporting
        ShadersToExport.append(selectedMat)
        
    mc.select(ShadersToExport)
    #File incrementer function that checks the destination folder for other files of the same version
    fileIncrementer = 1
    while os.path.exists(ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".mb"):
        fileIncrementer += 1

    # Writing to .json File
    json_object = json.dumps(MeshMaterials, indent = 4)
    with open(ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".json", "w") as outfile:
        outfile.write(json_object)
    #Export the selected ShadersToExport list as a file with the same name and destination as the JSON file for easy parsing later
    mc.file(ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".mb", force=True, op="v=0;", typ="mayaBinary", pr=True, es=True)
    print ("Shaders Exported: "+str(ShadersToExport) + "| As: " + BaseSurfacingName + str(fileIncrementer) +".mb")
    mc.select(cl = True)



def ImportLatestShaders():
    SelectedShaderVer = mc.intField(ShaderVerInput, q = True, value = True)
    SceneGeometryList = mc.ls(selection = True)
    #One of the loops import the surfacing file for every mesh, 
    #this array is to prevent it from doing that.
    PreviouslyVisitedDirectories=[]
    #Checks if the user has selected any meshes
    #if nothing has been selected, select all geometry objects and apply shaders
    if(len(SceneGeometryList) == 0):
        print("No Meshes Selected - Importing All Shaders")
        AllSceneGeometryList = mc.ls(geometry=True)
        SceneGeometryList = AllSceneGeometryList
    else:
        print("Meshes Selected: " +str(SceneGeometryList)+ "Importing Shaders")

    for SceneGeometry in range(len(SceneGeometryList)):
        #Reverse searches by using the folder location of the referenced objects and replacing
        #words to reach that model's surfacing folder.
        ModelReferenceDir = mc.referenceQuery(SceneGeometryList[SceneGeometry], filename=True)
        ShaderPUB_Dir = ModelReferenceDir.replace("model/source", "surfacing")
        
        #Same directory slicing and dicing as before, with some minot changes to make it function properly
        ShaderPUB_DirArray=[]
        for DirSplitFwdSlsh in ShaderPUB_Dir.split('/'):
            ShaderPUB_DirArray.append(DirSplitFwdSlsh)
        FileNameArray=[]
        for DirSplitPeriod in ShaderPUB_DirArray[-1].split('.'):
            FileNameArray.append(DirSplitPeriod)
        BaseSurfacingName = FileNameArray[0]
        BaseSurfacingName = BaseSurfacingName.replace("model", "surface")
        ShaderPUB_DirArray.remove(ShaderPUB_DirArray[-1])
        ShaderPUB_Dir = '/'.join(ShaderPUB_DirArray) + "/"
        
        #Same File Incrementer as before
        fileIncrementer = 1
        while os.path.exists(ShaderPUB_Dir + BaseSurfacingName + ".v"+ str(fileIncrementer) +".mb"):
            fileIncrementer += 1
        ShaderVer = fileIncrementer - 1
        #Except this time it has a check against the input version number
        #if left at a default 0, it grabs the most recent one, otherwise it goes for
        #the selected shade ver.
        if(SelectedShaderVer > 0):
            ShaderVer = SelectedShaderVer
        
        LatestShaderMB_Dir = ShaderPUB_Dir + BaseSurfacingName + ".v"+ str(ShaderVer) +".mb"        #Shader Directory for most recent MayaBinary File
        LatestShaderJSON_Dir = ShaderPUB_Dir + BaseSurfacingName + ".v"+ str(ShaderVer) +".json"    #Shader Directory for most recent JSON File
        #If the maya binary and json directories exist and havent been visited in a previous loop
        if(os.path.exists(LatestShaderMB_Dir) & os.path.exists(LatestShaderJSON_Dir)):
            if(LatestShaderMB_Dir not in PreviouslyVisitedDirectories):
                #add this directory to previously visited
                PreviouslyVisitedDirectories.append(LatestShaderMB_Dir)
                #open and read the JSON file
                with open(LatestShaderJSON_Dir, 'r') as infile:
                    data=infile.read()
                obj = json.loads(data)
                #and import the maya binary shader file
                #VERY IMPORTANT: As part of the namespace, that prepends the shaders being imported
                #we attach the version number and the file it came from. This is super important for parsing which version and where the material came from
                #as multiple different models can use different variants of the same material
                mc.file(LatestShaderMB_Dir, i=True, type="mayaBinary", ra=True, rdn=True, mnc=False, ns="v_"+str(ShaderVer)+BaseSurfacingName, op="v=0", pr=True, an=True, itr="keep", mnr=True)
                
                for set in obj:
                    Obj_Material=[]
                    #since we stored the material and mesh it was attached to in the title of the json list
                    #we can just split it
                    for i in set.split(':'):            
                        Obj_Material.append(i)
                    ObjTransformList = mc.ls("*:"+Obj_Material[0]+"*")
                    #using the namespace to find and assign the right 
                    MaterialList = mc.ls("*v_"+str(ShaderVer)+BaseSurfacingName+"*:"+Obj_Material[1]+"*")
                    if(ObjTransformList):
                        ObjTransform = ObjTransformList[0]
                        Material = MaterialList[0]
                        print("Mesh: " + ObjTransform + " | Material: " + Material + " | Shader Ver. Being Applied: " + str(ShaderVer))
                        mc.select(ObjTransform)
                        #i wasted a solid week trying to reassign connections, attributes and nodes
                        #BECAUSE FOR SOME REASON WHEN MANUALLY USING HYPERSHADE, IT NEVER USES ITS OWN FUNCTION
                        mc.hyperShade(assign=str(Material))
                        mc.select(cl=True)
                    else:
                        print("WARNING - Lighting Scene Model does not match published model, Expected: " + Obj_Material[0] + 
                              " | Recieved: " + SceneGeometryList[SceneGeometry] + " Please Update References")
                infile.close()
        else:
            print("WARNING - " + SceneGeometryList[SceneGeometry] + " Does Not Have Published Shader Version: " + str(ShaderVer))


def RemoveUnused():
    mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
    
    print("Removed Unused Materials")
    
    
#Obsolete Removed Code to replace and update references in the scene
def ReloadReferences():
    selected = mc.ls(selection = True)
    AllSceneGeometryList = mc.ls(geometry=True)
    SceneGeometryList = AllSceneGeometryList
    for SceneGeometry in SceneGeometryList:
        if(mc.referenceQuery(SceneGeometry, isNodeReferenced=True)):
            print(SceneGeometry+"Is a reference")
            
            parents = mc.ls(SceneGeometry, long=True)[0].split('|')[1:-1]
            print(parents)
            selectedParent = mc.ls(parents[1])[0]
            print(selectedParent)
            if(mc.referenceQuery(selectedParent, isNodeReferenced=True)):
                print(selectedParent+"is also a ref")
                
                print(mc.referenceQuery(selectedParent, f=True))
                ModelReference_Dir = mc.referenceQuery(selectedParent, f=True, p=True)
                
                ModelReference_DirArray=[]
                for DirSplitFwdSlsh in ModelReference_Dir.split('/'):
                    ModelReference_DirArray.append(DirSplitFwdSlsh)
                    
                FileNameArray=[]
                for DirSplitPeriod in ModelReference_DirArray[-1].split('.'):
                    FileNameArray.append(DirSplitPeriod)
                    
                if(FileNameArray[-1] == "mb"):
                    BaseSurfacingName = FileNameArray[0]
                    
                    ModelReference_DirArray.remove(ModelReference_DirArray[-1])
                    ModelReference_Dir = '/'.join(ModelReference_DirArray) + "/"                    
                    fileIncrementer = 1
                    while os.path.exists(ModelReference_Dir + BaseSurfacingName + ".v00"+ str(fileIncrementer) +".mb"):
                        fileIncrementer += 1
                    ShaderVer = fileIncrementer - 1
                    
                    LatestModelRef_Dir = ModelReference_Dir + BaseSurfacingName + ".v00"+ str(ShaderVer) +".mb"
                    print(LatestModelRef_Dir)
                    #mc.file(LatestModelRef_Dir, loadReference=SceneGeometry)
                
                else:
                    print("Reference Is NOT a MB File")
              
        else:
            print(SceneGeometry+"Is NOT a ref")

#Mel Eval
#Hypershader
#Node Editor



### Yucky Gui Stuff ###
if mc.window('Shader_Publishing', exists = True):
    mc.deleteUI('Shader_Publishing')
mc.window('Shader_Publishing', resizeToFitChildren = True)
mc.columnLayout(adjustableColumn = True, cal = "center", w=300)
mc.separator(h=10)
mc.text('SceneDirectory')
mc.separator(h=10)
mc.textField(tx = SceneDir)

mc.separator(h=10)
mc.text('Surfacing')
### Shader Exporting Functions ###
mc.separator(h=10)
mc.text('Publish All Shaders - or Select Meshes to Publish')
mc.separator(h=10)
mc.button(label = 'Export Shaders to Publish', command = 'PublishShaders()', en = (not isCurrentlyInLighting) & (not UserSeemsToBeALittleLost))


mc.separator(h=30)
mc.text('Lighting')
### Shader Importing Functions ###
mc.separator(h=10)
mc.text('Select Objects to Re-Apply Materials')
mc.separator(h=10)
mc.button(label = 'Apply Shaders', command = 'ImportLatestShaders()', en = isCurrentlyInLighting & (not UserSeemsToBeALittleLost))
mc.separator(h=10)

mc.button(label = 'Remove Unused Shaders', command = 'RemoveUnused()', en = isCurrentlyInLighting & (not UserSeemsToBeALittleLost))
mc.separator(h=30)
mc.text('Leave at 0 to Import Latest')
mc.separator(h=10)

mc.gridLayout(ch=20,cw=150, nrc=[3,2], autoGrow= True)

mc.text('Enter Version Number:')
ShaderVerInput = mc.intField(width = 50, v=0, en = isCurrentlyInLighting & (not UserSeemsToBeALittleLost))

mc.separator(h=10)
mc.separator(h=10)

mc.showWindow('Shader_Publishing')