#!$BLENDER_PATH/python/bin python

"""
NFT Blender - BPY - MDL

"""

import typing

import bpy


def node_get_nodes_from_node_tree(
    node_tree,
    node_types: typing.Iterable = (bpy.types.Node),
    sub_grps: bool = True,
) -> list:
    """Works for any tree of nodes, including Materials, Groups, and NodeTrees"""

    nodes = []

    for n in node_tree.nodes:

        if isinstance(n, node_types):
            nodes.append(n)

        if sub_grps and isinstance(n, (
            bpy.types.CompositorNodeGroup,
            bpy.types.GeometryNodeGroup,
            bpy.types.NodeGroup,
            bpy.types.ShaderNodeGroup,
            bpy.types.TextureNodeGroup,
        )):
            nodes.extend(node_get_nodes_from_node_tree(
                n.node_tree,
                sub_grps,
                node_types
            ))
    
    return nodes
