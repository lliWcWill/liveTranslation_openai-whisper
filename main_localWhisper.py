# main_LocalWhisper.py
import os
import yaml
import whisper
import requests
import json
import sys
import wavio
from datetime import datetime
import argparse
import warnings
import sounddevice as sd
from scipy.io.wavfile import write
from pydub import AudioSegment
from pydub.silence import split_on_silence
from colorama import Fore, Style, init
from tqdm import tqdm

# Initialize colorama
init(autoreset=True)

# Ignore FP16 warning from whisper
warnings.filterwarnings("ignore", category=UserWarning, module="whisper.transcribe")

# Baseline variables for recording audio for a specified duration and filename
record_audio_duration = 30  # seconds
record_audio_filename = f"audio_record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="Real-time translation tool")
parser.add_argument(
    "-d",
    "--duration",
    type=int,
    choices=[4, 8, 10, 20, 30],
    help="Duration of the recording in seconds",
)
parser.add_argument(
    "-f",
    "--file",
    type=str,
    help="Path to an existing audio file to transcribe and translate",
)
args = parser.parse_args()

# Use the provided duration or default to 5 seconds if none is provided
duration = args.duration if args.duration else 5


# Load configuration
def load_config():
    """
    Loads the configuration from the 'config.yaml' file.

    Returns:
        The loaded configuration as a dictionary.
    """
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)


config = load_config()
openai_api_key = config["openai"]["api_key"]


def record_audio():
    """
    Record audio using the global duration and filename settings.
    Returns the path to the recorded audio file.
    """
    print(
        f"{Fore.GREEN}Recording audio for {record_audio_duration} seconds...{Style.RESET_ALL}"
    )
    audio_data = sd.rec(
        int(record_audio_duration * 16000), samplerate=16000, channels=1, dtype="int16"
    )
    sd.wait()  # Wait until recording is finished
    wavio.write(record_audio_filename, audio_data, 16000, sampwidth=2)
    print(f"Audio saved to {record_audio_filename}")
    return record_audio_filename  # Return the filename of the recorded audio


# Usage- used to trigger and save audip recording, good use for testing functions
# record_audio(duration=record_audio_duration, filename=record_audio_filename)


def transcribe_audio(audio_file_path):
    """
    Transcribes audio from a file using Whisper.
    """
    try:
        model = whisper.load_model("small")
        result = model.transcribe(audio_file_path)
        return result["text"]
    except Exception as e:
        print(f"Transcription failed: {e}")
        return None


def translate_text(text, openai_api_key):
    """
    Translates the given text using the OpenAI API.

    Args:
        text (str): The text to be translated.
        openai_api_key (str): The API key for accessing the OpenAI API.

    Returns:
        str: The translated text.
    """
    # Determine the language of the input and set the target language
    if text.isascii():
        source_language = "English"
        target_language = "Spanish"
    else:
        source_language = "Spanish"
        target_language = "English"

    # Craft the translation prompt
    translation_prompt = f"[{source_language} to {target_language} translation]: {text}"

    # Prepare the API request
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {openai_api_key}",
        },
        json={
            "model": "gpt-4-1106-preview",  # Specify the correct model here
            "messages": [
                {
                    "role": "system",
                    "content": "It is a highly productive September midday and you are a highly motivated world class translation assistant specialized in Latin Spanish and Enlgish.",
                },
                {"role": "user", "content": translation_prompt},
            ],
        },
    )

    # Parse the response
    if response.status_code == 200:
        response_data = json.loads(response.text)
        translated_text = response_data["choices"][0]["message"]["content"]
        return translated_text.strip()
    else:
        print(f"Failed to translate text: {response.text}")
        return None


def main():
    """
    The main function is the entry point of the program. It prints a welcome message and checks if a file path is provided. If a file path is provided, it checks if the file exists. If the file does not exist, it prints an error message and exits the program. If a file path is not provided, it records new audio and gets the file path. It then transcribes the audio, translates the transcribed text using the OpenAI API, and prints the translated text. If the transcription fails, it prints an error message. The function handles keyboard interrupts and exits the program gracefully.
    """
    print(Fore.YELLOW + Style.BRIGHT + "Welcome to the real-time translation tool.")

    # Check if a file path is provided
    if args.file:
        audio_file_path = args.file
        if not os.path.isfile(audio_file_path):
            print(f"The file {audio_file_path} does not exist.")
            sys.exit(1)
    else:
        # Record new audio and get the file path
        audio_file_path = record_audio()

    try:
        transcribed_text = transcribe_audio(audio_file_path)
        if transcribed_text:
            translated_text = translate_text(transcribed_text, openai_api_key)
            if translated_text:
                print(f"Translated text: {translated_text}")
        else:
            print("Transcription failed, please try again.")
    except KeyboardInterrupt:
        print("\nExiting the program...")
        sys.exit(0)


if __name__ == "__main__":
    main()
