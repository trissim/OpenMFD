from make_device import *
base_path="./designs/open_chamber/2compartment_duplicates_4x4_v2/"
design = "open"
wells_pos=3
well_rad=2
rows=1
columns=2
casing_x=12
casing_y=6

chan_gap=0.03
chan_w=0.01
chan_l=1
chan_l_extra=chan_l*3
num_chans=int(well_rad/(chan_gap+chan_w))

chamber_len_until=3
chamber_width=well_rad*2

grid_size = [4,4]
dims = [17.5, 17.5, 0]
alignment_offset=[(dims[0]-casing_x*rows)/2.0,(dims[1]-casing_y*columns)/2]
units_from_center=(2.3,2.3)
alignment_mark_size=1

wafer_size=100
wafer_flat_len=32.5
wafer_thickness=0.500
outer_mask_thickness=1
wafer_line_thickness=0.3
#height of 3d printed walls
wall_height=10
#thickness of 3d printed walls
wall_thickness=1
#area to center device in

#wafer_holder

margin=3
notch_len=10
notch_height=2
oversize=1.0025



"""Make single unit"""
(chamber_wells_many_single,_),_,_=make_device(design=design,wells_pos=wells_pos,
                                         well_rad=well_rad,chan_l=chan_l,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                         rows=rows,columns=columns,casing_x=casing_x,casing_y=casing_y,chamber_len_until=chamber_len_until,rotate_units=0,
                                              alignment=None,chamber_width=chamber_width)

_,(channels_many_single,_),_=    make_device(design=design,wells_pos=wells_pos,
                                        well_rad=well_rad,chan_l=chan_l*4,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                        rows=rows,columns=columns,casing_x=casing_x,casing_y=casing_y,chamber_len_until=chamber_len_until,rotate_units=0,
                                              alignment=None,chamber_width=chamber_width)

save_model(channels_many_single,base_path,"open_duplicates_4mm_bottom")
save_model(chamber_wells_many_single,base_path,"open_duplicates_4mm_top")
save_model(solid.union()(chamber_wells_many_single,channels_many_single),base_path,"open_duplicates_4mm_aligned")

"""Make wall"""
walls,wafer_wall,wafer_walls,= make_walls(wafer_size,wall_thickness,grid_size,dims,height=wall_height,segments=256,make_inner=False)
wall = solid.translate([-alignment_offset[0],-alignment_offset[1]])(wafer_walls)
wall_2d = solid.projection()(wall)
r.render(wall,outfile=osp.join(base_path,"wall_open_duplicates_4x4_walls.stl"))

""" make outline"""
outline=solid.translate([-alignment_offset[0],-alignment_offset[1]])(walls)
outline = solid.projection()(outline)

