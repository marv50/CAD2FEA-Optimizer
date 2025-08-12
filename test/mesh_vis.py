import meshio
import pyvista as pv

# Read STL
mesh = meshio.read("data/output_mesh.stl")

# Save as VTK
meshio.write("data/model.vtk", mesh)

# Visualize with PyVista
pv_mesh = pv.read("data/output_mesh.vtk")
pv_mesh.plot(show_edges=True)
