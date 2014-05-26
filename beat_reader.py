#!/bin/python

"""
  Generates wavs and graphs from beat data files

  Requires matploblib and pydub
"""

import math
import sys
import pydub
import matplotlib.pyplot as plt


class BeatReader:
  tickFile = './tick.wav'

  def __init__(self, beatFile): 
    self.beatSets = []
    self.beatFile = beatFile

    file = open(beatFile)
    for line in file:
      beats = []
      for time in line.split():
        beats.append(float(time))
      self.beatSets.append(beats)
    file.close()

  def createBeatFiles(self, overlayFile=None, outDirectory='./'):
    tickData = pydub.AudioSegment.from_wav(BeatReader.tickFile)
    for (counter, beat) in enumerate(self.beatSets):
      # set output wav length to be time of last beat + enough time to play tick noise
      outDuration = beat[len(beat) - 1] + tickData.duration_seconds
      audioData = pydub.AudioSegment.silent(duration=outDuration*1000.0)

      # for each individual beat, overlay the tick sound effect
      for time in beat:
        audioData = audioData.overlay(tickData, position=time*1000.0)

      # overlay the original source audio on top of the beat audio, if specified
      if overlayFile:
        overlayData = pydub.AudioSegment.from_wav(overlayFile)
        audioData = audioData.overlay(overlayData)

      outFilePrefix = 'undefined'
      if overlayFile:
        outFilePrefix = 'overlay'
      else:
        outFilePrefix = 'beat'

      audioData.export(outDirectory + '/' + outFilePrefix + str(counter) + '.wav', format='wav')

  def createGraph(self, outFile=None):
    x, y = [], []
    for (counter, beat) in enumerate(self.beatSets):
      for time in beat:
        x.append(time)
        y.append(counter)
    plt.xlabel('Seconds')
    plt.ylabel('Line number')
    plt.ylim((-0.5, len(self.beatSets)))
    plt.title(self.beatFile)
    plt.plot(x, y, 'ro')

    if outFile == None:
      plt.show()
    else:
      plt.savefig(outFile)

if __name__ == '__main__':
  if len(sys.argv) != 3 and len(sys.argv) != 4:
    print 'usage:' 
    print '  python beat_reader.py beatdata.txt outDirectory/'
    print '  or'
    print '  python beat_reader.py beatdata.txt outDirectory/ overlayAudio.wav'
  else:
    br = BeatReader(sys.argv[1])
    if (len(sys.argv) == 3):
      br.createBeatFiles(outDirectory=sys.argv[2])
    else: 
      br.createBeatFiles(outDirectory=sys.argv[2], overlayFile=sys.argv[3])
    br.createGraph(sys.argv[2] + '/graph.pdf')

