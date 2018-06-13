#! /usr/bin/python2

"""Polar histogram is based on this StackOverflow answer:
https://stackoverflow.com/a/13508205
"""


ANGULAR_RESOLUTION = 5 # degrees


from time import sleep
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim


#antenna_data = np.genfromtxt('../GNU Radio OLD/rad_pattern.csv', delimiter=',', skip_header=1)

#antenna_heading = antenna_data[:,0] * np.pi/180.0
#antenna_heading = np.append(antenna_heading[:-1], antenna_heading[:-1] + np.pi)
#antenna_rad = antenna_data[:,1]
#antenna_rad = np.append(antenna_rad, antenna_rad[-1:1:-1])


data = np.genfromtxt('../samples/processed.csv', delimiter=',', skip_header=1)

heading = data[:,5]
snr = 10*np.log10(data[:,0])

heading = heading[snr>10]
snr = snr[snr>10]

#antenna_rad_scaled = antenna_rad - np.max(antenna_rad) + np.max(snr)


snr_by_heading = np.histogram(
    heading,
    bins=np.arange(0, 360, 1.0),
    weights=snr)[0]

heading_n_samples = np.histogram(heading, bins=np.arange(0, 360, 1.0))[0]

for i in xrange(len(snr_by_heading)):
    if(heading_n_samples[i]) != 0:
        snr_by_heading[i] /= heading_n_samples[i]



def polar_corr(data1, data2, n_samples):
    data1 = np.interp(
        np.arange(0, 1, 1.0/n_samples),
        np.arange(0, 1, 1.0/len(data1)),
        data1, period=1)
    data2 = np.interp(
        np.arange(0, 1, 1.0/n_samples),
        np.arange(0, 1, 1.0/len(data2)),
        data2, period=1)

    data1 = np.append(data1, data1)
    return np.argmax(np.correlate(data1, data2))

#print(polar_corr(10**snr_by_heading, 10**antenna_rad_scaled, n_samples=360))




H, xedges, yedges\
    = np.histogram2d(
        heading, snr,
        bins=(360/ANGULAR_RESOLUTION, 100),
        range=[[0, 360],[np.min(snr), np.max(snr)]])
theta, r = np.mgrid[0:2*np.pi:360j/ANGULAR_RESOLUTION, 1:np.max(snr):100j]

fig = plt.figure()
ax = fig.add_subplot(1, 1, 1, projection='polar')
ax.pcolormesh(theta, r, H, cmap=plt.cm.Blues)
#ax.scatter(antenna_heading, antenna_rad_scaled, 1, color='#DDDDDD', marker='.')
plt.show(block=False)

plt.show()
