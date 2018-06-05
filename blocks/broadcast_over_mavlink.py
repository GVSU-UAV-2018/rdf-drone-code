from top_level_radio_processing import RDFRadioProcessing_output_types
from top_level_radio_processing import RDFRadioProcessing_output_slots

from gnuradio import gr

"""
"""

class BroadcastOverMavlink(gr.sync_block):
    def __init__(self):

        gr.sync_block.__init__(self,
            name="BroadcastOverMavlink",
            in_sig=[size for size in RDFRadioProcessing_output_types.values()],
            out_sig=[])

    def work(self, input_items, output_items):

        return len(input_items[0])
