import solid
import numpy as np
import os.path as osp
import os
import math

"""
96-Well Plate with Reservoirs Generator
This script generates a 3D model of a 96-well plate with configurable reservoirs.
It uses solid-python to generate OpenSCAD code for 3D printing.
"""

def get_default_config():
    """
    Returns a dictionary containing default configuration parameters.
    
    Returns:
        dict: Default configuration parameters for the plate model
    """
    version = "print_hips_2"
    base_name = "96_well_plate_reservoirs_"+version
    config = {
        # Version and naming
        "version": version,
        "base_name": base_name,
        "base_path": osp.join("./plates/",base_name),
        
        # Basic plate dimensions
        "plate_size_outer": [127.5, 85.35],
        "plate_size_inner": [124.15, 82],
        "plate_height_outer": 8.5,
        "plate_height_inner": 8.5,
        "plate_under_depth": 1.5,
        "skirt_thickness": 1.2,
        
        # Corner dimensions
        "corner_x": 7.5,
        "corner_y": 7.5,
        
        # Grid configuration
        "grid_size": [1, 1],
        
        # Device dimensions
        "device_dims": [107, 71],
        
        # Reservoir configuration
        "reservoir_x_tol": 8,
        "reservoir_y_tol": 5,
        "reservoir_depth": 12,
        "reservoir_number_x": 3,
        "reservoir_number_y": 4,
        "reservoir_wall_thickness": 4,
        "lower_wall_height": 0,
        
        # Release holes configuration
        "release_holes": False,
        "release_radius": 2.5,
        
        # Groove configuration
        "groove_width": 1.6,  # Width of the groove (gw)
        "groove_depth": .8,  # Depth of the groove (gd)
        "gap_device": 1,    # Distance from device slot to groove
        
        # Negative chamfer configuration
        "corner_chamfer_depth": 5,
        "use_negative_chamfer": False,    # Toggle for negative chamfer
        "negative_chamfer_angle": 45,     # Angle in degrees (typically 45)
        "negative_chamfer_height": 2.0,   # Height of the chamfer
        "negative_chamfer_face": "top" # Which face to apply it to: "bottom", "top", "left", or "right"
    }
    
    # Derived values
    config["plate_height"] = config["plate_height_inner"] + config["plate_height_outer"]
    config["skirt_hole_dims"] = config["plate_size_outer"].copy()
    
    # Calculate reservoir dimensions based on device dimensions
    config["reservoir_dims_x"] = [
        config["device_dims"][0] - config["reservoir_x_tol"],
        (config["plate_size_inner"][1] - config["device_dims"][1] - config["reservoir_y_tol"]) / 2.0
    ]
    
    config["reservoir_dims_y"] = [
        (config["plate_size_inner"][0] - config["device_dims"][0] - config["reservoir_x_tol"]) / 2.0,
        config["device_dims"][1] - config["reservoir_y_tol"]
    ]
    
    return config

def save_model(model, base_path, base_name):
    """
    Saves the 3D model to an OpenSCAD file.
    
    Args:
        model: The solid-python 3D model
        base_path (str): Directory path to save the model
        base_name (str): Filename base for the model
    """
    if not osp.exists(base_path):
        os.makedirs(base_path)
    scad_path = osp.join(base_path, base_name + ".scad")
    solid.scad_render_to_file(model, osp.join(scad_path))

def center_unit_array(model, dims, grid_size):
    """
    Centers a unit array in the given grid.
    
    Args:
        model: The solid-python 3D model
        dims (list): Dimensions of the unit
        grid_size (list): Grid size [x, y]
        
    Returns:
        The centered model
    """
    model = solid.translate([dims[0]/2.0, dims[1]/2.0, 0])(model)
    model = solid.translate([
        -dims[0]*(grid_size[0]/2.0),
        -dims[1]*(grid_size[1]/2.0), 0
    ])(model)
    return model

def corners_from_x_y(x, y):
    """
    Generate corner coordinates from x and y dimensions.
    
    Args:
        x (float): X dimension
        y (float): Y dimension
        
    Returns:
        list: List of corner coordinates
    """
    return [
        [-x/2.0, y/2.0],
        [x/2.0, y/2.0],
        [-x/2.0, -y/2.0],
        [x/2.0, -y/2.0]
    ]

