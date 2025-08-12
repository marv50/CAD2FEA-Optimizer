import pyvista as pv

# Load the VTK file using PyVista
pv_mesh = pv.read("data/DA_mesh.vtk")

# Plot the volumetric mesh
pv_mesh.plot(show_edges=True)

