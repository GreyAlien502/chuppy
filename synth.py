print('importing...')
import itertools, sys, collections, time
from collections import defaultdict

import numpy as np
import scipy.signal
import pyaudio
import mido
import matplotlib.pyplot

from utils.gen import sin, saw, sqr, env, midiFreq
from utils.proc import filter, echo, reverber, normalize
from utils.samp import fromFile, sub, resample, stretch_resample, add, write

RATE    = 48000

from utils.instr import synthesizer, sampler, midi_audio, polyphonic


#matplotlib.pyplot.figure().add_subplot(111).plot(
#	(fromFile('hit.wav')[1])*2**24,
#)[0].figure.get_axes()[0].plot(
#	fromFile('hite.wav')[1]
#)[0].figure.savefig('plt.png')
#
#1/0


print('making filters...');

def ltrim(sound):
	return sound[np.where(reverb==max(reverb))[0][0]:]

_,reverb = fromFile('resources/room.wav');
reverb = filter('high',RATE,(20,))(sub(
	RATE,
	ltrim(reverb),
	0,
	.08
))
reverb = reverb/np.sqrt(sum(reverb**2))
reverb_filter = reverber(reverb/np.sqrt(sum(reverb**2)))
def distort(x,gain,wetness=1):
	return (
		(1-wetness)*x
		+ wetness*np.max([
			np.min([
				x*gain,
				x*0+1
			],axis=0),
			x*0-1
			],axis=0
		)
	)
class maximizer:
	def __init__(self):
		self.filter = reverber( np.linspace(1,0,int(.050*RATE)) )
	def __call__(self,x):
		volumes = self.filter(x**2)
		print(int(volumes[0]))
		return x/(np.sqrt(volumes+.01))




tempo = 125




print('making instruments...');


print('making basynth...')
class basslines(synthesizer):
	rate = RATE
	def synthesize(self,x):
		f = midiFreq(self.note)/1
		return 3/5*(
			env(x,.04,3,.5,.1,self.length)*(saw(x,f)+saw(x,f/4)/3)/4
			+
			env(x,.0,31,.4,.2,self.length)*(saw(x,f*2))/2

		)
bassline = polyphonic(basslines) * filter('low',RATE,(10000,),1)

print('making piano...')
piano_sound = sub(
		*fromFile('resources/a single note - the finale-IjY5QwXvbVM.m4a'),
		1.475,
		5
	)
piano = polyphonic(sampler(
	defaultdict(lambda x=normalize(add(piano_sound,scipy.signal.decimate(piano_sound,2))):x),
	RATE,
	73-12*np.log2(44100/48000),
)) #* (lambda x:distort(x,2000,.5)/20) * filter('low',RATE,(10000,),2);

print('making drums...')
drums = polyphonic(sampler(
	defaultdict(lambda:np.zeros(0),{
		36: normalize(filter('low',RATE,(4000,),2)(resample(sub(*fromFile('resources/hit.wav'),.35,.4),-32))),
		38: normalize(filter('band',RATE,(2000,8000),2)(sub(*fromFile('resources/cht.wav'),.55,.7))),
		40: normalize(filter('high',RATE,(6000,),2)(resample(sub(*fromFile('resources/sss.wav'),.16,1),13)))/13.4,
		41: normalize(reverb_filter(resample(sub(*fromFile('resources/ch.wav'),.8,.9),0)))/4,
		41: normalize(reverb_filter(resample(sub(*fromFile('resources/tss.wav'),.8,1.9),0)))/4,
	}),
	RATE
))
			
print('making pad...')
class pad(synthesizer):
	rate = RATE
	def synthesize(self,x):
		f = midiFreq(self.note)*3
		return 1/10*(
			env(x,attack=.1,sustain=.3,decay=3,release=.2,length=self.length)*sin(x,f)
			+
			env(x,attack=.3,release=.3,length=self.length)*
			sin(x+.03/(tremolo_freq:=tempo/60*4)/2/np.pi*sin(x,tremolo_freq),f/2)
			#np.sin(x*2*np.pi*f/2 + 1/(tremolo_freq:=tempo/60*2*np.pi)*np.sin(x*tremolo_freq) )
		)*(sin(x,tempo/60/2)*.3+.8)
pad = polyphonic(pad) *(
reverber(
 	1*add(
		(reverb_sample:=sub(*fromFile('resources/44 Magnum Single Gunshot Sound Effect-iKmaMjesWQc.m4a'),1.09,1.9).astype(np.float64))
		/
		np.sqrt(sum(reverb_sample**2))/2,
		np.array([1])
	)
)
)* filter('band',RATE,(300,13000),1)






#f = \sin( \int odt )
#f = \sin( \bar o ( 1 + \alpha \sin( \beta t ) ) dt )
#f = \sin( \bar o ( 1 + \alpha \sin( \beta t ) ) dt/d(\beta t)d(\beta t) )
#f = \sin( \bar o ( 1 + \alpha/\beta \sin( \beta t ) ) d(\beta t) )
#f = \sin( \bar o ( 1 + \alpha/\beta \cos( \beta t ) ) )







echoer = echo(RATE*.1,.1)










print('setting up player...');


#write( (pad(mido.MidiFile(sys.argv[2]),145)*2**31).astype(np.int32), RATE, 'test.wav')
#1/0


live = midi_audio(sys.argv[1],piano+bassline+pad,RATE)
if len(sys.argv) == 2:
	while live.player.is_active():time.sleep(1)
else:
	midi_file = sys.argv[2]






background = np.zeros(0);lambda: add(
	bassline(mido.MidiFile('bassline.midi'),tempo)/3,
add(
	piano(mido.MidiFile('sequence.midi'),tempo)*.6,
	np.tile(drums(mido.MidiFile('drums.midi'),tempo)*6,4),
))

import os;
last_time = 0;
while live.player.is_active():
	try:
		if last_time < os.stat(midi_file).st_mtime:
			last_time = os.stat(midi_file).st_mtime;
			print('writing...........');
			piano.get(2)
			write(
				( (

					filter('band',RATE,(20,20000),5)(#add(
						#background,
						piano(mido.MidiFile(midi_file),tempo)
					)#)
				)*2**31).astype(np.int32),
				RATE,
				'test.wav'
			);
	except FileNotFoundError:...
	time.sleep(.1);



live.close();
