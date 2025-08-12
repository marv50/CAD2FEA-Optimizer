import os

from src.stl_exporter import load_stl
from src.stl_converter import stl_to_vtk

if __name__ == "__main__":
    document_id = os.environ.get("DOCUMENT_ID")
    workspace_id = os.environ.get("WORKSPACE_ID")
    element_id = os.environ.get("ELEMENT_ID")
    part_name = os.environ.get("PART_NAME")
    access_key = os.environ.get("ACCESS_KEY")
    secret_key = os.environ.get("SECRET_KEY")
    
    params = {
        "mindihedral": 50,
        "minratio": 1.1,
    }

    stl = load_stl(part_name, document_id, workspace_id,
                   element_id, access_key, secret_key)

    stl_to_vtk(stl, "data/DA_mesh.vtk")
