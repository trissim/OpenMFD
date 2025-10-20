from make_device import *
#pair of device for 12 well plate
#make pair of device to fit in one 12 well plate well
base_path="./designs/open_chamber/gradient_layout/"
base_name="closed_gradient_single_device"
well_gap=6.36
well_rad=6.94/2.0
chan_l=well_gap
chan_gap=0.01
chan_w=0.01
num_chans=int((well_rad/1.5)/(chan_gap+chan_w))
oligo_channel_width=0.1
_,_,(open_chamber,_)= make_open_chamber(wells_pos=wells_pos_from_center_2(well_gap),
                                        well_rad=well_rad,chan_l=chan_l*0.9,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                        rows=1,columns=1,casing_x=0,casing_y=0,chamber_len_until=chan_l,
                                        rotate_units=0,alignment=None)

open_chamber2=solid.rotate([0,0,90])(open_chamber)
connected_chambers=solid.union()(open_chamber,open_chamber2)
width_all_channels=num_chans*chan_w+(num_chans-1)*chan_gap
common_area = solid.square([width_all_channels,width_all_channels],center=True)()
connected_chambers = solid.union()(common_area,connected_chambers)

connected_chambers=solid.rotate([0,0,45])(connected_chambers)
dxf_path=osp.join(base_path,"devices_"+base_name+".scad")
solid.scad_render_to_file(connected_chambers,osp.join(dxf_path))
to_dxf(dxf_path)


##dimensions of each cut-out device
dims = [9*2, 9*2, 0]
##number of devices
grid_size = [6,4]
base_name="closed_gradient_multi_device"
##make array of all the individual pairs of devices
device_array = make_unit_array(connected_chambers,dims,grid_size, dxf=True, alignment = None)
devices_dxf_path=osp.join(base_path,"devices_"+base_name+".scad")
solid.scad_render_to_file(device_array,devices_dxf_path)
to_dxf(devices_dxf_path)
