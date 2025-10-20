import solid
import os.path as osp
import os 

def save_model(model,base_path,base_name):
    if not osp.exists(base_path):
        os.makedirs(base_path)
    scad_path=osp.join(base_path,base_name+".scad")
    solid.scad_render_to_file(model,osp.join(scad_path))


version="final_cnc"
#base_path="./designs/plasma_racks/4mm_well_0.5inch_diam_device_"+version+"/"
base_path="./orders/cnc_order_final_march_13th/"
base_name="single_adapter_0.5inch_"+version
adapter_diam=22
water_well_diam_out=20.5
water_well_diam_in=17
device_diam=15.5
water_well_height=4
adapter_height=5
floor_thickness=1

#floor
floor = solid.cylinder(r=adapter_diam/2.0, h=floor_thickness, segments=64, center = True)
floor_hole = solid.cylinder(r=device_diam/2.0, h=floor_thickness, segments=64, center = True)
floor = solid.difference()(floor,floor_hole)
floor = solid.translate([0,0,floor_thickness/2.0])(floor)


#plate wells
well = solid.cylinder(r=adapter_diam/2.0, h=adapter_height, segments=64, center = True)
well = solid.translate([0,0,adapter_height/2.0+floor_thickness])(well)
well_inner = solid.cylinder(r=water_well_diam_out/2.0, h=adapter_height, segments=64, center = True)
well_inner = solid.translate([0,0,adapter_height/2.0+floor_thickness])(well_inner)
well = solid.difference()(well,well_inner)


##water wells
water_well_out = solid.cylinder(r=water_well_diam_in/2.0, h=water_well_height, segments=64, center = True)
water_well_out = solid.translate([0,0,water_well_height/2.0+floor_thickness])(water_well_out)
water_well_in = solid.cylinder(r=device_diam/2.0, h=water_well_height, segments=64, center = True)
water_well_in = solid.translate([0,0,water_well_height/2.0+floor_thickness])(water_well_in)
water_well=solid.difference()(water_well_out,water_well_in)

adapter= solid.union()(floor,well,water_well)


save_model(adapter,base_path,base_name)
