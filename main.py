import logging
import os
import yaml
import requests
import json
import sys
import textwrap
import wavio
import readchar
import speech_recognition as sr
from pynput import keyboard
import sounddevice as sd
from openai import OpenAI
from datetime import datetime
import argparse
import warnings
import subprocess
import time
from colorama import Fore, Style, init
import shutil

# Initialize colorama and logging
init(autoreset=True)
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# Global variable to control the recording state
is_recording = False

# Constants for recording
WAVE_OUTPUT_FILENAME = "temp_audio.wav"
CHANNELS = 1
SAMPLE_WIDTH = 2
RATE = 16000
FORMAT = "int16"


# Ignore FP16 warning from whisper
warnings.filterwarnings("ignore", category=UserWarning, module="whisper.transcribe")

# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="\nReal-time translation tool\n")
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
# Define a sentinel value for the default content
DEFAULT_CONTENT = "You are a Spanish and English translation and interpretator assistant. Your purpose is to translate to help bridge the gap for english and spanish speakers. If you detect Spanish you translate to english and if you detect english you translate to spanish. If you dectect both spanish and english and it is Clearly distinguishable, please continue to translate to the opposite language. example of detecting both languages) Translation: I want to know why I have to go to the store to get a deal rather than shopping online. Quieres mi corazon para mi vida porque no me importa."
SPECIAL_CONTENT = "It is a beautiful highly productive September sunny day and you are highly motivated, and you a World Class Expert AI multilingual translator interpreter. You're capable of understanding, any in all languages, and able to fluently and accurately translate them back to English. Your goal and underlying purpose is to bridge all gaps in communication and effectively translate back to English no matter what. You have done this you are capable of doing this and you will do this. Important: Translate any text to ENGLISH"

# Modify the argparse setup
parser.add_argument(
    "-c",
    "--content",
    type=str,
    nargs="?",
    const=SPECIAL_CONTENT,
    default=DEFAULT_CONTENT,
    help="Custom content for the API call to Whisper",
)
# Define a sentinel value for the default voice
voice_choices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
parser.add_argument(
    "-v",
    "--voice",
    choices=voice_choices,
    help="Choose a TTS voice for speaking the translation.",
)
args = parser.parse_args()


# Load configuration and initialize OpenAI client
def load_config():
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)


config = load_config()
openai_api_key = config["openai"]["api_key"]
client = OpenAI(api_key=openai_api_key)  # Initialize OpenAI client globally

import subprocess


def play_audio(audio_content):
    try:
        # Start a subprocess that runs ffplay
        ffplay_proc = subprocess.Popen(
            ["ffplay", "-nodisp", "-autoexit", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

        # Write the audio content to ffplay's stdin
        ffplay_proc.stdin.write(audio_content)
        ffplay_proc.stdin.flush()

        # Close the stdin and wait for ffplay to finish playing the audio
        ffplay_proc.stdin.close()
        ffplay_proc.wait()
    except Exception as e:
        logger.error(Fore.RED + f"Error playing audio with ffplay: {e}\n")


def voice_stream(input_text, chosen_voice):
    try:
        response = client.audio.speech.create(
            model="tts-1", voice=chosen_voice, input=input_text
        )

        # Play the audio
        play_audio(response.content)  # Implement play_audio to play the actual audio
    except Exception as e:
        logger.error(Fore.RED + f"Failed to speak text: {e}\n")


def print_json_formatted(data, indent=4, width_percentage=0.65):
    # Get the width of the terminal
    terminal_width = shutil.get_terminal_size((80, 20)).columns

    # Calculate the maximum width based on the terminal width and the given width percentage
    max_width = int(terminal_width * width_percentage)

    # Iterate over the key-value pairs in the data dictionary
    for key, value in data.items():
        # Create a string representation of the key, without the value
        key_str = json.dumps({key: ""}, indent=indent).rstrip(": {}\n")

        # Create a string representation of the value
        value_str = json.dumps(value, ensure_ascii=False)

        # Create a text wrapper that wraps the value with the specified maximum width
        wrapper = textwrap.TextWrapper(
            width=max_width, subsequent_indent=" " * (indent + len(key) + 4)
        )

        # Determine the color based on the key
        if key == "Transcription":
            color = Fore.GREEN
        elif key == "Translation":
            color = Fore.MAGENTA
        else:
            color = Fore.CYAN

        # Print the key in yellow, followed by a colon
        print(wrapper.fill(Fore.YELLOW + key_str + Style.RESET_ALL + ":"), end="")

        # Print the value in the specified color
        print(color + value_str + Style.RESET_ALL)


# Record Audio Function
def record_audio(duration=20):
    filename = f"audio_record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    print(Fore.GREEN + f"\nRecording for {duration} seconds...\n" + Style.RESET_ALL)
    audio_data = sd.rec(
        int(duration * RATE), samplerate=RATE, channels=CHANNELS, dtype=FORMAT
    )
    sd.wait()  # Wait until the recording is finished
    wavio.write(filename, audio_data, RATE, sampwidth=SAMPLE_WIDTH)
    logger.info(Fore.GREEN + f"Confirmed Audio Saved!\n")
    return filename


# Transcribe Audio Function with Corrected Handling
def transcribe_audio(audio_file_path):
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )

            # f"Full API Response: {response}\n"

            # Check for transcription text
            if hasattr(response, "text") and response.text:
                return response.text
            else:
                logger.error(Fore.RED + "No transcription data found in the response\n")
                return None
    except Exception as e:
        logger.error(Fore.RED + f"Transcription failed due to an error: {e}\n")
        return None


def translate_text(text, custom_content=None):
    try:
        # Determine the content based on the custom_content and text arguments
        if custom_content is not None:
            if text:
                # When -c is used and there is text following, use the user's text
                content = custom_content
            else:
                # When -c is used and no text is following, use the special content
                content = custom_content
        else:
            # If -c is not used, use the default content
            content = DEFAULT_CONTENT

        # source_language = "English" if text.isascii() else "Spanish"
        # target_language = "Spanish" if source_language == "English" else "English"

        # print(f"Source Language: {source_language}")
        # print(f"Target Language: {target_language}")

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_api_key}",
            },
            json={
                "model": "gpt-4-1106-preview",
                "messages": [
                    {
                        "role": "system",
                        "content": content,
                    },
                    {"role": "user", "content": f"{text}"},
                ],
            },
        )

        if response.status_code == 200:
            response_data = json.loads(response.text)
            translated_text = response_data["choices"][0]["message"]["content"].strip()
            return translated_text
        else:
            logger.error(Fore.RED + f"Failed to translate text: {response.text}\n")
            return None
    except Exception as e:
        logger.error(Fore.RED + f"Translation failed: {e}\n")
        return None


