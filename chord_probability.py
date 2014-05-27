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

  returns (jointProbabilityTable, conditionalProbabilityTable, jointSampleCounts, conditionalSampleCounts)
"""
def generateProbabilityTables(chordData):
  # calculate joint probabilities
  jointProbabilityTable = collections.Counter()
  jointSampleCounts = collections.Counter() # numerator and denom of jointProbabilityTable entries
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
    # store the numerator and denominator of the probabilities to gage accuracy
    jointSampleCounts[chordSequence] = (
      jointProbabilityTable[chordSequence],
      occurrenceCounter[len(chordSequence)]
    )
    jointProbabilityTable[chordSequence] = jointSampleCounts[chordSequence][0] / float(jointSampleCounts[chordSequence][1])

  # calculate conditional probabilities
  conditionalProbabilityTable = collections.Counter()
  conditionalSampleCounts = collections.Counter() # numerator and denom of conditionalProbabilityTable entries

  # for each chord sequence with length > 1, find the conditional probability
  for chordSequence in jointProbabilityTable.keys():
    if len(chordSequence) != 1: 
      unknown = chordSequence[-1]
      observed = list(chordSequence)[:-1]

      jointSamples = jointSampleCounts[chordSequence][0]
      # sum samples where the length and first events match the sequence
      observedSamples = sum(
        [sample[0]
          for (sequence, sample)
          in jointSampleCounts.iteritems()
          if len(sequence) == len(chordSequence)
            and list(sequence)[:-1] == observed
        ]        
      )
      conditionalSampleCounts[(unknown, tuple(observed))] = (jointSamples, observedSamples)
      # P(unknown | observed) = P(observed, unobserved) / P(observed, anything)
      conditionalProbabilityTable[(unknown, tuple(observed))] = jointSamples / float(observedSamples)

  return (jointProbabilityTable, conditionalProbabilityTable, jointSampleCounts, conditionalSampleCounts)  

"""
  Plot a table of P(t+1 | t+0) values. probabilityTable must be conditional
"""
def visualizeConditional(probabilityTable, outFile=None):
  import matplotlib.pyplot as plt
  from matplotlib.patches import Rectangle

  xChords = list(set([x[1][0] for x in probabilityTable.keys() if len(x[1]) == 1])) # get unique values
  # convert to Chord class for sorting, then convert back to string
  xChords = [Chord(x) for x in xChords]
  xChords.sort()
  xChords = [str(x) for x in xChords]

  yChords = list(set([x[0] for x in probabilityTable.keys() if len(x[1]) == 1]))
  yChords = [Chord(x) for x in yChords]
  yChords.sort()
  yChords = [str(x) for x in yChords]

  plt.rc('font', **{'size': 5})
  plt.xlabel('t+0')
  plt.ylabel('t+1')
  plt.xticks(range(len(xChords)), xChords)
  plt.yticks(range(len(yChords)), yChords)
  plt.xlim(-0.5, len(xChords) - 0.5)
  plt.ylim(-0.5, len(yChords) - 0.5)
  plt.title('P(y-axis | x-axis) (columns sum to 1.0)')

  gca = plt.gca()
  for (x, chord0) in enumerate(xChords):
    for (y, chord1) in enumerate(xChords):
      prob = probabilityTable[(chord1, (chord0,))]
      color = 'black'
      if (prob == 0.0):
        color = 'grey'
      gca.text(x, y, str(round(prob, 3)), horizontalalignment='center', verticalalignment='center', color=color)
      gca.add_patch(Rectangle((x-0.5, y-0.5), 1, 1, facecolor='none', edgecolor='b'))
      gca.add_patch(Rectangle((x-0.5, y-0.5), 1, prob, facecolor='r'))

  if outFile == None:
    plt.show()
  else:
    plt.savefig(outFile)
  # clear plot and axis 
  plt.clf()
  plt.cla()

"""
  Plot a table of P(t+0, t+1) values. probabilityTable must be joint
"""
def visualizeJoint(probabilityTable, outFile=None):
  import matplotlib.pyplot as plt
  from matplotlib.patches import Rectangle

  residentChords = [x[0] for x in probabilityTable.keys() if len(x) == 1]
  # convert to Chord class for sorting, then convert back to string
  residentChords = [Chord(x) for x in residentChords]
  residentChords.sort()
  residentChords = [str(x) for x in residentChords]

  plt.rc('font', **{'size': 5})
  plt.xlabel('t+0')
  plt.ylabel('t+1')
  plt.xticks(range(len(residentChords)), residentChords)
  plt.yticks(range(len(residentChords)), residentChords)
  plt.xlim(-0.5, len(residentChords) - 0.5)
  plt.ylim(-0.5, len(residentChords) - 0.5)
  plt.title('P(x-axis, y-axis) (all entries sum to 1.0)')

  gca = plt.gca()
  for (x, chord0) in enumerate(residentChords):
    for (y, chord1) in enumerate(residentChords):
      prob = probabilityTable[(chord0, chord1)]
      color = 'black'
      if (prob == 0.0):
        color = 'grey'
      gca.text(x, y, str(round(prob, 3)), horizontalalignment='center', verticalalignment='center', color=color)
      gca.add_patch(Rectangle((x-0.5, y-0.5), 1, 1, facecolor='none', edgecolor='b'))
      gca.add_patch(Rectangle((x-0.5, y-0.5), 1, prob, facecolor='r'))

  if outFile == None:
    plt.show()
  else:
    plt.savefig(outFile)
  # clear plot and axis 
  plt.clf()
  plt.cla()

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
        outPrefix = sys.argv[2] + '/' + str(directory.split('/')[-1])
        out = open(outPrefix + '_table.txt', 'w+')
        chordData = readChordData(directory + '/' + file, transpose=int(sys.argv[3]))
        (joint, conditional, jointSamples, conditionalSamples) = generateProbabilityTables(chordData)

        # write output to file
        print >> out, 'Joint probabilities: P(t, t+1, ..., t+n) (where t+1 occurs right after t)'
        for (chordSequence, probability) in joint.iteritems():
          samples = jointSamples[chordSequence]
          print >> out, '  P(', list(chordSequence), ') = ', probability, '(', samples[0], '/', samples[1], ')' 

        print >> out, '\n'

        print >> out, 'Conditional probabilities: P(t+n | t, t+1, ..., t+(n-1))'
        for ((unknown, observed), probability) in conditional.iteritems():
          samples = conditionalSamples[(unknown, observed)]
          print >> out, '  P(', unknown, '|', list(observed), ') =', probability, '(', samples[0], '/', samples[1], ')'

        visualizeJoint(joint, outFile=(outPrefix + '_joint.pdf'))
        visualizeConditional(conditional, outFile=(outPrefix + '_conditional.pdf'))

        out.close()

