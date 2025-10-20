from make_device import *
"""
MAKE SINGLE DEVICE GRID
"""
well_rad=2
#number of devices
grid_size = [4,4]
#_,_,(open_chamber,_)
base_path="./designs/closed_chamber/4x4/"
casing_x=12
casing_y=12
rows=1
columns=1
chan_gap=0.03
chan_w=0.01
chan_l=0.4
chamber_len_until=1.5
num_chans=int(well_rad/(chan_gap+chan_w)*2)
alignment_mark_size=1
wafer_size=100
wafer_flat_len=32.5
wafer_thickness=0.500
outer_mask_thickness=3
wafer_line_thickness=0.3
dims = [17.5, 17.5, 0]
units_from_center=(2.3,2.3)

"""Make single unit"""
(chamber_wells_many_single,_),_,_=make_device(design='closed',wells_pos=2.5,
                                              well_rad=well_rad,chan_l=chan_l,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                              rows=rows,columns=columns,casing_x=casing_x,casing_y=casing_y,chamber_len_until=chamber_len_until,rotate_units=0,
                                              alignment=None)

_,(channels_many_single,_),_=    make_device(design='closed',wells_pos=2.5,
                                              well_rad=well_rad,chan_l=1.5,chan_w=chan_w,chan_gap=chan_gap,num_chans=int(num_chans*0.98),
                                              rows=rows,columns=columns,casing_x=casing_x,casing_y=casing_y,chamber_len_until=chamber_len_until,rotate_units=0,
                                              alignment=None)

save_model(channels_many_single,base_path,"closed_bottom")
save_model(chamber_wells_many_single,base_path,"closed_top")
save_model(solid.union()(chamber_wells_many_single,channels_many_single),base_path,"closed_top_bottom")

"""Make wall"""
alignment_offset=[(dims[0]-casing_x*rows)/2.0,(dims[1]-casing_y*columns)/2]
#height of 3d printed walls
wall_height=10
#thickness of 3d printed walls
wall_thickness=1
walls,wafer_wall,wafer_walls,= make_walls(wafer_size,wall_thickness,grid_size,dims,height=wall_height,segments=256,make_inner=False)
wall = solid.translate([-alignment_offset[0],-alignment_offset[1]])(wafer_walls)
wall_2d = solid.projection()(wall)
r.render(wall,outfile=osp.join(base_path,"wall_closed_chamber_4mm_4x4.stl"))

""" make outline"""
outline=solid.translate([-alignment_offset[0],-alignment_offset[1]])(walls)
outline = solid.projection()(outline)


"""Make multi version"""
#channels
closed_chamber_4x4_bottom = make_unit_array(channels_many_single,dims,grid_size, dxf=True, alignment = "full",units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
#add outline
closed_chamber_4x4_bottom = solid.union()(closed_chamber_4x4_bottom,outline)
#wells and chambers
closed_chamber_4x4_top = make_unit_array(chamber_wells_many_single,dims,grid_size, dxf=True, alignment = "hollow",units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
#both layers together
closed_chamber_4x4_aligned = solid.union()(closed_chamber_4x4_top,closed_chamber_4x4_bottom)

"""put features in mask with a wafer outline"""
closed_chamber_4x4_bottom_final = add_wafer_to_mask(wafer_size,wafer_flat_len,closed_chamber_4x4_bottom,grid_size,dims,alignment_offset=alignment_offset)
save_model(closed_chamber_4x4_bottom_final,base_path,"closed_chamber_4x4_bottom")
closed_chamber_4x4_top_final = add_wafer_to_mask(wafer_size,wafer_flat_len,closed_chamber_4x4_top,grid_size,dims,alignment_offset=alignment_offset)
save_model(closed_chamber_4x4_top_final,base_path,"closed_chamber_4x4_top")
closed_chamber_4x4_aligned_final = add_wafer_to_mask(wafer_size,wafer_flat_len,closed_chamber_4x4_aligned,grid_size,dims,alignment_offset=alignment_offset)
save_model(closed_chamber_4x4_aligned_final,base_path,"closed_chamber_4x4_aligned")


"""Overlay walls and device"""
wall_and_devices = solid.union()(wall_2d,closed_chamber_4x4_bottom)
save_model(wall_and_devices, base_path,"wall_closed_chamber_4x4_top")



"""make posts to make wells"""
platform_height=5
(wells_many_single,_),_,_=make_device(design='closed',wells_pos=2.5,
                                              well_rad=well_rad,chan_l=chan_l,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                              rows=rows,columns=columns,casing_x=casing_x,casing_y=casing_y,chamber_len_until=chamber_len_until,rotate_units=0,
                                              alignment=None,add_chambers=False)
closed_chamber_4x4_wells = make_unit_array(wells_many_single,dims,grid_size, dxf=True, alignment = None,units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
posts = make_posts(closed_chamber_4x4_wells,30)
#
walls = solid.translate([-alignment_offset[0],-alignment_offset[1]])(walls)
posts_platform=solid.hull()(walls)
posts_platform=solid.projection()(posts_platform)
posts_platform=solid.linear_extrude(height=platform_height)(posts_platform)
posts = solid.translate([0,0,platform_height])(posts)
posts = solid.union()(posts_platform,posts)
save_model(posts,base_path,"2compartment_multi_device_posts",dxf=False)
