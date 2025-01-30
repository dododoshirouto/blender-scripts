import bpy

def main():
    print("start rename_bone")
    armatures = get_selected_armatures()

    print("armature count: " + str(len(armatures)))

    for armature in armatures:
        bones = get_bones_in_armature(armature)
        for bone in bones:
            rename_bone(bone)
        
        print("end armature: " + armature.name)
        pass

    print("end rename_bone")
    pass



def get_selected_armatures()->list[bpy.types.Object]:
    selObj = bpy.context.selected_objects
    armatures = []
    for obj in selObj:
        if (obj.type == 'ARMATURE') :
            armatures.append(obj)
    return armatures

def get_bones_in_armature(armature:bpy.types.Object)->list[bpy.types.Object]:
    return armature.pose.bones

def rename_bone(bone:bpy.types.Object):
    # replace '*_L_*' to '*_*.L'
    if '_L_' in bone.name:
        bone.name = bone.name.replace('_L_', '_') + '.L'
    if '_R_' in bone.name:
        bone.name = bone.name.replace('_R_', '_') + '.R'
    if '_C_' in bone.name:
        bone.name = bone.name.replace('_C_', '_')



main()