from make_device import *
from functools import partial
base_path="./designs/open_chamber/2compartment_duplicates_4x4_refactored_inserts_v9_200um/"
design = "open"
wells_pos=3
well_rad=2
rows=1
columns=2
casing_x=12
casing_y=6

chan_gap=0.03
chan_w=0.01
chan_l=0.2
chan_l_extra=3
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

#well_inserts
degrees_out=12
degrees_in=35
insert_height=4
insert_height_in=0.40
taper_len_out_extra=0.1
taper_len_in_extra=0.95
pin_height=0.06
pin_inner_height=2
taper_height=0.5
degrees_taper=45
chamber_hole_dims=(2,2)
pin_dims=(1.9,1.9)
pin_dims_outer=(1.9,1.9)
insert_pin_offset=-0.5

#tip rack
rack_x=wafer_size
rack_y=wafer_size*1.3
rack_thickness=5
bolt_width=8.5
tip_rad=6.7/2

"""MAKE SINGLE UNIT"""
#chamber/well
make_chambers = partial(make_device,design=design,wells_pos=wells_pos,
                                         chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                         rows=rows,columns=columns,casing_x=casing_x,casing_y=casing_y,chamber_len_until=chamber_len_until,rotate_units=0,
                                              alignment=None,chamber_width=chamber_width)
(chamber_wells_many_single,_),_,_ = make_chambers(well_rad=well_rad,chan_l=chan_l,chamber_width=chamber_width,add_chambers=True)

#microchannels
_,(channels_many_single,_),_ = make_device(design=design,wells_pos=wells_pos,
                                        well_rad=well_rad,chan_l=chan_l*4,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                        rows=rows,columns=columns,casing_x=casing_x,casing_y=casing_y,chamber_len_until=chamber_len_until,rotate_units=0,
                                              alignment=None,chamber_width=chamber_width)
#insert holes
make_chamber_insert_holes = partial(make_device,design=design,wells_pos=wells_pos+insert_pin_offset,
                                              chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                              rows=rows,columns=columns,casing_x=casing_x,casing_y=casing_y,chamber_len_until=chamber_len_until,rotate_units=0,
                                              alignment=None)
(chamber_insert_holes,_),_,_ = make_chamber_insert_holes(well_rad=chamber_hole_dims,chan_l=chan_l,chamber_width=chamber_width,add_chambers=False)

chamber_wells_many_single=solid.difference()(chamber_wells_many_single,chamber_insert_holes)
aligned= solid.union()(chamber_wells_many_single,channels_many_single)

"""SAVE FEATURES TOP AND BOTTOM LAYERS"""
save_model(channels_many_single,base_path,"open_duplicates_4mm_bottom")
save_model(chamber_wells_many_single,base_path,"open_duplicates_4mm_top")
save_model(aligned,base_path,"open_duplicates_4mm_aligned")


"""MAKE WALL"""
walls,wafer_wall,wafer_walls,= make_walls(wafer_size,wall_thickness,grid_size,dims,height=wall_height,segments=256,make_inner=False)
r.render(wafer_walls,outfile=osp.join(base_path,"wall_open_duplicates_4x4_walls.stl"))


"""MAKE OUTLINE FOR ALL DEVICES"""
outline = solid.translate([-alignment_offset[0],-alignment_offset[1]])(walls)
outline = solid.projection()(outline)


"""MAKE MULTI VERSION"""
#channels
open_duplicates_4mm_4x4_bottom = make_unit_array(channels_many_single,dims,grid_size, dxf=True, alignment = "full",units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
#add outline
open_duplicates_4mm_4x4_bottom = solid.union()(open_duplicates_4mm_4x4_bottom,outline)
#wells and chambers
open_duplicates_4mm_4x4_top = make_unit_array(chamber_wells_many_single,dims,grid_size, dxf=True, alignment = "hollow",units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
#both layers together
open_duplicates_4mm_4x4_aligned = solid.union()(open_duplicates_4mm_4x4_top,open_duplicates_4mm_4x4_bottom)
"""MAKE WALL"""
walls,wafer_wall,wafer_walls,= make_walls(wafer_size,wall_thickness,grid_size,dims,height=wall_height,segments=256,make_inner=False)
r.render(wafer_walls,outfile=osp.join(base_path,"wall_open_duplicates_4x4_walls.stl"))


"""PUT FEATURES IN MASK WITH A WAFER OUTLINE"""
#bottom layer
open_duplicates_4mm_4x4_bottom_final = add_wafer_to_mask(wafer_size,wafer_flat_len,open_duplicates_4mm_4x4_bottom,grid_size,dims,wafer_line_thickness=wafer_line_thickness,outer_mask_thickness=outer_mask_thickness,alignment_offset=alignment_offset)
#top layer
open_duplicates_4mm_4x4_top_final = add_wafer_to_mask(wafer_size,wafer_flat_len,open_duplicates_4mm_4x4_top,grid_size,dims,wafer_line_thickness=wafer_line_thickness,outer_mask_thickness=outer_mask_thickness,alignment_offset=alignment_offset)
#aligned
open_duplicates_4mm_4x4_aligned_final = add_wafer_to_mask(wafer_size,wafer_flat_len,open_duplicates_4mm_4x4_aligned,grid_size,dims,wafer_line_thickness=wafer_line_thickness,outer_mask_thickness=outer_mask_thickness,alignment_offset=alignment_offset)


"""SAVE MULTI VERSION"""
save_model(open_duplicates_4mm_4x4_bottom_final,base_path,"open_duplicates_4mm_4x4_bottom")
save_model(open_duplicates_4mm_4x4_top_final,base_path,"open_duplicates_4mm_4x4_top")
save_model(open_duplicates_4mm_4x4_aligned_final,base_path,"open_duplicates_4mm_4x4_aligned")


"""MAKE 3D PRINTED WELL FEATURES_V3"""
def make_well_insert(make_fun,degrees,height,add_chambers,taper_len_extra=0,well_rad=well_rad,chan_l=chan_l):
    taper_len = deg_taper_len(height,degrees)
    taper_len=taper_len+taper_len_extra
    chamber_width_edit = chamber_width
    chan_l_edit = chan_l+taper_len*2
    if not (type(well_rad) is tuple or type(well_rad) is list):
        chamber_width_edit = well_rad*2
        well_rad = well_rad-taper_len
    (inserts,_),_,_ = make_fun(well_rad=well_rad,chan_l=chan_l_edit,chamber_width=chamber_width_edit-taper_len*2,add_chambers=add_chambers)
    inserts = make_unit_array(inserts,dims,grid_size, dxf=True, alignment = None,units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
    if not degrees == 0:
        inserts = chamfer_extrude(height,degrees,segments=20)(inserts)
    else:
        inserts = solid.linear_extrude(height=height)(inserts)
    return inserts, well_rad, chan_l_edit

def make_well_insert_all(degrees_in,degrees_out,height_in,height_out):
    #make well inserts outer part
    open_duplicates_4x4_wells, well_rad_outer_top, chan_l_outer_top = make_well_insert(make_chambers,degrees_out,height_out,True,taper_len_extra=taper_len_out_extra,well_rad=well_rad)

    #make well inserts inner part
    open_duplicates_4x4_empty_top, _, _  = make_well_insert(make_chamber_insert_holes,degrees_in,height_in,False,taper_len_extra=taper_len_in_extra,well_rad=pin_dims)

    #taper off the top to reduce adhesion
    taper_top, _ , _ = make_well_insert(make_chambers,degrees_taper,taper_height,True,taper_len_extra=0,well_rad=well_rad_outer_top,chan_l = chan_l_outer_top)
    taper_top=solid.translate([0,0,height_out])(taper_top)
    save_model(taper_top,base_path,"taper_top",dxf=False)
    open_duplicates_4x4_wells = solid.union()(taper_top,open_duplicates_4x4_wells)


    open_duplicates_4x4_empty_top=solid.translate([0,0,-0.001])(open_duplicates_4x4_empty_top)
    open_duplicates_4x4_wells = solid.difference()(open_duplicates_4x4_wells,open_duplicates_4x4_empty_top)
    open_duplicates_4x4_wells=solid.translate([0,0,pin_height])(open_duplicates_4x4_wells)


    return open_duplicates_4x4_wells

open_duplicates_4x4_wells = make_well_insert_all(degrees_in, degrees_out,insert_height_in, insert_height)

#open_duplicates_4x4_wells = make_well_insert(degrees_in,taper_height,taper_len_extra=taper_len_out_extra)
save_model(open_duplicates_4x4_wells,base_path,"open_duplicates_4x4_wells_insert_pre",dxf=False)
#inserts_taper = make_well_insert(degrees_taper,taper_height,taper_len_extra=taper_len_out_extra)

#make pins for inserts
#make pin with dims pin_dims
(chamber_insert_holes,_),_,_ = make_device(design=design,wells_pos=wells_pos+insert_pin_offset,
                                              well_rad=pin_dims,chan_l=chan_l,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                              rows=rows,columns=columns,casing_x=casing_x,casing_y=casing_y,chamber_len_until=chamber_len_until,rotate_units=0,
                                              alignment=None,chamber_width=chamber_width,add_chambers=False)
#make pin 3D
chamber_insert_holes_extrude = solid.linear_extrude(height=pin_height+pin_inner_height)(chamber_insert_holes)
#tile pin with same pos as square hole on wafer
chamber_insert_holes_extrude_multi = make_unit_array(chamber_insert_holes_extrude,dims,grid_size, dxf=True, alignment = None,units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
open_duplicates_4x4_wells=solid.union()(open_duplicates_4x4_wells,chamber_insert_holes_extrude_multi)
save_model(open_duplicates_4x4_wells,base_path,"open_duplicates_4x4_wells_insert",dxf=False)

"""MAKE WAFER HOLDER"""
wafer_holder = make_wafer_empty(wafer_size,wafer_flat_len,wafer_thickness,margin,notch_len=notch_len,notch_height=notch_height,oversize=oversize)
wafer_holder = solid.translate([grid_size[1]*dims[1]/2.0,grid_size[0]*dims[0]/2.0])(wafer_holder)
wafer_holder=solid.translate([-alignment_offset[0],-alignment_offset[1]])(wafer_holder)
save_model(wafer_holder,base_path,"wafer_holder",dxf=False)

""" CREATE TIP RACK """
(wells,_),_,_=make_device(design=design,wells_pos=wells_pos,
                          well_rad=tip_rad,chan_l=chan_l,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                          rows=rows,columns=columns,casing_x=casing_x,casing_y=8,chamber_len_until=chamber_len_until,rotate_units=0,
                          alignment=None,chamber_width=chamber_width,add_chambers=False)
wells=make_unit_array(wells,dims,grid_size, dxf=True, alignment=None, units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
rack, rack_support = make_rack(wells,dims,grid_size,alignment_offset,rack_x,rack_y,rack_thickness,bolt_width)
save_model(rack,base_path,"rack",dxf=False)
save_model(rack_support,base_path,"rack_support",dxf=False)

"""CREATE PILLAR ARRAY"""
degrees=28
pillar_height=50
taper_len = deg_taper_len(insert_height,degrees)
#taper_len=insert_height*math.tan(math.radians(degrees))
(wells,_),_,_=make_device(design=design,wells_pos=wells_pos,
                                              well_rad=well_rad-taper_len,chan_l=chan_l+taper_len*2,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                              rows=rows,columns=columns,casing_x=casing_x,casing_y=casing_y,chamber_len_until=chamber_len_until,rotate_units=0,
                                              alignment=None,chamber_width=chamber_width-taper_len*2)
wells=make_unit_array(wells,dims,grid_size, dxf=True, alignment=None, units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
pillars, rack_support = make_pillar(wells,dims,grid_size,alignment_offset,rack_x,rack_x,pillar_height,rack_thickness,bolt_width,bolt_position_corner=1)
save_model(rack_support,base_path,"pillar_rack_support",dxf=False)
save_model(pillars,base_path,"pillar_rack",dxf=False)
