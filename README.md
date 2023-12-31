# Live Translation Tool with OpenAI Whisper

## Description
This live translation tool is a real-time audio translation application utilizing OpenAI's Whisper model and GPT-4 for accurate and efficient language translation. It's designed to provide seamless translation between English and Spanish, making it ideal for various real-world applications.

## Installation
### Prerequisites
- Python 3.x
- Whisper
- Pydub
- SoundDevice
- Requests

### Steps
1. Clone the repository: `git clone https://github.com/yourusername/liveTranslation_openai-whisper.git`
2. Install required libraries: `pip install -r requirements.txt`

## Usage
To use the tool, run `python main_localWhisper.py` with the following arguments:
- `-d`: Duration of the recording in seconds (options: 4, 8, 10, 20, 30)
- `-f`: Path to an existing audio file to transcribe and translate

Example: `python main_localWhisper.py -d 10`

## Configuration
Before using the tool, configure `config.yaml` with your OpenAI API key:
```yaml
openai:
  api_key: "Your-OpenAI-API-Key"
```

## Dependencies
- `whisper`: For audio transcription
- `pydub`: Audio manipulation library
- `sounddevice`: Audio recording
- `requests`: For API requests

## Troubleshooting
If you encounter any issues, ensure that your microphone settings are correctly configured and the OpenAI API key is valid.

## Contributing
Contributions to improve the tool or extend its functionalities are welcome. Please fork the repository and submit a pull request with your changes.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
For more information, contact me at [your-email@example.com](mailto:your-email@example.com).

## Acknowledgments
Special thanks to the OpenAI team for Whisper and GPT-4 models.
