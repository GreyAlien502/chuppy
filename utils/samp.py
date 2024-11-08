import numpy as n
import scipy.signal as sig

class Sound:
	def __init__(self,rate,data):
		self.a = data
		self.rate = float(rate)
	def fromFile(filename):
		import pydub as pd
		sound = pd.AudioSegment.from_file(filename).split_to_mono()[0]
		return Sound(
			sound.frame_rate,
			n.array(sound.get_array_of_samples())
		)
	def write(self,filename):
		from scipy.io.wavfile import write
		write(filename,rate,data.astype('int32'))
	def __getitem__(self,key):
		def index(time):
			return int(time*self.rate)
		return Sound(self.rate,self.a[index(key.start):index(key.stop)])
	def respeed(self,step):
		return Sound(self.rate,sig.resample(self.a,len(self.a)*2**(step/12)))

def write(data,rate,filename):
	from scipy.io.wavfile import write
	write(filename,rate,data.astype('int32'))

def fromArray(array,rate):
	return array,rate
def fromFile(filename):
	import pydub as pd
	sound = pd.AudioSegment.from_file(filename).split_to_mono()[0]
	return (
		sound.frame_rate,
		n.array(sound.get_array_of_samples())
	)
def sub(sampleRate,data,start,stop):
	def index(time):
		return int(time*sampleRate)
	return data[index(start):index(start)+index(stop-start)]


def reverb(sound,room,wetness):
	start = n.argmax(room)
	return (
		(1-wetness)*sound
		+wetness * sig.convolve(
			sound,
			.4*room/n.sum(room)#n.sqrt(n.sum(room**2))
		)[start:start+len(sound)]
	)

def resample(sound,halfsteps):
	print(f'''I'm now resampling by {halfsteps} halfsteps.''')
	return n.interp(
		n.arange(len(sound),step=2**(halfsteps/12)),
		n.arange(len(sound)),
		sound,
	)
def stretch_resample(sound,ratio,window_size):
	sample_range = n.linspace(0,int(len(sound)*ratio),num=len(sound),endpoint=False,dtype=n.int)
	phase = sample_range % window_size 
	window = (sample_range / ratio / window_size).astype(n.int)
	return (
		+n.take(sound, window*window_size + phase,mode='clip')*n.sqrt(phase/window_size)
		+n.take(sound, (window+1)*window_size + phase, mode='clip')*n.sqrt(1-phase/window_size)
	)

def add(*sounds):
	def resize(array,size):
		array = array.copy()
		array.resize(size)
		return array

	return n.sum(
		[sounds[0]]+[resize(sound,sounds[0].shape) for sound in sounds[1:]],
		axis=0
	)
