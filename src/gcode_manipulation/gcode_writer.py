from gcode_manipulation.gcode import GCode
from gcode_manipulation.gcode_parser import GCode_Parser

class Gcode_Writer():

    def __init__(self):
        self.start_gcode = None
        self.end_gcode = None

    def add_information_text(self):

        new_start = []
        new_start.append("M117 Print is starting")
        for line in self.end_gcode.startup_code:
            new_start.append(line)
        self.end_gcode.startup_code = new_start

        new_main = []
        current_layer = 0
        current_move = 0

        movement_commands = ["G0", "G1", "G2", "G3", "G5"]

        for index, line in enumerate(self.end_gcode.main_body):
            if any(x in line for x in movement_commands):
                text = "M117 Mov " + str(current_move) + "/" + str(self.end_gcode.movements_per_layer_list[current_layer]) + " Lay " + str(current_layer + 1) + "/" + str(self.end_gcode.amount_layers)
                new_main.append(text)
                current_move += 1
            new_main.append(line)

            if index == self.end_gcode.time_elapsed_index_list[current_layer]:
                current_layer += 1
                current_move = 0

        self.end_gcode.main_body = new_main

        new_end = []
        new_end.append("M117 Print is winding down")
        for line in self.end_gcode.shutdown_code:
            new_end.append(line)
        self.end_gcode.shutdown_code = new_end

        return self.end_gcode


    def stop_each_layer(self):

        previous_index = 0
        last_index = len(self.start_gcode.main_body)

        gcode_list = []

        for layer_index in self.start_gcode.time_elapsed_index_list:

            for index in range(previous_index, layer_index):
                gcode_list.append(self.start_gcode.main_body[index])

            gcode_list.append("G4 S10")
            previous_index = layer_index

        for index in range(previous_index, last_index):
            gcode_list.append(self.start_gcode.main_body[index])

        self.end_gcode.main_body = gcode_list

        return self.end_gcode

    def retract_syringe_end_of_print(self):

        if self.start_gcode.largest_extrusion_value <= 1000:
            largest_one_time_retraction = self.start_gcode.largest_extrusion_value
            still_to_rectract = 0
            repeat_insertion = False
        else:
            largest_one_time_retraction = 1000
            still_to_rectract = self.start_gcode.largest_extrusion_value - 1000
            repeat_insertion = True

        new_end_gcode = []

        for index, line in enumerate(self.start_gcode.shutdown_code):
            new_end_gcode.append(line)
            if "G1 X0 Y220" in line:
                while repeat_insertion is True:
                    new_reverse_extrusion = "G1 E-" + str(largest_one_time_retraction)
                    new_end_gcode.append(new_reverse_extrusion)

                    if still_to_rectract > 0:
                        if still_to_rectract <= 1000:
                            largest_one_time_retraction = still_to_rectract
                            still_to_rectract = 0
                        else:
                            temp = still_to_rectract
                            largest_one_time_retraction = still_to_rectract - 1000
                            still_to_rectract = temp - largest_one_time_retraction
                    else:
                        repeat_insertion = False

        self.end_gcode.shutdown_code = new_end_gcode

        return self.end_gcode

    def set_gcode(self, new_gcode: GCode):
        self.start_gcode = new_gcode
        self.end_gcode = new_gcode