import mido

traaq = mido.MidiFile('old/ce-soir.midi').tracks[0]
print(*traaq,sep='\n')

e='mc squaredt'
