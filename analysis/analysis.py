import numpy as np

def max_peak_location(calibration, spectrum):
    l = np.argmax(spectrum)
    return (calibration[l], spectrum[l])