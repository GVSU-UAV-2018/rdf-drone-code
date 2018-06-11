from configparser import ConfigParser
from argparse import ArgumentParser


def _get_file_config():
    parser = ConfigParser()
    with open('settings.ini', 'r') as config_file:
        parser.readfp(config_file)

    return {
        section_name:{k:eval(v) for k,v in parser.items(section_name)}
            for section_name in parser.sections()}


def get_radio_cmdline_config():
    file_config = _get_file_config()
    s = file_config['signal detection']
    parser = ArgumentParser()
    parser.add_argument('SIGNAL_FREQUENCY', type=int,
        help='Frequency to look for in Hz')

    parser.add_argument('-d', '--direction', type=int,
        default=-1,
        help='Direction antenna is pointing during sampling, in degrees')
    parser.add_argument('-t', '--time', type=int,
        default=s['hold time'],
        help='Time to run sampling, in seconds')
    parser.add_argument('-f', '--sample-rate', type=int,
        default=s['sample rate'],
        help='Desired sample rate in samples/second')
    parser.add_argument('-r', '--fft-resolution', type=int,
        default=s['fft resolution'],
        help='Resolution of FFT in bins over the whole sampled band')
    parser.add_argument('-b', '--signal-bandwidth', type=int,
        default=s['signal bandwidth'],
        help='Signal bandwidth in Hz')

    parser.add_argument('--record-in',
        default=file_config['recording']['recording folder'],
        help='Record to the file <direction>.wav in the given recording folder')
    parser.add_argument('--frequency-offset', type=int,
        default=s['frequency offset'],
        help='Offset of the tuner frequency from the search frequency, in Hz')
    return parser.parse_args()

def get_playback_cmdline_config():
    file_config = _get_file_config()
    s = file_config['signal detection']
    parser = ArgumentParser()
    parser.add_argument('INPUT_FOLDER',
        help='Input folder')
    parser.add_argument('OUTPUT_FILE',
        help='Output file')

    parser.add_argument('-r', '--fft-resolution', type=int,
        default=s['fft resolution'],
        help='Resolution of FFT in bins over the whole sampled band')
    parser.add_argument('-b', '--signal-bandwidth', type=int,
        default=s['signal bandwidth'],
        help='Signal bandwidth in Hz')

    parser.add_argument('--frequency-offset', type=int,
        default=s['frequency offset'],
        help='Offset of the tuner frequency from the search frequency, in Hz\n'
            +'This should be the same as the frequency offset used to create the recording')
    return parser.parse_args()
