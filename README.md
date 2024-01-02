# Real-Time Translation Tool with API-Powered Models

## Branch Overview
This branch of the Real-Time Translation Tool is distinct from the main branch in its approach to processing audio and text. Unlike the main branch, which uses a local implementation of OpenAI's Whisper model for transcription and an API call for GPT-4 translation, this branch utilizes API calls to power both the transcription and translation processes. This method leverages the full capabilities of OpenAI's Whisper and GPT models, offering a seamless and enhanced experience in transcribing and translating spoken words. Additionally, this branch includes the feature of GPT-powered voice output for the translated text, further enriching the user experience.

## Description
The tool is designed to provide real-time audio translation, utilizing API calls to access the power of OpenAI's advanced Whisper and GPT models. This setup ensures high accuracy and efficiency in both transcribing spoken language and translating the transcribed text. The added functionality of GPT voice output for translations enhances the tool, making it more interactive and user-friendly.


## Features
- Real-time audio recording and transcription using OpenAI's Whisper model.
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
