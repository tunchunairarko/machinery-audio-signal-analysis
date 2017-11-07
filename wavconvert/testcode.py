# -*- coding: utf-8 -*-
"""
Created on Thu May  4 22:58:03 2017

@author: tunch
"""

from scipy.io import wavfile
import numpy as np
from scipy.signal import fftconvolve, correlate
import matplotlib.pyplot as plt
#from parabolic import parabolic
from matplotlib.mlab import find
import matplotlib as mat


rate, signal = wavfile.read('50Hz harmonics.wav')
corr=np.s
#corr = fftconvolve(signal, signal[::-1], mode='full')
#corr = corr[len(corr)//2:]
#
#d = np.diff(corr)
#start = find(d > 0)[0]
#peak = np.argmax(corr[start:]) + start
##px, py = parabolic(corr, peak)
plt.plot(corr)
plt.show()
    