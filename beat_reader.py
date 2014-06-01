#!/bin/python

"""
  Generates wavs and graphs from beat data files

  Requires matploblib and pydub
"""

import math
import sys
import pydub
import matplotlib.pyplot as plt
import essentia.standard

class BeatReader:
  tickFile = './tick.wav'

  def __init__(self, beatFile): 
    self.beatSets = []
    self.beatFile = beatFile
    self.beatConfidence = [] # from text = None, from wav = [0, 1.0]

    # add beats from beat (plaintext) file
    file = open(beatFile)
    for line in file:
      beats = []
      for time in line.split():
        beats.append(float(time))
      self.beatSets.append(beats)
      self.beatConfidence.append(None)
    file.close()

  """
    Use a beatfinding algorithm to add the estimated beats of a wav file to
    self.beatSets
  """
  def addBeatsFromWav(self, wavFile):
    BTMF_MAX_CONFIDENCE = 5.32
    loader = essentia.standard.MonoLoader(filename=wavFile)
    audio = loader()
    btmf = essentia.standard.BeatTrackerMultiFeature()
    (beats, confidence) = btmf(audio)

    self.beatSets.append(beats)
    # scale confidence to [0, 1.0]
    self.beatConfidence.append(confidence / BTMF_MAX_CONFIDENCE)

  """
    Create wav files of self.beatSets
  """
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
    for (counter, beat) in enumerate(self.beatSets):
      for time in beat:
        color = 'red'
        confidence = self.beatConfidence[counter]
        if confidence != None:
          brightness = '{0:x}'.format(int(confidence * 255))
          color = '#' + (brightness * 3)
        plt.plot(time, counter, 'ro', color=color)
    plt.xlabel('Seconds')
    plt.ylabel('Line number')
    plt.ylim((-0.5, len(self.beatSets)))
    plt.title(self.beatFile)

    if outFile == None:
      plt.show()
    else:
      plt.savefig(outFile)
    # clear plot and axis
    plt.clf()
    plt.cla()

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
      br.addBeatsFromWav(sys.argv[3])
      br.createBeatFiles(outDirectory=sys.argv[2], overlayFile=sys.argv[3])
    br.createGraph(sys.argv[2] + '/graph.pdf')

