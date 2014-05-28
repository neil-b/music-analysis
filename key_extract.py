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

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print 'proper usage: python key_extract.py inputDirectory'
    print 'This program will automatically crawl into all subdirectories in inputDirectory'

  else:
    dataDirectories = [x for x in os.walk(sys.argv[1])]
    for (directory, subDirs, files) in dataDirectories:
      if 'bothchroma.csv' in files:
        # print key from unnormalized pcp vectors
        (bassPCP, treblePCP) = readPCPFile(directory + '/' + 'bothchroma.csv', norm=False)
        bassKey = extractKey(bassPCP)
        trebleKey = extractKey(treblePCP)
        print directory, 'bass:', bassKey, 'treble:', trebleKey, '(not normalized)'

        # print key from normalized pcp vectors
        (bassPCP, treblePCP) = readPCPFile(directory + '/' + 'bothchroma.csv', norm=True)
        bassKey = extractKey(bassPCP)
        trebleKey = extractKey(treblePCP)
        print directory, 'bass:', bassKey, 'treble:', trebleKey, '(normalized)'

