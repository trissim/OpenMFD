import solid
import numpy as np
from make_device import make_unit_array
import os.path as osp
import os 
import math

chamfer_extrude=solid.import_scad("./chamfer_extrude.scad")
chamfer_extrude=chamfer_extrude.chamfer_extrude
version="print_resin_v4"
base_name="96_well_plate_reservoirs_"+version
base_path="./plates/"+base_name
#basic plate dims
plate_size_outer=[127.5,85.35]
plate_size_inner=[124.15,82]
plate_height_outer=8.5
plate_height_inner=8.5
plate_height=plate_height_inner+plate_height_outer
plate_under_depth=2
skirt_thickness=1.5
skirt_hole_dims=[plate_size_outer[0],plate_size_outer[1]]
corner_x=7.5
corner_y=7.5
grid_size=[1,1]
#device_tol=2
#dims = [110-device_tol,74-device_tol,0]
#device_dims=[110-device_tol,74-device_tol]
dims = [112,74,0]
device_dims=[112,74]
reservoir_x_tol=5
reservoir_y_tol=5
reservoir_dims_x=[device_dims[0]-reservoir_x_tol,(plate_size_inner[1]-device_dims[1]-reservoir_y_tol)/2.0]
reservoir_dims_y=[(plate_size_inner[0]-device_dims[0]-reservoir_x_tol)/2.0,device_dims[1]-reservoir_y_tol*1.5]
reservoir_depth=12
lower_wall_height=0
release_radius=2.5
reservoir_number_x=3
reservoir_number_y=4
reservoir_wall_thickness=4


def save_model(model,base_path,base_name):
    if not osp.exists(base_path):
        os.makedirs(base_path)
    scad_path=osp.join(base_path,base_name+".scad")
    solid.scad_render_to_file(model,osp.join(scad_path))

def center_unit_array(model,dims,grid_size):
    model = solid.translate([dims[0]/2.0,dims[1]/2.0,0])(model)
    model = solid.translate([-dims[0]*(grid_size[0]/2.0),
                             -dims[1]*(grid_size[1]/2.0),0])(model)
    return model


#plate_chassis
plate_height_diff=plate_height-plate_height_inner

#outer_plate as base
plate=solid.cube((*plate_size_outer,plate_height_diff),center=True)
plate=solid.translate([0,0,plate_height_diff/2.0])(plate)
#inner plate goes on top
plate_inner=solid.cube((*plate_size_inner,plate_height_inner),center=True)
plate_inner=solid.translate([0,0,plate_height_inner/2.0+plate_height_diff])(plate_inner)
plate=solid.union()(plate,plate_inner)


plate_under_remove_out=solid.cube((*plate_size_outer,plate_under_depth),center=True)
plate_under_remove_out=solid.translate([0,0,plate_under_depth/2.0])(plate_under_remove_out)
plate_under_remove_in=solid.cube((plate_size_outer[0]-skirt_thickness,plate_size_outer[1]-skirt_thickness,plate_under_depth),center=True)
plate_under_remove_in=solid.translate([0,0,plate_under_depth/2.0])(plate_under_remove_in)

plate_under_remove=solid.difference()(plate_under_remove_out,plate_under_remove_in)

corners_from_x_y = lambda x,y: [[-x/2.0,y/2.0],
                                    [x/2.0, y/2.0],
                                    [-x/2.0, -y/2.0],
                                    [x/2.0, -y/2.0]]
plate_under_remove_corner=solid.cube((*skirt_hole_dims,plate_under_depth),center=True)
plate_under_remove_corner=solid.translate([0,0,plate_under_depth/2.0])(plate_under_remove_corner)
plate_corners_pos=corners_from_x_y(*plate_size_outer)
plate_under_remove_corners=[]
for corner_pos in plate_corners_pos:
    temp_corner=solid.translate([*corner_pos,0])(plate_under_remove_corner)
    plate_under_remove_corners.append(temp_corner)

corners_remove=solid.union()(*plate_under_remove_corners)
skirt=solid.intersection()(plate_under_remove,corners_remove)
#chamfer skirt
#skirt=solid.projection()(skirt)
#skirt=chamfer_extrude(plate_under_depth,45,segments=20)(skirt)
#skirt=solid.linear_extrude(height=plate_under_depth)(skirt)
#skirt=solid.intersection()(plate,skirt)
#
#skirt=solid.translate([0,0,-plate_under_depth/2.0])(skirt)
#skirt=solid.rotate([0,180,0])(skirt)
#skirt=solid.translate([0,0,plate_under_depth/2.0])(skirt)

plate=solid.difference()(plate,plate_under_remove_out)
plate=solid.union()(plate,skirt)



#corners
#               0       1        2        3         4          5
corner_points=[[0,0,0],[0,corner_y,10],[0,corner_y,0],[0,corner_y,10],[corner_x,corner_y,10],[corner_x,corner_y,0]]
corner=solid.polygon(points=corner_points)()
corner=solid.linear_extrude(height=plate_height_inner)(corner)

corner_top_left=corner
corner_top_left=solid.translate([0,-corner_y,0])(corner_top_left)
corner_top_left=solid.translate([-plate_size_inner[0]/2.0,plate_size_inner[1]/2.0,plate_height_diff])(corner_top_left)

