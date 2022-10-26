import maya.cmds as mc
import os.path
import ntpath
import json

#Gets Relative File path of model 
SceneDir = str(mc.file(q=True, exn=True))

if(SceneDir.find("surfacing") != -1):
    isCurrentlyInLighting = False
elif(SceneDir.find("light") != -1):
    isCurrentlyInLighting = True


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


#print("New ShaderPUB_Dir: "+ ShaderPUB_Dir)

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
    selected = mc.ls(selection = True)
    #mc.select(cl = True)
    #selected = mc.ls(geometry=True)
    #mc.select(selected)
    
    if(len(selected) == 0):
        print("No Meshes Selected - Importing All Shaders")
        selected = mc.ls(geometry=True)
        mc.select(selected)
        
    else:
        print("Meshes Selected: Importing Shaders")
        
    for i in range(len(selected)):
        modelReferenceDir = mc.referenceQuery(selected[i], filename=True)
        ShaderPUB_Dir = modelReferenceDir.replace("model/source", "surfacing")
        ShaderPUB_DirArray=[]
        for i in ShaderPUB_Dir.split('/'):
            ShaderPUB_DirArray.append(i)
        FileNameArray=[]
        for i in ShaderPUB_DirArray[-1].split('.'):
            FileNameArray.append(i)
            #print(i)
        BaseSurfacingName = FileNameArray[0] + ".v"
        BaseSurfacingName = BaseSurfacingName.replace("model", "surface")
        ShaderPUB_DirArray.remove(ShaderPUB_DirArray[-1])
        ShaderPUB_Dir = '/'.join(ShaderPUB_DirArray) + "/" 
        
        fileIncrementer = 1
        while os.path.exists(ShaderPUB_Dir + BaseSurfacingName + str(fileIncrementer) +".mb"):
            fileIncrementer += 1
        LatestVer = fileIncrementer - 1
        
        LatestShaderMB_Dir = ShaderPUB_Dir + BaseSurfacingName + str(LatestVer) +".mb"
        LatestShaderJSON_Dir = ShaderPUB_Dir + BaseSurfacingName + str(LatestVer) +".json"
        if(os.path.exists(LatestShaderMB_Dir) & os.path.exists(LatestShaderJSON_Dir)):
            print("Latest version File Directory: " + LatestShaderMB_Dir)
            mc.file(LatestShaderMB_Dir, i=True, type="mayaBinary", ra=True, rdn=True, mnc=False, ns="test", op="v=0", pr=True, an=True, itr="keep", mnr=True)
            
            with open(LatestShaderJSON_Dir, 'r') as infile:
                data=infile.read()
            
            obj = json.loads(data)
            
            print(obj)
            for set in obj:
                Obj_Material=[]
                for i in set.split(':'):            
                    Obj_Material.append(i)
                print("#1: " + Obj_Material[0] + " #2: " + Obj_Material[1])
                ObjTransform = mc.ls("*:"+Obj_Material[0]+"*")[0]
                print("Mesh: " + ObjTransform)
                Material = mc.ls("*:"+Obj_Material[1]+"*")[0]
                
                
                print("Material: " + Material)
                
                #ObjMesh = mc.listRelatives(ObjTransform, shapes=True)[0]
                ObjShadingEngine = mc.listConnections(ObjTransform, type="shadingEngine")[0]
                ObjMat = mc.listConnections(ObjShadingEngine + ".surfaceShader")[0]
                
                mc.select(ObjTransform)
                mc.hyperShade(assign=str(Material))
                
                #mc.replaceNode(ObjMat, Material)
                #mc.setAttr(ObjMat, Material)
                print(ObjMat)
            
            infile.close()
            
        else:
            print("Mesh Does Not Have Published Shaders")


def ApplyCustomShaders():
    ShaderVer = mc.intField(LightingVerInput, q = True, value = True)
    
    print("ApplyLighting")
    

def ReloadLighting():
    
    #list of currently applied shaders
    #remove from list of all shaders
    #delete all shaders that are not currently applied
    
    
    
    #¯\_(ツ)_/¯# Placeholder Function
    selected = mc.ls(mat=True)
    mc.select(selected)
    for i in selected:
        print(i)






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
mc.button(label = 'Export Shaders to Publish', command = 'PublishShaders()', en = not isCurrentlyInLighting)

### Shader Importing Functions ###
mc.separator(h=30)
mc.text('Lighting: Select Objects to Re-Apply Materials')
mc.separator(h=10)
mc.button(label = 'Apply Latest Shaders', command = 'ImportLatestShaders()', en = isCurrentlyInLighting)
mc.separator(h=10)

mc.gridLayout(ch=20,cw=150, nrc=[3,2], autoGrow= True)

mc.text('Enter Version Number:')
ShaderVerInput = mc.intField(width = 50, v=0, en = isCurrentlyInLighting)

mc.separator(h=10)
mc.separator(h=10)

mc.button(label = 'Apply Custom Shaders', command = 'ApplyCustomShaders()', en = isCurrentlyInLighting)
mc.button(label = 'Reload Shaders', command = 'ReloadLighting()', en = isCurrentlyInLighting)

mc.separator(h=10)
mc.separator(h=10)

mc.showWindow('Shader_Publishing')