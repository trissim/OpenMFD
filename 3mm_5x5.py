from make_device import *
#pair of device for 12 well plate
#make pair of device to fit in one 12 well plate well
_,_,(open_chamber,_)= make_open_chamber(wells_pos=wells_pos_from_center_2(2),
                                        well_rad=1.5,chan_l=1,chan_w=0.01,chan_gap=0.02,num_chans=60,
                                        rows=1,columns=2,casing_x=12,casing_y=5,chamber_len_until=1,
                                        rotate_units=0,alignment=None)
#dimensions of each cut-out device
dims = [14, 14, 0]
#number of devices
grid_size = [5,5]
#height of 3d printed walls
wall_height=10
#thickness of 3d printed walls
wall_thickness=2
#diameter of wafer in mm
wafer_size=101.4
base_path="./designs/open_chamber/3mm_pairs_5x5"
base_name="3mm_pairs_5x5"

#make array of all the individual pairs of devices
open_chamber_5x5_duplicates = make_unit_array(open_chamber,dims,grid_size, dxf=True, alignment = None)
#translate back since unit array is already translated by the offset in the make_open_chamber functions call
open_chamber_5x5_duplicates = solid.translate([-6,-5,0])(open_chamber_5x5_duplicates)
devices_dxf_path=osp.join(base_path,"devices_"+base_name+".scad")
solid.scad_render_to_file(open_chamber_5x5_duplicates,devices_dxf_path)
to_dxf(devices_dxf_path)

wall = make_walls(wafer_size,wall_thickness,grid_size,dims,height=wall_height,segments=256)
wall_2d = solid.projection()(wall)
wall_path=osp.join(base_path,"wall_"+base_name+".scad")
solid.scad_render_to_file(wall,wall_path)
r.render(wall, outfile=wall_path.replace("scad","stl"))

wall_and_devices = solid.union()(wall_2d,open_chamber_5x5_duplicates)
wall_and_devices_path=osp.join(base_path,"wall_and_devices_"+base_name+".scad")
solid.scad_render_to_file(wall_and_devices,wall_and_devices_path)
to_dxf(wall_and_devices_path)
