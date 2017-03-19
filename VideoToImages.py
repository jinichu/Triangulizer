import pylab
import skvideo.io
import imageio
import numpy as np
import sys
import scipy as sp
from scipy.misc import imsave
from Naked.toolshed.shell import execute_js, muterun_js

filename = '/Users/tyler/Desktop/NWhacks/TriVideo/tmp/Waves.mp4'
imageio.plugins.ffmpeg.download()
vid = imageio.get_reader(filename,  'ffmpeg')
fps = vid.get_meta_data()['fps']

writer = imageio.get_writer('/Users/tyler/Desktop/NWhacks/TriVideo/tmp/processed_Waves.mp4', fps=fps)
j = 200
for im in vid:
    j = j + 1
    #if j < 745:
    if j < 202:
        filename = 'Frames/Frame%d.jpg' % j
        #filtered_im = sp.ndimage.filters.gaussian_filter(im)
        filtered_im = im
        imsave(filename,filtered_im)
        ### process image here
        #processedImage = imageio.imread(response)
        processedImage = imageio.imread(filename)
        writer.append_data(processedImage[:, :, 1])
writer.close()