def create_plate_base(config):
    """
    Creates the base plate structure.
    
    Args:
        config (dict): Configuration parameters
        
    Returns:
        The base plate model
    """
    plate_size_outer = config["plate_size_outer"]
    plate_size_inner = config["plate_size_inner"]
    plate_height_inner = config["plate_height_inner"]
    plate_height_diff = config["plate_height"] - plate_height_inner
    
    # Create outer plate as base
    plate = solid.cube((*plate_size_outer, plate_height_diff), center=True)
    plate = solid.translate([0, 0, plate_height_diff/2.0])(plate)
    
    # Create inner plate on top
    plate_inner = solid.cube((*plate_size_inner, plate_height_inner), center=True)
    plate_inner = solid.translate([0, 0, plate_height_inner/2.0 + plate_height_diff])(plate_inner)
    
    # Combine plates
    plate = solid.union()(plate, plate_inner)
    
    return plate

def create_plate_skirt(config):
    """
    Creates the skirt for the plate.
    
    Args:
        config (dict): Configuration parameters
        
    Returns:
        The plate skirt model
    """
    plate_size_outer = config["plate_size_outer"]
    plate_under_depth = config["plate_under_depth"]
    skirt_thickness = config["skirt_thickness"]
    skirt_hole_dims = config["skirt_hole_dims"]
    
    # Create removal shapes for skirt
    plate_under_remove_out = solid.cube((*plate_size_outer, plate_under_depth), center=True)
    plate_under_remove_out = solid.translate([0, 0, plate_under_depth/2.0])(plate_under_remove_out)
    
    plate_under_remove_in = solid.cube((
        plate_size_outer[0] - skirt_thickness, 
        plate_size_outer[1] - skirt_thickness, 
        plate_under_depth
    ), center=True)
    plate_under_remove_in = solid.translate([0, 0, plate_under_depth/2.0])(plate_under_remove_in)
    
    plate_under_remove = solid.difference()(plate_under_remove_out, plate_under_remove_in)
    
    # Create corner removal
    plate_under_remove_corner = solid.cube((*skirt_hole_dims, plate_under_depth), center=True)
    plate_under_remove_corner = solid.translate([0, 0, plate_under_depth/2.0])(plate_under_remove_corner)
    
    plate_corners_pos = corners_from_x_y(*plate_size_outer)
    plate_under_remove_corners = []
    
    for corner_pos in plate_corners_pos:
        temp_corner = solid.translate([*corner_pos, 0])(plate_under_remove_corner)
        plate_under_remove_corners.append(temp_corner)
    
    corners_remove = solid.union()(*plate_under_remove_corners)
    skirt = solid.intersection()(plate_under_remove, corners_remove)
    
    return skirt, plate_under_remove_out

def create_corners(config):
    """
    Creates the corners for the plate.
    
    Args:
        config (dict): Configuration parameters
        
    Returns:
        The corners model
    """
    plate_size_inner = config["plate_size_inner"]
    plate_size_outer = config["plate_size_outer"]
    plate_height_inner = config["plate_height_inner"]
    plate_height_diff = config["plate_height"] - plate_height_inner
    xtra_x = (plate_size_outer[0]-plate_size_inner[0])/2.0
    xtra_y = (plate_size_outer[1]-plate_size_inner[1])/2.0
    #corner_x = config["corner_x"]+10
    #corner_y = config["corner_y"]+xtra_y
    corner_x = config["corner_x"]+xtra_x*2
    corner_y = config["corner_y"]+xtra_y*2
    corner_chamfer_depth = config["corner_chamfer_depth"]
    
    # Define corner points
    corner_thickness = 20
    corner_points = [
        [0, 0, 0],
        [0, corner_y, corner_thickness],
        [0, corner_y, 0],
        [0, corner_y, corner_thickness],
        [corner_x, corner_y, corner_thickness],
        [corner_x, corner_y, 0]
    ]
    
    # Create corner polygon
    corner = solid.polygon(points=corner_points)()
    corner = solid.linear_extrude(height=plate_height_inner+corner_chamfer_depth)(corner)
    
    # Create top-left corner
    corner_top_left = corner
    corner_top_left = solid.translate([0, -corner_y, 0])(corner_top_left)
    corner_top_left = solid.translate([
        -plate_size_outer[0]/2.0-0.001, 
        plate_size_outer[1]/2.0+0.001, 
        plate_height_diff - corner_chamfer_depth
    ])(corner_top_left)
    #corner_top_left = solid.translate([0, -corner_y, 0])(corner_top_left)
    #corner_top_left = solid.translate([
    #    -plate_size_inner[0]/2.0, 
    #    plate_size_inner[1]/2.0, 
    #    plate_height_diff - corner_chamfer_depth
    #])(corner_top_left)
    
    # Create bottom-left corner
    #corner_bottom_left = solid.rotate(90)(corner)
    #corner_bottom_left = solid.translate([corner_x, 0, 0])(corner_bottom_left)
    #corner_bottom_left = solid.translate([
    #    -plate_size_inner[0]/2.0, 
    #    -plate_size_inner[1]/2.0, 
    #    plate_height_diff
    #])(corner_bottom_left)
    corner_bottom_left = solid.rotate(90)(corner)
    corner_bottom_left = solid.translate([corner_x, 0, 0])(corner_bottom_left)
    corner_bottom_left = solid.translate([
        -plate_size_outer[0]/2.0-0.001, 
        -plate_size_outer[1]/2.0-0.001, 
        plate_height_diff - corner_chamfer_depth
    ])(corner_bottom_left)
    
    # Combine corners
    corners = solid.union()(corner_top_left, corner_bottom_left)
    
    return corners

def create_device_slot(config):
    """
    Creates the device slot for the plate.
    
    Args:
        config (dict): Configuration parameters
        
    Returns:
        The device slot model
    """
    device_dims = config["device_dims"]
    plate_height = config["plate_height"]
    
    device_slot = solid.cube((*device_dims, plate_height), center=True)
    device_slot = solid.translate([0, 0, plate_height/2.0])(device_slot)
    
    return device_slot

def create_device_groove(config):
    """
    Creates a groove around the device slot.
    
    Args:
        config (dict): Configuration parameters
        
    Returns:
        The groove model to be subtracted from the plate
    """
    device_dims = config["device_dims"]
    plate_height = config["plate_height"]
    groove_width = config["groove_width"]
    groove_depth = config["groove_depth"]
    gap_device = config["gap_device"]
    plate_under_depth = config["plate_under_depth"]
    
    # Calculate inner and outer dimensions for the groove
    inner_dims = [
        device_dims[0] + 2 * gap_device,
        device_dims[1] + 2 * gap_device,
        groove_depth
    ]
    
    outer_dims = [
        inner_dims[0] + 2 * groove_width,
        inner_dims[1] + 2 * groove_width,
        groove_depth
    ]
    
    # Create outer cube
    outer_cube = solid.cube(outer_dims, center=True)
    
    # Create inner cube (to be subtracted)
    inner_cube = solid.cube(inner_dims, center=True)
    
    # Create groove by subtracting inner from outer
    groove = solid.difference()(outer_cube, inner_cube)
    
    # Position the groove at the correct height
    # The top of the groove should be at the plate height
    #groove = solid.translate([0, 0, plate_height - groove_depth/2.0])(groove)
    groove = solid.translate([0, 0, plate_under_depth + groove_depth/2.0 -0.001])(groove)
    
    return groove

