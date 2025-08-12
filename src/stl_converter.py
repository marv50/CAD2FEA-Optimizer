"""
mesh_pipeline.py

A pipeline for converting STL surface meshes into volumetric tetrahedral meshes and saving them in VTK format.
This is useful for preprocessing CAD geometry for finite element simulations.

Functions:
    - create_2d_mesh
    - clean_mesh
    - tetrahedralize_mesh
    - save_mesh_to_vtk
    - stl_to_vtk

Dependencies:
    - trimesh
    - tetgen
    - meshio
    - pymeshfix

Author: Marvin Frommer
Date: 2025-08-05
"""

import trimesh
import tetgen
import meshio
import pymeshfix
from io import BytesIO


def create_2d_mesh(stl_data):
    """
    Load STL data and extract vertices and triangular surface faces.

    Args:
        stl_data (bytes): Binary STL data, e.g., downloaded from an API.

    Returns:
        tuple:
            - vertices (ndarray): Nx3 array of vertex coordinates.
            - faces (ndarray): Mx3 array of face indices.
    """
    trimesh_mesh = trimesh.load(BytesIO(stl_data), file_type='stl')
    vertices = trimesh_mesh.vertices
    faces = trimesh_mesh.faces

    return vertices, faces


def clean_mesh(vertices, faces):
    meshfix = pymeshfix.MeshFix(vertices, faces)
    meshfix.repair(verbose=True, joincomp=True,
                   remove_smallest_components=False)
    return meshfix.v, meshfix.f


def tetrahedralize_mesh(vertices, faces, tetgen_options: dict = None):
    """
    Convert a surface mesh to a volumetric tetrahedral mesh using TetGen.

    Args:
        vertices (ndarray): Nx3 array of surface vertices.
        faces (ndarray): Mx3 array of surface triangle indices.
        tetgen_options (dict, optional): Optional keyword arguments passed to tgen.tetrahedralize().
                                         Example: {"maxvolume": 1.0, "mindratio": 1.5}

    Returns:
        tuple:
            - node (ndarray): Points of the volumetric mesh.
            - elem (ndarray): Connectivity array (tetrahedrons).
    """
    tgen = tetgen.TetGen(vertices, faces)
    tetgen_options = tetgen_options or {}
    tgen.tetrahedralize(**tetgen_options)
    return tgen.node, tgen.elem


def save_mesh_to_vtk(nodes, cells, path):
    """
    Save a volumetric tetrahedral mesh to a VTK file using MeshIO.

    Args:
        nodes (ndarray): Nx3 array of mesh points.
        cells (ndarray): Mx4 array of tetrahedral cell indices.
        path (str): File path for saving the VTK mesh.
    """
    mesh = meshio.Mesh(points=nodes, cells=[("tetra", cells)])
    meshio.write(path, mesh)


def stl_to_vtk(stl_data, output_path, tetgen_options: dict = None):
    """
    Complete pipeline to convert STL surface mesh data to a volumetric VTK file.

    Args:
        stl_data (bytes): Raw STL file content (binary).
        output_path (str): File path for saving the VTK mesh. Default is "data/output.vtk".
        tetgen_options (dict, optional): Parameters for controlling TetGen behavior.
    """
    vertices, faces = create_2d_mesh(stl_data)
    clean_vertices, clean_faces = clean_mesh(vertices, faces)
    nodes, cells = tetrahedralize_mesh(
        clean_vertices, clean_faces, tetgen_options)
    save_mesh_to_vtk(nodes, cells, output_path)