#!/bin/python

import os
import sys
import essentia.standard
import numpy

"""
  Returns all bass and treble pcp vectors in the file specified by path as 
  two 12xN arrays in the tuple (bass, treble).
"""
def readPCPFile(path, norm=False):
  file = open(path, 'r')
  bassPCPVectors = []
  treblePCPVectors = []
  for line in file:
    line = line.rstrip('\n')
    columns = line.split(',')
    assert len(columns) == 26 # 1 empty + 1 time + 12 bass + 12 treble

    bassPCP = [float(x) for x in columns[2:14]]
    treblePCP = [float(x) for x in columns[14:26]]

    # normalize if specified
    if norm:
      baseNorm = numpy.linalg.norm(bassPCP)
      trebleNorm = numpy.linalg.norm(treblePCP)
      if baseNorm:
        bassPCP = bassPCP / baseNorm
      if trebleNorm:
        treblePCP = treblePCP / trebleNorm

    bassPCPVectors.extend(bassPCP)
    treblePCPVectors.extend(treblePCP)

  return (bassPCPVectors, treblePCPVectors)

def extractKey(pcpVectors):
  key = essentia.standard.Key()
  return key(pcpVectors)

"""
"""
def visualizeKeyChunks(chunkTable, chunkSizes, outFile=None):
  from chord import Chord
  import matplotlib.pyplot as plt
  from matplotlib.patches import Rectangle

  plt.xlabel('Time')
  plt.ylabel('Chunk sizes')
  plt.xticks(range(1))
  plt.yticks(range(len(chunkSizes)+1), chunkSizes)
  plt.title(outFile)

  gca = plt.gca()
  for (i, chunks) in enumerate(chunkTable):
    for (j, chunk) in enumerate(chunks):
      width = 1.0 / float(len(chunks))
      height = 1.0
      x = j * width
      y = i
      color = Chord(chunk).toColor()
      gca.add_patch(Rectangle((x, y), width, height, facecolor=color, edgecolor='#000000'))
      gca.text(x + width/2.0, y + height/2.0, chunk, horizontalalignment='center', verticalalignment='center')

  if outFile == None:
    plt.show()
  else:
    plt.savefig(outFile)
  # clear plot and axis
  plt.clf()
  plt.cla()


""" 
  Returns arr split into numChunks sublists, where the length of each is 
  a multiple of vectorLength
"""
def chunkVector(arr, numChunks, vectorLength):
  chunks = [[] for x in range(0, numChunks)]
  chunkIndex = 0
  chunkSize = len(arr) / numChunks
  for i in xrange(0, len(arr), vectorLength):
    chunks[chunkIndex].extend(arr[i:i+vectorLength])
    if len(chunks[chunkIndex]) > chunkSize and chunkIndex != numChunks-1:
      chunkIndex += 1

  return chunks

if __name__ == '__main__':
  if len(sys.argv) != 3:
    print 'proper usage: python key_extract.py inputDirectory/ outDirectory/'
    print 'This program will automatically crawl into all subdirectories in inputDirectory'

  else:
    dataDirectories = [x for x in os.walk(sys.argv[1])]
    for (directory, subDirs, files) in dataDirectories:
      outPrefix = sys.argv[2] + '/' + str(directory.split('/')[-1])
      if 'bothchroma.csv' in files:
        (bassPCP, treblePCP) = readPCPFile(directory + '/' + 'bothchroma.csv', norm=False)
        (normBassPCP, normTreblePCP) = readPCPFile(directory + '/' + 'bothchroma.csv', norm=True)
        for (name, vectors) in {
          'bass': bassPCP, 'treble': treblePCP,
          'norm_bass': normBassPCP, 'norm_treble': normTreblePCP}.iteritems():
          chunkTable = []
          chunkSizes = [1, 2, 4, 8, 16]
          for numChunks in chunkSizes:
            chunkTable.append([])
            for (i, chunk) in enumerate(chunkVector(vectors, numChunks, 12)):
              key = extractKey(chunk)[0]
              chunkTable[-1].append(key)
          visualizeKeyChunks(chunkTable, chunkSizes, outFile=(outPrefix + name + '.pdf'))
        print outPrefix, 'finished'
