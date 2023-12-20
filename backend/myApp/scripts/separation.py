import os
import demucs.separate

def main(input_file_name, stems):
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    separated_dir = os.path.join(curr_dir, "separated")
    input_file_path = os.path.join(curr_dir,"../", "inputs", input_file_name)
    file_base_name = str(os.path.splitext(os.path.basename(input_file_path))[0])
    
    if stems == 'vocals':
        demucs.separate.main(["--two-stems", "vocals", "-o", separated_dir, "--filename", "{track}_{stem}.{ext}", input_file_path])