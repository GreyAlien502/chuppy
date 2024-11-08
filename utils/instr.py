import numpy as np
import pyaudio
import mido

from utils.samp import resample, stretch_resample

class instrument:
	def __add__(self,other):
		class combinationSynth(instrument):
			def __init__(self,*synths):
				self.synths = synths
			def set(self,mess):
				for synth in self.synths:
					synth.set(mess)
			def get(self,size):
				return sum( synth.get(size) for synth in self.synths )
		return combinationSynth(self,other)
	def __call__(self,midi_file,tempo,rate):
		output = []
		for mess in midi_file.tracks[0]:
			output.append(self.get(int(mess.time/midi_file.ticks_per_beat/tempo*60*rate)))
			self.set(mess)
		#print(np.max(np.concatenate(output)))
		return np.concatenate(output)
	def __mul__(self,other):
		class filterSynth(instrument):
			def get(this,size):
				return other(self.get(size))
			def set(this,mess):
				return self.set(mess)
		return filterSynth()
		
class polyphonic(instrument):
	def __init__(self,f):
		self.notes = {}
		self.monophone = f
	def set(self,mess):
		#print(mess)
		#print(list(self.notes.keys()))
		if not 'note' in mess.type:
			return
		if mess.type == 'note_off' or mess.velocity == 0:
			try:
				self.notes[mess.note].set(mess)
			except KeyError:...
		elif mess.type == 'note_on':
			self.notes[mess.note] = self.monophone(mess)
	def get(self,size):
		for note,synth in list(self.notes.items()):
			if not synth.busy:
				del self.notes[note]
		return sum(
			(
				synth.get(size)
				for synth 
				in list(self.notes.values())
			),
			np.array([0]*size)
		)


class synthesizer(instrument):
	def __init__(self,mess):
		self.i = 0
		self.busy = True

		self.note = mess.note
		self.velocity = mess.velocity

		self.length = float('inf')
	def set(self,mess):
		if mess.type  == 'note_off' or mess.type == 'note_on' and mess.velocity == 0:
			self.length = self.i/self.rate
	def get(self,size):
		times = np.linspace(self.i/self.rate,(self.i+size)/self.rate,size, endpoint=False)
		self.i += size
		output = self.synthesize(times)
		if output.size > 0 and self.i/self.rate > self.length and np.all(output < 1e-10):
			self.busy = False
		return output

def sampler(samples,sample_rate,root=None,resample_method='stretch'):
	if root == None:
		resampler = lambda x,n: x
	elif resample_method == 'normal':
		resampler = lambda x,n: resample(x,2**((n-root)/12))
	elif resample_method == 'stretch':
		resampler = lambda x,n: stretch_resample(x,2**((n-root)/12),int(sample_rate*.05))
	else:
		raise Exception("invalid sampler type "+resample)
	samples = {
		notenum: resampler(samples[notenum],notenum)
		for notenum
		in range(12,135)#36,85)
	}
	class output(synthesizer):
		rate = sample_rate
		def synthesize(self,x):
			if len(x) ==0: return np.zeros(0)
			if len(x)>0 and self.length < x[-1]:
				self.busy = False
			sample = samples[self.note]
			if len(sample) == 0: return np.zeros(len(x))
			return np.take(sample,(x*self.rate).astype(np.int),mode='clip')/10
	return output



class midi_audio:
	def __init__(self, midi_port, instrument, rate, chunk=128*8, audio_device='default'):
		self.midi_portname = midi_port
		self.midiport= mido.open_input(
			midi_port,
			callback = instrument.set
		)

		def gen( size ):
			i=instrument.get( size )#/1e2
			i*=100
			return i
		def playing(audio):
			player.write(
				(32768 * audio).astype(np.int16),
				chunk
			)
		self.pyaudio               =   pyaudio.PyAudio()
		self.player = self.pyaudio.open(
			output_device_index= {i for i in range(self.pyaudio.get_device_count()) if self.pyaudio.get_device_info_by_index(i)['name']==audio_device}.pop(),
			format=pyaudio.paInt16,
			channels=1,
			rate=rate,
			output=True,
			frames_per_buffer=chunk,
			stream_callback=lambda input_data,frame_count,time_info,status_flag: ((32768 * gen(frame_count)).astype(np.int16),pyaudio.paContinue),
		)
	def close(self):
		self.player.stop_stream()
		self.player.close()
		self.pyaudio.terminate()
		self.midiport.close()
	def __enter__(self):
		return self
	def __exit__(self, exc_type, exc_val, exc_tb):
		self.close()

