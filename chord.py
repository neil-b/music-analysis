#!/bin/python

class Chord:
  # in ascending semitone order
  # roots in the same subarray are considererd equivalent
  validRoots = {
    'standard': [
      ['A'],
      ['A#', 'Bb'],
      ['B', 'Cb'],
      ['C'],
      ['C#', 'Db'],
      ['D'],
      ['D#', 'Eb'],
      ['E', 'Fb'],
      ['F'],
      ['F#', 'Gb'],
      ['G'],
      ['G#', 'Ab'],
    ],
    'nonstandard': [
      ['N'],
      ['X'],
    ]
  }

  def __init__(self, chordString):
    self.rootClass = None # 'standard' or 'nonstandard'
    self.rootIndex = None # left side of : (eg D#)
    self.quality = None # right side of : (eg min7)

    chordString = chordString.split(':')

    if len(chordString) != 1 and len(chordString) != 2:
      print chordString
      raise Exception('bad chordString')

    # search the validRoots for anything that matches the input string
    for rootClass in Chord.validRoots.keys():
      for (index, roots) in enumerate(Chord.validRoots[rootClass]):
        for root in roots:
          if chordString[0] == root:
            self.rootIndex = index
            self.rootClass = rootClass

    # if couldn't find anything in valid roots
    if self.rootIndex == None:
      raise Exception('bad chordString')

    if len(chordString) == 2:
      self.quality = chordString[1]

  def __str__(self):
    ret = Chord.validRoots[self.rootClass][self.rootIndex][0]
    if self.quality != None:
      ret += ':' + self.quality
    return ret

  def __eq__(self, other):
    return str(self) == str(other)

  def transposed(self, numSemitones):
    newChord = Chord(str(self))
    # don't transpose if the note is nonstandard (eg 'X' or 'N')
    if self.rootClass == 'standard':
      newChord.rootIndex = (newChord.rootIndex + numSemitones) % len(Chord.validRoots[self.rootClass])
    return newChord

# some quick unit tests
if __name__ == '__main__': 
  assert Chord('Bb:maj') == Chord('A#:maj')
  assert Chord('F:7').transposed(1) == Chord('F#:7')
  assert Chord('G:7').transposed(11) == Chord('F#:7')
  assert Chord('X:7') != Chord('A#:7')
  assert Chord('N') != Chord('X')
  print 'All tests passed'