def create_reservoirs(config):
    """
    Creates the reservoirs for the plate.
    
    Args:
        config (dict): Configuration parameters
        
    Returns:
        The reservoirs model and lower wall model
    """
    plate_size_inner = config["plate_size_inner"]
    device_dims = config["device_dims"]
    reservoir_dims_x = config["reservoir_dims_x"]
    reservoir_dims_y = config["reservoir_dims_y"]
    reservoir_depth = config["reservoir_depth"]
    plate_height = config["plate_height"]
    lower_wall_height = config["lower_wall_height"]
    
    # Create X and Y reservoirs
    reservoir_x = solid.cube((*reservoir_dims_x, reservoir_depth), center=True)
    reservoir_x = solid.translate([0, 0, plate_height - reservoir_depth/2.0])(reservoir_x)
    
    reservoir_y = solid.cube((*reservoir_dims_y, reservoir_depth), center=True)
    reservoir_y = solid.translate([0, 0, plate_height - reservoir_depth/2.0])(reservoir_y)
    
    # Calculate positions
    plate_top_x_thickness = (plate_size_inner[0] - device_dims[0]) / 2.0
    x_pos_reservoir = plate_size_inner[0] / 2.0 - plate_top_x_thickness / 2.0
    
    plate_top_y_thickness = (plate_size_inner[1] - device_dims[1]) / 2.0
    y_pos_reservoir = plate_size_inner[1] / 2.0 - plate_top_y_thickness / 2.0
    
    # Position reservoirs
    reservoir_x_top = solid.translate([0, y_pos_reservoir, 0])(reservoir_x)
    reservoir_x_bottom = solid.translate([0, -y_pos_reservoir, 0])(reservoir_x)
    reservoir_y_left = solid.translate([x_pos_reservoir, 0, 0])(reservoir_y)
    reservoir_y_right = solid.translate([-x_pos_reservoir, 0, 0])(reservoir_y)
    
    # Combine reservoirs
    reservoirs = solid.union()(
        reservoir_x_bottom, 
        reservoir_x_top, 
        reservoir_y_right, 
        reservoir_y_left
    )
    
    # Create lower wall
    reservoir_lower_wall_x = solid.cube((
        reservoir_dims_x[0], 
        y_pos_reservoir * 2, 
        lower_wall_height
    ), center=True)
    reservoir_lower_wall_x = solid.translate([
        0, 0, plate_height - lower_wall_height / 2.0
    ])(reservoir_lower_wall_x)
    
    reservoir_lower_wall_y = solid.cube((
        x_pos_reservoir * 2, 
        reservoir_dims_y[1], 
        lower_wall_height
    ), center=True)
    reservoir_lower_wall_y = solid.translate([
        0, 0, plate_height - lower_wall_height / 2.0
    ])(reservoir_lower_wall_y)
    
    reservoir_lower_wall = solid.union()(
        reservoir_lower_wall_y, 
        reservoir_lower_wall_x
    )
    
    return reservoirs, reservoir_lower_wall, x_pos_reservoir, y_pos_reservoir

def create_reservoir_walls(config, x_pos_reservoir, y_pos_reservoir):
    """
    Creates the walls for the reservoirs.
    
    Args:
        config (dict): Configuration parameters
        x_pos_reservoir (float): X position of reservoir
        y_pos_reservoir (float): Y position of reservoir
        
    Returns:
        The reservoir walls models
    """
    plate_size_inner = config["plate_size_inner"]
    reservoir_dims_x = config["reservoir_dims_x"]
    reservoir_dims_y = config["reservoir_dims_y"]
    reservoir_wall_thickness = config["reservoir_wall_thickness"]
    reservoir_depth = config["reservoir_depth"]
    reservoir_number_x = config["reservoir_number_x"]
    reservoir_number_y = config["reservoir_number_y"]
    plate_height = config["plate_height"]
    
    # Create X wall
    reservoir_x_wall = solid.cube((
        plate_size_inner[0], 
        reservoir_wall_thickness, 
        reservoir_depth
    ), center=True)
    reservoir_x_wall = solid.translate([
        0, 
        -reservoir_dims_y[1] / 2.0, 
        plate_height - reservoir_depth / 2.0
    ])(reservoir_x_wall)
    
    # Create Y wall
    reservoir_y_wall = solid.cube((
        reservoir_wall_thickness, 
        plate_size_inner[1], 
        reservoir_depth
    ), center=True)
    reservoir_y_wall = solid.translate([
        -reservoir_dims_x[0] / 2.0, 
        0, 
        plate_height - reservoir_depth / 2.0
    ])(reservoir_y_wall)
    
    # Calculate spacings
    spacing_x = reservoir_dims_y[1] / reservoir_number_x
    spacing_y = reservoir_dims_x[0] / reservoir_number_y
    
    # Create multiple X walls
    reservoir_x_walls = []
    for i in range(reservoir_number_x - 1):
        reservoir_x_walls.append(
            solid.translate([0, spacing_x * (i + 1), 0])(reservoir_x_wall)
        )
    
    # Create multiple Y walls
    reservoir_y_walls = []
    for i in range(reservoir_number_y - 1):
        reservoir_y_walls.append(
            solid.translate([spacing_y * (i + 1), 0, 0])(reservoir_y_wall)
        )
    
    return reservoir_x_walls, reservoir_y_walls, spacing_x, spacing_y

