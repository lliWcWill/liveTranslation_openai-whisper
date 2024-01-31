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

import glob
from pathlib import Path
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
    "European Spanish (Spain)": ("Español Europeo", "Buenos días, ¿cómo estás hoy?"),
    "Spanish": ("Español", "¿Qué onda? ¿Todo bien?"),
    "Caribbean Spanish (Cuba, Puerto Rico, Dominican Republic)": (
        "Español Caribeño",
        "Hace mucho calor hoy, ¿verdad?",
    ),
    "Central American Spanish (Guatemala, Honduras, Nicaragua)": (
        "Español Centroamericano",
        "Vamos a la playa este fin de semana.",
    ),
    "Andean Spanish (Peru, Bolivia, Ecuador)": (
        "Español Andino",
        "La comida aquí es muy deliciosa.",
    ),
    "Rioplatense Spanish (Argentinna and Uruguay)": (
        "Español Rioplatense",
        "¿Me pasás la yerba, por favor?",
    ),
    "Chilean Spanish": ("Español Chileno", "¿Cachai lo que te estoy diciendo?"),
    "Colombian Spanish": ("Español Colombiano", "¿Quieres ir a tomar un tinto?"),
    "Venezuelan Spanish": (
        "Español Venezolano",
        "Vamos a comer unas arepas esta noche.",
    ),
    "Canary Islands Spanish": ("Español Canario", "El cielo está muy despejado hoy."),
    "Mandarin Chinese": ("普通话", "你好，你吃饭了吗？"),
    "French": ("Français", "Bonjour, où se trouve la bibliothèque?"),
    "German": ("Deutsch", "Kannst du mir helfen, bitte?"),
    "Portuguese": ("Português", "Bom dia, como você está?"),
    "Russian": ("Русский", "Как дела? Всё хорошо?"),
    "Japanese": ("日本語", "こんにちは、元気ですか？"),
    "Italian": ("Italiano", "Dove posso trovare un buon ristorante?"),
    "Arabic": ("العربية", "مرحبا، كيف حالك اليوم؟"),
    "Hindi": ("हिंदी", "नमस्ते, आप कैसे हैं?"),
    "Korean": ("한국어", "안녕하세요, 잘 지내세요?"),
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
    Loads the application's configuration settings from a YAML file named 'config.yaml'. This function is essential
    for initializing the application with specific parameters, API keys, and other configuration details that are
    stored externally in a YAML file.

    The function specifically looks for a file named 'config.yaml' in the same directory. It is expected that this
    file contains structured data in YAML format, which this function reads and parses.

    Returns:
        dict: A dictionary containing the configuration data loaded from 'config.yaml'. The structure of this dictionary
              will mirror the structure of the YAML file.

    Example usage:
        config = load_config()
        print(config)
        # Output: {'openai': {'api_key': 'your-api-key'}}

    Notes:
        - The configuration file must be structured correctly in YAML format. For instance, API keys and other
          sensitive information can be stored under specific keys.
        - The function uses 'yaml.safe_load' for security reasons, as it safely loads the YAML file without
          executing any arbitrary code.
        - Ensure that 'config.yaml' is present in the same directory as this script or adjust the file path
          as necessary.
    """
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)


config = load_config()
openai_api_key = config["openai"]["api_key"]
client = OpenAI(api_key=openai_api_key)  # Initialize OpenAI client globally

import subprocess


def create_session_folder():
    """
    Creates a new folder dedicated to storing the audio files and transcriptions for a specific session.
    This function is integral to organizing the output files generated during a session, such as recordings,
    transcriptions, and translations, in a structured and easily accessible manner.

    The folder is named with a unique timestamp to differentiate it from other sessions. This naming convention
    ensures that each session's data is kept separate and prevents any overwriting of files from different sessions.

    Returns:
        str: The file path to the newly created session folder. The folder name includes a timestamp
             to ensure uniqueness (format: 'Collections/session_YYYYMMDD_HHMMSS').

    Example:
        session_folder_path = create_session_folder()
        print(session_folder_path)
        # Output: 'Collections/session_20211231_235959'

    Notes:
        - The function uses 'os.makedirs' with 'exist_ok=True' to create the session folder. This means if the
          folder already exists, the function will not raise an error, making it robust for repeated calls.
        - The folder is created within a 'Collections' directory; ensure this directory exists or adjust the
          path as needed based on your application's directory structure.
    """
    session_folder = f"Collections/session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    os.makedirs(session_folder, exist_ok=True)
    return session_folder


def save_transcription(folder, original, translated):
    """
    Saves the transcription and its translation into a text file within the specified folder. This function is
    designed to record the original transcribed text and its translated counterpart in a structured format,
    making it easy to review and reference.

    The function appends each new transcription and translation pair to a file named 'transcriptions.txt' in
    the specified folder. This approach ensures that all transcriptions from a session are collected in a single
    document, preserving the context and sequence of the translated conversations or audio segments.

    Args:
        folder (str): The file path to the folder where the transcription and its translation will be saved.
                      The function will append to the 'transcriptions.txt' file in this folder.
        original (str): The original text obtained from transcribing the audio.
        translated (str): The translated version of the original text.

    Returns:
        None

    Example:
        save_transcription("/path/to/session_folder", "Hello, how are you?", "Hola, ¿cómo estás?")

    Notes:
        - The function opens the file in append mode ('a'), which allows for multiple write operations without
          overwriting the existing content.
        - Each entry in the 'transcriptions.txt' file is formatted with the original text labeled as 'Original'
          and the translated text labeled as 'Translated', followed by two newline characters for readability.
    """

    with open(os.path.join(folder, "transcriptions.txt"), "a") as file:
        file.write(f"Original: {original}\nTranslated: {translated}\n\n")


def play_audio(audio_content=None, file_path=None):
    """
    Plays audio using the 'ffplay' command-line tool. This function can handle audio either as raw byte content
    or from a specified file path. It is versatile for various audio playback scenarios, including immediate
    playback of synthesized speech or playing saved audio files.

    The function uses the 'ffplay' tool, which is part of the FFmpeg suite, known for its efficiency and
    compatibility with various audio formats. It is designed to execute 'ffplay' in a non-blocking manner,
    allowing the Python script to continue running other tasks while audio is playing.

    Args:
        audio_content (bytes, optional): The audio content in bytes to be played directly. Used if no file_path is provided.
        file_path (str, optional): The path to an audio file that should be played. If specified, audio_content is ignored.

    Raises:
        Exception: If an error occurs while attempting to play the audio using ffplay, the exception is caught and logged.

    Returns:
        None

    Notes:
        - The function uses subprocess to run 'ffplay'. Depending on the argument provided, it either streams the byte
          content to ffplay's standard input or directly plays from the provided file path.
        - If both 'audio_content' and 'file_path' are provided, 'file_path' takes precedence.
        - The '-nodisp' and '-autoexit' flags ensure that ffplay runs without displaying a window and exits immediately
          after playback.
    """
    try:
        cmd = ["ffplay", "-nodisp", "-autoexit"]
        stdin_pipe = None

        if file_path:
            cmd.append(file_path)
        else:
            cmd.append("-")
            stdin_pipe = subprocess.PIPE

        ffplay_proc = subprocess.Popen(
            cmd,
            stdin=stdin_pipe,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

        if audio_content and not file_path:
            # Write the audio content to ffplay's stdin if it's from bytes
            ffplay_proc.stdin.write(audio_content)
            ffplay_proc.stdin.flush()
            ffplay_proc.stdin.close()

        ffplay_proc.wait()
    except Exception as e:
        logger.error(Fore.RED + f"Error playing audio with ffplay: {e}\n")


def voice_stream(
    input_text, chosen_voice, session_folder
):  # Add session_folder parameter
    """
    Converts the given text into speech using the specified voice, through the OpenAI API's text-to-speech synthesis.
    The generated speech is both played immediately and saved as an audio file in the specified session folder.

    This function is integral to applications requiring audio feedback or interaction, particularly in scenarios
    like language translation where the translated text is vocalized. It serves the dual purpose of providing
    immediate audio playback and storing the audio for possible replay.

    Args:
        input_text (str): The text that needs to be converted into speech.
        chosen_voice (str): The identifier of the voice model to be used for the synthesis.
        session_folder (str): The directory path where the synthesized audio file will be saved.

    Returns:
        str: The file path of the saved AI audio file, allowing for subsequent access and replay.

    Raises:
        Exception: An exception is raised and logged if there's an error during the synthesis process.

    Notes:
        The function first synthesizes the speech and then saves the audio content in a WAV file within the session folder.
        The filename includes a timestamp to ensure uniqueness. After saving, the function also plays the audio file for immediate feedback.
    """
    try:
        response = client.audio.speech.create(
            model="tts-1", voice=chosen_voice, input=input_text
        )
        ai_audio_filename = f"ai_voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        ai_audio_path = os.path.join(session_folder, ai_audio_filename)
        with open(ai_audio_path, "wb") as f:
            f.write(response.content)
        print(f"AI voice saved in {ai_audio_path}")
        play_audio(response.content)  # Play the audio
        # No changes needed for the replay logic
    except Exception as e:
        logger.error(Fore.RED + f"Failed to speak text: {e}\n")
        return None
    return ai_audio_path  # Return the path to the saved AI audio file


def print_json_formatted(data, indent=4, width_percentage=0.65):
    """
    Prints a dictionary in a formatted JSON style within the terminal, offering a visually structured representation of the data.
    This function enhances readability by formatting the JSON data with indentation and color-coding, and adapts to the width of the terminal.

    It's particularly useful for displaying complex data structures in a human-readable format, which can be beneficial for debugging,
    logging, or presenting information to the user.

    Args:
        data (dict): The dictionary containing the data to be printed.
        indent (int, optional): The number of spaces used for indentation in the JSON output. Defaults to 4.
        width_percentage (float, optional): The percentage of the terminal's width to be used for text wrapping.
                                            This helps in ensuring the JSON data fits within the terminal window. Defaults to 0.65.

    Returns:
        None

    Notes:
        - The function uses 'json.dumps' for converting dictionary keys and values into a JSON-formatted string.
        - The terminal's width is dynamically calculated to adapt the output formatting to different terminal sizes.
        - Color coding is applied for different elements: keys are highlighted in yellow, and values are colored
          based on their types (e.g., green for transcriptions, magenta for translations).
        - The function is designed to handle and properly display nested dictionaries and lists.

    Example:
        data = {'Transcription': 'Hello, world!', 'Translation': 'Hola, mundo!'}
        print_json_formatted(data)
        # Output will be a color-coded, indented JSON representation of the data dictionary.
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


