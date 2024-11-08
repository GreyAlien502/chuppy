import sys, tempfile

import mido

from utils.midi import toText, fromText 


if sys.argv[1] == '-d':
	text=sys.stdin.read()
	fromText(text,int(sys.argv[2])).save('/dev/stdout')
else:
	with tempfile.NamedTemporaryFile() as tmp:
		tmp.write(sys.stdin.buffer.read())
		tmp.flush()
		resolution,measures = map(int,sys.argv[1:])
		file = mido.MidiFile(tmp.name)
		text = toText(
			file.tracks[0],
			file.ticks_per_beat/resolution
		)
		print(text)
		print()
		print('# vim: nowrap colorcolumn='+
			','.join(str(column) for column in range(9,999,resolution*measures) )
		)




















