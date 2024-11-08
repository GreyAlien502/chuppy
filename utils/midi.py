import sys, re
from collections import defaultdict
from itertools import groupby
from functools import reduce

import numpy as n
import mido

prin = lambda x:(print(x,file=sys.stderr),x)[1]


default_note = 'CI.'
	
def toText(track,resolution=4,example_note=default_note):
	start_char,contiuation_char,bg_char = example_note
	for i in range(len(track)-1):
		track[i+1].time += track[i].time
	notes = [
		m
		for m in track
		if 'note' in m.type
	]
	note_numbers = [
		n.note
		for n in notes
	]
	if not note_numbers: return '\n'
	note_range = range(
		max(note_numbers),
		min(note_numbers)-1,
		-1
	)

	def keyColor(number):
		return number%12 in [1,3,6,8,10]

	lines = {
		note: [
			'# ' if keyColor(note) else '  ',
			str(note),
			'\t',
		]
		for note in note_range
	}
	note_state = defaultdict(lambda:bg_char)
	tick = 0
	for message in track:
		while tick+resolution/2 < message.time:
			for note in note_range:
				lines[note].append(note_state[note])
				if note_state[note] == start_char:
					note_state[note] = contiuation_char
			tick += resolution
		if 'note' in message.type:
			note_state[message.note] =(
				start_char
				if message.type == 'note_on' and message.velocity!=0 else
				bg_char
			)
		
	return '\n'.join(''.join(lines[note]) for note in note_range);

def fromText(text,resolution,example_note=default_note):
	start_char,contiuation_char,bg_char = example_note
	file = mido.MidiFile(type=0)
	lines = text.splitlines()+['']
	lines = lines[:lines.index('')]
	import sys
	lines = [
		re.search(fr'^[# ] (\d*)\t(.*)$',line)
		for line in lines
	]
	notes_by_absolute_time = [
		(beat, mido.Message(type,note=notenum))
		for (notenum,note_data) in (
			(int(line.group(1)),line.group(2))
			for line in lines
		)
		for match in re.finditer(fr'{re.escape(start_char)}{re.escape(contiuation_char)}*',note_data)
		for (beat,type) in (
			(match.start(),'note_on'),
			(match.end(),'note_off'),
		)
	] + [
		(len(lines[0].group(2)), mido.MetaMessage('end_of_track'))
	]
	notes_by_absolute_time.sort(key=lambda n:n[0])
	
	absolute_ticks=0
	for note_info in notes_by_absolute_time:
		note_info[1].time = int(note_info[0]*file.ticks_per_beat/resolution) - absolute_ticks
		absolute_ticks += note_info[1].time

	file.add_track().extend([ note_info[1] for note_info in notes_by_absolute_time ])
	return file


def gen(track, instrument, sample_rate=8000):
	def group_by(items,grouper):
		return dict(map(
			lambda group: (group[0], list(group[1])),
			groupby(sorted(items,key=grouper),grouper)
		))
	for i in range(len(track)-1):
		track[i+1].time += track[i].time
	messages_by_type = group_by(track, lambda message: message.type)

	if 'set_tempo' in messages_by_type:
		tempo = messages_by_type['set_tempo'][0].tempo/1e9
	else:
		tempo = .5
	tempo = 1.2/1000

	length = messages_by_type['end_of_track'][0].time

	notes = sorted(
		map(
			lambda notes:
				( notes[0].time, notes[1].time, notes[0].note, notes[0].velocity/100),
			reduce(list.__add__,
				map(
					lambda notes: list(zip(*(iter(sorted(notes,key=lambda note:note.time)),) * 2)),
					group_by(messages_by_type['note_on'],lambda message: message.note).values()
				)
			)
		),
		key= lambda note: note[0]
	)

	output = n.zeros(int(sample_rate*tempo*length))
	for note in notes:
		if(note[1]-note[0]) > 0:
			audio = instrument(sample_rate,(note[1]-note[0])*tempo,note[2],note[3])
			start_sample = int(note[0]*tempo*sample_rate)
			output[start_sample:start_sample+len(audio)] += audio*note[3]
	return output

def fileFromTrack(track):
	output = mido.MidiFile()
	output.tracks.append(track)
	return output

def absoluteTime(track):
	output = mido.MidiTrack(mess.copy() for mess in track)
	time = 0
	for mess in output:
		time += mess.time
		mess.time = time
	return output

def archipegio(pattern,chord):
	pattern = pattern.tracks[0]
	input_notes = sorted({message.note for message in pattern if message.type =='note_on'})
	note_map = {input:output for (input,output) in zip(input_notes,chord)}
	output = mido.MidiTrack(mess.copy() for mess in pattern)
	for message in output:
		if 'note' in message.type:
			message.note = note_map[message.note]
	return fileFromTrack(output)

def chords(file):
	track = file.tracks[0]
	notes = [set()]
	for mess in absoluteTime(track):
		if mess.time != 0:
			notes.append(set())
		if 'note' in mess.type:
			notes[-1].add(mess.note)
	return notes[:-1]

def transpose(file,amount):
	track = file.tracks[0]
	output = mido.MidiTrack(mess.copy() for mess in track)
	for mess in output:
		if 'note' in mess.type:
			mess.note += amount
	return fileFromTrack(output)

def concat(*files):
	track = file[0].track[0]
	for next_file in files[1:]:
		final_rest = track.pop().time
		track.append(next_file.track[0][0])
		track[-1].time += final_rest
		track.extend(next_file.track[0][1:])
	return file[0]


def overlay(*files):
	messages = []
	for file in files:
		time = 0
		for message in file.tracks[0]:
			time += message.time
			messages.append( (time,message) )
	sort(messages)

	track = tracks[0].copy()
	for time,message in messages:
		track.append(message.copy(time=time))

	files[0].tracks = [track]
	return files[0]
