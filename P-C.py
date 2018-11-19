#!/usr/bin/env python3

import threading
import time
import random
import queue
import cv2
import os
from DisplayFrames import *

BUF_SIZE = 10
q1 = queue.Queue(BUF_SIZE)
q2 = queue.Queue(BUF_SIZE)
outputDir    = 'frames'
clipFileName = 'clip.mp4'
count = 0
frameDelay = 42
vidcap = cv2.VideoCapture(clipFileName)

class ProducerExtractFrames(threading.Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ProducerExtractFrames,self).__init__()
        self.target = target
        self.name = name

        if not os.path.exists(outputDir):
            print("Output directory {} didn't exist, creating".format(outputDir))
            os.makedirs(outputDir)

    def run(self):
        count = 0
        condition = True
        while condition:
            if not q1.full():
                success,image = vidcap.read()
                if (success):
                    q1.put(image)
                    cv2.imwrite("{}/frame_{:04d}.jpg".format(outputDir, count), image)
                    print('Reading frame {}'.format(count))
                    count += 1
                else:
                    condition = False
                    print("DONE extracting")
        return

class ConsumerConvertToGrayscale(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ConsumerConvertToGrayscale,self).__init__()
        self.target = target
        self.name = name
        return

    def run(self):
        count = 0
        condition = True
        while condition:
            if not q1.empty():
                image = q1.get()
                inFileName = "{}/frame_{:04d}.jpg".format(outputDir, count)
                inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)
                if (inputFrame is not None):
                    print("Converting frame {}".format(count))
                    grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)
                    outFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)
                    q2.put(cv2.imwrite(outFileName, grayscaleFrame))
                    count += 1
                    inFileName = "{}/frame_{:04d}.jpg".format(outputDir, count)
                    success, jpgImage = cv2.imencode('.jpg', image)
                    # inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)

        return

class ConsumerDisplayFrames(threading.Thread):
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        super(ConsumerDisplayFrames,self).__init__()
        self.target = target
        self.name = name
        return

    def run(self):
        count = 0
        condition = True
        while condition:
            if not q2.full():
                q2.get()
                startTime = time.time()
                # Generate the filename for the first frame
                frameFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)
                # load the frame
                frame = cv2.imread(frameFileName)
                if (frame is not None):
                    print("Displaying frame {}".format(count))
                    # Display the frame in a window called "Video"
                    cv2.imshow("Video", frame)
                    # compute the amount of time that has elapsed
                    # while the frame was processed
                    elapsedTime = int((time.time() - startTime) * 1000)
                    print("Time to process frame {} ms".format(elapsedTime))
                    # determine the amount of time to wait, also
                    # make sure we don't go into negative time
                    timeToWait = max(1, frameDelay - elapsedTime)
                    count += 1
                    # Wait for 42 ms and check if the user wants to quit
                    if cv2.waitKey(timeToWait) and 0xFF == ord("q"):
                        break
                # get the start time for processing the next frame
                        startTime = time.time()
                        count += 1
                # get the next frame filename
                        frameFileName = "{}/grayscale_{:04d}.jpg".format(outputDir, count)
                # Read the next frame file
                        frame = cv2.imread(frameFileName)
                # make sure we cleanup the windows, otherwise we might end up with a mess
                        cv2.destroyAllWindows()

                else:
                    condition = False
                    print("Video over")



if __name__ == '__main__':

    p = ProducerExtractFrames(name='producerExtract')
    c = ConsumerConvertToGrayscale(name='consumerConvert')
    c2 = ConsumerDisplayFrames(name='consumerDisplay')

    p.start()
    c.start()
    c2.start()
