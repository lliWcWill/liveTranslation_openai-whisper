# OpenAI Whisper-Enhanced Live Translation Tool

## Description
The OpenAI Whisper-Enhanced Live Translation Tool now boasts full API integration for transcribing, translating, and speech synthesis, transforming global communication and language education. With the new -c argument, users enjoy expanded multilingual support and can experience translated content with voice output. Future updates may include an AI language teacher assistant, further enriching the immersive learning experience. This tool represents a leap forward in accessible language technology, fostering understanding across diverse linguistic barriers.

### Latest Release Highlights
- **Full API Integration**: Leverage the power of OpenAI's API for transcription, translation, and text-to-speech, ensuring an uninterrupted and cohesive experience.
- **Expanded Multilingual Support**: Utilize the `-c` argument to select from an extensive list of supported languages, catering to diverse linguistic needs.
- **Enhanced Text-to-Speech**: Bring translations to life with the `-v` voice option, offering an engaging auditory experience for users.
- **Roadmap to AI Language Assistant**: Anticipate the evolution of the tool into an interactive AI language teacher assistant, expanding educational possibilities and user interaction.

### Installation & Setup
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
```
# 4-second live translation in Spanish with toggle recording
python main.py -d 4 -c Spanish

# 10-second live translation in continuous mode
python main.py -d 10 -t

# Translate an existing audio file with Shimmer's voice
python main.py -f audioFileName.wav -v shimmer

# Smart Select with Nova voice, 8-second recording in continuous mode
python main.py -c 'Smart Select' -v nova -d 8 -t
```


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
