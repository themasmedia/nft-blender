#Usage:
#assumes your character mesh is selected
#assumes you enter in a weight file path
#little error checking. use at your own risk.
#exportWeightOnSelected(json_file_path)
#importWeightOnSelected(json_file_path)


import bpy
import json
import os
import pathlib
import re


def exportWeightOnSelected(
        json_file_path: pathlib.Path,
        mirror: bool = True
    ):
    """
    export skin weights on selected character
    """
    #assumes your character is selected
    #no error checking
    
    json_data = {
        'groups': {},
        'vertices': {}
    }

    bpy.ops.object.mode_set(mode="EDIT")
    edit_obj = bpy.context.edit_object

    for vtx_grp in edit_obj.vertex_groups:

        vtx_grp_index = str(vtx_grp.index)
        vtx_grp_name = vtx_grp.name

        if mirror:

            mirror_pattern = re.compile(r'(\.|_)(L|R)(?![a-zA-Z0-9])', re.I)
            mirror_match = mirror_pattern.search(vtx_grp_name)
            if mirror_match:
                l_str = 'L' if mirror_match.group(2).isupper() else 'l'
                r_str = 'R' if mirror_match.group(2).isupper() else 'r'
                swap_str = l_str if mirror_match.group(2) == r_str else r_str
                repl_str = f'{mirror_match.group(1)}{swap_str}'
                vtx_grp_name = mirror_pattern.sub(repl_str, vtx_grp_name)

        json_data['groups'][vtx_grp_index] = vtx_grp_name

    for vtx in edit_obj.data.vertices:

        vtx_index = str(vtx.index)
        json_data['vertices'][vtx_index] = {}

        for vtx_grp_element in vtx.groups:
            
            vtx_group_id = vtx_grp_element.group
            vtx_weight = vtx_grp_element.weight
            json_data['vertices'][vtx_index][vtx_group_id] = round(vtx_weight, 4)

    if mirror:

        mirror_match = re.search(r'(\.|_)(L|R)', json_file_path.stem)
        if mirror_match:
            repl_str = f'{mirror_match.group(1)}{"L" if mirror_match.group(2) == "R" else "R"}'
            mirror_stem = re.sub(r'(\.|_)(L|R)', repl_str, json_file_path.stem)
            json_file_path = json_file_path.with_name(
                f'{mirror_stem}{json_file_path.suffix}'
            )

    bpy.ops.object.mode_set(mode="OBJECT")
        
    #export weights to file
    with json_file_path.open('w') as wf:
        wf.write(json.dumps(json_data, indent=2))

    bpy.ops.object.select_all(action='DESELECT')
    

def importWeightOnSelected(json_file_path):
    """
    import skin weights on selected character
    """
    #assumes your character is selected
    #no error checking
    #apply armature modifier but leave vertex groups empty

    with json_file_path.open('r') as rf:
        json_data = json.load(rf)
    
    bpy.ops.object.mode_set(mode="EDIT")
    edit_obj = bpy.context.edit_object
    bpy.ops.object.mode_set(mode="OBJECT")
    active_obj = bpy.context.active_object

    for vtx_grp_name in json_data['groups'].values():
        active_obj.vertex_groups.new(name=vtx_grp_name)
    
    for vtx_index, vtx_grp_data in json_data['vertices'].items():

        for vtx_grp_id, vtx_weight in vtx_grp_data.items():

            vtx_grp_name = json_data['groups'][vtx_grp_id]
            vtx_grp = edit_obj.vertex_groups.get(vtx_grp_name)
            if vtx_grp is not None:
                print(vtx_index, 'will be added to', vtx_grp_name, 'with weight:', vtx_weight)
                vtx_grp.add([int(vtx_index)], float(vtx_weight), 'REPLACE')
    
    bpy.ops.object.vertex_group_lock(action='LOCK')
    bpy.ops.object.select_all(action='DESELECT')


if __name__ == '__main__':

    os.system('cls')

    output_dir_path = pathlib.Path('/')
    json_file_path = output_dir_path.joinpath(f'{bpy.context.active_object.name}.json')

    exportWeightOnSelected(json_file_path)

    # importWeightOnSelected(json_file_path)
