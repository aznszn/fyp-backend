import sys
import os

current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(current_path))

import argparse
import subprocess as sp
import demucs.api
import io
from pathlib import Path
import select
from shutil import rmtree
from typing import Dict, Tuple, Optional, IO
import addchords
import Generate
import demucs.separate


# def copy_process_streams(process: sp.Popen):
#     def raw(stream: Optional[IO[bytes]]) -> IO[bytes]:
#         assert stream is not None
#         if isinstance(stream, io.BufferedIOBase):
#             stream = stream.raw
#         return stream
#
#     p_stdout, p_stderr = raw(process.stdout), raw(process.stderr)
#     stream_by_fd: Dict[int, Tuple[IO[bytes], io.StringIO, IO[str]]] = {
#         p_stdout.fileno(): (p_stdout, sys.stdout),
#         p_stderr.fileno(): (p_stderr, sys.stderr),
#     }
#     fds = list(stream_by_fd.keys())
#
#     while fds:
#         # `select` syscall will wait until one of the file descriptors has content.
#         ready, _, _ = select.select(fds, [], [])
#         for fd in ready:
#             p_stream, std = stream_by_fd[fd]
#             raw_buf = p_stream.read(2 ** 16)
#             if not raw_buf:
#                 fds.remove(fd)
#                 continue
#             buf = raw_buf.decode()
#             std.write(buf)
#             std.flush()
# def separate(inp=None, outp=None, model='htdemucs', mp3=False, float32=False, int24=True, two_stems='vocals'):
#     cmd = ["python3", "-m", "demucs.separate", "-o", str(outp), "-n", model]
#     if mp3:
#         cmd += ["--mp3", f"--mp3-bitrate="]
#     if float32:
#         cmd += ["--float32"]
#     if int24:
#         cmd += ["--int24"]
#     if two_stems is not None:
#         cmd += [f"--two-stems={two_stems}"]
#
#     files = [str(inp)]
#
#     print("Going to separate the files:")
#     print('\n'.join(files))
#     print("With command: ", " ".join(cmd))
#     p = sp.Popen(cmd + files, stdout=sp.PIPE, stderr=sp.PIPE)
#     copy_process_streams(p)
#     p.wait()
#     if p.returncode != 0:
#         print("Command failed, something went wrong.")

def main(input_file_name, drums='normal', piano=True, length=30):
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    input_file_path = os.path.join(curr_dir,"../", "inputs", input_file_name)
    file_base_name = str(os.path.splitext(os.path.basename(input_file_path))[0])
    
    separated_dir = os.path.join(curr_dir, "separated")
    separated_vocals_file_path = os.path.join(separated_dir, "htdemucs", file_base_name + "_vocals.wav")
    
    midi_vox_dir = os.path.join(curr_dir, "vox_midi")
    vox_midi_file_path = os.path.join(midi_vox_dir, file_base_name + "_vocals_basic_pitch.mid")
    
    midi_output_dir = os.path.join(curr_dir, "midi_output")
    midi_output_file_path = os.path.join(midi_output_dir, file_base_name + "_complete.mid")
    
    generated_output_dir = os.path.join(curr_dir, "generated")
    generated_midi_output_file_path = os.path.join(generated_output_dir, file_base_name+"_generated.mid")
    generated_output_file_path = os.path.join(generated_output_dir, file_base_name+"_generated.wav")
    
    
    final_output_file_path = os.path.join(curr_dir, "../","outputs", file_base_name + ".wav")
    
    demucs.separate.main(["--two-stems", "vocals", "-o", separated_dir, "--filename", "{track}_{stem}.{ext}", input_file_path])
    
    basic_pitch_command = f'basic-pitch {midi_vox_dir} {separated_vocals_file_path}'
    sp.run(basic_pitch_command, shell=True, check=True)

    addchords.main(vox_midi_file_path, file_base_name, midi_output_dir, drums, piano)

    Generate.main(midi_output_file_path,
                  os.path.join(generated_output_dir, file_base_name + "_generated.mid"),
                  os.path.join(generated_output_dir, file_base_name + "_generated.wav"),
                  length)
    
    merge_command = "ffmpeg -i " + generated_output_file_path + " -i " + separated_vocals_file_path + " -filter_complex amix=inputs=2:duration=shortest -y " + final_output_file_path
    sp.run(merge_command, shell=True, check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some musical options.')
    
    parser.add_argument('--drums', choices=[None, 'half_time', 'double_time', 'normal'], help='Select drum type')
    parser.add_argument('--piano', type=bool, help='Include piano (True/False)')
    parser.add_argument('--input_file_path', help='Input File path')
    parser.add_argument('--output_file_path', help='Output File Path')
    args = parser.parse_args()
    main(args)