def record_audio(duration, session_folder):
    """
    Records audio for a specified duration and saves the recording as a WAV file in the given session folder.
    This function is essential for capturing audio input, typically from a microphone, and storing it for later
    processing or playback.

    The recording is initiated immediately upon calling this function and continues for the specified duration.
    The audio data is then saved as a WAV file, which is a standard format for uncompressed audio. The filename
    includes a timestamp to ensure uniqueness and easy identification.

    Parameters:
        duration (int): The duration for which audio should be recorded, in seconds.
        session_folder (str): The file path to the session folder where the audio file will be saved. The session
                              folder is used to organize audio files related to a specific run or session.

    Returns:
        str: The file path of the saved audio file. The path includes the session folder and the generated filename.

    Notes:
        - The function uses the 'sounddevice' library for audio recording, which should be configured correctly with
          the system's audio input device.
        - The saved audio file's format is WAV, known for its lossless quality and wide compatibility.
        - The function prints a message indicating the start and end of the recording process and logs the file path
          after successfully saving the audio file.

    Example:
        filepath = record_audio(10, "/path/to/session/folder")
        print(f"Audio recorded and saved at: {filepath}")
        # Example output: "/path/to/session/folder/user_voice_20220101_120000.wav"
    """
    filename = f"user_voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    filepath = os.path.join(session_folder, filename)

    print(Fore.GREEN + f"\nRecording for {duration} seconds...\n" + Style.RESET_ALL)

    audio_data = sd.rec(
        int(duration * RATE), samplerate=RATE, channels=CHANNELS, dtype=FORMAT
    )
    sd.wait()  # Wait until the recording is finished

    wavio.write(
        filepath, audio_data, RATE, sampwidth=SAMPLE_WIDTH
    )  # Save in session_folder
    logger.info(Fore.GREEN + f"Confirmed Audio Saved in {filepath}!\n")

    return filepath


