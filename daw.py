import sys, time, importlib, os, threading, traceback
import numpy as n

import mido

from utils.instr import instrument, midi_audio

arguments=dict(x.lstrip('-').split('=') for x in sys.argv[1:])

TEMPO=int(arguments.get('tempo',120))
RATE=48000

print=lambda*args,**kwargs:__builtins__.print(*args,**kwargs,flush=True)
		
def printn(args):
	print(args)
	return args
def printError(e):
	print(''.join(traceback.TracebackException.from_exception(e).format()))


class looper(instrument):
	def __init__(self,song):
		self.song = song
		self.samplenum = 0
	def get(self,size):
		samplenum_0 = self.samplenum
		self.samplenum = (self.samplenum+size) % len(self.song)
		return n.take(
			self.song,
			n.r_[samplenum_0:samplenum_0+size],
			mode='wrap'
		)
	def set(self,message):...
class multiplexer(instrument):
	def __init__(self,instruments):
		self.instrument = None
		self.instruments = instruments

	def get(self,size):
		current_instrument = self.get_instrument()
		return ( 0
			if not isinstance(current_instrument,instrument)
			else current_instrument.get(size)
		)
	def set(self,message):
		if self.get_instrument():
			self.get_instrument().set(message)
	def get_instrument(self):
		try:
			return getattr(self.instruments,self.instrument)
		except AttributeError:...
		except TypeError:...
class midi_recorder(instrument):
	def __init__(self,followee,loop_length,file):
		self.file = file
		self.followee = followee

		self.last_tick = 0
		self.midi_tracks = [[]]
	def get(self,size):
		samplenum_0 = self.followee.samplenum
		if (
			samplenum_0 % self.loop_length_in_samples() < (samplenum_0-size) % self.loop_length_in_samples()
			and
			self.midi_tracks[-1]
		):
			print(f">>{len(self.midi_tracks)}")
			self.add_message(mido.MetaMessage('end_of_track'),self.loop_length_in_samples())
			self.last_tick = 0
			self.midi_tracks.append([])
			self.write_track(-2)#threading.Thread(target=lambda: self.write_track(-2) ,daemon=True).start()
		return n.zeros(size)
	def set(self,message):
		if not self.midi_tracks[-1]:
			self.write_track() # clear the file before writing to it
		if not message.is_realtime:
			self.add_message(message,self.followee.samplenum%self.loop_length_in_samples())
	def write_track(self,track_index=None):
		print('>>>'+str(track_index))
		midi_file = mido.MidiFile(type=0)
		midi_file.add_track().extend(
			self.midi_tracks[track_index]
			if track_index != None else
			[mido.MetaMessage('end_of_track',time=self.samples_to_ticks(self.loop_length_in_samples()))]
		)
		try:
			midi_file.save(self.file)
		except IOError as e:
			print(e)
	def add_message(self,message,samples):
		message.time = max(0, self.samples_to_ticks(samples)-self.last_tick)
		self.last_tick += message.time
		self.midi_tracks[-1].append(message)
	def samples_to_ticks(self,samples):
		return int((samples)/RATE/60*TEMPO*mido.MidiFile(type=0).ticks_per_beat)
		

	def loop_length_in_samples(self):
		return len(self.followee.song)
	


sauce = sys.argv[0]

class updater:
	def __init__(self,file,module):
		self.file =  file
		self.module = module
		self.last_checked = time.time()
	def get_latest(self):
		last_updated = os.stat(self.file).st_mtime
		if self.last_checked < last_updated:
			self.last_checked = last_updated
			importlib.reload(self.module)
			return self.module

sys.path.append('.')
import instruments
instrument_updater = updater('instruments.py',instruments)
import song
song_updater = updater('song.py',song)


volume = 1
song_loop = looper(song.generate(instruments))
live = multiplexer(instruments)
recorder = midi_recorder(song_loop,4,'/dev/null')
combo_player = song_loop+live+recorder

live.instrument=arguments.get('instrument',None)
def reload_files():
	print=lambda*args:__builtins__.print(*args,flush=True)
	midi_audio_player = midi_audio(arguments.get('port','Midi Through Port-0'),combo_player*(lambda x:x*volume),RATE,chunk=128*3,audio_device=arguments.get('audio-device','HDA Intel PCH: ALC3235 Analog (hw:0,0)'))
	while True:
		try:
			if not midi_audio_player.player.is_active():
				print('reconecting_to_audio')
				midi_audio_player.close()
				midi_audio_player = midi_audio(sys.argv[1],combo_player,RATE)
			if instrument_updater.get_latest():
				print('reloading instrument')
				live.instruments = instruments
				song_loop.song = song.generate(instruments)
			if song_updater.get_latest():
				print('reloading song')
				song_loop.song = song.generate(instruments)
				print(len(song_loop.song)/recorder.loop_length_in_samples())
		except Exception as e:
			printError(e)
		time.sleep(1)
threading.Thread(target=reload_files,daemon=True).start()

for line in sys.stdin:
	try:
		command = line.rstrip().split()
		if len(command) == 0:
			...
		elif command[0] == 'i':
			if len(command) == 1:
				print(f'i:{live.instrument}')
			else:
				live.instrument = command[1]
		elif command[0] == 'l':
			if len(command) == 1:
				print(f'l:{recorder.loop_length}')
			else:
				recorder.loop_length = int(command[1])
		elif command[0] == 'f':
			if len(command) == 1:
				print(f'f:{recorder.file}')
			else:
				recorder.file = command[1]
		elif command[0] == 'w':
			if len(command) == 1:
				print(len(recorder.midi_tracks))
			else:
				recorder.write_track(int(command[1]))
		elif command[0] == 't':
			if len(command) == 1:
				print(f't:{TEMPO}')
			else:
				TEMPO=int(command[1])
		elif command[0] == 'v':
			if len(command) == 1:
				print(f'v:{volume}')
			else:
				volume=float(command[1])
		elif command[0] == '0':
			song_loop.samplenum = 0
		elif command == ['clear']:
			recorder.midi_tracks = [[]]
		elif command == ['q']:
			break
		else:
			print(f'''I don't know what "{command[0]}" means''')
	except Exception as e:
		printError(e)
