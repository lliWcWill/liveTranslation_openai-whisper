Real-Time Translation Tool with GPT Voice
Description
This tool is designed for real-time audio translation leveraging the power of OpenAI's Whisper and GPT models. It provides a seamless experience in transcribing and translating spoken words, with the added capability of GPT voice output.

Features
Real-time audio recording and transcription using OpenAI's Whisper model.
Accurate translation between English and Spanish through GPT-3.
Text-to-Speech (TTS) output for translations, activated with the -v argument.
Requirements
To use this tool, ensure the following dependencies are installed:

Python 3.x
sounddevice
openai
wavio
requests
speech_recognition
colorama
pynput
textwrap
Installation
Clone the repository or download the script.
Install the necessary Python dependencies.
Set up your OpenAI API key in a config.yaml file for authentication.
Usage
Run the script using Python. You can customize your experience using these command-line arguments:

-d, --duration: Specify the recording duration in seconds (optional).
-f, --file: Use an existing audio file for transcription and translation (optional).
-c, --content: Custom content for the API call to Whisper (optional).
-v, --voice: Enable TTS voice for speaking the translation (optional).
Basic Operation
Press the space bar to start and stop audio recording.
The script transcribes the recorded audio and then translates it.
If -v is used, the translated text is spoken using a TTS voice.
Text-to-Speech Output
The -v argument enables the TTS feature, where the translation is read aloud. This feature supports multiple voices, offering a diverse and engaging user experience.

License
This project is released under the MIT license.
