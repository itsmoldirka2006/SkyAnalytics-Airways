import open3d as o3d
import numpy as np
import os
import matplotlib.pyplot as plt

def save_screenshot(vis, filename, description):
    """Capture and save screenshot from Open3D visualizer"""
    os.makedirs("assignment5_screenshots", exist_ok=True)
    filepath = os.path.join("assignment5_screenshots", filename)
    
    # Capture the image
    image = vis.capture_screen_float_buffer()
    plt.imsave(filepath, np.asarray(image))
    
    print(f"✓ Saved: {filename} | {description}")

def custom_draw_geometry_with_screenshot(geometries, filename, description, width=800, height=600):
    """Custom function to display geometry/geometries and save screenshot"""
    vis = o3d.visualization.Visualizer()
    vis.create_window(width=width, height=height, visible=False)
    
    # Handle both single geometry and list of geometries
    if isinstance(geometries, list):
        for geometry in geometries:
            vis.add_geometry(geometry)
    else:
        vis.add_geometry(geometries)
    
    # Set background color to white for better visibility
    opt = vis.get_render_option()
    opt.background_color = np.asarray([1, 1, 1])
    opt.point_size = 3.0
    
    vis.poll_events()
    vis.update_renderer()
    
    # Save screenshot
    save_screenshot(vis, filename, description)
    
    vis.destroy_window()

