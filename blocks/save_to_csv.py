import csv
from top_level_radio_processing import RDFRadioProcessing_output_types
from top_level_radio_processing import RDFRadioProcessing_output_python_types
from top_level_radio_processing import RDFRadioProcessing_output_slots

from gnuradio import gr

"""
Saves the output of the top-level radio processing to a CSV file.
"""

class SaveToCsv(gr.sync_block):
    def __init__(self, filename):

        gr.sync_block.__init__(self,
            name="SaveToCsv",
            in_sig=[T for T in RDFRadioProcessing_output_python_types.values()],
            out_sig=[])

        self.data_file = open(filename, "w")
        print filename
        self.data_recorder = csv.writer(self.data_file)
        self.data_recorder.writerow(RDFRadioProcessing_output_slots.keys())

    def work(self, input_items, output_items):
        self.data_recorder.writerow(
            [input_items[i][0]
                for i in RDFRadioProcessing_output_slots.values()])

        return 1
