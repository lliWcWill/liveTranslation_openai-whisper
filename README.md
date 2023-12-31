# Live Translation Tool with OpenAI Whisper

## Description
This live translation tool leverages OpenAI's Whisper model for real-time audio transcription and GPT-4 for accurate language translation. It supports seamless English-Spanish translation suitable for diverse applications.

## Installation
### Prerequisites
- Python 3.x
- Whisper
- Pydub
- SoundDevice
- Requests

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

## Usage
Run the tool using `python main_localWhisper.py` with optional arguments:
- `-d`: Specify the recording duration in seconds (options: 4, 8, 10, 20, 30)
- `-f`: Provide the path to an existing audio file for transcription and translation - if file is in the same directory just name the file

Example: `python main_localWhisper.py -d 10`
Example 2: `python main_localWhisper.py -f audioFileName.wav`

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
