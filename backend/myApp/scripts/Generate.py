import sys,time

import midi2audio
import transformers
from transformers import AutoModelForCausalLM

from anticipation import ops
from anticipation.sample import generate
from anticipation.tokenize import extract_instruments
from anticipation.convert import events_to_midi,midi_to_events
from anticipation.visuals import visualize
from anticipation.config import *
from anticipation.vocab import *

def synthesize(file_path, file_path_wav, fs, tokens):
    mid = events_to_midi(tokens)
    mid.save(file_path)
    fs.midi_to_audio(file_path, file_path_wav)
    return file_path_wav

def main(input_file, output_path, output_path_wav, length=30, start=0, melody_instrument=4):
    SMALL_MODEL = 'stanford-crfm/music-small-800k'     # faster inference, worse sample quality
    MEDIUM_MODEL = 'stanford-crfm/music-medium-800k'   # slower inference, better sample quality

# load an anticipatory music transformer
    model = AutoModelForCausalLM.from_pretrained(SMALL_MODEL).cuda()

# a MIDI synthesizer
    fs = midi2audio.FluidSynth('/usr/share/sounds/sf2/FluidR3_GM.sf2')
    events = midi_to_events(input_file)


    melody_instrument = 4

    segment = ops.clip(events, start, start + length)
    segment = ops.translate(segment, -ops.min_time(segment, seconds=False))

    print(ops.get_instruments(segment).keys())
    events, melody = extract_instruments(segment, [melody_instrument])

    history = ops.clip(events, 0, 5, clip_duration=False)

    accompaniment = generate(model, 5, length, inputs=history, controls=melody, top_p=0.96, debug=False)
    # output = ops.clip(ops.combine(accompaniment, melody), 0, length, clip_duration=True)
    synthesize(output_path, output_path_wav, fs, accompaniment)

    # synthesize(output_path, fs, output)

# the MIDI synthesis script



