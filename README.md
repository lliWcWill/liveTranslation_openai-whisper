<h1 align="center">● Real-Time Translation Tool with API-Powered Models</h1>

## Description
Introducing 'Linguistic Pioneer v1.9' - our latest iteration of the Real-Time Translation Tool, which now includes groundbreaking enhancements and sets the stage for the future AI language assistant mode. Powered by OpenAI's API, this version offers unmatched transcription, translation, and text-to-speech capabilities, making global communication and language learning more accessible and effective.

## Release Notes for Linguistic Pioneer v1.9 🚀
### New Features 🌟
- **Repeat AI Voice Function**: Users can now replay the last AI-generated voice translation by pressing 'r', adding a new dimension to the user experience.
- **Enhanced Audio Recording**: Streamlined audio recording process, enabling users to **record and save their voice** more efficiently in session folders.
- **AI Voice Saving**: AI-generated voice responses are **automatically saved** in session folders, allowing for easy review and replay.
- **User Experience Refinement**: Optimized user flow and reduced prompts for a **more intuitive and smoother experience**.
- **Session Data Control**: Enhanced options to **save or delete session files**, granting users greater control over their data.

### Improvements 💡
- **Voice Stream Enhancements**: Upgraded the voice stream function to seamlessly integrate with session folders, ensuring **accurate saving of AI voice responses**.
- **Advanced Session Folder Management**: Refined session folder creation and management for better **organization and accessibility of session data**.
- **Robust Error Handling**: Strengthened error handling mechanisms, particularly for file operations and API interactions, to enhance application stability.

### Roadmap and Future Plans 🛣️
- **AI Language Assistant Mode**: Laying the groundwork for an upcoming feature that transforms the tool into an AI-powered language teacher, making language learning interactive, personalized, and more effective.

Stay tuned for more updates as we continue to innovate and enhance the capabilities of the Real-Time Translation Tool.


### Installation & Setup
Ensure you have Python 3.x and necessary libraries installed, along with ffmpeg for audio process.

- It also requires the command-line tool ffmpeg to be installed on your system, which is available from most package managers:
```bash
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
1. Clone the repository:
```bash
git clone https://github.com/yourusername/liveTranslation_openai-whisper.git
```

2. Navigate to the cloned directory:
```bash
cd liveTranslation_openai-whisper`
```

3. Install required libraries:
```bash
pip install -r requirements.txt
```

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
```bash
python main.py -d 4 -c Spanish
```

---

- 10-second live translation in continuous mode
```bash
python main.py -d 10 -t
```

---

- Translate an existing audio file with Shimmer's voice
```bash
python main.py -f audioFileName.wav -v shimmer
```

---


- Smart Select with Nova voice, 8-second recording in continuous mode
```bash
python main.py -c 'Smart Select' -v nova -d 8 -t
```

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
