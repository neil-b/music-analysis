#!/bin/python

import os
import sys 
import itertools
import collections

from chord import Chord

"""
  Returns the chord data of a file in a format that can be used by generateProbabilityTables.
  Use the transpose argument to set the number of concatenated transpositions
"""
def readChordData(fileName, transpose=0):
  file = open(fileName)
  chordData = []

  for line in file:
    line = line.rstrip('\n')
    columns = line.split('\t')
    if len(columns) == 3: # if line is an actual entry and not whitespace
      # (startTime, endTime, chord) 
      chordData.append((float(columns[0]), float(columns[1]), Chord(columns[2])))

  # apply transposition
  coreChordData = chordData[:]
  loopLength = chordData[-1][1]
  for i in range(1, transpose + 1):
    # adjust time and transpose the core chord data, then add it to the returned array
    chordData.extend([
      ((i * loopLength) + timeStart, (i * loopLength) + timeEnd, chord.transposed(i))
      for (timeStart, timeEnd, chord) in coreChordData
    ])

  return chordData

"""
  Finds the joint and conditional probability tables of some chordData

  chordData must be an array of tuples following the format: (startTime, endTime, chord). This function assumes chordData is ordered by startTime.

  returns (jointProbabilityTable, conditionalProbabilityTable)
"""
def generateProbabilityTables(chordData):
  # calculate joint probabilities
  jointProbabilityTable = collections.Counter()
  occurrenceCounter = collections.Counter() # num occurrences based on sequence length

  # the range of the length of chord sequences to analyze
  for sequenceLength in range(1, 4):
    # for each sequence of the array
    for sequenceIndex in range(0, len(chordData)):
      chordSequence = chordData[sequenceIndex : sequenceIndex + sequenceLength]
      # the length may be too short once sequenceIndex gets close to the end
      if len(chordSequence) == sequenceLength:
        chords = tuple([str(x[2]) for x in chordSequence]) # extract chord names
        jointProbabilityTable[chords] += 1
        occurrenceCounter[sequenceLength] += 1

  # divide through by the number of occurrences to get the final joint probabilies
  for chordSequence in jointProbabilityTable.keys():
    jointProbabilityTable[chordSequence] /= (float(occurrenceCounter[len(chordSequence)]))

  # calculate conditional probabilities
  conditionalProbabilityTable = collections.Counter()

  # for each chord sequence with length > 1, find the conditional probability
  for chordSequence in jointProbabilityTable.keys():
    if len(chordSequence) != 1: 
      unknown = chordSequence[-1]
      observed = list(chordSequence)[:-1]

      jointProbability = jointProbabilityTable[chordSequence] # P(observed, unknown)
      # sum probabilities where the length and first events match the sequence
      observedProbability = sum(
        [prob
          for (sequence, prob)
          in jointProbabilityTable.iteritems()
          if len(sequence) == len(chordSequence)
            and list(sequence)[:-1] == observed
        ]
      ) # P(observed, anything) 
      conditionalProbabilityTable[(unknown, tuple(observed))] = jointProbability / observedProbability

  return (jointProbabilityTable, conditionalProbabilityTable)  

"""
  Writes probability info from files specified by the command line
"""
if __name__ == '__main__':
  if len(sys.argv) != 4:
    print 'proper usage: python chord_probability.py inputDirectory outputDirectory numTranspositions'
    print 'This program will automatically crawl into all subdirectories in inputDirectory'

  else:
    dataDirectories = [x for x in os.walk(sys.argv[1])]
    for (directory, subDirs, files) in dataDirectories:
      for file in files:
        # get probability tables
        out = open(sys.argv[2] + '/' + str(directory.split('/')[-1]) + '.txt', 'w+')
        chordData = readChordData(directory + '/' + file, transpose=int(sys.argv[3]))
        (joint, conditional) = generateProbabilityTables(chordData)

        # write output to file
        print >> out, 'Joint probabilities: P(t, t+1, ..., t+n) (where t+1 occurs right after t)'
        for (chordSequence, probability) in joint.iteritems():
          print >> out, '  P(', list(chordSequence), ') = ', probability

        print >> out, '\n'

        print >> out, 'Conditional probabilities: P(t+n | t, t+1, ..., t+(n-1))'
        for ((unknown, observed), probability) in conditional.iteritems():
          print >> out, '  P(', unknown, '|', list(observed), ') =', probability

        out.close()

