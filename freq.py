import numpy as n
from scipy.signal import stft
import matplotlib as plot
import cv2
import sys

from utils.samp import fromFile

rate, song = fromFile(sys.argv[1])#'old/out/test.wav')#"/home/greyalien502/lib/music/Alice et Moi - Filme Moi (Clip Officiel)-NRqbMMTxmfw.mkv")

freqs, times, amplitudes = stft(
	song,
	rate,
	nperseg = rate/10,#,int(len(song)/(3840-2)+.0)),
	noverlap =  0,
)
#number_of_frequencies = n.where(freqs>4e3)[0][0]
#freqs = freqs[:number_of_frequencies]
#amplitudes = abs(amplitudes)[:number_of_frequencies,]
max_amp = amplitudes.max(axis=1)

hue = n.tile( n.log(freqs+.0001)/n.log(2)%1, (len(times),1) ).T
#saturations = (
#	( amplitudes/max_amp.max()* n.tile( amplitude/ max_amp, (len(times),1) ).T  )
#	for amplitude in amplitudes.T
#)
#value = (amplitudes / max_amp.max())

def square(vector):
	return n.tile(vector,(len(vector),1))

hue = n.log(square(freqs)/(square(freqs).T+.0001))/n.log(2)%1
saturation = 1+0*hue
values = (
	square(amplitude)*square(amplitude).T/max(amplitude)**2
	for amplitude
	in amplitudes.T
)

	

print(freqs.shape)
print(times.shape)
print(amplitudes.shape)
print(1/times[1])

print(amplitudes.shape[::-1])
print(hue.shape)
output = cv2.VideoWriter(
	'/tmp/output.mp4',
	cv2.VideoWriter_fourcc(*'mp4v'),
	1/times[1],
	hue.shape,
)
i=0
for value in values:
	import timeit
	#print ( [e.shape for e in ( hue, saturation, value )])
	output.write(
		(plot.colors.hsv_to_rgb(
			n.stack(
				( hue, saturation, value ),
				axis=-1,
			)
		)*255).astype('uint8')
	)
	i+=1
	print(str(i))
	if i == 100:
#...
		 break


output.release()