def transcribe_audio(audio_file_path):
    """
    Transcribes spoken words from an audio file into text using the OpenAI Whisper model. This function is
    designed for applications that require converting audio content (like recordings, interviews, or speeches)
    into written text format. It's particularly useful in scenarios where automated transcription of audio files
    is needed.

    The function sends the audio file to the OpenAI API, requesting a transcription. The API response includes
    the transcribed text, which is then returned by the function. It is important to note that the transcription
    accuracy depends on the clarity and quality of the audio input.

    Parameters:
        audio_file_path (str): The filesystem path to the audio file to be transcribed.

    Returns:
        str: The transcribed text as a string if the transcription is successful; None if the transcription
             fails or if the response does not contain transcription text.

    Notes:
        - The function utilizes the 'whisper-1' model from OpenAI for transcription, which is designed to provide
          accurate results across a wide range of audio types and languages.
        - Error handling is implemented to catch and log any issues that occur during the API call or transcription
          process.
        - The transcription maintains the original language and context of the audio as much as possible, as
          instructed in the API prompt.

    Example:
        transcription = transcribe_audio("/path/to/audio_file.wav")
        if transcription:
            print("Transcription:", transcription)
        else:
            print("Transcription failed or no text found.")
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
    Leverages the OpenAI GPT-4 language model to translate provided text into a specified language.
    The translation can be customized via a system prompt, which can be specified by the user through
    the `custom_content` parameter. If `custom_content` is not provided, the function defaults to using
    predefined content that directs the translation model to handle various language inputs and output
    seamlessly.

    Args:
        text (str): The text string that needs translation.
        custom_content (str, optional): A custom system prompt that guides the translation process.
                                        This could include specific instructions or context for the model
                                        to follow during translation. If not provided, the function uses
                                        `DEFAULT_CONTENT` which contains standard instructions for translation.

    Returns:
        str: The translated text as a string. If the translation process is unsuccessful, or if the API call
             fails, the function returns None.

    Raises:
        Exception: If any exception is encountered during the API call, it is logged as an error with the
                   reason for the failure.

    Notes:
        The function makes an HTTP POST request to the OpenAI API endpoint, passing the text along with the
        system prompt (either `custom_content` or `DEFAULT_CONTENT`) in the body of the request. It expects
        a successful HTTP 200 status code and the translated text in the response. If the response indicates
        an error or if an exception occurs, the function logs the error details and returns None.

    Example:
        translated_text = translate_text("Hello, world!", custom_content="Translate this to French.")
        # Expected output: "Bonjour le monde!"
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


def voice_to_text():
    """
    Transcribes spoken words from recorded audio data into text. This function first compiles the collected
    audio frames into a WAV file and then uses the Whisper model from the OpenAI API to transcribe the audio
    content into textual form.

    The function is designed to be used in applications that require converting spoken language into written
    text, such as voice-controlled systems or automated transcription services. It plays a crucial role in
    scenarios where real-time or near-real-time transcription is needed.

    Returns:
        str: The transcribed text as a string. If the transcription is successful, it returns the text extracted
             from the audio. In case of failure (e.g., no audio data, API error), it may return an empty string
             or None, depending on the response from the Whisper model.

    Notes:
        - The function assumes that the global variable `audio_frames` contains the audio data to be transcribed.
        - It first writes this audio data to a file named 'WAVE_OUTPUT_FILENAME' in WAV format.
        - Then, it sends this file to the OpenAI API for transcription.
        - The success of transcription depends on the clarity of the audio and the capabilities of the Whisper model.

    Example:
        transcribed_text = voice_to_text()
        print(transcribed_text)
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
    Initiates continuous audio recording, storing incoming audio frames in memory until the recording is
    stopped. It relies on the `sounddevice.InputStream` to capture audio in real-time, with a designated
    callback function that processes and stores each audio frame.

    This function is designed to be part of a larger system that requires real-time audio data capture, such
    as a speech translation or voice command application. It will record indefinitely until the `is_recording`
    global variable is explicitly set to False, typically by another part of the application in response to
    a user command or action.

    Parameters:
        None

    Returns:
        bytes: A bytes object that contains all recorded audio frames concatenated together. This object can
               be written to a file, processed, or streamed further depending on the application's requirements.

    Notes:
        The recording loop runs on the main thread, with actual audio capture happening on a background thread
        managed by the `sounddevice` library. The function prints a message to the console indicating it is
        ready to record and will continue to do so until it is instructed to stop.

    Example:
        # Begin recording
        audio_data = record_audio_continuous()
        # To stop recording, set is_recording to False from another thread or signal handler.
    """
    global is_recording
    print(Fore.GREEN + "Say 'stop' to end recording..." + Style.RESET_ALL)
    with sd.InputStream(channels=1, samplerate=RATE, callback=record_callback):
        while is_recording:
            time.sleep(0.1)
    return b"".join(audio_frames)


def record_callback(indata, frames, time, status):
    """
    Callback function for the sounddevice.InputStream that processes incoming audio data.
    This function is called from a separate thread for each audio block captured by the
    audio input stream. It appends the captured audio frames to a global list if recording
    is active. It also handles the reporting of any audio stream statuses, such as overflows
    or underflows, which are indicators of potential issues with the recording process.

    Parameters:
        indata (numpy.ndarray): A two-dimensional NumPy array containing the captured audio data
                                for each frame, where each row represents one frame.
        frames (int): The number of frames (block size) of the audio data captured.
        time (CData): An instance of sounddevice._ffi.CData containing the timestamp of the first sample
                      in 'indata'. The structure contains 'inputBufferAdcTime' and 'currentTime' attributes.
        status (sounddevice.CallbackFlags): An instance of sounddevice.CallbackFlags indicating the status
                                            of the audio input stream.

    Notes:
        - The function modifies the global `audio_frames` list, appending new audio data if `is_recording` is True.
        - Any important `status` flags are printed to the standard error stream to alert of issues like buffer overflows.
        - This callback is designed to operate in the background, and its efficiency is crucial to avoid latency or
          loss of audio data. Therefore, operations within the callback should be kept to a minimum.
    """

    global is_recording, audio_frames
    if is_recording:
        audio_frames.append(indata.copy())
    if status:
        print(status, file=sys.stderr)


def continuous_run_mode(content):
    """
    Initiates the continuous run mode of the real-time translation application. In this mode, the application
    persistently records, transcribes, and translates audio without requiring manual intervention between recordings.
    The translations, along with the transcriptions, are stored, and optionally, the application can generate
    and play AI-generated audio of the translated text if a voice has been specified.

    This function is responsible for:
    - Creating a session folder for the current run to organize the resulting files.
    - Continuously recording audio based on a predefined or user-specified duration.
    - Using the transcribe_audio function to convert speech in the audio files to text.
    - Employing the translate_text function to translate the transcribed text into the desired language,
      following the guidance of the provided content.
    - Saving the transcription and translation in the session folder.
    - If a voice is set, synthesizing the translated text into speech and saving the AI-generated audio.
    - Tracking all generated files for potential cleanup or preservation based on user preference.

    Args:
        content (str): A custom system prompt or instructions provided to guide the AI translation model. This content
                       can significantly influence the context and style of the translation output.

    Raises:
        KeyboardInterrupt: Captures and handles the user's interrupt signal, typically initiated by pressing Ctrl+C, to
                           gracefully exit the continuous run mode.

    Notes:
        The user can exit continuous run mode by issuing a KeyboardInterrupt (Ctrl+C). Upon exit, the user can decide
        whether to keep or delete the recorded and generated files. If the 'save_recordings' command-line argument is
        set, the function will preserve all files in the session folder; otherwise, it will delete them.

    Example:
        continuous_run_mode("Translate this conversation to French using casual language.")
    """
    print(Fore.GREEN + "\nContinuous run mode activated.\n" + Style.RESET_ALL)
    session_folder = create_session_folder()
    audio_files = []  # Track all audio files for potential cleanup

    try:
        while True:
            audio_file_path = record_audio(
                args.duration, session_folder
            )  # Modified to pass session_folder
            audio_files.append(audio_file_path)  # Add to the list of audio files
            transcribed_text = transcribe_audio(audio_file_path)

            if transcribed_text:
                translated_text = translate_text(transcribed_text, content)
                save_transcription(session_folder, transcribed_text, translated_text)

                if args.voice:
                    # Modified voice_stream function to accept session_folder and save AI audio
                    ai_audio_path = voice_stream(
                        translated_text, args.voice, session_folder
                    )
                    audio_files.append(ai_audio_path)  # Track AI audio file as well

    except KeyboardInterrupt:
        print(Fore.RED + "\nExiting continuous run mode." + Style.RESET_ALL)
    finally:
        # Cleanup or save logic for audio files
        if not args.save_recordings:  # Assume a new argument to keep recordings
            for file_path in audio_files:
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(
                        Fore.RED
                        + f"Failed to delete file {file_path}: {e}"
                        + Style.RESET_ALL
                    )
        else:
            print(
                Fore.GREEN
                + f"All audio files are saved in {session_folder}."
                + Style.RESET_ALL
            )


def single_run_mode(content):
    """
    Executes the single-run mode of the real-time translation tool. In this mode, the user manually initiates
    audio recording and translation operations. The function handles recording, transcription, translation,
    and audio playback, including an option to replay the last translation or continue to the next recording.

    The single_run_mode orchestrates the following steps:
    - Creates a session folder for organizing audio and transcription files.
    - Waits for user input to start audio recording (space bar), replay the last translation ('r'), or exit the application ('exit').
    - Records audio for a duration specified by command-line arguments or defaults to 20 seconds.
    - Utilizes the transcribe_audio function to convert the audio to text.
    - Employs the translate_text function to translate the transcription, using the provided content as guidance.
    - Saves both the original transcription and the translated text within the session folder.
    - If a text-to-speech voice is specified, invokes the voice_stream function to synthesize and play the translation.
    - Offers the option to replay the last AI voice translation by pressing 'r'.
    - Formats and displays the transcription and translation in JSON format.
    - Upon completion, prompts the user to delete or keep the session files.

    Args:
        content (str): Custom content or system prompt used for guiding the translation model.

    Notes:
        The function maintains the path of the last AI-generated audio file to enable replay functionality.
        It responds to user inputs for controlling the flow of recording and translation.
    """
    session_folder = create_session_folder()  # Create a session folder
    audio_files = []  # Keep track of recorded audio files
    last_ai_audio_path = None  # Keep track of the last AI audio file

    print(
        Fore.GREEN
        + "Press the space bar to start recording, 'r' to replay the last translation, or 'exit' to quit:"
        + Style.RESET_ALL
    )

    while True:
        try:
            user_input = readchar.readkey()
            if user_input == " ":
                audio_file_path = record_audio(
                    args.duration if args.duration else 20, session_folder
                )
                audio_files.append(audio_file_path)
                transcribed_text = transcribe_audio(audio_file_path)

                if transcribed_text:
                    translated_text = translate_text(transcribed_text, content)
                    save_transcription(
                        session_folder, transcribed_text, translated_text
                    )

                    if args.voice:
                        ai_audio_path = voice_stream(
                            translated_text, args.voice, session_folder
                        )
                        audio_files.append(
                            ai_audio_path
                        )  # Save AI audio path for cleanup
                        last_ai_audio_path = ai_audio_path  # Update last AI audio path

                    print_json_formatted(
                        {"Original": transcribed_text, "Translation": translated_text}
                    )

            elif user_input.lower() == "r":  # Replay last translation
                if last_ai_audio_path:
                    play_audio(file_path=last_ai_audio_path)

            elif user_input.lower() == "exit":
                break

        except KeyboardInterrupt:
            break

    # At the end of the session, decide whether to delete or keep the files
    if (
        input(
            Fore.YELLOW
            + "Press 'd' to delete or any other key to keep the session files: "
            + Style.RESET_ALL
        ).lower()
        == "d"
    ):
        for file_path in audio_files:
            os.remove(file_path)
        print(Fore.GREEN + "All session files have been deleted." + Style.RESET_ALL)
    else:
        print(
            Fore.GREEN
            + f"Session files are saved in {session_folder}."
            + Style.RESET_ALL
        )


# Note: Ensure the record_audio and voice_stream functions are adapted to save files to session_folder


# Function to save transcription (and translation) to a text file on the desktop
def save_to_desktop(file_name, content):
    desktop_path = Path.home() / "Desktop"
    file_path = desktop_path / file_name
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Saved: {file_path}")


def main():
    """
    This function acts as the entry point of the program. It facilitates real-time audio translation by prompting the user to select a translation language and operates in either continuous run mode or single run mode, influenced by command line arguments.

    Continuous Run Mode:
    - In this mode, the program persistently records audio, transcribes it, and translates the transcription.
    - If a voice option is specified, it generates AI-audio based on the translated text.
    - A session folder is created for storing audio files and transcriptions.
    - This mode can be interrupted and exited by the user pressing Ctrl+C.

    Single Run Mode:
    - The user initiates audio recording by pressing the space bar or can exit by typing 'exit'.
    - It records audio for a pre-set duration, transcribes, translates, and stores these transcriptions in a session folder.
    - If a voice is specified, it synthesizes speech from the translated text and plays the audio.
    - Upon session completion, the user can choose to delete or keep the session files.

    Content Handling:
    - DEFAULT_CONTENT and SPECIAL_CONTENT variables define system prompts sent to the specified OAI model.
    - These prompts delegate the language of translation chosen by the user, aligning the translate function with the user's choice for a seamless experience.
    - When the '-c' argument is used, the placeholders in DEFAULT_CONTENT are replaced with the user's chosen language and a corresponding phrase.
    - SPECIAL_CONTENT maps directly to the "Smart Select" option in the drop-down list, triggered after '-c' is called.

    Example Usage:
    main()
    """
    print(
        Fore.GREEN + "\nWelcome to the real-time translation tool.\n" + Style.RESET_ALL
    )

    # Handling `-f` argument with interactive choices
    if args.file:
        action_choice = input(
            "Choose action: 1 for 'transcribe and translate', 2 for 'only transcribe': "
        ).strip()
        if action_choice not in ["1", "2"]:
            print("Invalid choice. Exiting.")
            sys.exit(1)

        file_choice = (
            input("Process all audio files in the same directory? (yes/no): ")
            .strip()
            .lower()
        )
        files_to_process = []
        if file_choice == "yes":
            directory_path = input("Enter the directory path: ").strip()
            files_to_process = glob.glob(os.path.join(directory_path, "*.wav"))
        elif file_choice == "no":
            file_path = input("Enter the full path to the audio file: ").strip()
            files_to_process.append(file_path)
        else:
            print("Invalid choice. Exiting.")
            sys.exit(1)

        for file_path in files_to_process:
            base_name = os.path.basename(file_path)
            text_file_name = f"{os.path.splitext(base_name)[0]}_transcription.txt"
            if action_choice == "1":  # Transcribe and translate
                transcribed_text = transcribe_audio(file_path)
                if transcribed_text:
                    translated_text = translate_text(transcribed_text, DEFAULT_CONTENT)
                    content = (
                        f"Original: {transcribed_text}\nTranslation: {translated_text}"
                    )
                    save_to_desktop(text_file_name, content)
            elif action_choice == "2":  # Only transcribe
                transcribed_text = transcribe_audio(file_path)
                if transcribed_text:
                    content = f"Transcription: {transcribed_text}"
                    save_to_desktop(text_file_name, content)
    else:
        # Existing logic for continuous or single run mode remains unchanged...
        if args.continuous:
            continuous_run_mode(DEFAULT_CONTENT)
        else:
            single_run_mode(DEFAULT_CONTENT)


if __name__ == "__main__":
    main()
