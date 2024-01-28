# Real-Time Translation Tool with API-Powered Models

## Description
This release (v1.8) of our Real-Time Translation Tool brings significant enhancements, leveraging OpenAI's API for improved transcription, translation, and text-to-speech capabilities. It's a powerful tool for global communication and language learning, with an upcoming AI language teacher assistant feature.

## Release Notes for v1.8
### New Features
- **Enhanced Audio Recording**: Integrated changes to record and save user's voice in session folders.
- **AI Voice Saving**: AI-generated voice responses are now saved in session folders, providing a comprehensive record of interactions.
- **Streamlined User Experience**: Reduced unnecessary prompts and refined the user flow for a smoother experience.
- **Session Data Management**: Added options to save or delete session files, giving users more control over their data.

### Improvements
- **Voice Stream Functionality**: Refined the voice stream function to accept a session folder, ensuring AI voice responses are properly saved.
- **Session Folder Management**: Improved session folder creation and management, enabling better organization of session data.
- **Error Handling**: Enhanced error handling for robustness, especially in file operations and external API interactions.

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

## Feedback and Feature Requests
Your feedback is invaluable to us. If you have any suggestions or would like to request new features, please feel free to open an issue on GitHub or submit a pull request. We're always looking to improve and your contributions are greatly appreciated!

---
