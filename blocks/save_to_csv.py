import csv
import numpy

from gnuradio import gr

"""
Saves the output of the top-level radio processing to a CSV file.
"""

class SaveToCsv(gr.sync_block):
    def __init__(self, filename):

        gr.sync_block.__init__(self,
            name="SaveToCsv",
            in_sig=[(numpy.float32, 1)],
            out_sig=[])

        self.data_file = open(filename, "w")
        print filename
        self.data_recorder = csv.writer(self.data_file)
        self.data_recorder.writerow(
            ['signal', 'direction'])
        self.direction = -1

    def work(self, input_items, output_items):
        self.data_recorder.writerow(
            [input_items[i][0] for i in range(len(input_items))]
            + [self.direction])

        return 1

    def set_direction(self, direction):
        self.direction = direction
