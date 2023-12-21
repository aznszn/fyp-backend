import sys
import os

current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_path))

import demucs.separate
import Generate
import addchords
from typing import Dict, Tuple, Optional, IO
from shutil import rmtree
import select
from pathlib import Path
import io
import demucs.api
import subprocess as sp
import argparse
from pydub import AudioSegment

def main(input_file_name, drums='normal', piano=True, length=30):
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(curr_dir, "../", "inputs", input_file_name)
    file_base_name = str(os.path.splitext(
        os.path.basename(input_file_path))[0])

    separated_dir = os.path.join(curr_dir, "separated")
    separated_vocals_file_path = os.path.join(
        separated_dir, "htdemucs", file_base_name + "_vocals.wav")

    midi_vox_dir = os.path.join(curr_dir, "vox_midi")
    vox_midi_file_path = os.path.join(
        midi_vox_dir, file_base_name + "_vocals_basic_pitch.mid")

    midi_output_dir = os.path.join(curr_dir, "midi_output")
    midi_output_file_path = os.path.join(
        midi_output_dir, file_base_name + "_complete.mid")

    generated_output_dir = os.path.join(curr_dir, "generated")
    generated_midi_output_file_path = os.path.join(
        generated_output_dir, file_base_name+"_generated.mid")
    generated_output_file_path = os.path.join(
        generated_output_dir, file_base_name+"_generated.wav")

    final_output_file_path = os.path.join(
        curr_dir, "../", "outputs", file_base_name + ".wav")

    demucs.separate.main(["--two-stems", "vocals", "-o", separated_dir, "--filename", "{track}_{stem}.{ext}", input_file_path])

    basic_pitch_command = f'basic-pitch {midi_vox_dir} {separated_vocals_file_path}'
    sp.run(basic_pitch_command, shell=True, check=True)

    addchords.main(vox_midi_file_path, file_base_name, midi_output_dir, drums, piano)

    Generate.main(midi_output_file_path,
                  os.path.join(generated_output_dir, file_base_name + "_generated.mid"),
                  os.path.join(generated_output_dir, file_base_name + "_generated.wav"),
                  length)
    print("Generation done, rendering...")
    merge_command = "ffmpeg -i " + generated_output_file_path + " -i " + separated_vocals_file_path + " -filter_complex amix=inputs=2:duration=shortest -y " + final_output_file_path
    (AudioSegment.from_file(generated_output_file_path) + 13).overlay(AudioSegment.from_file(separated_vocals_file_path)).export(final_output_file_path, format="wav")
    # sp.run(merge_command, shell=True, check=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Process some musical options.')

    parser.add_argument(
        '--drums', choices=[None, 'half_time', 'double_time', 'normal'], help='Select drum type')
    parser.add_argument('--piano', type=bool,
                        help='Include piano (True/False)')
    parser.add_argument('--input_file_path', help='Input File path')
    parser.add_argument('--output_file_path', help='Output File Path')
    args = parser.parse_args()
    main(args)
