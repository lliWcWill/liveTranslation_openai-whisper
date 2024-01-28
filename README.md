# Real-Time Translation Tool with API-Powered Models

## Description
Elevate your global communication with our API-powered Live Translation Tool. This advanced tool, now in version 1.6, leverages the full capabilities of OpenAI's API for seamless transcription, translation, and text-to-speech synthesis. It's ideal for international communication, language learning, and is set to evolve with an AI language teacher assistant feature.

## Release Notes for v1.6
- **API-Powered Transcription & Translation**: Full integration for a streamlined translation workflow.
- **Text-to-Speech (TTS) Voice Output**: Interactive translations in a wide range of supported languages using the `-v` argument.
- **Multilingual Translation**: Expansive language support, now accessible through the `-c` argument for user-specific needs.

### Installation & Setup
Ensure you have Python 3.x and necessary libraries installed, along with ffmpeg for audio process.

- It also requires the command-line tool ffmpeg to be installed on your system, which is available from most package managers:
```
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on Arch Linux
sudo pacman -S ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg

# on Windows using Scoop (https://scoop.sh/)
scoop install ffmpeg
```

### Steps
1. Clone the repository: `git clone https://github.com/yourusername/liveTranslation_openai-whisper.git`
2. Navigate to the cloned directory: `cd liveTranslation_openai-whisper`
3. Install required libraries: `pip install -r requirements.txt`

## Configuration
Set up your OpenAI API key in `config.yaml`:
1. Rename `config.yaml.default` to `config.yaml`
2. Enter your OpenAI API key in the `config.yaml` file:
```yaml
openai:
  api_key: "Your-OpenAI-API-Key"
```

## Args
Execute with `python main.py` and the following optional flags:
- `-d <seconds>`: Set the duration for audio capture.
- `-f <filename.wav>`: Translate from an existing audio file.
- `-c <language>`: Choose a specific language or use `Smart Select` for automatic detection.
- `-t`: Enable continuous translation mode. (No Spacebar toggle record)
- `-v <voice_name>`: Activate text-to-speech for the translated text.


### Usage Examples

- 4-second live translation in Spanish with toggle recording
  
`python main.py -d 4 -c Spanish`

---

- 10-second live translation in continuous mode

`python main.py -d 10 -t`

---

- Translate an existing audio file with Shimmer's voice
  
`python main.py -f audioFileName.wav -v shimmer`

---


- Smart Select with Nova voice, 8-second recording in continuous mode
  
`python main.py -c 'Smart Select' -v nova -d 8 -t`

---


## Troubleshooting
If you encounter issues, check your microphone settings and ensure the OpenAI API key is valid.

## Contributing
Contributions are welcome. Fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
For more information, contact me at [willTheNightFox@gmail.com](mailto:willTheNightFox@gmail.com).

## Acknowledgments
Special thanks to the OpenAI team for the Whisper and GPT-4 models.

## Release Notes for v1.6
We're excited to announce the release of version 1.6 of the Real-Time Translation Tool. This update brings API-powered transcription and translation capabilities, along with the integration of GPT-powered voice output for an enriched user experience.

### What's New in v1.6
- Integration of API-powered transcription and translation for enhanced accuracy and efficiency.
- Addition of Text-to-Speech (TTS) voice output for translations, providing an interactive and engaging user experience.

We encourage you to update to the latest version to enjoy these new features.

## Branch Overview
This branch of the Real-Time Translation Tool is distinct from the main branch in its approach to processing audio and text. Unlike the main branch, which uses a local implementation of OpenAI's Whisper model for transcription and an API call for GPT-4 translation, this branch utilizes API calls to power both the transcription and translation processes. This method leverages the full capabilities of OpenAI's Whisper and GPT models, offering a seamless and enhanced experience in transcribing and translating spoken words. Additionally, this branch includes the feature of GPT-powered voice output for the translated text, further enriching the user experience.

## Description
The tool is designed to provide real-time audio translation, utilizing API calls to access the power of OpenAI's advanced Whisper and GPT models. This setup ensures high accuracy and efficiency in both transcribing spoken language and translating the transcribed text. The added functionality of GPT voice output for translations enhances the tool, making it more interactive and user-friendly.

## Features
- Real-time audio recording and transcription using OpenAI's Whisper model API.
- Accurate translation between English and Spanish through GPT-4 Turbo.
- Text-to-Speech (TTS) output for translations, activated with the `-v` argument.

## Requirements
To use this tool, ensure the following dependencies are installed:
- Python 3.x
- sounddevice
- openai
- wavio
- requests
- speech_recognition
- colorama
- pynput
- textwrap

## Installation
1. Clone the repository or download the script.
2. Install the necessary Python dependencies.
3. Set up your OpenAI API key in a `config.yaml` file for authentication.

## Usage
Run the script using Python. You can customize your experience using these command-line arguments:
- `-d`, `--duration`: Specify the recording duration in seconds (optional).
- `-f`, `--file`: Use an existing audio file for transcription and translation (optional).
- `-c`, `--content`: Custom content for the translation API call to GPT4 (optional).
- `-v`, `--voice`: Enable TTS voice for speaking the translation (optional).

### Basic Operation
- Press the space bar to start and stop audio recording.
- The script transcribes the recorded audio and then translates it.
- If `-v` is used, the translated text is spoken using a TTS voice.

### Text-to-Speech Output
The `-v` argument enables the TTS feature, where the translation is read aloud. This feature supports multiple voices, offering a diverse and engaging user experience.

## License
This project is released under the MIT license.

## Feedback and Feature Requests
Your feedback is invaluable to us. If you have any suggestions or would like to request new features, please feel free to open an issue on GitHub or submit a pull request. We're always looking to improve and your contributions are greatly appreciated!

---
