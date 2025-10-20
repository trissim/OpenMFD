from make_device import *
from functools import partial
import numpy as np
import pudb
version=26
base_path="./designs/open_chamber/2_compartment_4x4_300um_suex100_v"+str(version)+"/"
device_name="2_compartment_4x4_300um_suex100_v"+str(version)

design = "open"
cure_temp = 0
scale_percent, cure_text = scale_percent_pdms_heat_shrinkage(cure_temp)
wells_pos=3
well_rad=2
chan_gap=0.03
chan_w=0.01
chan_l=0.3
chan_l_extra=6
num_chans=int(well_rad/(chan_gap+chan_w))
chamber_len_until=wells_pos
chamber_width=well_rad*2

rows=1
columns=2
casing_x=12
casing_y=6


#multi device parameters
grid_size = [4,4]
dims = [17.5, 17.5, 0]
alignment_offset=[(dims[0]-casing_x*rows)/2.0,(dims[1]-casing_y*columns)/2]
units_from_center=(2.3,2.3)
alignment_mark_size=1

#device outline
glass_size=[110,74]
glass_error=4
wall_thickness=7
outline_alignment_thickness=1

wafer_size=100
wafer_flat_len=32.5
wafer_thickness=0.500
outer_mask_thickness=1
wafer_line_thickness=0.3
#height of 3d printed walls
wall_height=10
#thickness of 3d printed walls
#wall_thickness=1
wall_padx=0
wall_pady=0
#area to center device in


#wafer_holder
margin=3
notch_len=10
notch_height=2
oversize=1.0025

#well_inserts
degrees_out=16
degrees_in=35
insert_height=3.4
insert_height_in=0.40
taper_len_out_extra=0.250
taper_len_in_extra=0.91
pin_height=0.06
pin_inner_height=2
taper_height=0
degrees_taper=0
chamber_hole_dims=(2,2)
pin_dims=(1.85,1.85)
insert_pin_offset=-0.5
skirt_thickness1=.4
skirt_height1=0.660
skirt_empty1=0.3
skirt_thickness2=.4
skirt_height2=.04

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
                                        well_rad=well_rad,chan_l=chan_l+chan_l_extra,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
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
save_model(channels_many_single,base_path,device_name+"_single_bottom")
save_model(chamber_wells_many_single,base_path,device_name+"_single_top")
save_model(aligned,base_path,device_name+"_single_aligned")


"""MAKE WALL"""
walls,wafer_wall,wafer_walls,= make_walls(wafer_size,wall_thickness,grid_size,dims,height=wall_height,segments=256,make_inner=False,padx=wall_padx,pady=wall_pady)
r.render(wafer_walls,outfile=osp.join(base_path,"wall_single_"+device_name+".stl"))


"""MAKE OUTLINE FOR ALL DEVICES"""
#outline of wall to be glued
glass_size=np.array(glass_size)
outline=make_outline(glass_size-glass_error,wall_thickness,grid_size,dims,alignment_offset)
#make groove for alignment
outline_alignment_inner=glass_size-glass_error+wall_thickness/2.0-outline_alignment_thickness/2.0
outline_alignment=make_outline(outline_alignment_inner,outline_alignment_thickness,grid_size,dims,alignment_offset)
outline=solid.difference()(outline,outline_alignment)

