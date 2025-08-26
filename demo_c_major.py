#!/usr/bin/env python3
"""
Demo script showing how the C major constraint works in practice.
This script demonstrates generating music with the C major constraint active.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from midi_tokenizer import MIDITokenizerV2
import MIDI

def create_c_major_demo():
    """Create a demo showing C major constraint in action"""
    
    print("🎵 C Major Music Generation Demo")
    print("="*50)
    
    # Initialize tokenizer (same as used in the app)
    tokenizer = MIDITokenizerV2()
    print(f"Using tokenizer version: {tokenizer.version}")
    
    # Create a simple musical prompt in C major
    print("\n📝 Creating C major musical prompt...")
    
    # Start with basic structure
    prompt_sequence = [
        [tokenizer.bos_id] + [tokenizer.pad_id] * (tokenizer.max_token_seq - 1),
        tokenizer.event2tokens(["key_signature", 0, 0, 0, 0 + 7, 0]),  # C major key signature
        tokenizer.event2tokens(["set_tempo", 0, 0, 0, 120]),  # 120 BPM
        tokenizer.event2tokens(["patch_change", 0, 0, 0, 0, 0]),  # Piano on channel 0
    ]
    
    # Add a simple C major chord progression: C - F - G - C
    chord_progression = [
        # C major chord (C-E-G)
        [60, 64, 67],  # C4, E4, G4
        # F major chord (F-A-C) 
        [65, 69, 72],  # F4, A4, C5
        # G major chord (G-B-D)
        [67, 71, 74],  # G4, B4, D5
        # C major chord (C-E-G)
        [60, 64, 67],  # C4, E4, G4
    ]
    
    print("🎼 Adding chord progression: C - F - G - C")
    
    time_offset = 0
    for chord_idx, chord in enumerate(chord_progression):
        for note_idx, pitch in enumerate(chord):
            # Add note event: [event_type, time1, time2, track, channel, pitch, velocity, duration]
            note_event = tokenizer.event2tokens([
                "note", 
                time_offset, 0,  # time1, time2
                0,  # track
                0,  # channel
                pitch,  # pitch
                80,  # velocity
                480  # duration (quarter note)
            ])
            prompt_sequence.append(note_event)
        time_offset += 1  # Move to next beat
    
    print(f"✅ Created prompt with {len(prompt_sequence)} events")
    
    # Convert to MIDI to verify
    try:
        midi_data = tokenizer.detokenize(prompt_sequence)
        
        # Analyze the generated notes
        all_notes = []
        for track in midi_data[1:]:
            for event in track:
                if event[0] == "note":
                    pitch = event[4]
                    all_notes.append(pitch)
        
        print(f"\n🎹 Notes in the demo:")
        c_major_notes = {0, 2, 4, 5, 7, 9, 11}
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        
        for pitch in sorted(set(all_notes)):
            note_class = pitch % 12
            note_name = note_names[note_class]
            octave = pitch // 12 - 1
            in_c_major = note_class in c_major_notes
            print(f"  {note_name}{octave} (MIDI {pitch}) - {'✓' if in_c_major else '✗'}")
        
        # Save as MIDI file
        if not os.path.exists("demo_output"):
            os.makedirs("demo_output")
            
        output_path = "demo_output/c_major_demo.mid"
        with open(output_path, 'wb') as f:
            f.write(MIDI.score2midi(midi_data))
        
        print(f"\n💾 Saved demo MIDI to: {output_path}")
        print("   You can open this file in any MIDI player or DAW to hear the C major chord progression!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating demo: {e}")
        return False

def explain_filtering_mechanism():
    """Explain how the pitch filtering works"""
    
    print("\n" + "="*50)
    print("🔍 How the C Major Filtering Works")
    print("="*50)
    
    tokenizer = MIDITokenizerV2()
    c_major_notes = {0, 2, 4, 5, 7, 9, 11}
    
    print("\n1. 🎼 C Major Scale Definition:")
    note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    print("   Allowed notes (semitones from C):")
    for semitone in sorted(c_major_notes):
        print(f"     {semitone}: {note_names[semitone]}")
    
    print("\n2. 🎯 Token Filtering Process:")
    print("   During generation, when the model needs to choose a pitch:")
    print("   - All 128 possible MIDI pitches are available as tokens")
    print("   - We filter these to only include C major scale notes")
    print("   - The model can only choose from the filtered set")
    
    pitch_tokens = tokenizer.parameter_ids["pitch"]
    total_tokens = len(pitch_tokens)
    filtered_tokens = [i for i in pitch_tokens if (i - pitch_tokens[0]) % 12 in c_major_notes]
    filtered_count = len(filtered_tokens)
    
    print(f"\n3. 📊 Token Statistics:")
    print(f"   - Total pitch tokens: {total_tokens}")
    print(f"   - Filtered tokens (C major only): {filtered_count}")
    print(f"   - Reduction: {((total_tokens - filtered_count) / total_tokens * 100):.1f}% of tokens filtered out")
    
    print("\n4. 🎵 Example Filtering (first octave):")
    for i in range(12):
        note_name = note_names[i]
        in_c_major = i in c_major_notes
        status = "✅ ALLOWED" if in_c_major else "❌ BLOCKED"
        print(f"   {note_name:2s} (semitone {i:2d}): {status}")

def main():
    """Main demo function"""
    
    # Create the demo
    success = create_c_major_demo()
    
    # Explain the mechanism
    explain_filtering_mechanism()
    
    print("\n" + "="*50)
    print("🎯 Summary")
    print("="*50)
    
    if success:
        print("✅ Demo completed successfully!")
        print("\nThe C major constraint ensures that:")
        print("• All generated music uses C major key signature")
        print("• Only notes from the C major scale can be generated")
        print("• This works across all octaves and instruments")
        print("• The constraint is applied during token generation")
        
        print("\n🚀 To use the full application with C major constraint:")
        print("   python app.py")
        print("   (Then open the web interface and generate music)")
        
    else:
        print("❌ Demo failed - please check the implementation")

if __name__ == "__main__":
    main()