def create_release_holes(config, spacing_x, spacing_y):
    """
    Creates release holes for the plate if enabled.
    
    Args:
        config (dict): Configuration parameters
        spacing_x (float): X spacing between holes
        spacing_y (float): Y spacing between holes
        
    Returns:
        The release holes model or None if disabled
    """
    if not config["release_holes"]:
        return None
        
    plate_size_inner = config["plate_size_inner"]
    reservoir_number_x = config["reservoir_number_x"]
    reservoir_number_y = config["reservoir_number_y"]
    release_radius = config["release_radius"]
    reservoir_dims_x = config["reservoir_dims_x"]
    reservoir_dims_y = config["reservoir_dims_y"]
    plate_height = config["plate_height"]
    
    # Create X release hole
    release_x = solid.cylinder(r=release_radius, h=plate_size_inner[0], segments=64, center=True)
    release_x = solid.rotate([0, 90, 0])(release_x)
    release_x = solid.translate([0, -spacing_x / 2.0, 0])(release_x)
    
    # Create Y release hole
    release_y = solid.cylinder(r=release_radius, h=plate_size_inner[1], segments=64, center=True)
    release_y = solid.rotate([90, 0, 0])(release_y)
    release_y = solid.translate([-spacing_y / 2.0, 0, 0])(release_y)
    
    # Position release holes
    release_holes = []
    release_x = solid.translate([0, -reservoir_dims_y[1] / 2.0, 0])(release_x)
    
    for i in range(reservoir_number_x):
        release_holes.append(solid.translate([0, spacing_x * (i + 1), 0])(release_x))
    
    release_y = solid.translate([-reservoir_dims_x[0] / 2.0, 0, 0])(release_y)
    
    for i in range(reservoir_number_y):
        release_holes.append(solid.translate([spacing_y * (i + 1), 0, 0])(release_y))
    
    # Combine and position release holes
    release_holes = solid.union()(*release_holes)
    release_holes = solid.translate([0, 0, plate_height])(release_holes)
    
    return release_holes

def create_negative_chamfer(config):
    """
    Creates a negative chamfer (angled addition) to a surface.
    This function creates a solid that will be unioned with the main plate.
    
    Args:
        config (dict): Configuration parameters
        
    Returns:
        The negative chamfer solid model
    """
    if not config["use_negative_chamfer"]:
        return None
        
    plate_size_outer = config["plate_size_outer"]
    plate_height = config["plate_height"]
    chamfer_angle = config["negative_chamfer_angle"]
    chamfer_height = config["negative_chamfer_height"]
    face = config["negative_chamfer_face"]
    
    # Calculate the width of the chamfer based on the angle and height
    # For a 45 degree angle, width = height
    chamfer_width = chamfer_height / np.tan(np.radians(chamfer_angle))
    
    # Create points for the chamfer profile based on which face it's applied to
    if face == "bottom":
        # For the bottom face (green surface in the image)
        # Create a polygon with these points: origin, width outward, height downward
        points = [
            [0, 0, 0],                    # Origin point
            [chamfer_width, 0, 0],        # Width outward
            [0, 0, -chamfer_height]       # Height downward
        ]
        
        # Create a 2D polygon from these points
        polygon = solid.polygon(points=points)()
        
        # Extrude the polygon along the Y axis to create a 3D solid
        chamfer_profile = solid.linear_extrude(height=plate_size_outer[1], center=True)(polygon)
        
        # Create another extrusion along the X axis
        chamfer_profile = solid.rotate([0, 0, 90])(chamfer_profile)
        full_chamfer = solid.linear_extrude(height=plate_size_outer[0], center=True)(chamfer_profile)
        
        # Position the chamfer at the bottom of the plate
        full_chamfer = solid.translate([0, 0, 0])(full_chamfer)
        
    elif face == "top":
        # Implementation for top face
        # Similar process but different points and positioning
        points = [
            [0, 0, 0],                    
            [chamfer_width, 0, 0],        
            [0, 0, chamfer_height]        
        ]
        polygon = solid.polygon(points=points)()
        chamfer_profile = solid.linear_extrude(height=plate_size_outer[1], center=True)(polygon)
        chamfer_profile = solid.rotate([0, 0, 90])(chamfer_profile)
        full_chamfer = solid.linear_extrude(height=plate_size_outer[0], center=True)(chamfer_profile)
        full_chamfer = solid.translate([0, 0, plate_height])(full_chamfer)
        
    elif face == "left" or face == "right":
        # Implementation for side faces
        # Similar process but different orientation
        points = [
            [0, 0, 0],
            [0, chamfer_width, 0],
            [0, 0, chamfer_height]
        ]
        polygon = solid.polygon(points=points)()
        chamfer_profile = solid.linear_extrude(height=plate_size_outer[0], center=True)(polygon)
        full_chamfer = solid.rotate([90, 0, 0])(chamfer_profile)
        full_chamfer = solid.linear_extrude(height=plate_size_outer[1], center=True)(full_chamfer)
        
        # Position based on which side
        if face == "left":
            full_chamfer = solid.translate([-plate_size_outer[0]/2, 0, 0])(full_chamfer)
        else:  # right
            full_chamfer = solid.translate([plate_size_outer[0]/2, 0, 0])(full_chamfer)
    
    return full_chamfer

def create_96_well_plate(config=None):
    """
    Creates a complete 96-well plate with reservoirs.
    
    Args:
        config (dict, optional): Configuration parameters. If None, default config is used.
        
    Returns:
        The complete plate model
    """
    if config is None:
        config = get_default_config()
    
    # Create base plate
    plate = create_plate_base(config)
    
    # Create skirt
    skirt, plate_under_remove_out = create_plate_skirt(config)
    plate = solid.difference()(plate, plate_under_remove_out)
    plate = solid.union()(plate, skirt)
    
    # Create corners
    corners = create_corners(config)
    plate = solid.difference()(plate, corners)
    
    # Create device slot
    device_slot = create_device_slot(config)
    plate = solid.difference()(plate, device_slot)
    
    # Create device groove around the slot
    device_groove = create_device_groove(config)
    plate = solid.difference()(plate, device_groove)
    
    # Create reservoirs
    reservoirs, reservoir_lower_wall, x_pos_reservoir, y_pos_reservoir = create_reservoirs(config)
    plate = solid.difference()(plate, reservoirs)
    plate = solid.difference()(plate, reservoir_lower_wall)
    
    # Create reservoir walls
    reservoir_x_walls, reservoir_y_walls, spacing_x, spacing_y = create_reservoir_walls(
        config, x_pos_reservoir, y_pos_reservoir
    )
    
    # Create release holes if enabled
    release_holes = create_release_holes(config, spacing_x, spacing_y)
    if release_holes is not None:
        plate = solid.difference()(plate, release_holes)
    
    # Combine all walls with plate
    plate = solid.union()(
        *reservoir_x_walls,
        *reservoir_y_walls,
        plate
    )
    
    # Final device slot cut
    plate = solid.difference()(plate, device_slot)
    
    # Add negative chamfer if enabled
    negative_chamfer = create_negative_chamfer(config)
    if negative_chamfer is not None:
        plate = solid.union()(plate, negative_chamfer)
    
    return plate

def main():
    """
    Main function to generate and save the plate model.
    """
    # Load default configuration
    config = get_default_config()
    config["use_negative_chamfer"] = True
    
    # Create the plate
    plate = create_96_well_plate(config)
    
    # Save the model
    save_model(plate, config["base_path"], config["base_name"])

if __name__ == "__main__":
    # Import optional modules only when executing as main script
    try:
        chamfer_extrude = solid.import_scad("./chamfer_extrude.scad")
        chamfer_extrude = chamfer_extrude.chamfer_extrude
    except Exception as e:
        print(f"Warning: Could not import chamfer_extrude: {e}")
    
    main()