"""Make multi version"""
#channels
open_duplicates_4mm_4x4_bottom = make_unit_array(channels_many_single,dims,grid_size, dxf=True, alignment = "full",units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
#add outline
open_duplicates_4mm_4x4_bottom = solid.union()(open_duplicates_4mm_4x4_bottom,outline)
#wells and chambers
open_duplicates_4mm_4x4_top = make_unit_array(chamber_wells_many_single,dims,grid_size, dxf=True, alignment = "hollow",units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
#both layers together
open_duplicates_4mm_4x4_aligned = solid.union()(open_duplicates_4mm_4x4_top,open_duplicates_4mm_4x4_bottom)

"""put features in mask with a wafer outline"""
open_duplicates_4mm_4x4_bottom_final = add_wafer_to_mask(wafer_size,wafer_flat_len,open_duplicates_4mm_4x4_bottom,grid_size,dims,wafer_line_thickness=wafer_line_thickness,outer_mask_thickness=outer_mask_thickness,alignment_offset=alignment_offset)
save_model(open_duplicates_4mm_4x4_bottom_final,base_path,"open_duplicates_4mm_4x4_bottom")
open_duplicates_4mm_4x4_top_final = add_wafer_to_mask(wafer_size,wafer_flat_len,open_duplicates_4mm_4x4_top,grid_size,dims,wafer_line_thickness=wafer_line_thickness,outer_mask_thickness=outer_mask_thickness,alignment_offset=alignment_offset)
save_model(open_duplicates_4mm_4x4_top_final,base_path,"open_duplicates_4mm_4x4_top")
open_duplicates_4mm_4x4_aligned_final = add_wafer_to_mask(wafer_size,wafer_flat_len,open_duplicates_4mm_4x4_aligned,grid_size,dims,wafer_line_thickness=wafer_line_thickness,outer_mask_thickness=outer_mask_thickness,alignment_offset=alignment_offset)
save_model(open_duplicates_4mm_4x4_aligned_final,base_path,"open_duplicates_4mm_4x4_aligned")

"""Overlay walls and device"""
wall_and_devices = solid.union()(wall_2d,open_duplicates_4mm_4x4_bottom_final)
save_model(wall_and_devices, base_path,"wall_open_chamber_4x4_top")

"""make posts to make wells"""
platform_height=3
(wells_many_single,_),_,_=make_device(design=design,wells_pos=wells_pos,
                                              well_rad=well_rad,chan_l=chan_l,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                              rows=rows,columns=columns,casing_x=casing_x,casing_y=casing_y,chamber_len_until=chamber_len_until,rotate_units=0,
                                              alignment=None)
open_duplicates_4x4_wells = make_unit_array(wells_many_single,dims,grid_size, dxf=True, alignment = None,units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
posts = make_posts(open_duplicates_4x4_wells,2)
#
walls = solid.translate([-alignment_offset[0],-alignment_offset[1]])(walls)
posts_platform=solid.hull()(walls)
posts_platform=solid.projection()(posts_platform)
posts_platform=solid.linear_extrude(height=platform_height)(posts_platform)
posts = solid.translate([0,0,platform_height])(posts)
posts = solid.union()(posts_platform,posts)
save_model(posts,base_path,"open_duplicates_4mm_4x4_wells",dxf=False)


"""make posts to make wells"""
(wells_many_single,_),_,_=make_device(design=design,wells_pos=wells_pos,
                                              well_rad=well_rad,chan_l=chan_l,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                              rows=rows,columns=columns,casing_x=casing_x,casing_y=casing_y,chamber_len_until=chamber_len_until,rotate_units=0,
                                              alignment=None,chamber_width=chamber_width)
open_duplicates_4x4_wells = make_unit_array(wells_many_single,dims,[4,4], dxf=True, alignment = None,units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
posts = make_posts(open_duplicates_4x4_wells,1)

wafer_holder = make_wafer_empty(wafer_size,wafer_flat_len,wafer_thickness,margin,notch_len=notch_len,notch_height=notch_height,oversize=oversize)
wafer_holder = solid.translate([grid_size[1]*dims[1]/2.0,grid_size[0]*dims[0]/2.0])(wafer_holder)
wafer_holder=solid.translate([-alignment_offset[0],-alignment_offset[1]])(wafer_holder)
save_model(wafer_holder,base_path,"wafer_holder",dxf=False)


wells = solid.translate([0,0,wafer_thickness])(posts)
save_model(wells,base_path,"open_duplicates_4mm_4x4_wells",dxf=False)
wafer_holder_wells = solid.union()(wafer_holder,wells)
save_model(wafer_holder_wells,base_path,"open_duplicates_4mm_4x4_wafer_holder_wells",dxf=False)

""" print test"""
grid_size = [2,2]
open_duplicates_4x4_wells = make_unit_array(wells_many_single,dims,grid_size, dxf=True, alignment = None,units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
posts = make_posts(open_duplicates_4x4_wells,1)

wafer_holder = make_wafer_empty(wafer_size,wafer_flat_len,wafer_thickness,margin,notch_len=notch_len,notch_height=notch_height,oversize=oversize)
wafer_holder = solid.translate([grid_size[1]*dims[1]/2.0,grid_size[0]*dims[0]/2.0])(wafer_holder)
wafer_holder=solid.translate([-alignment_offset[0],-alignment_offset[1]])(wafer_holder)
save_model(wafer_holder,base_path,"wafer_holder",dxf=False)


wells = solid.translate([0,0,wafer_thickness])(posts)
save_model(wells,base_path,"open_duplicates_4mm_2x2_wells",dxf=False)

wafer_calibration_print=wafer_print_calibration(wafer_size,1,0.5,wafer_thickness)
save_model(wafer_calibration_print,base_path,"4inch_wafer_print_test",dxf=False)
