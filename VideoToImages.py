import imageio
import numpy
import os
from multiprocessing import Pool
from triangles.delaunay import triangularize
imageio.plugins.ffmpeg.download()
import time

def triangularize_frame(frame):
    fr, idx = frame
    frameFileName = '/Frames/Frame%d.jpg' % idx
    absolute_path = os.path.dirname(os.path.abspath(__file__)) + frameFileName
    print("Saving frame %s" % absolute_path)

    # convert img to triangle version
    return (timeout(triangularize, args=(absolute_path, fr,100), timeout_duration=30), idx)

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
        print("Processing frame %s Timedout" % kwargs)
        result = default
    finally:
        signal.alarm(0)

    return result


# Our map function
def getVideo(InputFileName):
    start_time = time.time()
    vid = imageio.get_reader("../tmp/" + InputFileName,  'ffmpeg')
    fps = vid.get_meta_data()['fps']
    FullFilePath =  InputFileName[0:len(InputFileName) - 4] + '_triangular' + InputFileName[len(InputFileName) - 4: len(InputFileName)]
    print("Processing file from %s" % FullFilePath)
    writer = imageio.get_writer("../tmp/" + FullFilePath, fps=fps)
    frames = processor.map(triangularize_frame, zip(vid, range(len(vid))))
    print("--- %s seconds before writing ---" % (time.time() - start_time))
    for fr, idx in frames:
        if fr is not None:
            writer.append_data(numpy.asarray(fr))
    print("--- %s seconds after writing ---" % (time.time() - start_time))

    return FullFilePath

processor = Pool(8)
