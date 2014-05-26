#!/bin/python

class Chord:
  # in ascending semitone order
  validRoots = [
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
  ]
  emptyChordStrings = ['N', 'X']

  def __init__(self, chordString):
    self.rootIndex = None # left side of : (eg D#)
    self.quality = None # right side of : (eg min7)

    chordString = chordString.split(':')

    # handle "empty" note case
    if chordString[0] in Chord.emptyChordStrings:
      self.rootIndex = -1
      self.quality = 'None'
    # handle "regular" note case
    else: 
      if len(chordString) != 2:
        print chordString
        raise Exception('bad chordString')

      # search the validRoots for anything that matches the input string
      for (index, roots) in enumerate(Chord.validRoots):
        for root in roots:
          if chordString[0] == root:
            self.rootIndex = index

      # if couldn't find anything in valid roots
      if self.rootIndex == None:
        raise Exception('bad chordString')

      self.quality = chordString[1]

  def __str__(self):
    if self.rootIndex == -1:
      return Chord.emptyChordStrings[0]
    else:
      return Chord.validRoots[self.rootIndex][0] + ':' + self.quality

  def __eq__(self, other):
    return str(self) == str(other)

  def transposed(self, numSemitones):
    # don't transpose if the note is empty
    newChord = Chord(str(self))
    if newChord.rootIndex != -1:
      newChord.rootIndex = (newChord.rootIndex + numSemitones) % len(Chord.validRoots)
    return newChord

# some quick unit tests
if __name__ == '__main__': 
  assert Chord('Bb:maj') == Chord('A#:maj')
  assert Chord('F:7').transposed(1) == Chord('F#:7')
  assert Chord('G:7').transposed(11) == Chord('F#:7')
  print 'All tests passed'


