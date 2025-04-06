import json
import os
import shutil
import soundfile as sf
from kokoro_onnx import Kokoro
import re
from pathlib import Path
from pydub import AudioSegment
import configparser

def extract_language_from_filename(filename):
    """Extract language code from filename (e.g., dialog_de.json -> de)"""
    match = re.search(r'_([a-z]{2})\.json$', filename)
    if match:
        return match.group(1)
    return "en"  # Default to English if no language code found

def get_language_code_for_tts(lang_code):
    """Convert 2-letter language code to TTS language code"""
    language_mapping = {
        "en": "en-us",
        "de": "de",  # Assuming German is supported
        # Add more mappings as needed
    }
    return language_mapping.get(lang_code, "en-us")

def parse_json(json_file):
    """Read and parse the JSON file"""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_unique_speakers(dialog_data):
    """Extract unique speakers from dialog data"""
    speakers = set()
    for entry in dialog_data["dialog"]:
        speakers.add(entry["speaker"])
    return list(speakers)

def assign_voices(speakers, lang_code):
    """Assign a unique voice to each speaker based on language"""
    # Voice selection based on language
    voice_mapping = {
        "de": {
            # German voices (if available) or fallback to other voices
            0: "af_bella",  # Female voice
            1: "am_fenrir",  # Male voice
            2: "af_nicole",  # Female voice
            3: "am_michael",  # Male voice
        },
        "en": {
            0: "af_bella",  # Female voice
            1: "am_fenrir",  # Male voice
            2: "af_nicole",  # Female voice
            3: "am_michael",  # Male voice
        }
        # Add more languages as needed
    }
    
    # Use default English voices if language not supported
    voices = voice_mapping.get(lang_code, voice_mapping["en"])
    
    # Assign voices to speakers
    speaker_voices = {}
    for i, speaker in enumerate(speakers):
        voice_index = i % len(voices)
        speaker_voices[speaker] = list(voices.values())[voice_index]
    
    return speaker_voices

def generate_audio(text, voice, output_file, lang_code, kokoro_instance):
    """Generate audio file for a dialog entry"""
    # Skip if file already exists
    if os.path.exists(output_file):
        print(f"File {output_file} already exists, skipping...")
        return
    
    # Generate audio
    tts_lang = get_language_code_for_tts(lang_code)
    samples, sample_rate = kokoro_instance.create(
        text, voice=voice, speed=1.0, lang=tts_lang
    )
    
    # Save as temporary WAV file
    temp_wav_file = output_file.replace('.mp3', '.wav')
    sf.write(temp_wav_file, samples, sample_rate)
    
    # Convert WAV to MP3
    sound = AudioSegment.from_wav(temp_wav_file)
    sound.export(output_file, format="mp3")
    
    # Remove temporary WAV file
    os.remove(temp_wav_file)
    
    print(f"Created {output_file}")

def merge_mp3_files(directory, output_file):
    """Merge all MP3 files in a directory into a single file"""
    # Get all MP3 files and sort them numerically
    mp3_files = [f for f in os.listdir(directory) if f.endswith('.mp3') and f != output_file]
    mp3_files.sort()
    
    if not mp3_files:
        print(f"No MP3 files found in {directory}")
        return False
    
    # Check if merged file already exists
    if os.path.exists(output_file):
        print(f"Merged file {output_file} already exists, skipping...")
        return True
    
    print(f"Merging {len(mp3_files)} MP3 files...")
    
    # Create an empty audio segment
    merged = AudioSegment.empty()
    
    # Append each MP3 file
    for mp3_file in mp3_files:
        file_path = os.path.join(directory, mp3_file)
        audio = AudioSegment.from_mp3(file_path)
        merged += audio
    
    # Export merged audio
    merged.export(output_file, format="mp3")
    print(f"Created merged file: {output_file}")
    return True

def process_dialog_file(input_file, output_base_dir="output"):
    """Process a dialog JSON file and generate audio files"""
    # Extract base name and language
    base_name = os.path.basename(input_file)
    folder_name = os.path.splitext(base_name)[0]  # e.g., "dialog_de"
    lang_code = extract_language_from_filename(base_name)
    
    # Create output directory
    output_dir = os.path.join(output_base_dir, folder_name)
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse JSON
    dialog_data = parse_json(input_file)
    
    # Get unique speakers and assign voices
    speakers = get_unique_speakers(dialog_data)
    speaker_voices = assign_voices(speakers, lang_code)
    
    # Initialize Kokoro
    kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
    
    # Generate audio files
    for i, entry in enumerate(dialog_data["dialog"]):
        speaker = entry["speaker"]
        text = entry["text"]
        voice = speaker_voices[speaker]
        
        # Format output filename with leading zeros (0001.mp3, 0002.mp3, etc.)
        output_file = os.path.join(output_dir, f"{i+1:04d}.mp3")
        
        # Generate audio
        generate_audio(text, voice, output_file, lang_code, kokoro)
    
    # Merge all MP3 files into a single file
    merged_file = os.path.join(output_dir, f"{folder_name}_complete.mp3")
    merge_mp3_files(output_dir, merged_file)
    
    # Move input file to output directory
    shutil.move(input_file, os.path.join(output_dir, base_name))
    print(f"Moved {input_file} to {output_dir}")

def load_settings():
    """Load settings from settings.ini file"""
    config = configparser.ConfigParser()
    
    # Set default values
    config['Directories'] = {
        'input_dir': 'input',
        'output_dir': 'output'
    }
    
    # Read settings from file if it exists
    if os.path.exists('settings.ini'):
        config.read('settings.ini')
    else:
        # Create settings file with default values if it doesn't exist
        with open('settings.ini', 'w') as f:
            config.write(f)
    
    return config

def main():
    """Main function to process all dialog files in the input directory"""
    # Load settings
    config = load_settings()
    input_dir = config['Directories']['input_dir']
    output_dir = config['Directories']['output_dir']
    
    print(f"Using input directory: {input_dir}")
    print(f"Using output directory: {output_dir}")
    
    # Create directories if they don't exist
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all JSON files in the input directory
    for file in os.listdir(input_dir):
        if file.endswith(".json"):
            input_file = os.path.join(input_dir, file)
            process_dialog_file(input_file, output_dir)

if __name__ == "__main__":
    main()
