from make_device import *
#make 96-well version of device with one mask
_,_,(open_chamber,_) = make_open_chamber(wells_pos=wells_pos_from_center_2(2),well_rad=1.5, chan_l=1, chan_w=0.01, chan_gap=0.02, num_chans=60,
                                         rows=6,columns=8,casing_x=9,casing_y=4.5,chamber_len_until=1, rotate_units=0,alignment=None)
file_path="./designs/open_chamber/device_96_well_3mm_diameter.scad"
solid.scad_render_to_file(open_chamber,file_path)
to_dxf(file_path)

#rotated version of 96-well
_,_,(open_chamber,_) = make_open_chamber(wells_pos=wells_pos_from_center_2(2),well_rad=1.5, chan_l=1, chan_w=0.01, chan_gap=0.02, num_chans=60,
                                         rows=12,columns=4,casing_x=4.5,casing_y=9,chamber_len_until=1, rotate_units=90,alignment=None)
file_path="./designs/open_chamber/device_96_well_3mm_diameter_rotated.scad"
solid.scad_render_to_file(open_chamber,file_path)
to_dxf(file_path)
