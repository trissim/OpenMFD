from make_device import *
#pair of device for 12 well plate
#make pair of device to fit in one 12 well plate well
base_path="./designs/open_chamber/2compartment_96well_v2/"
well_gap=4.5
well_rad=6.94/2.0
chan_l=(well_gap-well_rad)
chan_gap=0.03
chan_w=0.01
#num_chans=int((well_rad*.75)/(chan_gap+chan_w))
#num_chans=int((well_rad*2*0.75)/(chan_gap+chan_w))
num_chans=int(well_rad/(chan_gap+chan_w))
add_wells=True
add_chambers=True
add_channels=True
#dimensions of each cut-out device
dims = [9*2, 9, 0]
#number of devices
grid_size = [6,8]
units_from_center=(2,2)
len_until=(well_gap)
#height of 3d printed walls
wall_height=10
#thickness of 3d printed walls
wall_thickness=1

wafer_size=150
wafer_flat_len=57.5
wafer_thickness=0.620
outer_mask_thickness=3
wafer_line_thickness=0.3

#wafer holder
margin=3
notch_len=10
notch_height=2
oversize=1.0025



"""
MAKE SINGLE DEVICE
"""
##make bottom layer

_,(channels_single,_),_= make_open_chamber(wells_pos=wells_pos_from_center_2(well_gap),
                                        well_rad=well_rad,chan_l=chan_l,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                        rows=1,columns=2,casing_x=dims[0],casing_y=dims[1],chamber_len_until=len_until,
                                        rotate_units=0,add_channels=add_channels,add_wells=add_wells,
                                        add_chambers=add_chambers,alignment=None,units_from_center=units_from_center,chamber_width=well_rad*2)

(chambers_wells_single,_),(_,_),_= make_open_chamber(wells_pos=wells_pos_from_center_2(well_gap),
                                        well_rad=well_rad,chan_l=chan_l,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                        rows=1,columns=2,casing_x=dims[0],casing_y=dims[1],chamber_len_until=len_until,
                                        rotate_units=0,add_channels=add_channels,add_wells=add_wells,
                                        add_chambers=add_chambers,alignment=None,units_from_center=units_from_center,chamber_width=well_rad*2)

save_model(channels_single,base_path,"2compartment_single_device_bottom")
save_model(chambers_wells_single,base_path,"2compartment_single_device_top")
save_model(solid.union()(channels_single,chambers_wells_single),base_path,"2compartment_single_device_aligned")

"""
MAKE 96WELL DEVICE
"""


"""Make wall"""
#alignment_offset=[(dims[0]-casing_x*rows)/2.0,(dims[1]-casing_y*columns)/2]
#alignment_offset=[(dims[0]-dims[0]*grid_size[0])/2.0,(dims[1]-dims[1]*grid_size[1])/2]
#alignment_offset=[-dims[0]*grid_size[0]/2.0,-dims[1]*grid_size[1]/2]
alignment_offset=[9,9]
alignment_offset=[0,0]
walls,wafer_wall,wafer_walls,= make_walls(wafer_size,wall_thickness,grid_size,dims,height=wall_height,segments=256,make_inner=False,padx=9,pady=9)
wall = solid.translate([-alignment_offset[0],-alignment_offset[1]])(wafer_walls)
wall_2d = solid.projection()(wall)
r.render(wall,outfile=osp.join(base_path,"wall_2compartment_multi.stl"))

""" make outline"""
outline=solid.translate([-alignment_offset[0],-alignment_offset[1]])(walls)
outline = solid.projection()(outline)

"""make all channels"""
_,(channels_multi,_),_= make_open_chamber(wells_pos=wells_pos_from_center_2(well_gap),
                                        well_rad=well_rad,chan_l=4,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                        rows=grid_size[0],columns=grid_size[1],casing_x=dims[0],casing_y=dims[1],chamber_len_until=len_until,
                                        rotate_units=0,add_channels=add_channels,add_wells=add_wells,
                                        add_chambers=add_chambers,alignment=True,units_from_center=units_from_center,chamber_width=well_rad*2)

"""add outline to channel mask"""
channels_multi = solid.union()(channels_multi,outline)

"""make all wells"""
(chambers_wells_multi,_),(_,_),_= make_open_chamber(wells_pos=wells_pos_from_center_2(well_gap),
                                        well_rad=well_rad,chan_l=chan_l,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                        rows=grid_size[0],columns=grid_size[1],casing_x=dims[0],casing_y=dims[1],chamber_len_until=len_until,
                                        rotate_units=0,add_channels=add_channels,add_wells=add_wells,
                                        add_chambers=add_chambers,alignment=True,units_from_center=units_from_center,chamber_width=well_rad*2)
multi_aligned=solid.union()(channels_multi,chambers_wells_multi)


channels_multi = add_wafer_to_mask(wafer_size,wafer_flat_len,channels_multi,grid_size,dims,alignment_offset=alignment_offset)
chambers_wells_multi = add_wafer_to_mask(wafer_size,wafer_flat_len,chambers_wells_multi,grid_size,dims,alignment_offset=alignment_offset)
multi_aligned = add_wafer_to_mask(wafer_size,wafer_flat_len,multi_aligned,grid_size,dims,alignment_offset=alignment_offset)

save_model(channels_multi,base_path,"2compartment_multi_device_bottom")
save_model(chambers_wells_multi,base_path,"2compartment_multi_device_top")
save_model(multi_aligned,base_path,"2compartment_multi_device_aligned")


"""make posts"""
(chambers_wells_multi,_),(_,_),_= make_open_chamber(wells_pos=wells_pos_from_center_2(well_gap),
                                        well_rad=well_rad,chan_l=chan_l,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                        rows=grid_size[0],columns=grid_size[1],casing_x=dims[0],casing_y=dims[1],chamber_len_until=len_until,
                                        rotate_units=0,add_channels=add_channels,add_wells=add_wells,
                                        add_chambers=add_chambers,alignment=None,units_from_center=units_from_center,chamber_width=well_rad*2)

posts = make_posts(chambers_wells_multi,50)
save_model(posts,base_path,"2compartment_multi_device_posts",dxf=False)

"""make wafer_holder"""
wafer_holder = make_wafer_empty(wafer_size,wafer_flat_len,wafer_thickness,margin,notch_len=notch_len,notch_height=notch_height,oversize=oversize)
wafer_holder = solid.translate([grid_size[1]*dims[1]/2.0,grid_size[0]*dims[0]/2.0])(wafer_holder)
wafer_holder=solid.translate([-alignment_offset[0],-alignment_offset[1]])(wafer_holder)
save_model(wafer_holder,base_path,"wafer_holder",dxf=False)
wafer_holder=solid.projection()(wafer_holder)
save_model(wafer_holder,base_path,"wafer_holder_2d",dxf=True)
