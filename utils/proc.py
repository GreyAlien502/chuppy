import numpy as n
import scipy.signal as sig

class circular_buffer:
	def __init__(self,initial):
		self.index = 0
		self.buffer = initial
	def array(self):
		return n.roll(self.buffer, -self.index)
		#return n.concatenate(self.buffer[self.index:],self.buffer[:self.index])
	def append(self,input):
		self.buffer[self.index,self.index+len(input)] = input

def normalize(array,nuvomax=1):
	return array*(nuvomax/max(abs(array)))
def filt(type_,data, rate, cutoff, order=5):
    return sig.lfilter(
	*sig.butter(
		order,
		2*cutoff/rate,
		btype='low'
	),
	data
    )

class filterer:
	def __init__(self,state_0,processor):
		self.state = state_0
		self.processor = processor
	def __call__(self,data):
		output, self.state = self.processor(self.state,data)
		return output
def filter(type_, rate, cutoffs, order=5):
	coeffs = sig.butter(
		order,
		tuple(2*cutoff/rate for cutoff in cutoffs),
		btype=type_
	)
	def bitch(state,data):
			print(type_,cutoffs,order,'stts',len(data),len(data)  and n.max(abs(data)) , len(out[0])  and n.max(abs(out[0])), len(out[0])  and n.min(abs(out[0])) ),
			return out
	return filterer(
		sig.lfiltic(*coeffs,n.zeros(0)),
		lambda state,data:
			sig.lfilter(
				*coeffs,
				data,
				zi = state
			)
	)
# y(n) = (1-W)x(n) + Wy(n-D)
# b_0 = sqrt(1-W**2)
# a_D = W
# All the other ones are 0.

class echo:
	def __init__(self,delay,wetness):
		self.delay = delay
		self.wetness = wetness
		self.buffer = numpy.zeros(delay)
	def __call__(self,data):
		echo_sound = numpy.concatenate(uelf.buffer,data)
		output = numpy.array([])
		while len(output) < len(data):
			output = numpy.concatenate(output,b)
			
def echo(delay,wetness):
	delay=int(delay)
	return filterer(
		[0]*(delay-1),
		lambda state,data:
			sig.lfilter(
				n.array([n.sqrt(1-wetness**2)]+[0]*(delay-1)),
				n.array([1]+[0]*(delay-2)+[wetness]),
				data,
				zi = state
			)
	)
def slow_reverber(room):
	return filterer(
		n.zeros(len(room)),
		lambda state,data:
			sig.lfilter(
				room,
				n.array([1]+[0]*(len(room))),
				data,
				zi = state
			)
	)
class reverber:
	def __init__(self,room):
		self.room=room
		self.state=n.zeros(0)
	def __call__(self,data):
		if len(data) == 0:
			return data
		convolution = sig.convolve(data,self.room)
		self.state.resize(convolution.shape)
		convolution += self.state
		self.state = convolution[len(data):].copy()
		return convolution[:len(data)]


			

def reverb(sound,room,wetness):
	start = n.argmax(room)
	return (
		(1-wetness)*sound
		+wetness * sig.convolve(
			sound,
			.4*room/n.sum(room)#n.sqrt(n.sum(room**2))
		)[start:start+len(sound)]
	)

def resample(sound,factor):
		return sig.resample(sound,int(len(sound)*factor))
def f(halfsteps):
		return 2**(-halfsteps/12)

