import numpy as n
import scipy.signal as sig
from random import sample

import utils.samp
def printn(x):
	print(len(x))
	return x

def deoct(tone):
	return n.exp(n.log(tone)%n.log(2))
def synth(x,f):
	f *= 2
	return (
		env(x,.1,1,.9) * (
			n.mean([
				saw(x,f/2)/2,
				saw(x,f*3/2)/4,
				saw(x,f*5/4)/4,
				saw(x,f)*2,
			],axis=0)
		) * ( 1 + .7*sin(x,600) * env(x,0,3,.2) )
		+ sin(x,f) * env(x,.01)
	)
def saw(x,frequency):
	return x*frequency%2 -1
def sin(x,frequency):
	return n.sin(x*frequency*2*n.pi)
def sqr(x,frequency,duty=.5):
	return sig.square(x*frequency*2*n.pi,duty)

def env(x, attack = 0, decay = 0, sustain = 1, release = 0, length = float('inf')):
	def decaying_value(x):
		return 
	return n.piecewise(
		x,
		[
			x < attack,
			x >= attack
		],
		[
			lambda x: x/attack,
			lambda x: sustain + (1-sustain)*n.exp(-decay* (x-attack)),
		]
	) * n.piecewise(
		x,
		[
			x < length,
			n.logical_and( length <= x,x < length+release ),
			length+release <= x
		],
		[
			lambda x: 1,
			lambda x: 1 - (x-length)/release,
			lambda x: 0,
		]
	)


def midiFreq(notenum,tones=12):
	return 8.175798915*2**(notenum/tones)

def play(generator,tune, tones=12, freqGen=midiFreq):
	return n.concatenate([
		generator( line(rate,duration), freqGen(note[0]+69,tones) )
		for note in tune
	])
def line(rate,duration):
	return n.linspace(0,duration,rate*duration)

def gen(rate,duration,note,volume=1):
	frequency = midiFreq(note)
	return synth(line(rate,duration),frequency)*1e9*volume



import scipy.signal as sig

def filt(type_,data, rate, cutoff, order=5):
    return sig.lfilter(
	*sig.butter(
		order,
		2*cutoff/rate,
		btype='low'
	),
	data
    )
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

