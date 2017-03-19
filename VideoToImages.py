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
imageio.plugins.ffmpeg.download()

def triangularize_frame(frame):
    fr, idx = frame
    if idx % 4 == 0:
        frameFileName = '/Frames/Frame%d.jpg' % idx
        #absolute_path = '/Users/tyler/Desktop/NWhacks/TriVideo/' + frameFileName
        print("Saving frame %s" % absolute_path)
        imsave(frameFileName,fr)

        # convert img to triangle version
        return (timeout(triangularize, args=(absolute_path,500), timeout_duration=20), idx)
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
    print(FullFilePath)
    #writer = imageio.get_writer('/Users/tyler/Desktop/NWhacks/TriVideo/tmp/processed_Fireworks.mp4', fps=fps)
    #slowerfps = fps/4
    writer = imageio.get_writer(FullFilePath, fps=fps)
    p = Pool(8)
    frames = p.map(triangularize_frame, zip(vid, range(len(vid))))
    sorted_frames = sorted(frames, key=operator.itemgetter(1))
    for fr, idx in sorted_frames:
        if fr is not None:
            processedImage = imageio.imread(fr)
            writer.append_data(processedImage)
    return FullFilePath