corner_bottom_left=solid.rotate(90)(corner)
corner_bottom_left=solid.translate([corner_x,0,0])(corner_bottom_left)
corner_bottom_left=solid.translate([-plate_size_inner[0]/2.0,-plate_size_inner[1]/2.0,plate_height_diff])(corner_bottom_left)

corners = solid.union()(corner_top_left,corner_bottom_left)
#corners = solid.union()(corner_top_left)
plate=solid.difference()(plate,corners)

device_dims = np.array(device_dims)
device_slot = solid.cube((*device_dims,plate_height),center=True)
device_slot = solid.translate([0,0,plate_height/2.0])(device_slot)
plate = solid.difference()(plate,device_slot)

#reservoirs
reservoir_x = solid.cube((*reservoir_dims_x,reservoir_depth),center=True)
reservoir_x = solid.translate([0,0,plate_height-reservoir_depth/2.0])(reservoir_x)
reservoir_y = solid.cube((*reservoir_dims_y,reservoir_depth),center=True)
reservoir_y = solid.translate([0,0,plate_height-reservoir_depth/2.0])(reservoir_y)
plate_top_x_thickness=(plate_size_inner[0]-device_dims[0])/2.0
x_pos_reservoir=plate_size_inner[0]/2.0-plate_top_x_thickness/2.0
plate_top_y_thickness=(plate_size_inner[1]-device_dims[1])/2.0
y_pos_reservoir=plate_size_inner[1]/2.0-plate_top_y_thickness/2.0
reservoir_x_top = solid.translate([0,y_pos_reservoir,0])(reservoir_x)
reservoir_x_bottom = solid.translate([0,-y_pos_reservoir,0])(reservoir_x)
reservoir_y_left = solid.translate([x_pos_reservoir,0,0])(reservoir_y)
reservoir_y_right = solid.translate([-x_pos_reservoir,0,0])(reservoir_y)




reservoir_x_wall = solid.cube((plate_size_inner[0],reservoir_wall_thickness,reservoir_depth),center=True)
reservoir_x_wall = solid.translate([0,-reservoir_dims_y[1]/2.0,plate_height-reservoir_depth/2.0])(reservoir_x_wall)
reservoir_x_walls = [] 
spacing_x=reservoir_dims_y[1]/reservoir_number_x

reservoir_y_wall = solid.cube((reservoir_wall_thickness,plate_size_inner[1],reservoir_depth),center=True)
reservoir_y_wall = solid.translate([-reservoir_dims_x[0]/2.0,0,plate_height-reservoir_depth/2.0])(reservoir_y_wall)
reservoir_y_walls = [] 
spacing_y=reservoir_dims_x[0]/reservoir_number_y


reservoirs = solid.union()(reservoir_x_bottom,reservoir_x_top,reservoir_y_right,reservoir_y_left)
plate = solid.difference()(plate,reservoirs)
reservoir_lower_wall_x = solid.cube((reservoir_dims_x[0],y_pos_reservoir*2,lower_wall_height),center=True)
reservoir_lower_wall_x = solid.translate([0,0,plate_height-lower_wall_height/2.0])(reservoir_lower_wall_x)
reservoir_lower_wall_y = solid.cube((x_pos_reservoir*2,reservoir_dims_y[1],lower_wall_height),center=True)
reservoir_lower_wall_y = solid.translate([0,0,plate_height-lower_wall_height/2.0])(reservoir_lower_wall_y)
reservoir_lower_wall = solid.union()(reservoir_lower_wall_y,reservoir_lower_wall_x)
plate = solid.difference()(plate,reservoir_lower_wall)



#release holes
release_x = solid.cylinder(r=release_radius, h=plate_size_inner[0],segments=64,center=True)
release_x = solid.rotate([0,90,0])(release_x)
release_x = solid.translate([0,-spacing_x/2.0,0])(release_x)
release_y = solid.cylinder(r=release_radius, h=plate_size_inner[1],segments=64,center=True)
release_y = solid.rotate([90,0,0])(release_y)
release_y = solid.translate([-spacing_y/2.0,0,0])(release_y)
release_holes = []

for i in range(reservoir_number_x-1):
    reservoir_x_walls.append(solid.translate([0,spacing_x*(i+1),0])(reservoir_x_wall))

release_x = solid.translate([0,-reservoir_dims_y[1]/2.0,0])(release_x)
for i in range(reservoir_number_x):
    release_holes.append(solid.translate([0,spacing_x*(i+1),0])(release_x))


for i in range(reservoir_number_y-1):
    reservoir_y_walls.append(solid.translate([spacing_y*(i+1),0,0])(reservoir_y_wall))

release_y = solid.translate([-reservoir_dims_x[0]/2.0,0,0])(release_y)
for i in range(reservoir_number_y):
    release_holes.append(solid.translate([spacing_y*(i+1),0,0])(release_y))


release_holes = solid.union()(*release_holes)
release_holes = solid.translate([0,0,plate_height])(release_holes)
plate = solid.difference()(plate,release_holes)
plate = solid.union()(*reservoir_x_walls,*reservoir_y_walls,plate)
plate = solid.difference()(plate,device_slot)

save_model(plate,base_path,base_name)
