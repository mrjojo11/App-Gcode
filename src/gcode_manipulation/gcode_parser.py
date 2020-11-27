from gcode_manipulation.gcode import GCode

class GCode_Parser:

    def __init__(self, line_list):
        self.line_list = line_list

        self.gcode = None

    def create_gcode(self):
        new_gcode = GCode()
        new_gcode.main_body = self.line_list
        self.gcode = new_gcode

        self.analyze_gcode()

        return self.gcode

    def analyze_gcode(self):
        self.split_gcode()
        self.clean_gcode()

        self.gcode = self.find_indexes()

    def split_gcode(self):

        start_gcode = []
        main_gcode = []
        main_gcode_to_be_flatten = []
        end_gcode = []

        before_layer_0 = True
        temp_list = []

        for line in self.gcode.main_body:
            if ";LAYER:0" in line:
                before_layer_0 = False
            if before_layer_0 is True:
                start_gcode.append(line)
            elif ";TIME_ELAPSED:" in line:
                temp_list.append(line)
                main_gcode_to_be_flatten.append(temp_list)
                temp_list = []
            else:
                temp_list.append(line)

        end_gcode = temp_list

        for sublist in main_gcode_to_be_flatten:
            for item in sublist:
                main_gcode.append(item)

        self.gcode.startup_code = start_gcode
        self.gcode.main_body = main_gcode
        self.gcode.shutdown_code = end_gcode

    def clean_gcode(self):

        start_cura_bol = True
        start_cura_list = []
        layer_count_list = []

        for line in self.gcode.startup_code:
            if start_cura_bol is True:
                start_cura_list.append(line)
                if ";Generated with" in line:
                    start_cura_bol = False
            if ";LAYER_COUNT" in line:
                layer_count_list.append(line)

        new_start_cura_list = []
        new_start_cura_list.append("M105")
        new_start_cura_list.append("M109 S0")
        new_start_cura_list.append("M82 ;absolute extrusion mode")
        new_start_cura_list.append("M302 P1")
        new_start_cura_list.append("M106 S0")
        new_start_cura_list.append("G92 E0")
        new_start_cura_list.append("G28")
        new_start_cura_list.append("G1 Z5.0 F3000")
        new_start_cura_list.append("G92 E0")
        new_start_cura_list.append("G92 E0")

        new_start = start_cura_list + layer_count_list + new_start_cura_list
        self.gcode.startup_code = new_start


        new_main = []
        for line in self.gcode.main_body:
            if "M140" not in line:
                new_main.append(line)
        self.gcode.main_body = new_main

        new_end = []
        new_end.append("M140 S0")
        new_end.append("G91")
        new_end.append("G1 Z1.1 F2400")
        new_end.append("G1 X5 Y5 F3000")
        new_end.append("G1 Z10")
        new_end.append("G90")
        new_end.append("G1 X0 Y220")
        new_end.append("M106 S0")
        new_end.append("M104 S0")
        new_end.append("M140 S0")
        new_end.append("M84 E X Y E")
        new_end.append("M302 P0")
        new_end.append("M82 ;absolute extrusion mode")

        for line in self.gcode.shutdown_code:
            if ";SETTING_3" in line:
                new_end.append(line)

        self.gcode.shutdown_code = new_end


    def find_indexes(self):

        layer_list = []
        time_elapsed_list =[]
        movements_per_layer_list = []

        current_layer = -1
        movement_commands = ["G0", "G1", "G2", "G3", "G5"]
        largest_extrusion_value = 0

        for index, line in enumerate(self.gcode.main_body):
            if ";LAYER:" in line:
                layer_list.append(index)
                current_layer += 1
                movements_per_layer_list.append(0)
            elif any(x in line for x in movement_commands):
                movements_per_layer_list[current_layer] += 1

                split_line = line.split()
                for word in split_line:
                    if "E" in word:
                        extrusion_value = float(word[1:])
                        if extrusion_value > largest_extrusion_value:
                            largest_extrusion_value = extrusion_value

            elif ";TIME_ELAPSED:" in line:
                time_elapsed_list.append(index)

        self.gcode.layer_index_list = layer_list
        self.gcode.time_elapsed_index_list = time_elapsed_list
        self.gcode.movements_per_layer_list = movements_per_layer_list

        self.gcode.amount_layers = len(layer_list)
        self.gcode.largest_extrusion_value = largest_extrusion_value

        return self.gcode

    def set_gcode(self, gcode: GCode):
        self.gcode = gcode
