import collections
import sys
from configparser import ConfigParser
from argparse import ArgumentParser


class config_dict(collections.Mapping):
    """
    A dictionary specifically for configuration items.
    If a key does not exist in the dictionary,
    this prints a readable error message and exits
    instead of throwing an exception.
    """
    def __init__(self, source_items, missing_key_message):
        self._backing = dict(source_items)
        self._message = missing_key_message

    def __getitem__(self, key):
        if key in self._backing:
            return self._backing[key]
        else:
            print(self._message.format(key=key))
            print(self._backing)
            sys.exit(-1)

    def __iter__(self):
        return iter(self._backing)

    def __len__(self):
        return len(self._backing)


def get_file_config():
    config_file_name = 'settings.ini'

    parser = ConfigParser()
    with open(config_file_name, 'r') as config_file:
        parser.readfp(config_file)

    return config_dict(
        {section_name: config_dict(
            {k:eval(v) for k,v in parser.items(section_name)},
            missing_key_message='Configuration error\n'
            +'Could not find key \'{key}\' in file \''+config_file_name+'\', '
            +'section \''+section_name+'\'')
        for section_name in parser.sections()},
        missing_key_message='Configuration error\n'
        +'Could not find section \'{key}\' in file \''+config_file_name+'\'')



def add_config_section_recording(parser, recording_config):

    parser.add_argument('-o', '--recording-filename',
        default='test-sample.wav',
        help='Name of file to record to')

    parser.add_argument('-O', '--record-in',
        default=config_sections['recording']['recording folder'],
        help='Save recordings in the given recording folder')


def add_config_section_acquisition(parser, acquisition_config):

    parser.add_argument('-f', '--frequency', type=int,
        default=acquisition_config['default frequency'],
        help='Frequency to look for in Hz')

    parser.add_argument('--gains', type=int, nargs='+',
        default=acquisition_config['gains'],
        help='Gain of each amplifier stage, in device units')

    parser.add_argument('-t', '--time', type=int,
        default=acquisition_config['hold time'],
        help='Time to run sampling, in seconds')

    parser.add_argument('-s', '--sample-rate', type=int,
        default=acquisition_config['sample rate'],
        help='Desired sample rate in samples/second')


def add_config_section_system(parser, system_config):

    parser.add_argument('--frequency-offset', type=int,
        default=system_config['frequency offset'],
        help='Offset of the tuner frequency from the frequency-of-interest, in Hz')


def add_config_section_signal_detection(parser, detection_config):

    parser.add_argument('-m', '--detection-method',
        default=detection_config['detection method'],
        help='Detection method to use. (--list-detection-methods to see options)')

    parser.add_argument('-r', '--fft-resolution', type=int,
        default=detection_config['fft resolution'],
        help='Number of samples in each Fourier transform')

    parser.add_argument('-b', '--signal-bandwidth', type=int,
        default=detection_config['signal bandwidth'],
        help='Signal bandwidth in Hz')

    parser.add_argument('-l', '--snr-threshold', type=int,
        default=detection_config['snr threshold'],
        help='Minimum signal-to-noise ratio of a real signal (linear ratio)')
