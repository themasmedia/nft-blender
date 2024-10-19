#!$BLENDER_PATH/python/bin python

"""
MAS Blender - BPY - OBJ

"""

import bpy
import mathutils


def obj_apply_transforms(
    obj: bpy.types.Object,
    apply_location: bool = True,
    apply_rotation: bool = True,
    apply_scale: bool = True,
):
    """
    Apply object transformations to the given object and its children.

    This function applies the object's location, rotation, and scale transformations to its mesh data
    and updates the matrices of its children accordingly.

    Args:
        obj (bpy.types.Object): The object to apply transformations to.
        apply_location (bool, optional): Whether to apply the location transformation. Defaults to True.
        apply_rotation (bool, optional): Whether to apply the rotation transformation. Defaults to True.
        apply_scale (bool, optional): Whether to apply the scale transformation. Defaults to True.

    Example:
        >>> import bpy
        >>> obj = bpy.context.active_object
        >>> obj_apply_transforms(obj)
    """

    mat_basis = obj.matrix_basis
    mat_basis_decomp = mat_basis.decompose()
    id_mat = mathutils.Matrix()

    # Decompose the object's basis matrix into individual transformations
    translation = mathutils.Matrix.Translation(mat_basis_decomp[0])
    rotation = mat_basis.to_3x3().normalized().to_4x4()
    scale = mathutils.Matrix.Diagonal(mat_basis_decomp[2]).to_4x4()

    # Set up transformation matrices
    transform = [id_mat, id_mat, id_mat]
    basis = [translation, rotation, scale]

    # Apply transformations based on the provided flags
    if apply_location:
        transform[0], basis[0] = basis[0], transform[0]
    if apply_rotation:
        transform[1], basis[1] = basis[1], transform[1]
    if apply_scale:
        transform[2], basis[2] = basis[2], transform[2]

    # Combine transformations into a single matrix
    mat = transform[0] @ transform[1] @ transform[2]

    # Apply the combined transformation to the object's data
    if hasattr(obj.data, "transform"):
        obj.data.transform(mat)

    # Update the matrices of the object's children
    for c in obj.children:
        c.matrix_local = mat @ c.matrix_local

    # Update the object's basis matrix
    obj.matrix_basis = basis[0] @ basis[1] @ basis[2]


def obj_remove_custom_props(
    struct: bpy.types.bpy_struct,
    data: bool = False,
    materials: bool = False,
    exclude: list = []
):
    custom_prop_keys = [k for k in struct.keys() if k not in exclude]
    for k in custom_prop_keys:
        struct.pop(k)
    if data:
        custom_prop_keys = [k for k in struct.data.keys() if k not in exclude]
        for k in custom_prop_keys:
            struct.data.pop(k)
    if materials:
        for mtl in struct.data.materials:
            custom_prop_keys = [k for k in mtl.keys() if k not in exclude]
            for k in custom_prop_keys:
                mtl.pop(k)
