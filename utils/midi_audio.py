import itertools, sys, collections, time
from collections import defaultdict

import numpy as np
import pyaudio
import mido
import matplotlib.pyplot

from utils.gen import sin, saw, sqr, env, midiFreq
from utils.proc import filter, echo, reverber, normalize
from utils.samp import fromFile, sub, resample, add, write

class midi_audio:
	def __init__(self, midi_port, instrument):
		self.midi_portname = midi_port
		self.midiport= mido.open_input(
			midi_port,
			callback = instrument.set
		)

		def gen( size ):
			i=instrument.get( size )/1e2 #maximizer()(echoer( synth.get( size ) ))
			i*=100
			return i
		def playing(audio):
			player.write(
				(32768 * audio).astype(np.int16),
				CHUNK
			)
		self.pyaudio               =   pyaudio.PyAudio()
		self.player = self.pyaudio.open(
			output_device_index= {i for i in range(self.pyaudio.get_device_count()) if self.pyaudio.get_device_info_by_index(i)['name']=='default'}.pop(),
			format=pyaudio.paInt16,
			channels=1,
			rate=RATE,
			output=True,
			frames_per_buffer=CHUNK,
			stream_callback=lambda input_data,frame_count,time_info,status_flag: ((32768 * gen(frame_count)).astype(np.int16),pyaudio.paContinue),
		)
	def close(self):
		self.player.stop_stream()
		self.player.close()
		self.pyaudio.terminate()
		self.midiport.close()

