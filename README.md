# Real-Time Translation Tool with API-Powered Models

## Release Notes for v1.7 "Crisp Echo"

We are delighted to unveil version 1.7 "Crisp Echo" of the Real-Time Translation Tool. This new version introduces significant updates and features that enhance both functionality and user experience.

### What's New in v1.7 "Crisp Echo"
- **Mid-Recording Interruption Feature:** Users can now interrupt recordings mid-way, offering flexibility in recording sessions.
- **Save or Discard Option for Recordings:** Post-recording, users are prompted to either save or discard the partially recorded audio.
- **Enhanced User Interaction:** Improved command-line interface for a smoother user experience.

These updates are focused on providing more control and options to the users, ensuring a seamless and efficient translation process.

## Branch Overview
This branch continues to leverage the power of OpenAI's API for both transcription and translation. The focus remains on delivering a high-accuracy and efficiency tool for real-time audio translation, utilizing the advanced capabilities of OpenAI's Whisper and GPT models.

## Description
Designed to cater to the needs of real-time translation, this tool offers a sophisticated yet user-friendly solution for audio transcription and translation. The integration of OpenAI's models ensures top-notch performance, while the new interactive features make it more adaptable to various user requirements.

## Features
- Interruptible real-time audio recording.
- Post-recording options to save or discard audio.
- Translation between English and Spanish using your OpenAI model of choice.
- TTS output for translations, with voice selection.

## Requirements
The following dependencies are required:
```
Python 3.x
sounddevice
openai
wavio
requests
speech_recognition
colorama
pynput
textwrap
```


## Installation
1. Clone the repository or download the script.
2. Install the necessary Python dependencies.
3. Set up your OpenAI API key in a `config.yaml.default` file for authentication (remove `default` from file name after cloning repo and api key is saved in file).

## Usage
Run the script using Python to access real-time translation features. Customize your experience with these command-line arguments:

- `-d`, `--duration`: Specify the recording duration in seconds. Defaults to 20 seconds if not specified.
- `-f`, `--file`: Provide a path to an existing audio file for transcription and translation. This bypasses the need for live recording.
- `-c`, `--content`: Set custom content for the GPT-4 translation API call. This content influences the model's context and translation style.
- `-v`, `--voice`: Enable Text-to-Speech (TTS) voice output for speaking the translation. Useful for auditory feedback of translated content.

### Detailed Operation
1. **Start Recording:** Press the space bar to begin audio recording. The recording will last for the specified duration or until stopped manually.
2. **Interrupt Recording (New in v1.7):** Press a predefined key (e.g., 's') during recording to stop prematurely. You'll then be prompted to save or discard the recording.
3. **Transcription and Translation:** The script transcribes the recorded or provided audio and translates it into the target language.
4. **TTS Output:** If the `-v` option is used, the script utilizes TTS to vocalize the translated text.


#### Example Commands
- Start a 30-second recording session:
```
python3 main.py -d 30
```
- Translate from a pre-recorded file with voice of choice:
```
python3 main.py -v nova -f /path/to/audio.wav
```

-Enable TTS output:
```
python3 translation_tool.py -v nova
```

## Advanced Usage Example
Experience the full capabilities of the Real-Time Translation Tool with this advanced command. Ideal for extended sessions with a unique auditory experience.

```
python3 main.py -c -v onyx -t -d 250
```

### What This Command Does
- `python3 main.py`: Executes the translation tool.
- `-c`: Engages custom content mode, using predefined special content for translation.
- `-v onyx`: Activates the sophisticated "onyx" voice for Text-to-Speech output.
- `-t`: Initiates continuous run mode, ideal for longer interactions.
- `-d 250`: Sets each recording session to last for 250 seconds, providing ample time for detailed conversations or narratives.

### Perfect For:
- Extended translation sessions.
- Users desiring a unique auditory translation experience.
- Situations where ongoing translation is beneficial, like meetings or lectures.

Embrace the power and versatility of the Real-Time Translation Tool with this advanced setup!


### Text-to-Speech Voices
When using the `-v` argument, you can select from various TTS voices for diverse and engaging output. The choice of voice can impact the user experience, offering variations in tone and style.

## Limitations
- **Network Dependency:** Requires a stable internet connection for API calls.
- **API Key Requirement:** An OpenAI API key is needed for transcription and translation services.
- **Language Limitation:** Currently supports English and Spanish. Expansion to other languages depends on API capabilities.
- **Hardware Requirements:** Adequate microphone and audio output for recording and TTS features.

## License
This project is released under the MIT license.

## Feedback and Feature Requests
Your feedback is invaluable to us. If you have any suggestions or would like to request new features, please feel free to open an issue on GitHub or submit a pull request. We're always looking to improve and your contributions are greatly appreciated!


---
