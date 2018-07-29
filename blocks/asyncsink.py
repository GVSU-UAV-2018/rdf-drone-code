import sys
import numpy
import math

from math import ceil, floor

from gnuradio import gr

class AsyncSink(gr.sync_block):
    def __init__(self):

        gr.sync_block.__init__(self,
            name="SNRExtract",
            in_sig=[(numpy.float32)],
            out_sig=None)

        self._queue = []

    def work(self, input_items, output_items):
        self._queue.append(input_items[0][0])
        return 1

    def pop_all():
        self.lock()
        result = self._queue
        self._queue = []
        self.unlock()
        return result
