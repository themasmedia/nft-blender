#!$BLENDER_PATH/python/bin python

"""
NFT Blender - BPY - OBJ

"""

import bpy
import mathutils


def obj_apply_transforms(
        obj: bpy.types.Object,
        apply_location: bool = True,
        apply_rotation: bool = True,
        apply_scale: bool = True
):
    """"""
    mat_basis = obj.matrix_basis
    mat_basis_decomp = mat_basis.decompose()
    id_mat = mathutils.Matrix()
    translation = mathutils.Matrix.Translation(mat_basis_decomp[0])
    rotation = mat_basis.to_3x3().normalized().to_4x4()
    scale = mathutils.Matrix.Diagonal(mat_basis_decomp[2]).to_4x4()

    transform = [id_mat, id_mat, id_mat]
    basis = [translation, rotation, scale]

    if apply_location:
        transform[0], basis[0] = basis[0], transform[0]
    if apply_rotation:
        transform[1], basis[1] = basis[1], transform[1]
    if apply_scale:
        transform[2], basis[2] = basis[2], transform[2]
        
    mat = transform[0] @ transform[1] @ transform[2]
    if hasattr(obj.data, "transform"):
        obj.data.transform(mat)
    for c in obj.children:
        c.matrix_local = mat @ c.matrix_local
        
    obj.matrix_basis = basis[0] @ basis[1] @ basis[2]
