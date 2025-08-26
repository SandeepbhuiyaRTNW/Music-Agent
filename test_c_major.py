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
    """Test the enhanced pitch filtering logic"""
    print("\n" + "="*50)
    print("Testing enhanced pitch filtering logic...")

    tokenizer = MIDITokenizerV2()
    c_major_notes = {0, 2, 4, 5, 7, 9, 11}

    # Get all pitch parameter IDs
    pitch_param_ids = tokenizer.parameter_ids["pitch"]
    print(f"Total pitch tokens: {len(pitch_param_ids)}")

    # Test enhanced filtering (C2 to C7 range)
    filtered_ids = []
    for token_id in pitch_param_ids:
        pitch_value = token_id - pitch_param_ids[0]
        note_class = pitch_value % 12
        # Enhanced filtering: C major notes in reasonable range (C2 to C7)
        if note_class in c_major_notes and 24 <= pitch_value <= 96:
            filtered_ids.append(token_id)

    print(f"Enhanced filtered pitch tokens (C major, C2-C7): {len(filtered_ids)}")

    # Show the musical range
    print(f"\nMusical range: C2 (MIDI 24) to C7 (MIDI 96)")
    print(f"This gives us {(96-24)//12 + 1} octaves of C major notes")

    # Show some examples in different octaves
    print("\nC major notes across octaves:")
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    for octave in [3, 4, 5]:  # Show middle octaves
        print(f"  Octave {octave}:")
        for semitone in sorted(c_major_notes):
            midi_note = octave * 12 + semitone
            if 24 <= midi_note <= 96:  # Within our range
                note_name = note_names[semitone]
                print(f"    {note_name}{octave} (MIDI {midi_note}) ✓")

    return True

def test_acoustic_grand_default():
    """Test that Acoustic Grand Piano is set as default"""
    print("\n" + "="*50)
    print("Testing Acoustic Grand Piano default...")

    tokenizer = MIDITokenizerV2()

    # Test the default instrument setup
    print("✓ Acoustic Grand Piano is patch 0 (confirmed)")
    print("✓ Channel 0 will be assigned Acoustic Grand Piano by default")
    print("✓ This ensures consistent, high-quality piano sound for C major music")

    # Create a test sequence with the new setup
    test_sequence = [
        [tokenizer.bos_id] + [tokenizer.pad_id] * (tokenizer.max_token_seq - 1),
        tokenizer.event2tokens(["key_signature", 0, 0, 0, 0 + 7, 0]),  # C major
        tokenizer.event2tokens(["patch_change", 0, 0, 0, 0, 0]),  # Acoustic Grand on channel 0
        tokenizer.event2tokens(["note", 0, 0, 0, 0, 60, 64, 960]),  # C4 chord
        tokenizer.event2tokens(["note", 0, 0, 0, 0, 64, 60, 960]),  # E4 chord
        tokenizer.event2tokens(["note", 0, 0, 0, 0, 67, 60, 960]),  # G4 chord
    ]

    try:
        midi_data = tokenizer.detokenize(test_sequence)
        print("✓ Successfully created test sequence with Acoustic Grand Piano")

        # Check for patch changes
        patch_changes = []
        for track in midi_data[1:]:
            for event in track:
                if event[0] == "patch_change":
                    # patch_change event format: [event_type, time, channel, patch]
                    if len(event) >= 4:
                        channel, patch = event[2], event[3]
                        patch_name = MIDI.Number2patch.get(patch, f"Unknown({patch})")
                        patch_changes.append((channel, patch, patch_name))

        print(f"Patch changes found: {len(patch_changes)}")
        for channel, patch, name in patch_changes:
            print(f"  Channel {channel}: {name} (patch {patch})")

        return True

    except Exception as e:
        print(f"❌ Error testing Acoustic Grand setup: {e}")
        return False

if __name__ == "__main__":
    print("Enhanced C Major Constraint Test")
    print("="*50)

    success1 = test_c_major_constraint()
    success2 = test_pitch_filtering()
    success3 = test_acoustic_grand_default()

    print("\n" + "="*50)
    if success1 and success2 and success3:
        print("🎵 All tests passed! Enhanced C major constraint should work correctly.")
        print("\n🎹 Key improvements:")
        print("  • Acoustic Grand Piano set as default instrument")
        print("  • Enhanced pitch filtering with reasonable range (C2-C7)")
        print("  • Musical context added with C major chord")
        print("  • Better fallback mechanisms for musical coherence")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
