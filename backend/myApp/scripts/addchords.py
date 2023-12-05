from music21 import chord, stream, key, interval, converter, scale, note, instrument, dynamics, midi, meter, tempo
from math import ceil
import os

def arpeggiate(c, l):
    arpeggio_notes = []

    arpeggio_pattern = [0, 1, 2, 1, 3]
    arpeggio_quarter_length = l / len(arpeggio_pattern)

    for index in arpeggio_pattern:
        pitch = c.pitches[index % len(c.pitches)]  # Get the pitch from the chord
        note_obj = note.Note(pitch)
        note_obj.quarterLength = arpeggio_quarter_length  # Set the duration
        arpeggio_notes.append(note_obj)  # Append the note to the list of notes
    return arpeggio_notes

def addDrums(start_offset, measure_duration, drums_stream, drums):
    if(drums == 'half_time'):
        hihat_note = note.Note()
        hihat_note.pitch.midi = 42
        drums_stream.insert(start_offset + measure_duration/2, hihat_note)
        kick_note = note.Note()
        kick_note.pitch.midi = 35
        drums_stream.insert(start_offset + measure_duration/2, kick_note)
        
        hihat_note = note.Note()
        hihat_note.pitch.midi = 42
        drums_stream.insert(start_offset + measure_duration/8 + measure_duration/2, hihat_note)

        hihat_note = note.Note()
        hihat_note.pitch.midi = 42
        drums_stream.insert(start_offset + measure_duration/4 + measure_duration/2, hihat_note)
        snare_note = note.Note()
        snare_note.pitch.midi = 38
        drums_stream.insert(start_offset + measure_duration/4 + measure_duration/2, snare_note)
        
        hihat_note = note.Note()
        hihat_note.pitch.midi = 42
        drums_stream.insert(start_offset + 3*measure_duration/8 + measure_duration/2, hihat_note)
        
        


    
    if drums == 'normal':    
        kick_note = note.Note()
        kick_note.pitch.midi = 35
        drums_stream.insert(start_offset, kick_note)
        
        kick_note = note.Note()
        kick_note.pitch.midi = 35
        drums_stream.insert(start_offset + measure_duration/2, kick_note)
        

        snare_note = note.Note()
        snare_note.pitch.midi = 38
        drums_stream.insert(start_offset + measure_duration/8, snare_note)
        
        snare_note = note.Note()
        snare_note.pitch.midi = 38
        drums_stream.insert(start_offset + measure_duration/4, snare_note)

        hihat_note = note.Note()
        hihat_note.pitch.midi = 42
        drums_stream.insert(start_offset, hihat_note)
    
        hihat_note = note.Note()
        hihat_note.pitch.midi = 42
        drums_stream.insert(start_offset + measure_duration/8, hihat_note)
    
        hihat_note = note.Note()
        hihat_note.pitch.midi = 42
        drums_stream.insert(start_offset + measure_duration/4, hihat_note)

        hihat_note = note.Note()
        hihat_note.pitch.midi = 42
        drums_stream.insert(start_offset + measure_duration/2, hihat_note)
        
    
    return drums_stream


def findClosestNote(measure, k):
    notes_in_measure = measure.recurse().getElementsByClass(['Note', 'Chord'])
        
    if notes_in_measure:
        closest_note = min(notes_in_measure, key=lambda n: abs(n.offset))

        if isinstance(closest_note, chord.Chord):
            # Convert chord to a single note by taking the pitch of the first note in the chord
            closest_note_pitch = closest_note.pitches[0]
        else:
            closest_note_pitch = closest_note.pitch
    else:
        closest_note_pitch = note.Note(k.tonic).pitch

    closest_note_obj = note.Note(closest_note_pitch.nameWithOctave)

    return closest_note_obj, closest_note_pitch

