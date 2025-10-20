import math
wafer_size=100
su8_thickness=1
su8_perc=0.52

volume=math.pi*((wafer_size/2)**2)/su8_perc
print(volume/1000)
