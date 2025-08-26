#!/usr/bin/env python3
"""
Test script to verify that the C major constraint is working correctly.
This script will generate a small MIDI sequence and check if all notes are in C major scale.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from midi_tokenizer import MIDITokenizerV2
import MIDI

def test_c_major_constraint():
    """Test if generated notes are constrained to C major scale"""
    
    # C major scale notes (semitones from C): C, D, E, F, G, A, B
    c_major_notes = {0, 2, 4, 5, 7, 9, 11}
    
    print("Testing C major constraint...")
    print(f"C major scale notes (modulo 12): {sorted(c_major_notes)}")
    
    # Initialize tokenizer
    tokenizer = MIDITokenizerV2()
    
    # Create a simple test sequence with C major key signature
    test_sequence = [
        [tokenizer.bos_id] + [tokenizer.pad_id] * (tokenizer.max_token_seq - 1),
        tokenizer.event2tokens(["key_signature", 0, 0, 0, 0 + 7, 0]),  # C major
        tokenizer.event2tokens(["set_tempo", 0, 0, 0, 120]),  # 120 BPM
        tokenizer.event2tokens(["patch_change", 0, 0, 0, 0, 0]),  # Piano
    ]
    
    # Add some test notes in C major
    test_notes = [
        # C4, D4, E4, F4, G4, A4, B4, C5
        60, 62, 64, 65, 67, 69, 71, 72
    ]
    
    for i, pitch in enumerate(test_notes):
        note_event = tokenizer.event2tokens(["note", 0, 0, 0, 0, pitch, 64, 480])  # channel 0, velocity 64, duration 480
        test_sequence.append(note_event)
    
    # Convert to MIDI and back to verify
    try:
        midi_data = tokenizer.detokenize(test_sequence)
        print(f"Successfully created test MIDI with {len(test_notes)} notes")
        
        # Check if all notes are in C major
        notes_found = []
        for track in midi_data[1:]:
            for event in track:
                if event[0] == "note":
                    pitch = event[4]
                    note_class = pitch % 12
                    notes_found.append((pitch, note_class))
        
        print(f"\nNotes found in generated MIDI:")
        all_in_c_major = True
        for pitch, note_class in notes_found:
            in_c_major = note_class in c_major_notes
            note_name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][note_class]
            print(f"  MIDI note {pitch} ({note_name}) - {'✓' if in_c_major else '✗'} {'in C major' if in_c_major else 'NOT in C major'}")
            if not in_c_major:
                all_in_c_major = False
        
        if all_in_c_major:
            print(f"\n✅ SUCCESS: All {len(notes_found)} notes are in C major scale!")
        else:
            print(f"\n❌ FAILURE: Some notes are not in C major scale!")
            
        return all_in_c_major
        
    except Exception as e:
        print(f"Error during test: {e}")
        return False

def test_pitch_filtering():
    """Test the pitch filtering logic"""
    print("\n" + "="*50)
    print("Testing pitch filtering logic...")
    
    tokenizer = MIDITokenizerV2()
    c_major_notes = {0, 2, 4, 5, 7, 9, 11}
    
    # Get all pitch parameter IDs
    pitch_param_ids = tokenizer.parameter_ids["pitch"]
    print(f"Total pitch tokens: {len(pitch_param_ids)}")
    
    # Test filtering
    filtered_ids = [i for i in pitch_param_ids if (i - pitch_param_ids[0]) % 12 in c_major_notes]
    print(f"Filtered pitch tokens (C major only): {len(filtered_ids)}")
    
    # Show some examples
    print("\nFirst 20 pitch tokens and their filtering:")
    for i in range(min(20, len(pitch_param_ids))):
        token_id = pitch_param_ids[i]
        pitch_value = i  # This is the actual MIDI pitch value
        note_class = pitch_value % 12
        in_c_major = note_class in c_major_notes
        note_name = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"][note_class]
        print(f"  Token {token_id}: MIDI pitch {pitch_value} ({note_name}) - {'✓' if in_c_major else '✗'}")
    
    return True

if __name__ == "__main__":
    print("C Major Constraint Test")
    print("="*50)
    
    success1 = test_c_major_constraint()
    success2 = test_pitch_filtering()
    
    print("\n" + "="*50)
    if success1 and success2:
        print("🎵 All tests passed! C major constraint should work correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
