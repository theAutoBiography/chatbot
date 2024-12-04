from pathlib import Path
from openai import OpenAI
from google.cloud import texttospeech
from .helper_variables import STRICTNESS_CONTROL_API, DOMAINS, BHASHINI_LANGUAGE_CODES
import requests

def strictness_evaluator(strictness_level):
    if strictness_level == 'low':
        return STRICTNESS_CONTROL_API['low']
    elif strictness_level == 'high':
        return STRICTNESS_CONTROL_API['high']
    else:
        return STRICTNESS_CONTROL_API['medium']

def instantiate_openai_client():
    return OpenAI()

def get_response(text_input, api, strictness_level, chat_history):
    print(f"I'm receiving {text_input} from the user.")
    client = instantiate_openai_client()

    completion = client.chat.completions.create(
        model=api,
        messages=chat_history
        )
    return completion.choices[0].message.content        
    
# def get_audio_response(text):

#     client = instantiate_openai_client()
#     # speech_file_path = Path(__file__).parent / "speech.mp3"
#     response = client.audio.speech.create(
#         model="tts-1",
#         voice="alloy",
#         input=text
#     )
#     # Save the audio content to a file
#     with open("static/audios/audio.mp3", "wb") as f:
#         f.write(response.content)
#     print(response)
#     return response

def get_audio_response(text, language, output_file, assistant=0):
    print(f"{text} to be converted to speech.")
    print(output_file)
    # API endpoint URL
    url = "https://bhashini.ai/v1/synthesize"

    # Request headers
    headers = {
        "Content-Type": "application/json",
        # "Authorization": f"Bearer {api_key}"
    }

    # Request payload
    payload = {
        "text": text,
        "languageId": BHASHINI_LANGUAGE_CODES[language],
        "voiceId": assistant
    }
    # Make POST request to the API
    response = requests.post(url, json=payload, headers=headers)

    # Check if request was successful
    if response.status_code == 200:
        # Save the audio file
        
        with open(output_file, "wb") as f:
            print("Opened audio file")
            f.write(response.content)
        print("Text-to-speech conversion successful!")
    else:
        print("Error:", response.text)

def synthesize_text(text, language, output_file, assistant=0):
    print(output_file)
    client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)

    if assistant == 0:
        gender=texttospeech.SsmlVoiceGender.FEMALE
    elif assistant == 1:
        gender=texttospeech.SsmlVoiceGender.MALE
    else:
        gender=texttospeech.SsmlVoiceGender.NEUTRAL

    voice = texttospeech.VoiceSelectionParams(
        language_code=language, ssml_gender=gender
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    # Writes the audio content to the output file
    with open(output_file, "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written')