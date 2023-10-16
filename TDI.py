#!/usr/bin/env python
# coding: utf-8

# In[1]:


import h5py
import matplotlib.pyplot as plt
import numpy as np
import itertools
from scipy import signal
from tempfile import TemporaryFile


# In[3]:


get_ipython().run_line_magic('matplotlib', 'notebook')

### extract arrays from HDF5 file from measurement. ~30000 detector shots/images per file 
f = h5py.File('/data3/2021/2021_3_LCLS_LAO/smalldata/xpplv7918_Run0034.h5','r') ## Open Measurement HDF5
ipm2 = np.array(f['ipm2/sum'])## Intensity normalization
detec = np.array(f['jungfrau1M/ROIw_0_area'])## Detector image for each shot
xOn = np.array(f['lightStatus/xray']) ## X-ray On Boolean for each shot
laserOn = np.array(f['lightStatus/laser']) ## Laser On Boolean for each shot
timeDelay = np.array(f['scan/lxt_ttc'])*1e12  ## time delay between X-ray and Laser Pulse

thresh = 20.0### set the threshold, only take shots/images higher than this
detec_roi = detec[:,107:127, 69:89]### area where the X-ray feature is. 

#### sort the shots, for laser X-ray on, Laser ON, and Threshold
detec_on = detec_roi[np.where(np.logical_and(np.logical_and(xOn==1, laserOn==1), ipm2>thresh))]
delays_on = timeDelay[np.where(np.logical_and(np.logical_and(xOn==1, laserOn==1), ipm2>thresh))]
ipm_on = ipm2[np.where(np.logical_and(np.logical_and(xOn==1, laserOn==1), ipm2>thresh))]

#sort the shots, for laser X-ray on, Laser OFF, and Threshold
detec_off = detec_roi[np.where(np.logical_and(np.logical_and(xOn==1, laserOn==0), ipm2>thresh))]
delays_off = timeDelay[np.where(np.logical_and(np.logical_and(xOn==1, laserOn==0), ipm2>thresh))]
ipm_off = ipm2[np.where(np.logical_and(np.logical_and(xOn==1, laserOn==0), ipm2>thresh))]

### Time delay array, set the number of steps (bins). we know this is -2ps and 20ps from experiment
timeDelayBin = np.linspace(-2, 20, 50)

## initialize arrays
meanArray_on = np.zeros(len(timeDelayBin))
meanArray_off = np.zeros(len(timeDelayBin))

## loop over the time delays. Digitize returns an array putting each value of delays_on in a bin
## corresponding to the time delays. np.where then makes an array of indices.
for index in range(len(timeDelayBin)):
    avg_ipm_on = np.mean(ipm_on[np.where(np.digitize(delays_on, bins = timeDelayBin) == index)])
    meanArray_on[index] = np.mean(detec_on[np.where(np.digitize(delays_on, bins = timeDelayBin) == index)])/avg_ipm_on
    
for index in range(len(timeDelayBin)):
    avg_ipm_off = np.mean(ipm_off[np.where(np.digitize(delays_off, bins = timeDelayBin) == index)])
    meanArray_off[index] = np.mean(detec_off[np.where(np.digitize(delays_off, bins = timeDelayBin) == index)])/avg_ipm_off


plt.plot(timeDelayBin, meanArray_on, '-o', color='red', label='laser on')
plt.plot(timeDelayBin, meanArray_off, '-o', color='black', label='laser off')
plt.xlabel("time delay (ps)")
plt.ylabel("avg. detector intensity (arb. units.)")

plt.legend()


# In[ ]:




