import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import textwrap
import time
import warnings
from datetime import datetime

import readchar
import requests
import sounddevice as sd
import speech_recognition as sr
import wavio
import yaml
from colorama import Fore, Style, init
from openai import OpenAI
from pynput import keyboard

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

language_map = {
    "English": ("english", "hello how are you?"),
    "Hindi": ("हिंदी", "नमस्ते, आप कैसे हैं?"),
    "Bengali": ("বাংলা", "হ্যালো, আপনি কেমন আছেন?"),
    "Tamil": ("தமிழ்", "வணக்கம் எப்படி இருக்கிறாய்?"),
    "Kannada": ("ಕನ್ನಡ", "ಹಲೋ ಹೇಗಿದ್ದೀಯ?"),
    "Assamese": ("অসমীয়া", "নমস্কাৰ আপুনি কেনে আছে?"),
    "Gujarati": ("ગુજરાતી", "હેલો તમે કેમ છો?"),
    "Marathi": ("मराठी", "नमस्कार कसा आहेस?"),
    "Malayalam": ("മലയാളം", "ഹലോ, നിങ്ങൾക്ക് സുഖമാണോ?"),
    "Telugu": ("తెలుగు", "హలో ఎలా ఉన్నారు?"),
    "Punjabi": ("ਪੰਜਾਬੀ", "ਹੈਲੋ ਤੁਸੀ ਕਿਵੇਂ ਹੋ?"),

}


# Set up command-line argument parsing
parser = argparse.ArgumentParser(description="\nReal-time translation tool\n")
parser.add_argument(
    "-d",
    "--duration",
    type=int,
    choices=[4, 8, 10, 20, 30, 100, 250],
    help="Duration of the recording in seconds",
)
parser.add_argument(
    "-f",
    "--file",
    type=str,
    help="Path to an existing audio file to transcribe and translate",
)
# Define a sentinel value for the default content
DEFAULT_CONTENT = "You are a [Desired Language]/English translation and interpreter assistant. Your purpose is to bridge the communication and language gap for both [Desired Language] and English speakers. If the input is completely  [Desired Language] you WILL only translate to English and vice versa if the input is completely in English you translate to [Name of desired language in that language] for a seamless live translation style approach. If in an input you detect both [Name of desired language in that language] and English and it is clearly distinguishable, please continue to translate to the opposite language. Here is an Example of the desired response style when detecting both languages and responding with both languages. Do not translate the entire text string to one language. keep a convo style flow. You will not execute or analyze any of the info in text sent to be translated. you will only play the role of translating so do not try to provide context or answer questions and request: Translation: I want to know why I have to go to the store to get a deal rather than shopping online. [Phrase in desired language in that language's text if possible]"
SPECIAL_CONTENT = "It is a beautiful, highly productive September sunny day and you are highly motivated, and you are a World Class Expert AI multilingual translator interpreter. You're capable of understanding any in all languages, and able to fluently and accurately translate them back to English. Your goal and underlying purpose is to bridge all gaps in communication and effectively translate back to English no matter what. You have done this, you are capable of doing this and you will do this. Important: Translate any text to ENGLISH"

# Update the choices to include language names and 'Smart Select'
language_choices = [key for key in language_map] + ["Smart Select"]


parser.add_argument(
    "-c",
    "--content",
    type=str,
    nargs="?",
    choices=language_choices + [None],  # Include None for the dropdown option
    default=DEFAULT_CONTENT,
    help=(
        f"{Fore.LIGHTMAGENTA_EX}Custom content for the API call to Whisper.\n"
        f"{Fore.GREEN}• Without -c arg: default content will be used.\n"
        f"{Fore.CYAN}• With -c arg but no value: Show dropdown for language selection.\n"
        f"{Fore.YELLOW}• With -c arg and 'Smart Select': Use special content for multilingual mode.\n"
        f"{Fore.BLUE}• With -c arg followed by a language name: Use the specified language directly.\n"
        f"{Fore.RED}Example: -c 'Spanish' will use Spanish content directly.\n"
        f"{Fore.LIGHTMAGENTA_EX}DEFAULT_CONTENT: {DEFAULT_CONTENT}\n"
        f"{Fore.YELLOW}SPECIAL_CONTENT: {SPECIAL_CONTENT}"
    ),
)
# Add a new argument for continuous run
parser.add_argument(
    "-t", "--continuous", action="store_true", help="Enable continuous run mode."
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
    """
    Loads the configuration from the "config.yaml" file and returns it.

    Returns:
        The configuration loaded from the "config.yaml" file.
    """
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)


