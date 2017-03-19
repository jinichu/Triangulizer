import os
import pylab
import skvideo.io
import imageio
import numpy as np
import sys
import scipy as sp
import operator
from multiprocessing import Pool
from triangles.delaunay import triangularize
from scipy.misc import imsave
from Naked.toolshed.shell import execute_js, muterun_js
from mapreduce import MapReduce, Frame
imageio.plugins.ffmpeg.download()

def triangularize_frame(frame):
    fr, idx = frame
    if idx % 4 == 0:
        frameFileName = 'Frames/Frame%d.jpg' % idx
        absolute_path = '/Users/tyler/Desktop/NWhacks/TriVideo/' + frameFileName
        print("Saving frame %s" % absolute_path)
        imsave(frameFileName,fr)

        # convert img to triangle version
        return (timeout(triangularize, args=(absolute_path,100), timeout_duration=2), idx)
    else:
        return (None,idx) 

def timeout(func, args=(), kwargs={}, timeout_duration=1, default=None):
    import signal

    class TimeoutError(Exception):
        pass

    def handler(signum, frame):
        raise TimeoutError()

    # set the timeout handler
    signal.signal(signal.SIGALRM, handler) 
    signal.alarm(timeout_duration)
    try:
        result = func(*args, **kwargs)
    except TimeoutError as exc:
        result = default
    finally:
        signal.alarm(0)

    return result


# Our map function
def getVideo(InputFileName):
    #InputFileName = '/Users/tyler/Desktop/NWhacks/TriVideo/tmp/Fireworks.mp4'
    vid = imageio.get_reader(InputFileName,  'ffmpeg')
    fps = vid.get_meta_data()['fps']
    FullFilePath = InputFileName[0:len(InputFileName) - 4] + '_triangular' + InputFileName[len(InputFileName) - 4: len(InputFileName)]
    #writer = imageio.get_writer('/Users/tyler/Desktop/NWhacks/TriVideo/tmp/processed_Fireworks.mp4', fps=fps)
    slowerfps = fps/4
    writer = imageio.get_writer(FullFilePath, fps=slowerfps)
    p = Pool(8)
    frames = p.map(triangularize_frame, zip(vid, range(len(vid))))
    sorted_frames = sorted(frames, key=operator.itemgetter(1))
    for fr, idx in sorted_frames:
        if fr is not None:
            processedImage = imageio.imread(fr)
            writer.append_data(processedImage)

    # j = 5
    # for im in vid:
    #     j = j + 1
    #     if j % 5 != 0:
    #             continue 
    #     if j < 5000 and j > 2000:
    #         filename = 'Frames/Frame%d.jpg' % j
    #         absolute_path = '/Users/tyler/Desktop/NWhacks/TriVideo/' + filename 
    #         #filtered_im  = gaussian(im, sigma=0.4)
    #         filtered_im = im
    #         imsave(filename,filtered_im)
    #         # trigfile = triangularize(absolute_path,5000)
    #         trigfile = timeout(triangularize, args=(absolute_path,3000), timeout_duration=20)
    #         if trigfile is None:
    #             continue
    #         else:
    #             ### process image here
    #             processedImage = imageio.imread(trigfile)
    #             #filtered_im = processedImage.filter(ImageFilter.BLUR)
    #             filtered_im = processedImage
    #             # processedImage = imageio.imread(filename)
    #             writer.append_data(filtered_im)
    # writer.close()
    return FullFilePath

getVideo('/Users/tyler/Desktop/NWhacks/TriVideo/tmp/Fireworks.mp4')