"""MAKE CURE TEXT FOR MULTI VERSION"""
text1 = solid.text(cure_text,halign="center", valign="center",size = 2)
text2 = solid.text("Use 60mL of Sylgard 184 in 1:10 ratio",halign="center", valign="center",size = 2)
text = solid.union()(text1,solid.translate([0,-dims[1]/2])(text2))
text = solid.translate([alignment_offset[0],alignment_offset[1]])(text)
text = solid.translate([grid_size[0]*dims[0]/2.0,grid_size[1]*dims[1]/2.0])(text)
text = solid.translate([0,-(grid_size[1]+3)*dims[1]/2])(text)
"""MAKE MULTI VERSION"""
#channels
open_duplicates_4mm_4x4_bottom = make_unit_array(channels_many_single,dims,grid_size, dxf=True, alignment = "full",units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
#add cure text
open_duplicates_4mm_4x4_bottom=solid.union()(open_duplicates_4mm_4x4_bottom,text)
#wells and chambers
open_duplicates_4mm_4x4_top = make_unit_array(chamber_wells_many_single,dims,grid_size, dxf=True, alignment = "hollow",units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)
#add outline to wells and chambers
open_duplicates_4mm_4x4_top = solid.union()(open_duplicates_4mm_4x4_top,outline)
#both layers together
open_duplicates_4mm_4x4_aligned = solid.union()(open_duplicates_4mm_4x4_top,open_duplicates_4mm_4x4_bottom)


open_duplicates_4mm_4x4_bottom=solid.scale([scale_percent,scale_percent])(open_duplicates_4mm_4x4_bottom)
open_duplicates_4mm_4x4_top=solid.scale([scale_percent,scale_percent])(open_duplicates_4mm_4x4_top)
open_duplicates_4mm_4x4_aligned=solid.scale([scale_percent,scale_percent])(open_duplicates_4mm_4x4_aligned)

"""SCALE FEATURES TO CURING TEMPERATURE SHRINKAGE"""


"""PUT FEATURES IN MASK WITH A WAFER OUTLINE"""
#bottom layer
open_duplicates_4mm_4x4_bottom_final = add_wafer_to_mask(wafer_size,wafer_flat_len,open_duplicates_4mm_4x4_bottom,grid_size,dims,wafer_line_thickness=wafer_line_thickness,outer_mask_thickness=outer_mask_thickness,alignment_offset=alignment_offset,shrinkage_scale=scale_percent)
#top layer
open_duplicates_4mm_4x4_top_final = add_wafer_to_mask(wafer_size,wafer_flat_len,open_duplicates_4mm_4x4_top,grid_size,dims,wafer_line_thickness=wafer_line_thickness,outer_mask_thickness=outer_mask_thickness,alignment_offset=alignment_offset,shrinkage_scale=scale_percent)
#aligned
open_duplicates_4mm_4x4_aligned_final = add_wafer_to_mask(wafer_size,wafer_flat_len,open_duplicates_4mm_4x4_aligned,grid_size,dims,wafer_line_thickness=wafer_line_thickness,outer_mask_thickness=outer_mask_thickness,alignment_offset=alignment_offset,shrinkage_scale=scale_percent)

"""SAVE MULTI VERSION"""
save_model(open_duplicates_4mm_4x4_bottom_final,base_path,device_name+"_bottom")
save_model(open_duplicates_4mm_4x4_top_final,base_path,device_name+"_top")
save_model(open_duplicates_4mm_4x4_aligned_final,base_path,device_name+"_aligned")


"""MAKE 3D PRINTED WELL FEATURES_V3"""
def make_well_insert(make_fun,degrees,height,add_chambers,taper_len_extra=0,well_rad=well_rad,chan_l=chan_l):
    taper_len = deg_taper_len(height,degrees)
    taper_len=taper_len+taper_len_extra
    chamber_width_edit = chamber_width
    chan_l_edit = chan_l+taper_len*2
    if not (type(well_rad) is tuple or type(well_rad) is list):
        chamber_width_edit = well_rad*2
        well_rad = well_rad-taper_len
    (inserts,_),_,_ = make_fun(well_rad=well_rad,chan_l=chan_l_edit,
                               chamber_width=chamber_width_edit-taper_len*2,
                               add_chambers=add_chambers)
    inserts = make_unit_array(inserts,dims,grid_size, dxf=True, alignment = None,
                              units_from_center=units_from_center,alignment_offset=alignment_offset,
                              alignment_mark_size=alignment_mark_size)
    if not degrees == 0:
        inserts = chamfer_extrude(height,degrees,segments=20)(inserts)
    else:
        inserts = solid.linear_extrude(height=height)(inserts)
    return inserts, well_rad, chan_l_edit

def make_well_insert_all(degrees_in,degrees_out,height_in,height_out,inner_well_rad,add_chambers=False):
    #make well inserts outer part
    open_duplicates_4x4_wells, well_rad_outer_top, chan_l_outer_top = make_well_insert(make_chambers,degrees_out,height_out,True,
                                                                                       taper_len_extra=taper_len_out_extra,well_rad=well_rad)

    #taper off the top to reduce adhesion
    taper_top, _ , _ = make_well_insert(make_chambers,degrees_taper,taper_height,True,
                                        taper_len_extra=0,well_rad=well_rad_outer_top,
                                        chan_l = chan_l_outer_top)
    taper_top=solid.translate([0,0,height_out])(taper_top)
    save_model(taper_top,base_path,"taper_top",dxf=False)
    open_duplicates_4x4_wells = solid.union()(taper_top,open_duplicates_4x4_wells)


    open_duplicates_4x4_wells=solid.translate([0,0,pin_height+skirt_height1+skirt_height2])(open_duplicates_4x4_wells)


    return open_duplicates_4x4_wells

all_well_inserts = make_well_insert_all(degrees_in, degrees_out,insert_height_in, insert_height,3,add_chambers=True)

#make skirt for inserts
outer_skirt=solid.projection()(all_well_inserts)
inner_skirt=solid.offset(delta=-skirt_thickness1)(outer_skirt)
skirt_multi1=solid.difference()(outer_skirt,inner_skirt)
skirt_multi1_1=solid.linear_extrude(height=skirt_height1)(skirt_multi1)
skirt_multi1_1=solid.translate([0,0,pin_height])(skirt_multi1_1)
skirt_multi1_2=solid.linear_extrude(height=skirt_empty1)(outer_skirt)
skirt_multi1_2=solid.translate([0,0,pin_height+(skirt_height1-skirt_empty1)])(skirt_multi1_2)
skirt_multi1=solid.union()(skirt_multi1_1,skirt_multi1_2)

#make skirt for inserts
outer_skirt=solid.projection()(all_well_inserts)
inner_skirt=solid.offset(delta=-skirt_thickness2)(outer_skirt)
skirt_multi2=solid.difference()(outer_skirt,inner_skirt)
skirt_multi2=solid.linear_extrude(height=skirt_height2)(skirt_multi2)
skirt_multi2=solid.translate([0,0,pin_height-skirt_height2])(skirt_multi2)

skirt_multi=solid.union()(skirt_multi1,skirt_multi2)
skirt_multi=solid.translate([0,0,skirt_height2])(skirt_multi)
#skirt_multi=skirt_multi1
#make pins for inserts
#make pin with dims pin_dims
(chamber_insert_holes,_), _ , _ =make_chamber_insert_holes(well_rad=pin_dims,chan_l=chan_l,chamber_width=chamber_width,add_chambers=False)
#make pin 3D
chamber_insert_holes_extrude = solid.linear_extrude(height=pin_height+skirt_height1+skirt_height2+pin_inner_height)(chamber_insert_holes)
#tile pin with same pos as square hole on wafer
chamber_insert_holes_extrude_multi = make_unit_array(chamber_insert_holes_extrude,dims,grid_size, dxf=True, alignment = None,units_from_center=units_from_center,alignment_offset=alignment_offset,alignment_mark_size=alignment_mark_size)


all_well_inserts=solid.union()(all_well_inserts,chamber_insert_holes_extrude_multi,skirt_multi)
all_well_inserts=solid.scale([scale_percent,scale_percent,1])(all_well_inserts)
save_model(all_well_inserts,base_path,device_name+"_wells_insert",dxf=False)
#inserts_flat = solid.projection()(all_well_inserts)
#save_model(inserts_flat,base_path,device_name+"_wells_inserts_flat",dxf=True)

wafer=solid.projection()(make_wafer(wafer_size,wafer_flat_len,wafer_thickness))
save_model(wafer,base_path,"wafer",dxf=True)
#r.render(wafer,outfile=osp.join(base_path,"wafer.scad"))