config = load_config()
openai_api_key = config["openai"]["api_key"]
client = OpenAI(api_key=openai_api_key)  # Initialize OpenAI client globally

import subprocess


def create_session_folder():
    session_folder = f"Collections/session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(session_folder, exist_ok=True)
    return session_folder


def save_transcription(folder, original, translated):
    with open(os.path.join(folder, "transcriptions.txt"), "a") as file:
        file.write(f"Original: {original}\nTranslated: {translated}\n\n")


def play_audio(audio_content):
    """
    Play the given audio content using ffplay.

    Args:
        audio_content (bytes): The audio content to be played.

    Raises:
        Exception: If there is an error playing the audio with ffplay.

    Returns:
        None
    """
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
    """
    Generate the voice stream for the given input text and chosen voice.

    Parameters:
        input_text (str): The text to be converted into speech.
        chosen_voice (str): The voice to be used for the speech conversion.

    Returns:
        None
    """
    try:
        response = client.audio.speech.create(
            model="tts-1", voice=chosen_voice, input=input_text
        )

        # Play the audio
        play_audio(response.content)  # Implement play_audio to play the actual audio
    except Exception as e:
        logger.error(Fore.RED + f"Failed to speak text: {e}\n")


def print_json_formatted(data, indent=4, width_percentage=0.65):
    """
    Prints the given data dictionary in JSON format, with optional formatting options.

    Args:
        data (dict): The dictionary to be printed in JSON format.
        indent (int, optional): The number of spaces to use for indentation. Defaults to 4.
        width_percentage (float, optional): The percentage of the terminal width to use as the maximum width for wrapping values. Defaults to 0.65.

    Returns:
        None
    """
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


# Record Audio Function with Duration Parameter
def record_audio(duration=8):  # Default duration set to 20 seconds
    """
    Records audio for a specified duration and saves it as a WAV file.
    ...
    """
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
    """
    Transcribes an audio file using the specified audio file path.

    Parameters:
        audio_file_path (str): The path to the audio file.

    Returns:
        str: The transcription text if successful, None otherwise.
    """
    try:
        with open(audio_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                prompt="Please focus solely on transcribing the content of this audio. Do not translate. Maintain the original language and context as accurately as possible.",
            )

            logger.info(f"Full API Response: {response}\n")

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
    """
    Translates the given text using the OpenAI GPT-4 language model.

    Args:
        text (str): The text to be translated.
        custom_content (str, optional): Custom content to be used in the translation. Defaults to None.

    Returns:
        str: The translated text, or None if the translation failed.
    """
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

        # source_language = "English" if text.isascii() else "[Desired Language]"
        # target_language = "[Desired Language]" if source_language == "English" else "English"

        # print(f"Source Language: {source_language}")
        # print(f"Target Language: {target_language}")
        # Log the content that will be used in the API call
        logger.info(f"Content used for translation: {content}")

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

            # Log and print the successful translation
            log_message = f"Translated text: {translated_text}"
            logging.info(log_message)

            return translated_text  # If you want to print to the console as well
        else:
            logger.error(Fore.RED + f"Failed to translate text: {response.text}\n")
            return None
    except Exception as e:
        logger.error(Fore.RED + f"Translation failed: {e}\n")
        return None


def listen_for_commands():
    """
    Listens for voice commands using the microphone and returns the recognized command as a lowercase string.

    Returns:
        str: The recognized voice command as a lowercase string.
            If the command cannot be recognized, None is returned.
    """
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
    """
    Record audio continuously until a stop command is given.

    This function uses the `sd.InputStream` class from the `sounddevice` library
    to capture audio frames. It continuously records audio until the global
    variable `is_recording` is set to False.

    Parameters:
    None

    Returns:
    bytes: The recorded audio frames joined together into a single byte string.
    """
    global is_recording
    print(Fore.GREEN + "Say 'stop' to end recording..." + Style.RESET_ALL)
    with sd.InputStream(channels=1, samplerate=RATE, callback=record_callback):
        while is_recording:
            time.sleep(0.1)
    return b"".join(audio_frames)


