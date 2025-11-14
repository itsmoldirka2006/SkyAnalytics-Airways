import open3d as o3d
import numpy as np
import os
import matplotlib.pyplot as plt

def save_screenshot(vis, filename, description):
    os.makedirs("assignment5_screenshots", exist_ok=True)
    filepath = os.path.join("assignment5_screenshots", filename)
    image = vis.capture_screen_float_buffer()
    plt.imsave(filepath, np.asarray(image))
    print(f"✓ Saved: {filename} | {description}")

def custom_draw_geometry_with_screenshot(geometries, filename, description, width=800, height=600):
    vis = o3d.visualization.Visualizer()
    vis.create_window(width=width, height=height, visible=False)
    
    if isinstance(geometries, list):
        for geometry in geometries:
            vis.add_geometry(geometry)
    else:
        vis.add_geometry(geometries)
    
    opt = vis.get_render_option()
    opt.background_color = np.asarray([1, 1, 1])
    opt.point_size = 3.0
    
    vis.poll_events()
    vis.update_renderer()

    save_screenshot(vis, filename, description)
    vis.destroy_window()

def assignment_5_cup_fixed():
    os.makedirs("assignment5_screenshots", exist_ok=True)
    print("STEP 1: LOADING AND VISUALIZATION - AS POINT CLOUD")

    mesh = o3d.io.read_triangle_mesh("cup.obj")
    print(f"Number of vertices: {len(mesh.vertices)}")
    print(f"Number of triangles: {len(mesh.triangles)}")
    print(f"Has vertex colors: {mesh.has_vertex_colors()}")
    print(f"Has vertex normals: {mesh.has_vertex_normals()}")
    
    if not mesh.has_vertex_normals():
        mesh.compute_vertex_normals()
    bbox = mesh.get_axis_aligned_bounding_box()
    bbox_center = bbox.get_center()
    bbox_min = bbox.get_min_bound()
    bbox_max = bbox.get_max_bound()
    
    print(f"Cup bounding box center: {bbox_center}")
    
    step1_point_cloud = o3d.geometry.PointCloud()
    step1_point_cloud.points = mesh.vertices
    step1_point_cloud.paint_uniform_color([0.3, 0.5, 0.9])

    custom_draw_geometry_with_screenshot(step1_point_cloud, "step1_cup_original.png", "Step 1: Original Cup Model as Point Cloud")
    o3d.visualization.draw_geometries([step1_point_cloud], window_name="Step 1: Original Cup Model (Point Cloud)")
    print("\n" + "-" * 40)
    print("STEP 2: CONVERSION TO POINT CLOUD - SAMPLED")
    
    point_cloud = mesh.sample_points_poisson_disk(number_of_points=8000)
    print(f"Number of points: {len(point_cloud.points)}")
    print(f"Has colors: {point_cloud.has_colors()}")
    
    point_cloud.paint_uniform_color([0.9, 0.3, 0.3])
    custom_draw_geometry_with_screenshot(point_cloud, "step2_cup_point_cloud.png", "Step 2: Cup Point Cloud (Sampled)")
    o3d.visualization.draw_geometries([point_cloud], window_name="Step 2: Cup Point Cloud")

    print("\n" + "-" * 40)
    print("STEP 3: SURFACE RECONSTRUCTION")
    
    point_cloud_for_reconstruction = point_cloud
    if not point_cloud_for_reconstruction.has_normals():
        point_cloud_for_reconstruction.estimate_normals()
    
    mesh_reconstructed, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        point_cloud_for_reconstruction, depth=9)
    
    bbox = point_cloud.get_axis_aligned_bounding_box()
    mesh_reconstructed = mesh_reconstructed.crop(bbox)
    
    print(f"Number of vertices: {len(mesh_reconstructed.vertices)}")
    print(f"Number of triangles: {len(mesh_reconstructed.triangles)}")
    print(f"Has colors: {mesh_reconstructed.has_vertex_colors()}")
    
    mesh_reconstructed.paint_uniform_color([0.2, 0.8, 0.4])
    mesh_reconstructed.compute_vertex_normals()
    custom_draw_geometry_with_screenshot(mesh_reconstructed, "step3_cup_reconstructed.png", "Step 3: Reconstructed Cup")
    o3d.visualization.draw_geometries([mesh_reconstructed], window_name="Step 3: Reconstructed Cup")
    
    # ========== STEP 4: VOXELIZATION - CORRECTED ==========
    print("\n" + "-" * 40)
    print("STEP 4: VOXELIZATION")
    
    # Convert point cloud to voxel grid with proper voxel size
    voxel_size = 8.0
    voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(point_cloud, voxel_size=voxel_size)
    
    # Print required information
    print(f"Number of vertices: {len(point_cloud.points)}")
    print(f"Has colors: {voxel_grid.has_colors()}")
    print(f"Voxel size: {voxel_size}")
    print(f"Number of voxels: {len(voxel_grid.get_voxels())}")
    
    # Display voxels
    custom_draw_geometry_with_screenshot(voxel_grid, "step4_cup_voxels.png", "Step 4: Cup Voxel Grid")
    o3d.visualization.draw_geometries([voxel_grid], window_name="Step 4: Cup Voxel Grid")
    
    # ========== STEP 5: ADDING A PLANE ==========
    print("\n" + "-" * 40)
    print("STEP 5: ADDING A PLANE")
    
    # Get mesh bounding box for proper plane positioning
    bbox_mesh = mesh.get_axis_aligned_bounding_box()
    extent = bbox_mesh.get_extent()
    center = bbox_mesh.get_center()
    
    # Create vertical cutting plane
    cutting_plane = o3d.geometry.TriangleMesh.create_box(
        width=0.05,
        height=extent[1] * 1.5,
        depth=extent[2] * 1.5
    )
    cutting_plane.paint_uniform_color([1, 0, 0])  # Red color
    
    # Position plane to cut through the center
    cutting_plane.translate([
        center[0] - 0.025,
        bbox_mesh.min_bound[1] - extent[1] * 0.25,
        bbox_mesh.min_bound[2] - extent[2] * 0.25
    ])
    
    print("Cutting plane created - slices cup in HALF!")
    
    cup_for_display = mesh
    cup_for_display.paint_uniform_color([0.3, 0.5, 0.9])
    
    combined_geometries = [cup_for_display, cutting_plane]
    custom_draw_geometry_with_screenshot(combined_geometries, "step5_cup_with_planes.png", "Step 5: Cup with Cutting Plane")
    o3d.visualization.draw_geometries([cup_for_display, cutting_plane], 
                                    window_name="Step 5: Cup + Cutting Plane")
    
    # ========== STEP 6: SURFACE CLIPPING ==========
    print("\n" + "-" * 40)
    print("STEP 6: SURFACE CLIPPING")
    
    vertices = np.asarray(mesh.vertices)
    triangles = np.asarray(mesh.triangles)
    
    # Select triangles on left half by X-axis
    center_x = (vertices[:, 0].min() + vertices[:, 0].max()) / 2
    
    valid_triangles = []
    for tri in triangles:
        v0, v1, v2 = vertices[tri[0]], vertices[tri[1]], vertices[tri[2]]
        if v0[0] < center_x and v1[0] < center_x and v2[0] < center_x:
            valid_triangles.append(tri)
    
    clipped_mesh = o3d.geometry.TriangleMesh()
    clipped_mesh.vertices = mesh.vertices
    clipped_mesh.triangles = o3d.utility.Vector3iVector(np.array(valid_triangles))
    clipped_mesh.paint_uniform_color([0.7, 0.7, 0.7])
    clipped_mesh.compute_vertex_normals()
    
    print(f"Original triangles: {len(mesh.triangles)}")
    print(f"Remaining triangles after clipping: {len(clipped_mesh.triangles)}")
    print(f"Number of remaining vertices: {len(clipped_mesh.vertices)}")
    print(f"Has colors: {clipped_mesh.has_vertex_colors()}")
    print(f"Has normals: {clipped_mesh.has_vertex_normals()}")
    
    custom_draw_geometry_with_screenshot(clipped_mesh, "step6_cup_clipped.png", "Step 6: Clipped Cup (Half)")
    o3d.visualization.draw_geometries([clipped_mesh], window_name="Step 6: Clipped Cup (Half)")

    # ========== STEP 7: COLOR GRADIENT AND EXTREMES ==========
    print("\n" + "-" * 40)
    print("STEP 7: COLOR GRADIENT AND EXTREME POINTS")
    
    vertices = np.asarray(mesh.vertices)
    triangles = np.asarray(mesh.triangles)
    
    # Z-axis gradient: red (min) to blue (max)
    z_values = vertices[:, 2]
    z_min, z_max = z_values.min(), z_values.max()
    z_normalized = (z_values - z_min) / (z_max - z_min)
    
    vertex_colors = np.zeros((len(vertices), 3))
    vertex_colors[:, 0] = z_normalized  # Red channel
    vertex_colors[:, 1] = 0.3           # Green channel fixed
    vertex_colors[:, 2] = 1 - z_normalized  # Blue channel
    
    gradient_mesh = o3d.geometry.TriangleMesh()
    gradient_mesh.vertices = mesh.vertices
    gradient_mesh.triangles = mesh.triangles
    gradient_mesh.vertex_colors = o3d.utility.Vector3dVector(vertex_colors)
    gradient_mesh.compute_vertex_normals()
    
    # Find extreme points along Z-axis
    min_idx = np.argmin(z_values)
    max_idx = np.argmax(z_values)
    min_point = vertices[min_idx]
    max_point = vertices[max_idx]
    
    print(f"Minimum Z point (BOTTOM): {min_point}")
    print(f"Maximum Z point (TOP): {max_point}")
    print(f"Gradient range: Z from {z_min:.3f} to {z_max:.3f}")
    
    # Extreme points marked with spheres - adjusted size for cup
    sphere_radius = 2.0
    
    sphere_min = o3d.geometry.TriangleMesh.create_sphere(radius=sphere_radius)
    sphere_min.paint_uniform_color([1, 0, 0])  # Red for minimum
    sphere_min.translate(min_point)
    
    sphere_max = o3d.geometry.TriangleMesh.create_sphere(radius=sphere_radius)
    sphere_max.paint_uniform_color([0, 0, 1])  # Blue for maximum
    sphere_max.translate(max_point)
    
    final_geometries = [gradient_mesh, sphere_min, sphere_max]
    custom_draw_geometry_with_screenshot(final_geometries, "step7_cup_gradient_extremes.png", "Step 7: Cup with Gradient and Extremes")
    o3d.visualization.draw_geometries([gradient_mesh, sphere_min, sphere_max], 
                                    window_name="Step 7: Gradient Cup with Extremes")

if __name__ == "__main__":
    assignment_5_cup_fixed()