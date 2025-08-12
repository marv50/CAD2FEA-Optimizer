from netgen.occ import *

# STEP file path (make sure this is absolute or relative to the script's cwd)
stp_path = "data/DoubleArrowhead.step"

# Create OCC geometry directly from STEP file
geo = OCCGeometry(stp_path)

# Generate volumetric mesh
mesh = geo.GenerateMesh()

#help(mesh.Export)
# Save mesh in native Netgen format
mesh.Save("data/output_mesh.vol")


# Optional: Export to Gmsh
mesh.Export("data/output_mesh.stl", "STL Format")