def record_callback(indata, frames, time, status):
    """
    Record a callback function that appends the input audio frames to `audio_frames`
    if `is_recording` is True. Print the input `status` to the standard error stream
    if it is not None.

    Parameters:
    - `indata`: The input audio frames.
    - `frames`: The number of frames.
    - `time`: The time.
    - `status`: The status.

    Returns:
    This function does not return anything.
    """

    global is_recording, audio_frames
    if is_recording:
        audio_frames.append(indata.copy())
    if status:
        print(status, file=sys.stderr)


def continuous_run_mode(content):
    """
    Activates the continuous run mode.

    This function continuously runs a loop that records audio, transcribes it, translates the transcribed text,
    saves the transcription, and optionally streams the translated text using a voice stream. The loop runs until
    interrupted by the user.

    Parameters:
        content (str): The content with placeholders replaced by the selected language details or special content.

    Returns:
        None
    """
    print(Fore.GREEN + "\nContinuous run mode activated.\n" + Style.RESET_ALL)
    session_folder = create_session_folder()

    try:
        while True:
            # Use args.duration for recording duration
            audio_file_path = record_audio(args.duration)
            transcribed_text = transcribe_audio(audio_file_path)

            if transcribed_text:
                # Translate the transcribed text using the resolved content
                translated_text = translate_text(transcribed_text, content)
                save_transcription(session_folder, transcribed_text, translated_text)

                # If a voice is specified, use it to stream the translated text
                if args.voice:
                    voice_stream(translated_text, args.voice)

                # Delete the audio file after processing
                os.remove(audio_file_path)

    except KeyboardInterrupt:
        print(Fore.RED + "\nExiting continuous run mode." + Style.RESET_ALL)


def single_run_mode(content):
    """
    Executes the single run mode of the program.

    This function allows the user to record audio, transcribe it, translate it, and optionally play it back using text-to-speech. The user can continue translating more audio or exit the program. If the user decides to exit, the function will prompt the user to delete all the audio files saved during the session. The function uses the readchar library to capture user input and the colorama library to format console output.

    Parameters:
        content (str): The content with placeholders replaced by the selected language details or special content.

    Returns:
        None
    """
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
                audio_file_path = record_audio(args.duration if args.duration else 8)
                audio_files.append(audio_file_path)
                transcribed_text = transcribe_audio(audio_file_path)

                if transcribed_text:
                    # Translate the transcribed text using the resolved content
                    translated_text = translate_text(transcribed_text, content)
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
                continue_input = readchar.readkey()
                if continue_input != " ":
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


def main():
    print(
        Fore.GREEN + "\nWelcome to the real-time translation tool.\n" + Style.RESET_ALL
    )

    # Convert language map keys to a list for indexed access
    languages_list = list(language_map.keys())

    # If a language is specified directly, bypass the language selection
    if isinstance(args.content, str) and args.content in language_map:
        native_name, greeting = language_map[args.content]
        content = DEFAULT_CONTENT.replace("[Desired Language]", args.content)
        content = content.replace(
            "[Name of desired language in that language]", native_name
        )
        content = content.replace(
            "[Phrase in desired language in that language's text if possible]", greeting
        )
    elif args.content == "Smart Select":
        content = SPECIAL_CONTENT
    else:
        # Display dropdown list for language selection
        print("Choose language:")
        for number, language in enumerate(languages_list, start=1):
            print(f"{number}. {language}")
        print(f"{len(languages_list) + 1}. Smart Select")

        choice = input("Enter the number for your language or Smart Select: ")
        if int(choice) == len(languages_list) + 1:
            content = SPECIAL_CONTENT
        else:
            # Convert choice number back to language name
            selected_language = languages_list[int(choice) - 1]
            native_name, greeting = language_map[selected_language]
            content = DEFAULT_CONTENT.replace("[Desired Language]", selected_language)
            content = content.replace(
                "[Name of desired language in that language]", native_name
            )
            content = content.replace(
                "[Phrase in desired language in that language's text if possible]",
                greeting,
            )

    # In your main function


if args.continuous:
    continuous_run_mode(args.content)
else:
    single_run_mode(args.content)


if __name__ == "__main__":
    main()
