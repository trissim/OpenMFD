from make_device import *
#pair of device for 12 well plate
#make pair of device to fit in one 12 well plate well
base_path="./designs/open_chamber/3compartment/"
base_name="3compartment_single_device"
well_gap=4.5
well_rad=6.94/2.0
chan_l=(well_gap-well_rad)*2.0
chan_gap=0.01
chan_w=0.01
num_chans=int(well_rad/(chan_gap+chan_w))
num_connected_wells=2
add_wells=True
add_chambers=True
add_channels=True
#dimensions of each cut-out device
dims = [9*3, 9, 0]
#number of devices
grid_size = [4,8]

#make bottom layer
base_name="3compartment_single_device_bottom"
_,_,(open_chamber,_)= make_open_chamber(wells_pos=wells_pos_from_center_2(well_gap),
                                        well_rad=well_rad,chan_l=chan_l,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                        rows=1,columns=1,casing_x=0,casing_y=0,chamber_len_until=chan_l,
                                        rotate_units=0,alignment=None,add_channels=add_channels,add_wells=add_wells,
                                        add_chambers=add_chambers)
open_chamber=solid.translate([well_gap,0,0])(open_chamber)
connected_chambers = []
num_connected_wells=float(num_connected_wells)
for i in range(int(num_connected_wells)):
    connected_chambers.append(solid.rotate([0,0,(360.0/num_connected_wells)*i])(open_chamber))
connected_chambers = solid.union()(*connected_chambers)
dxf_path=osp.join(base_path,"devices_"+base_name+".scad")
solid.scad_render_to_file(connected_chambers,osp.join(dxf_path))
to_dxf(dxf_path)
#make array of all the individual pairs of devices
base_name="3compartment_multi_device_bottom"
device_array = make_unit_array(connected_chambers,dims,grid_size, dxf=True, alignment = None)
#translate back since unit array is already translated by the offset in the make_open_chamber functions call
device_array = solid.translate([-6,-5,0])(device_array)
devices_dxf_path=osp.join(base_path,"devices_"+base_name+".scad")
solid.scad_render_to_file(device_array,devices_dxf_path)
to_dxf(devices_dxf_path)

#make top layer
add_channels=False
_,_,(open_chamber,_)= make_open_chamber(wells_pos=wells_pos_from_center_2(well_gap),
                                        well_rad=well_rad,chan_l=chan_l,chan_w=chan_w,chan_gap=chan_gap,num_chans=num_chans,
                                        rows=1,columns=1,casing_x=0,casing_y=0,chamber_len_until=chan_l,
                                        rotate_units=0,alignment=None,add_channels=add_channels,add_wells=add_wells,
                                        add_chambers=add_chambers)
base_name="3compartment_single_device_top"
open_chamber=solid.translate([well_gap,0,0])(open_chamber)
connected_chambers = []
num_connected_wells=float(num_connected_wells)
for i in range(int(num_connected_wells)):
    connected_chambers.append(solid.rotate([0,0,(360.0/num_connected_wells)*i])(open_chamber))
connected_chambers = solid.union()(*connected_chambers)
dxf_path=osp.join(base_path,"devices_"+base_name+".scad")
solid.scad_render_to_file(connected_chambers,osp.join(dxf_path))
to_dxf(dxf_path)
#make array of all the individual pairs of devices
base_name="3compartment_multi_device_top"
device_array = make_unit_array(connected_chambers,dims,grid_size, dxf=True, alignment = None)
#translate back since unit array is already translated by the offset in the make_open_chamber functions call
device_array = solid.translate([-6,-5,0])(device_array)
devices_dxf_path=osp.join(base_path,"devices_"+base_name+".scad")
solid.scad_render_to_file(device_array,devices_dxf_path)
to_dxf(devices_dxf_path)


#dimensions of each cut-out device
dims = [9*3, 9, 0]
#number of devices
grid_size = [4,8]
#height of 3d printed walls
#wall_height=10
#thickness of 3d printed walls
#wall_thickness=2
#diameter of wafer in mm
#wafer_size=101.4
base_name="3compartment_multi_device_top"


#adjacent_devices=[]
#adjacent_devices.append(device_array)
#adjacent_devices.append(solid.translate([9*1,9*2,0])(device_array))
#adjacent_devices.append(solid.translate([9*3,9*1,0])(device_array))
#adjacent_devices.append(solid.translate([9*2,-9*1,0])(device_array))
#adjacent_devices=solid.union()(*adjacent_devices)
#end_device=[]
#end_device.append(adjacent_devices)
#end_device.append(solid.translate([9*5,0,0])(adjacent_devices))
##end_device.append(solid.translate([9*5-2,-9,0])(connected_chambers))
#end_device=solid.union()(*end_device)
#adjacent_devices=end_device
#device_array=adjacent_devices
#
#
#
devices_dxf_path=osp.join(base_path,"devices_"+base_name+".scad")
solid.scad_render_to_file(device_array,devices_dxf_path)
to_dxf(devices_dxf_path)
#
#wall = make_walls(wafer_size,wall_thickness,grid_size,dims,height=wall_height,segments=256)
#wall_2d = solid.projection()(wall)
#wall_path=osp.join(base_path,"wall_"+base_name+".scad")
#solid.scad_render_to_file(wall,wall_path)
#r.render(wall, outfile=wall_path.replace("scad","stl"))
#
#wall_and_devices = solid.union()(wall_2d,device_array)
#wall_and_devices_path=osp.join(base_path,"wall_and_devices_"+base_name+".scad")
#solid.scad_render_to_file(wall_and_devices,wall_and_devices_path)
#to_dxf(wall_and_devices_path)

