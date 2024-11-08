import sys, time, utils.instr, utils.gen

RATE = 48000
class synth(utils.instr.synthesizer):
	rate = RATE
	def synthesize(self,x):
		return utils.gen.env(x,length=self.length)*utils.gen.sin(x,utils.gen.midiFreq(self.note))/10

live = utils.instr.midi_audio(sys.argv[1],utils.instr.polyphonic(synth),RATE)
while live.player.is_active():time.sleep(1)
