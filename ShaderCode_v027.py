import maya.cmds as mc
import os
import ntpath
import json
import posixpath
import mtoa

#from pymel.all import mel

#Gets Relative File path of model 
SceneDir = str(mc.file(q=True, exn=True))

if(SceneDir.find("surfacing") != -1):
    isCurrentlyInLighting = False
elif(SceneDir.find("light") != -1):
    isCurrentlyInLighting = True
    
if(os.name == 'nt'):
    isRunningWindows = True


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


elif(isCurrentlyInLighting == True):
    #LightPUB_Dir = SceneDir.replace("model/source", "surfacing")
    print("Currently In A Lighting Scene")


def PublishShaders():
    #mc.select(cl = True)
    selected = mc.ls(selection = True)
    ShadersToExport = []
    MeshDataToExport = []
    MeshMaterials={}
    
    if(len(selected) == 0):
        print("No Meshes Selected - Exporting All Shaders")
        
        selected = mc.ls('mRef_*')
        mc.select(selected)
        
    else:
        print("Meshes Selected: Exporting Shaders")
        
    if(not mc.listRelatives(selected[0], s=True)):
        print("Selected Group or Transform, using children")
        selected = mc.listRelatives(selected[0], c=True)
    
    for i in range(len(selected)):
        selectedMesh = mc.listRelatives(selected[i], shapes=True)[0]
        selectedMeshShading = mc.listConnections(selectedMesh, type="shadingEngine")[0]
        selectedMat = mc.listConnections(selectedMeshShading + ".surfaceShader")[0]
        
        #adds the mesh and its material to a json Dict
        MeshMaterials[selectedMesh +":"+ selectedMat] = {"AttachedMaterial": selectedMat }
        
        ShadersToExport.append(selectedMat)
    mc.select(ShadersToExport)
    print("Shaders Exported: "+str(ShadersToExport))
        
    fileIncrementer = 1
    while os.path.exists(ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".mb"):
        fileIncrementer += 1

    # Writing to .json File
    json_object = json.dumps(MeshMaterials, indent = 4)
    with open(ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".json", "w") as outfile:
        outfile.write(json_object)
    
    mc.file(ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".mb", force=True, op="v=0;", typ="mayaBinary", pr=True, es=True)
    print ("To Directory: " + ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".mb")
    mc.select(cl = True)



def ImportLatestShaders():
    SelectedShaderVer = mc.intField(ShaderVerInput, q = True, value = True)
    SceneGeometryList = mc.ls(selection = True)
    
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
        ModelReferenceDir = mc.referenceQuery(SceneGeometryList[SceneGeometry], filename=True)
        ShaderPUB_Dir = ModelReferenceDir.replace("model/source", "surfacing")
        
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
        
        
        fileIncrementer = 1
        while os.path.exists(ShaderPUB_Dir + BaseSurfacingName + ".v"+ str(fileIncrementer) +".mb"):
            fileIncrementer += 1
        ShaderVer = fileIncrementer - 1
        
        if(SelectedShaderVer > 0):
            ShaderVer = SelectedShaderVer
        
        LatestShaderMB_Dir = ShaderPUB_Dir + BaseSurfacingName + ".v"+ str(ShaderVer) +".mb"        #Shader Directory for most recent MayaBinary File
        LatestShaderJSON_Dir = ShaderPUB_Dir + BaseSurfacingName + ".v"+ str(ShaderVer) +".json"    #Shader Directory for most recent JSON File
        
        if(os.path.exists(LatestShaderMB_Dir) & os.path.exists(LatestShaderJSON_Dir)):
            if(LatestShaderMB_Dir not in PreviouslyVisitedDirectories):
                #print("Selected File Directory: " + LatestShaderMB_Dir)
                PreviouslyVisitedDirectories.append(LatestShaderMB_Dir)
                with open(LatestShaderJSON_Dir, 'r') as infile:
                    data=infile.read()
                obj = json.loads(data)
                
                mc.file(LatestShaderMB_Dir, i=True, type="mayaBinary", ra=True, rdn=True, mnc=False, ns="v_"+str(ShaderVer)+BaseSurfacingName, op="v=0", pr=True, an=True, itr="keep", mnr=True)
                
                for set in obj:
                    Obj_Material=[]
                    for i in set.split(':'):            
                        Obj_Material.append(i)
                    ObjTransformList = mc.ls("*:"+Obj_Material[0]+"*")
                    MaterialList = mc.ls("*v_"+str(ShaderVer)+BaseSurfacingName+"*:"+Obj_Material[1]+"*")
                    if(ObjTransformList):
                        ObjTransform = ObjTransformList[0]
                        Material = MaterialList[0]
                        print("Mesh: " + ObjTransform + " | Material: " + Material + " | Shader Ver. Being Applied: " + str(ShaderVer))
                        mc.select(ObjTransform)
                        mc.hyperShade(assign=str(Material))
                        mc.select(cl=True)
                    else:
                        print("ERROR - Lighting Scene Model does not match published model, Expected: " + Obj_Material[0] + 
                              " | Recieved: " + SceneGeometryList[SceneGeometry] + " Please Update References")
                infile.close()
        else:
            print("ERROR - " + SceneGeometryList[SceneGeometry] + " Does Not Have Published Shader Version: " + str(ShaderVer))


def RemoveUnused():
    mel.eval('hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
    
    print("ApplyLighting")
    
    
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
mc.button(label = 'Export Shaders to Publish', command = 'PublishShaders()', en = not isCurrentlyInLighting)


mc.separator(h=30)
mc.text('Lighting')
### Shader Importing Functions ###
mc.separator(h=10)
mc.text('Select Objects to Re-Apply Materials')
mc.separator(h=10)
mc.button(label = 'Apply Shaders', command = 'ImportLatestShaders()', en = isCurrentlyInLighting)
mc.separator(h=10)

mc.button(label = 'Remove Unused Shaders', command = 'RemoveUnused()', en = isCurrentlyInLighting)
mc.separator(h=30)
mc.text('Leave at 0 to Import Latest')
mc.separator(h=10)

mc.gridLayout(ch=20,cw=150, nrc=[3,2], autoGrow= True)

mc.text('Enter Version Number:')
ShaderVerInput = mc.intField(width = 50, v=0, en = isCurrentlyInLighting)

mc.separator(h=10)
mc.separator(h=10)

mc.showWindow('Shader_Publishing')