import scipy.signal

def bandpass(order, low, high, sample_rate):
    nyquist = 0.5 * sample_rate
    l = low / nyquist
    h = high / nyquist
    return scipy.signal.butter(
        order, [l, h],
        btype='bandpass',
        analog=False,
        output='ba')