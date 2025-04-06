# JSON to Podcast Episode Converter

This Python script converts dialog from JSON files into MP3 audio files using text-to-speech, and merges them into a complete podcast episode.

## Features

- Processes JSON dialog files with multiple speakers
- Assigns different voices to different speakers
- Detects language from filename (e.g., `dialog_de.json` for German)
- Generates sequentially numbered MP3 files (0001.mp3, 0002.mp3, etc.)
- Merges all individual MP3 files into a single complete podcast file
- Skips generation of files that already exist
- Creates organized output directory structure
- Moves processed input files to output directory

## Requirements

- Python 3.6+
- Required Python packages (see `requirements.txt`)
- ffmpeg (for MP3 conversion)

## Installation

1. Clone this repository or download the source code
2. Create a virtual environment (recommended):
   ```
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
5. Download the Kokoro model files:
   ```
   wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
   wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
   ```

Place the downloaded files in the same directory as the script.

## Configuration

You can customize the input and output directories by editing the `settings.ini` file:

```ini
[Directories]
# Directory where input JSON files are located
input_dir = input

# Directory where output MP3 files will be stored
output_dir = output
```

The script will automatically create these directories if they don't exist.

## Usage

1. (Optional) Customize the input and output directories in `settings.ini`

2. Place your JSON dialog files in the input directory (default: `input`)

   - Name your files with language code: `dialog_en.json`, `dialog_de.json`, etc.
   - Format should match the example below

3. Run the script:

   ```
   python main.py
   ```

4. Find the generated audio files in the output directory (default: `output`):
   - Individual MP3 files (0001.mp3, 0002.mp3, etc.)
   - Complete merged podcast file (e.g., `dialog_de_complete.mp3`)

## JSON Format

Your input JSON files should follow this format:

```json
{
  "dialog": [
    {
      "speaker": "Host",
      "text": "Welcome to our podcast!"
    },
    {
      "speaker": "Guest",
      "text": "Thank you for having me."
    },
    ...
  ]
}
```

## Supported Languages

The script automatically detects the language from the filename:

- English: `_en.json`
- German: `_de.json`
- Add more languages by extending the `get_language_code_for_tts` function

## Voice Assignment

Different voices are assigned to different speakers. You can customize the voice assignments in the `assign_voices` function.

## Generating Dialog with LLMs

The repository includes a `prompt.txt` file that contains a prompt template you can use with LLMs like ChatGPT to generate dialog in the correct JSON structure for this tool.

To use it:

1. Open `prompt.txt`
2. Copy the content and paste it into your favorite LLM chat (ChatGPT, Claude, etc.)
3. Replace `[INSERT YOUR TOPIC HERE]` with your desired podcast topic
4. The LLM will generate a properly formatted JSON dialog that you can save to the `input` directory
5. Remember to name your file with the appropriate language code (e.g., `dialog_en.json`)

This makes it easy to quickly generate test content or even create complete podcast episodes on any topic.

## License

This project is open source and available under the MIT License.