def addChords(measure, k, chords_stream, key_scale, start_offset, measure_duration):
    closest_note_obj, closest_note_pitch = findClosestNote(measure, k)

    scale_notes = [n.name for n in key_scale.getPitches()]
    relative_scale_notes = [n.name for n in key_scale.getPitches()]

    if closest_note_obj.name in scale_notes:
        i = key_scale.getScaleDegreeAndAccidentalFromPitch(closest_note_pitch)[0] - 1
        # i = 0

        root_pitch = key_scale.pitches[i]
        third_pitch = key_scale.pitches[(i + 2) % (7)]
        fifth_pitch = key_scale.pitches[(i + 4) % (7)]
        seventh_pitch = key_scale.pitches[(i + 6) % (7)]
    
        measure_chord = chord.Chord([root_pitch, third_pitch, fifth_pitch, seventh_pitch])
    
        print(measure_chord.pitchedCommonName)

        # arpeggio_notes = arpeggiate(measure_chord, measure_duration)
        # print(arpeggio_notes)
        # for i in range(len(arpeggio_notes)):
        #     chords_stream.insert(start_offset + i*measure_duration/4, arpeggio_notes[i])
    
        chords_stream.insert(start_offset + measure_duration/2, measure_chord)
        chords_stream[-1].quarterLength = measure_duration
    
    return chords_stream


def addInstruments(score, drums, piano, num_measures):
    # Find key
    k = score.analyze('key')

    if(k.mode == "major"):
        key_scale = scale.MajorScale(k.tonic)
    else:
        key_scale = scale.MinorScale(k.tonic)

    chords_stream = stream.Stream()
    chords_stream.insert(0, instrument.Piano())
    
    drums_stream = stream.Stream()
    drums_stream.insert(0, instrument.BassDrum())
    
    parts = score.parts if hasattr(score, 'parts') else [score]
    
    for part in parts:
        measures = part.getElementsByClass('Measure')[num_measures-1:num_measures]
        last = None
        for measure in measures:
            start_offset = measure.offset
            measure_duration = measure.duration.quarterLength

            if drums is not None:
                drums_stream = addDrums(start_offset, measure_duration, drums_stream, drums)

            if piano is not None:
                chords_stream = addChords(measure, k, chords_stream, key_scale, start_offset, measure_duration)
            
    
    return chords_stream, drums_stream

def setAttributes(chords_stream, drums_stream):
    for n in chords_stream.recurse().getElementsByClass(['Chord', 'Note']):
        n.volume.velocity = 65
    
    for n in drums_stream.recurse().getElementsByClass(['Chord', 'Note']):
        n.volume.velocity = 65

def output(file_name, output_path, score, chords_stream, drums_stream):
    combined_score = stream.Score()
    combined_score.insert(0, score)
    combined_score.insert(0, chords_stream)

    combined_score.write('midi', fp=os.path.join(output_path, file_name + "_with_chords.mid"))

    mf = midi.MidiFile()
    mf.open(os.path.join(output_path, file_name + "_with_chords.mid"))
    mf.read()
    mf.close()
    # print(mf.tracks)
    drum_track = midi.translate.streamHierarchyToMidiTracks(drums_stream)[1]
    drum_track.setChannel(10)
    mf.tracks.append(drum_track)
    mf.open(output_path + "_complete.mid", 'wb')
    mf.write()
    mf.close()

def main(input_file_path, file_name, output_path, drums, piano):
    # if args.drums:
    #     print(f"Selected drums: {args.drums}")

    # if args.piano is not None:
    #     print(f"Piano included: {args.piano}")

    # if args.input_file_path:
    #     print(f"File path provided: {args.input_file_path}")

    # Load MIDI file or music score file
    score = converter.parse(input_file_path)

    ts = None
    tempo_ = None

    for el in score.flat:
        if isinstance(el, meter.TimeSignature):
            ts = el.ratioString
        elif isinstance(el, tempo.MetronomeMark):
            tempo_ = el.getQuarterBPM()

    if ts is not None and tempo_ is not None:
        beats_per_measure = int(ts.split('/')[0])  # Get beats per measure from the time signature
        seconds_per_minute = 60.0  # Seconds per minute

        duration_of_measure = (seconds_per_minute / tempo_) * beats_per_measure

    num_measures = ceil(5.0/duration_of_measure)

    chords_stream, drums_stream = addInstruments(score, drums, piano, num_measures)
    setAttributes(chords_stream, drums_stream)
    
    output(file_name, output_path, score, chords_stream, drums_stream)
    
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='Process some musical options.')
    
#     parser.add_argument('--drums', choices=[None, 'half_time', 'double_time', 'normal'], help='Select drum type')
#     parser.add_argument('--piano', type=bool, help='Include piano (True/False)')
#     parser.add_argument('--file_path', help='File path')

#     args = parser.parse_args()
#     main(args)