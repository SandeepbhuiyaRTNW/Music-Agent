# C Major Music Constraint Implementation

This document explains how the C major constraint has been implemented in the MIDI music generation project to ensure that only C major music is outputted.

## Overview

The implementation uses a two-pronged approach to ensure all generated music is in C major:

1. **Key Signature Enforcement**: Forces all generated music to use C major key signature
2. **Pitch Filtering**: Filters note generation to only allow notes from the C major scale

## Implementation Details

### 1. Key Signature Enforcement

**Files Modified**: `app.py`, `app_onnx.py`

The key signature is now forced to C major (sf=0, mi=0) regardless of user input:

```python
# Force C major key signature (sf=0, mi=0) - always add this for C major constraint
mid.append(tokenizer.event2tokens(["key_signature", 0, 0, 0, 0 + 7, 0]))
```

**What this does**:
- Sets the key signature to C major (0 sharps/flats)
- Provides a musical context hint to the model
- Ensures the generated MIDI file has the correct key signature metadata

### 2. Pitch Filtering During Generation

**Files Modified**: `app.py`, `app_onnx.py`

During the token generation process, when the model is selecting pitch values, we filter the available options to only include notes from the C major scale:

```python
elif param_name == "pitch":
    # Filter to only allow C major scale notes (C, D, E, F, G, A, B)
    # C major scale: 0, 2, 4, 5, 7, 9, 11 (modulo 12)
    c_major_notes = {0, 2, 4, 5, 7, 9, 11}  # C, D, E, F, G, A, B
    mask_ids = [i for i in mask_ids if (i - tokenizer.parameter_ids[param_name][0]) % 12 in c_major_notes]
```

**What this does**:
- Restricts the model to only generate notes that belong to the C major scale
- Works across all octaves (uses modulo 12 arithmetic)
- Applies to all channels and instruments

## C Major Scale Notes

The C major scale consists of the following notes:
- **C** (semitone 0)
- **D** (semitone 2) 
- **E** (semitone 4)
- **F** (semitone 5)
- **G** (semitone 7)
- **A** (semitone 9)
- **B** (semitone 11)

These are represented as `{0, 2, 4, 5, 7, 9, 11}` in the code, where the numbers represent semitones from C.

## How It Works

### Generation Process

1. **Initialization**: When starting generation, a C major key signature is automatically added
2. **Token Generation**: During each step of music generation:
   - When the model needs to select a pitch token
   - The available pitch options are filtered to only include C major scale notes
   - The model can only choose from these filtered options
3. **Output**: The resulting MIDI will only contain notes from the C major scale

### Compatibility

The implementation works with both:
- **PyTorch version** (`app.py`) - for GPU/CPU inference
- **ONNX version** (`app_onnx.py`) - for optimized inference

## Testing

A test script `test_c_major.py` is provided to verify the constraint works correctly:

```bash
python test_c_major.py
```

This script:
- Creates a test MIDI sequence
- Verifies all notes are in the C major scale
- Tests the pitch filtering logic

## Usage

### Running the Application

The constraint is automatically applied - no additional configuration needed:

```bash
# PyTorch version
python app.py

# ONNX version  
python app_onnx.py
```

### Web Interface

When using the Gradio web interface:
- The key signature setting is now ignored (always C major)
- All other settings (instruments, tempo, etc.) work normally
- Generated music will automatically be in C major

## Technical Notes

### Why This Approach?

1. **Model-Level Filtering**: By filtering at the token generation level, we ensure the constraint is applied consistently regardless of the model's training data
2. **Preserves Musical Structure**: The model can still generate complex musical patterns, just restricted to the C major scale
3. **Efficient**: The filtering happens during generation, not as post-processing

### Limitations

- The model was trained on music in various keys, so forcing C major might occasionally produce less natural-sounding transitions
- Some musical expressions that rely on chromatic notes (outside the major scale) will not be possible

### Future Enhancements

Possible improvements could include:
- Support for other major/minor keys
- Allowing occasional chromatic passing tones
- Mode-specific constraints (Dorian, Mixolydian, etc.)

## Files Modified

1. **app.py**: Main PyTorch application
   - Added key signature forcing (line ~164)
   - Added pitch filtering (lines ~87-91)

2. **app_onnx.py**: ONNX optimized application  
   - Added key signature forcing (line ~341)
   - Added pitch filtering (lines ~220-224)

3. **test_c_major.py**: Test script (new file)
4. **C_MAJOR_CONSTRAINT.md**: This documentation (new file)

## Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Check system status
python run_c_major_app.py
```

### 2. Run the Application
```bash
# Start the web interface
python app.py

# Open browser to http://localhost:7860
# Load a model and start generating C major music!
```

### 3. Test the Constraint
```bash
# Run automated tests
python test_c_major.py

# See a demonstration
python demo_c_major.py
```

## Verification

To verify the constraint is working:

1. Generate some music using the web interface
2. Download the generated MIDI files
3. Open them in a MIDI editor or music software
4. Check that all notes are from the C major scale (C, D, E, F, G, A, B)

The key signature should show as C major (no sharps or flats), and all note events should only use pitches that correspond to white keys on a piano when transposed to the C major scale.

## Additional Files Created

- **`test_c_major.py`**: Automated test to verify the constraint works
- **`demo_c_major.py`**: Demonstration script showing C major chord progression
- **`run_c_major_app.py`**: Startup script with dependency checking
- **`C_MAJOR_CONSTRAINT.md`**: This documentation file
