#!$BLENDER_PATH/python/bin python

"""
NFT Blender - BPY - ANI

"""

import copy
import pathlib
import typing

import mathutils

import bpy

from nft_blender.nft_bpy._bpy_core import bpy_scn


class AniKeyingSetHelper(object):
    """
    Helper object for managing Blender Keying Sets for assets in a project.
    """
    def __init__(self, ks_dir_path: typing.Union[pathlib.Path, str]) -> None:
        """
        Constructor method.

        :param ks_dir_path: Path to the Keying Set directory.
        """
        self._ks_root_dir_path = pathlib.Path(ks_dir_path)

    def get_existing_keying_set_names(self) -> list:
        """
        Gets a list of all Keying Set names in the current Scene.

        :returns: A list of Keying Set names.
        """
        existing_keying_sets = bpy.context.scene.keying_sets_all
        existing_keying_set_names = [ks.bl_idname for ks in existing_keying_sets]

        return existing_keying_set_names

    def get_keying_set_names_for_asset(
        self,
        asset_name: str,
        exists_ok: bool = False,
    ) -> list:
        """
        Gets the Keying Set name(s) for the given asset in the current project.

        :param asset_name: The name of the asset.
        :param exists_ok: If False,
            only return Keying Set names that do not exist yet in current Scene (default: False).
        :returns: A list of Keying Set names.
        """
        keying_set_dir_path = self._ks_root_dir_path.joinpath(asset_name)

        if keying_set_dir_path.is_dir():

            keying_set_names = [ks_path.stem for ks_path in keying_set_dir_path.glob('*.py')]

            if not exists_ok:

                existing_keying_set_names = self.get_existing_keying_set_names()

                keying_set_names = [
                    ks for ks in keying_set_names if ks not in existing_keying_set_names
                ]

            keying_set_names.sort()

            return keying_set_names

        return []

    def load_keying_sets_for_asset(
        self,
        asset_name: str,
        ks_name: str,
    ) -> bool:
        """
        Creates a new Keying Set in the current scene from the given asset and Keying Set name.

        :param asset_name: The name of the asset.
        :param ks_name: The name of the Keying Set to load.
        :returns: Success result of creating the new Keying Set.
        """
        existing_ks_names = self.get_existing_keying_set_names()

        if ks_name in existing_ks_names:

            return False

        ks_file_path = self._ks_root_dir_path.joinpath(
            asset_name, ks_name
        ).with_suffix('.py')

        if ks_file_path.is_file():
            # bpy.utils.execfile(ks_file_path.as_posix())
            with ks_file_path.open('r', encoding='utf-8') as ks_rf:
                exec(ks_rf.read())
            bpy.ops.anim.keying_set_active_set(type=ks_name)

            return True

        return False


def ani_break_inputs(
    target_object: bpy.types.Object,
    on_data: bool = False,
    on_object: bool = False,
) -> None:
    """TODO"""
    obj_anim_data = target_object.animation_data if on_object else None
    shape_key_anim_data = None

    if target_object.active_shape_key is not None:
        active_shape_key_name = target_object.active_shape_key.id_data.name
        shape_key_anim_data = \
            bpy.data.shape_keys[active_shape_key_name].animation_data if on_data else None

    for anim_data in (obj_anim_data, shape_key_anim_data):
        if anim_data is not None:
            action_fcrvs = anim_data.action.fcurves if anim_data.action else []
            for _ in action_fcrvs:
                action_fcrvs.remove(action_fcrvs[0])
            driver_fcrvs = anim_data.drivers
            for _ in driver_fcrvs:
                driver_fcrvs.remove(driver_fcrvs[0])


