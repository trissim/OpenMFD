import argparse
def read_gcode(gcode_file):
    with open(gcode_file) as f:
            lines = f.readlines()
    return lines

def delete_offset_layer(gcode_lines):
    end_offset_index = gcode_lines.index("M600\n")
    gcode_lines[end_offset_index]=";M600\n"
    start_offset_index=None
    for i,line in enumerate(gcode_lines):
        if "; printing object" in line:
            start_offset_index=i
            break
    gcode_lines=gcode_lines[0:start_offset_index]+gcode_lines[end_offset_index:]
    new_end_offset_index = gcode_lines.index(";M600\n")
    return gcode_lines,new_end_offset_index

def get_pause_lines():
    return [';pause\n','G28 X Y\n', 'G1 Z100\n', 'M25\n']

def get_purge_lines(gcode_lines):
    begin_purge_line = gcode_lines.index("G80 ; mesh bed leveling\n")+1
    end_purge_line = None
    for i in range(begin_purge_line, len(gcode_lines),1):
        if len(gcode_lines[i].strip()) == 0:
            end_purge_line = i
            break
    purge_lines = gcode_lines[begin_purge_line:end_purge_line]
    set_y_pos_line = purge_lines[1].replace("Y-3","Y2")
    purge_lines[1] = set_y_pos_line
    return purge_lines

def insert_lines(gcode_lines,lines,insert_line):
    gcode_lines = gcode_lines[0:insert_line+1]+lines+gcode_lines[insert_line+1:]
    end_insert_line = insert_line+len(lines)
    return gcode_lines,end_insert_line

def write_modified_file(path,gcode_lines):
    path = path.replace(".gcode", "_edited.gcode")
    with open(path, 'w') as f:
        for line in gcode_lines:
            f.write("%s\n" % line)

def parse_args():
    parser = argparse.ArgumentParser()
    # Required positional argument
    parser.add_argument("gcode", help="gcode to edit")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    path = args.gcode
    gcode_lines = read_gcode(path)
    purge_lines = get_purge_lines(gcode_lines)
    pause_lines = get_pause_lines()
    gcode_lines,end_offset_index = delete_offset_layer(gcode_lines)
    gcode_lines,end_pause_line = insert_lines(gcode_lines,pause_lines,end_offset_index)
    gcode_lines,end_purge_line = insert_lines(gcode_lines,purge_lines,end_pause_line)
    gcode_lines,end_upline = insert_lines(gcode_lines,['G1 Z.5 F720\n'],end_purge_line)
    write_modified_file(path,gcode_lines)


if __name__ == "__main__":
    main()