def listen_for_commands():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for voice commands...")
        audio = r.listen(source)
        try:
            command = r.recognize_google(audio)
            return command.lower()
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None


def voice_to_text():
    """
    Transcribes voice from recorded audio data.
    """
    global audio_frames
    # Save the recorded audio data to a WAV file
    wavio.write(WAVE_OUTPUT_FILENAME, audio_frames, RATE, sampwidth=SAMPLE_WIDTH)

    # Transcribe the saved audio file
    with open(WAVE_OUTPUT_FILENAME, "rb") as f:
        transcript = client.audio.transcriptions.create(model="whisper-1", file=f)
        return transcript.text


# Global variable to store audio frames
audio_frames = []


def record_audio_continuous():
    global is_recording
    print(Fore.GREEN + "Say 'stop' to end recording..." + Style.RESET_ALL)
    with sd.InputStream(channels=1, samplerate=RATE, callback=record_callback):
        while is_recording:
            time.sleep(0.1)
    return b"".join(audio_frames)


def record_callback(indata, frames, time, status):
    global is_recording, audio_frames
    if is_recording:
        audio_frames.append(indata.copy())
    if status:
        print(status, file=sys.stderr)


def main():
    print(
        Fore.GREEN + "\nWelcome to the real-time translation tool.\n" + Style.RESET_ALL
    )
    audio_files = []  # Keep track of recorded audio files for cleanup

    while True:
        try:
            print(
                Fore.GREEN
                + "Press the space bar to start recording or 'exit' to quit:"
                + Style.RESET_ALL
            )
            user_input = readchar.readkey()

            if user_input == " ":
                audio_file_path = record_audio(args.duration if args.duration else 20)
                audio_files.append(audio_file_path)
                transcribed_text = transcribe_audio(audio_file_path)

                # Common translation and output logic
                if transcribed_text:
                    translated_text = translate_text(transcribed_text)
                    json_output = {
                        "Original Content": transcribed_text,
                        "Translation": translated_text,
                    }
                    print_json_formatted(json_output)

                    if args.voice:
                        voice_stream(translated_text, args.voice)
                        print(
                            Fore.GREEN
                            + "\nDo you want to translate more? (Press space to continue)"
                            + Style.RESET_ALL
                        )
                        user_input = readchar.readkey()
                        if user_input != " ":
                            break

            elif user_input.lower() == "exit":
                print(Fore.RED + "\nExiting the program." + Style.RESET_ALL)
                break

        except KeyboardInterrupt:
            print(Fore.RED + "\nExiting the program." + Style.RESET_ALL)
            break

    # Clean up logic
    print(
        Fore.YELLOW
        + "\nDo you want to "
        + Fore.RED
        + "delete all"
        + Fore.YELLOW
        + " audio files saved during this session?"
        + Style.RESET_ALL
    )
    print(
        Fore.YELLOW
        + "Press the "
        + Fore.MAGENTA
        + "S P A C E B A R"
        + Fore.YELLOW
        + " to delete all or press "
        + Fore.GREEN
        + "E N T E R"
        + Fore.YELLOW
        + " to save and exit."
        + Style.RESET_ALL
    )
    audio_files = []
    try:
        user_input = readchar.readkey()
        if user_input == " ":
            for file_path in audio_files:
                os.remove(file_path)
            print(Fore.GREEN + "All audio files have been deleted." + Style.RESET_ALL)
        else:
            print(
                Fore.GREEN + "Exiting without deleting audio files." + Style.RESET_ALL
            )
    except Exception as e:
        print(Fore.RED + f"An error occurred: {e}" + Style.RESET_ALL)


if __name__ == "__main__":
    main()
