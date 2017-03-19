import pylab
import skvideo.io
import imageio
import numpy as np
import sys
import scipy as sp
from triangles.delaunay import triangularize
from scipy.misc import imsave
from Naked.toolshed.shell import execute_js, muterun_js
from PIL import ImageFilter

filename = '/Users/tyler/Desktop/NWhacks/TriVideo/tmp/Waves.mp4'
imageio.plugins.ffmpeg.download()
vid = imageio.get_reader(filename,  'ffmpeg')
fps = vid.get_meta_data()['fps']

writer = imageio.get_writer('/Users/tyler/Desktop/NWhacks/TriVideo/tmp/processed_Waves.mp4', fps=fps)

mapper = MapReduce(triangularize_frames, get_frame_info)
frames = mapper(zip([1:len(vid)],vid))
frames.sort(key=operator.itemgetter(1))

for frame in frames:
    idx, frame = frame
    writer.append_data(frame)
writer.close()
#j = 5
#for im in vid:
#    j = j + 5
#    if j < 20000:
#        filename = 'Frames/Frame%d.jpg' % j
#        absolute_path = '/Users/tyler/Desktop/NWhacks/TriVideo/' + filename 
#        #filtered_im  = gaussian(im, sigma=0.4)
#        filtered_im = im
#        imsave(filename,filtered_im)
#        # trigfile = triangularize(absolute_path,5000)
#        trigfile = timeout(triangularize, args=(absolute_path,500), timeout_duration=10)
#        if trigfile is None:
#            continue
#        else:
#            ### process image here
#            processedImage = imageio.imread(trigfile)
#            filtered_im = processedImage.filter(ImageFilter.BLUR)
#            # filtered_im = processedImage
#            # processedImage = imageio.imread(filename)
#            writer.append_data(filtered_im)
#writer.close()

# Our map function
def triangularize_frames(frames):

    print multiprocessing.current_process().name, 'reading', filename
    output = []

    for frame in frames:
        idx, img = frame
        filename = 'Frames/Frame%d.jpg' % idx
        absolute_path = '/Users/tyler/Desktop/NWhacks/TriVideo/' + filename
        imsave(filename,img)

        # convert img to triangle version
        triangleFile = timeout(triangularize, args=(absolute_path,500), timeout_duration=10)
        if triangleFile is None:
            continue
        else:
            processedImg = imageio.imread(triangleFile)
            output.append((idx, processImg))
    return output

# our reduce function
def get_frame_info(frame):
    frame_idx, frame_img = frame
    return (frame_idx, frame_img)

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