def assignment_5_cup_fixed():
    print("=" * 60)
    print("ASSIGNMENT #5 - 3D CUP PROCESSING WITH OPEN3D (FIXED)")
    print("=" * 60)
    
    # Create screenshots directory
    os.makedirs("assignment5_screenshots", exist_ok=True)
    
    # Step 1: Loading and Visualization - AS POINT CLOUD
    print("\n" + "=" * 40)
    print("STEP 1: LOADING AND VISUALIZATION - AS POINT CLOUD")
    print("=" * 40)
    
    # Load the cup model
    mesh = o3d.io.read_triangle_mesh("cup.obj")
    
    # Print original model information
    print(f"Number of vertices: {len(mesh.vertices)}")
    print(f"Number of triangles: {len(mesh.triangles)}")
    print(f"Has vertex colors: {mesh.has_vertex_colors()}")
    print(f"Has vertex normals: {mesh.has_vertex_normals()}")
    
    if not mesh.has_vertex_normals():
        mesh.compute_vertex_normals()
    
    # Get the cup's bounding box for proper positioning
    bbox = mesh.get_axis_aligned_bounding_box()
    bbox_center = bbox.get_center()
    bbox_min = bbox.get_min_bound()
    bbox_max = bbox.get_max_bound()
    
    print(f"Cup bounding box center: {bbox_center}")
    
    # STEP 1 FIX: Show as POINT CLOUD (dots) instead of solid mesh
    # Convert mesh vertices to point cloud for Step 1
    step1_point_cloud = o3d.geometry.PointCloud()
    step1_point_cloud.points = mesh.vertices
    step1_point_cloud.paint_uniform_color([0.3, 0.5, 0.9])  # Blue color
    
    # Display as point cloud (dots)
    custom_draw_geometry_with_screenshot(step1_point_cloud, "step1_cup_original.png", "Step 1: Original Cup Model as Point Cloud")
    o3d.visualization.draw_geometries([step1_point_cloud], window_name="Step 1: Original Cup Model (Point Cloud)")
    
    # Step 2: Conversion to Point Cloud - SAMPLED VERSION
    print("\n" + "=" * 40)
    print("STEP 2: CONVERSION TO POINT CLOUD - SAMPLED")
    print("=" * 40)
    
    point_cloud = mesh.sample_points_poisson_disk(number_of_points=8000)
    print(f"Number of points: {len(point_cloud.points)}")
    print(f"Has colors: {point_cloud.has_colors()}")
    
    point_cloud.paint_uniform_color([0.9, 0.3, 0.3])
    custom_draw_geometry_with_screenshot(point_cloud, "step2_cup_point_cloud.png", "Step 2: Cup Point Cloud (Sampled)")
    o3d.visualization.draw_geometries([point_cloud], window_name="Step 2: Cup Point Cloud")
    
    # Step 3: Surface Reconstruction
    print("\n" + "=" * 40)
    print("STEP 3: SURFACE RECONSTRUCTION")
    print("=" * 40)
    
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
    
    # Step 4: Voxelization
    print("\n" + "=" * 40)
    print("STEP 4: VOXELIZATION")
    print("=" * 40)
    
    voxel_size = 0.1
    voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(point_cloud, voxel_size=voxel_size)
    
    print(f"Voxel size: {voxel_size}")
    print(f"Number of voxels: {len(voxel_grid.get_voxels())}")
    print(f"Has colors: {voxel_grid.has_colors()}")
    
    custom_draw_geometry_with_screenshot(voxel_grid, "step4_cup_voxels.png", "Step 4: Cup Voxel Grid")
    o3d.visualization.draw_geometries([voxel_grid], window_name="Step 4: Cup Voxel Grid")
    
    # Step 5: Adding a Plane
    print("\n" + "=" * 40)
    print("STEP 5: ADDING A PLANE")
    print("=" * 40)
    
    # Calculate proper positions based on cup dimensions
    cup_height = bbox_max[1] - bbox_min[1]
    cup_width = bbox_max[0] - bbox_min[0]
    cup_depth = bbox_max[2] - bbox_min[2]
    
    # Create a table plane that fits under the cup
    table_width = cup_width * 2.5
    table_depth = cup_depth * 2.5
    
    plane = o3d.geometry.TriangleMesh.create_box(width=table_width, height=0.02, depth=table_depth)
    
    # Position table directly under the cup
    table_x = bbox_center[0] - table_width/2
    table_y = bbox_min[1] - 0.1
    table_z = bbox_center[2] - table_depth/2
    
    plane.translate([table_x, table_y, table_z])
    plane.paint_uniform_color([0.7, 0.7, 0.7])
    
    # Create a visible cutting plane
    cutting_plane_height = cup_height * 1.5
    cutting_plane_depth = cup_depth * 1.5
    cutting_plane_width = 0.1
    
    cutting_plane = o3d.geometry.TriangleMesh.create_box(
        width=cutting_plane_width, 
        height=cutting_plane_height, 
        depth=cutting_plane_depth
    )
    
    # Position cutting plane to slice through the middle of the cup
    cutting_x = bbox_center[0] - cutting_plane_width/2
    cutting_y = bbox_min[1] - 0.2
    cutting_z = bbox_center[2] - cutting_plane_depth/2
    
    cutting_plane.translate([cutting_x, cutting_y, cutting_z])
    cutting_plane.paint_uniform_color([1.0, 0.6, 0.0])
    
    # Display cup with planes
    cup_for_display = mesh
    cup_for_display.paint_uniform_color([0.3, 0.5, 0.9])
    
    combined_geometries = [cup_for_display, plane, cutting_plane]
    custom_draw_geometry_with_screenshot(combined_geometries, "step5_cup_with_planes.png", "Step 5: Cup with Planes")
    o3d.visualization.draw_geometries([cup_for_display, plane, cutting_plane], 
                                    window_name="Step 5: Cup with Planes")
    
    # Step 6: Surface Clipping
    print("\n" + "=" * 40)
    print("STEP 6: SURFACE CLIPPING")
    print("=" * 40)
    
    points = np.asarray(mesh.vertices)
    
    # Clip points: keep points on the LEFT side of the cutting plane
    clipping_threshold = bbox_center[0]
    clipped_indices = points[:, 0] < clipping_threshold
    clipped_points = points[clipped_indices]
    
    # Create clipped point cloud for Step 6
    clipped_pcd = o3d.geometry.PointCloud()
    clipped_pcd.points = o3d.utility.Vector3dVector(clipped_points)
    
    print(f"Original number of vertices: {len(points)}")
    print(f"Remaining vertices after clipping: {len(clipped_points)}")
    print(f"Percentage removed: {(1 - len(clipped_points)/len(points))*100:.1f}%")
    
    clipped_pcd.paint_uniform_color([0.8, 0.2, 0.2])
    custom_draw_geometry_with_screenshot(clipped_pcd, "step6_cup_clipped.png", "Step 6: Clipped Cup")
    o3d.visualization.draw_geometries([clipped_pcd], window_name="Step 6: Clipped Cup")
    
    # Step 7: Working with Color and Extremes - ON CLIPPED MODEL
    print("\n" + "=" * 40)
    print("STEP 7: COLOR GRADIENT AND EXTREME POINTS - ON CLIPPED MODEL")
    print("=" * 40)
    
    # STEP 7 FIX: Apply color gradient and extremes to the CLIPPED model (like Step 6)
    
    # Create a new point cloud from the CLIPPED points
    colored_clipped_pcd = o3d.geometry.PointCloud()
    colored_clipped_pcd.points = o3d.utility.Vector3dVector(clipped_points)
    
    # Apply gradient based on Y coordinate (height) to CLIPPED points
    clipped_points_array = np.asarray(clipped_points)
    y_coords = clipped_points_array[:, 1]
    y_min, y_max = np.min(y_coords), np.max(y_coords)
    
    # Create gradient colors for CLIPPED model
    colors = np.zeros((len(clipped_points_array), 3))
    for i, y in enumerate(y_coords):
        t = (y - y_min) / (y_max - y_min)
        colors[i] = [t, 0.3, 1 - t]  # Blue (low) to Red (high)
    
    colored_clipped_pcd.colors = o3d.utility.Vector3dVector(colors)
    
    # Find extreme points in the CLIPPED model
    min_y_index = np.argmin(y_coords)
    max_y_index = np.argmax(y_coords)
    min_point = clipped_points_array[min_y_index]
    max_point = clipped_points_array[max_y_index]
    
    print(f"Lowest point in clipped model: {min_point} (Y = {min_point[1]:.4f})")
    print(f"Highest point in clipped model: {max_point} (Y = {max_point[1]:.4f})")
    
    # Create spheres to highlight extreme points in CLIPPED model
    min_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.03)
    min_sphere.translate(min_point)
    min_sphere.paint_uniform_color([0, 1, 0])  # Green for lowest point
    
    max_sphere = o3d.geometry.TriangleMesh.create_sphere(radius=0.03)
    max_sphere.translate(max_point)
    max_sphere.paint_uniform_color([1, 0, 0])  # Red for highest point
    
    # Combine CLIPPED model with gradient and extreme points
    final_geometries = [colored_clipped_pcd, min_sphere, max_sphere]
    custom_draw_geometry_with_screenshot(final_geometries, "step7_cup_gradient_extremes.png", "Step 7: Clipped Cup with Gradient and Extreme Points")
    o3d.visualization.draw_geometries([colored_clipped_pcd, min_sphere, max_sphere], 
                                    window_name="Step 7: Clipped Cup with Gradient and Extreme Points")
    
    # Final summary
    print("\n" + "=" * 60)
    print("ASSIGNMENT COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("All 7 steps completed with teacher's requirements:")
    print("✓ Step 1: Model shown as point cloud (dots)")
    print("✓ Step 7: Color gradient applied to CLIPPED model (half cup)")
    print(f"Screenshots saved in: {os.path.abspath('assignment5_screenshots')}")

if __name__ == "__main__":
    assignment_5_cup_fixed()