def ani_reset_armature_transforms(
    armature_obj: bpy.types.Object,
    reference_frame: int = 1,
    set_to_rest: bool = False,
) -> None:
    """
    Clears the current action and resets armature transforms for the given Armature Object.

    :param armature_obj: The Armature Object.
    :param reference_frame: The frame to set the Timeline to.
    :param set_to_rest: Set the Armature to Rest Position upon completion.
    """
    # Ensure it is an Armature Object.
    if isinstance(armature_obj.data, bpy.types.Armature):

        # Select the Armature Object for operator functions.
        bpy_scn.scn_select_items(items=[armature_obj])

        # Reset the Timeline and clear the current Action  on the Armature.
        bpy.context.scene.frame_set(reference_frame)
        armature_obj.animation_data.action = None

        # Reset transforms on Pose Bones
        for bone in armature_obj.pose.bones:
            bone.location = (0, 0, 0)
            bone.rotation_quaternion = (1, 0, 0, 0)
            bone.rotation_axis_angle = (0, 0, 1, 0)
            bone.rotation_euler = (0, 0, 0)
            bone.scale = (1, 1, 1)
        # bpy.ops.object.mode_set(mode='POSE')
        # bpy.ops.pose.select_all(action='SELECT')
        # bpy.ops.pose.transforms_clear()

        # Reset the Armature to rest pose (reset to t-pose for character rigs).
        if set_to_rest:
            armature_obj.data.pose_position = 'REST'

        bpy.ops.object.mode_set(mode='OBJECT')


def ani_reset_fcurve_modifiers(
    armature_obj: bpy.types.Object,
    reset_modifiers: bool = True,
    create_cycles: bool = False,
    create_stepped: bool = False,
    stepped_frame_step: int = 2,
) -> None:
    """TODO"""
    current_action = armature_obj.animation_data.action
    fcrvs = current_action.fcurves if current_action else []
    for fcrv in fcrvs:

        if reset_modifiers:
            for mdfr in fcrv.modifiers:
                fcrv.modifiers.remove(mdfr)

        if create_cycles:
            cyc_mdfr = fcrv.modifiers.new('CYCLES')
            cyc_mdfr.cycles_after = 1
            cyc_mdfr.cycles_before = 1

        if create_stepped:
            step_mdfr = fcrv.modifiers.new('STEPPED')
            step_mdfr.frame_step = stepped_frame_step


def ani_rigify_for_ue(
    rigifiy_armature_obj_name: str = 'rig',
    active_bone_layer_ids: typing.Sequence = (),
    pole_vectors: int = 1,
    reset_scale: bool = True,
) -> bpy.types.Object:
    """TODO"""
    rigify_armature_obj = bpy.data.objects[rigifiy_armature_obj_name]

    for i in range(32):
        rigify_armature_obj.data.layers[i] = i in active_bone_layer_ids

    for pose_bone in rigify_armature_obj.pose.bones:

        # Turn off stretch constraints on deform bones
        if pose_bone.bone.use_deform:
            stretch_cnsts = [
                cnst for cnst in pose_bone.constraints if isinstance(
                    cnst, bpy.types.StretchToConstraint
                )
            ]
            if stretch_cnsts:
                for cnst in stretch_cnsts:
                    cnst.enabled = False

        elif not pose_bone.bone.use_deform:
            if pose_bone.get('pole_vector') is not None:
                pose_bone['pole_vector'] = pole_vectors
            if pose_bone.get('IK_Stretch') is not None:
                pose_bone['IK_Stretch'] = 0.0

        #
        if reset_scale:
            if pose_bone.scale != mathutils.Vector([1.0, 1.0, 1.0]):
                pose_bone.scale = mathutils.Vector([1.0, 1.0, 1.0])

    return rigify_armature_obj


def ani_set_data_path_values(
    target_object: bpy.types.Object,
    modifier_data: dict = None,
    shape_key_data: dict = None
) -> typing.Tuple[dict, dict]:
    """TODO"""
    modifier_data = modifier_data if isinstance(modifier_data, dict) else {}
    shape_key_data = shape_key_data if isinstance(shape_key_data, dict) else {}
    current_modifier_data = copy.deepcopy(modifier_data)
    current_shape_key_data = copy.deepcopy(shape_key_data)

    for mdfr_k, mdfr_v in modifier_data.items():
        for input_k, input_v in mdfr_v.items():
            current_modifier_data[mdfr_k][input_k] = target_object.modifiers[mdfr_k][input_k]
            target_object.modifiers[mdfr_k][input_k] = input_v

    for shape_k, shape_v in shape_key_data.items():
        shape_keys = target_object.data.shape_keys.key_blocks
        current_shape_key_data[shape_k] = shape_keys[shape_k].value
        shape_keys[shape_k].value = shape_v

    return (current_modifier_data, current_shape_key_data)
