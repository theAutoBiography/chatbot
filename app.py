from flask import Flask, render_template, redirect, request, jsonify
from flask_wtf import FlaskForm
from wtforms import SubmitField, FileField, SelectField, StringField, BooleanField, validators
from flask_wtf.file import FileRequired, FileAllowed
import os, requests
from dotenv import load_dotenv
from flask_bootstrap import Bootstrap
from helpers.openai_helpers import get_response, get_audio_response, synthesize_text
from helpers.helper_variables import STRICTNESS_UI_DISPLAY, STRICTNESS_CONTROL_API
from helpers.openai_helpers import strictness_evaluator

load_dotenv()
app = Flask(__name__)
Bootstrap(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

chat_history = []
follow_up_count = 0

PROMPTS = [
    "மகாபலிபுரம் சிற்பங்கள் எவ்வாறு தமிழ் கலையின் வளர்ச்சியை பிரதிபலிக்கின்றன?",
    "தமிழ்நாட்டில் பொங்கல் விழா எவ்வாறு கொண்டாடப்படுகிறது, அதன் சிறப்புகள் என்ன?",
    "தஞ்சாவூரின் பெரிய கோவிலின் வாஸ்து கலை பற்றிய விவரங்களை விவரிக்கவும்.",
    "जयपुर के जंतर मंतर की खगोलीय महत्व क्या है?",
    "वाराणसी के घाटों का भारतीय संस्कृति में क्या महत्व है?",
    "मुग़ल साम्राज्य की वास्तुकला में ताजमहल का क्या स्थान है?",
    "What are the key elements of classical Indian dance that can be seen in Bharatanatyam performances?",
    "How does the Indian caste system influence traditional practices and social interactions in rural areas?",
    "Discuss the significance of the Indian Railways in connecting and influencing the cultural landscapes of India.",
    "What role does spirituality play in the daily lives of Indians, and how is it reflected in places like Haridwar and Rishikesh?",
    "சோழர் கால ஓவியங்களின் பண்புகளை விவரிக்கவும்.",
    "மதுரை மீனாட்சி அம்மன் கோவிலின் வரலாறு என்ன?",
    "திருவண்ணாமலை கிரிவலம் ஏன் முக்கியமானது என விளக்கவும்.",
    "கம்பராமாயணம் தமிழ் இலக்கியத்தில் என்ன பங்காற்றுகிறது?",
    "खजुराहो के मंदिरों की शिल्पकला की विशेषताएं क्या हैं?",
    "उदयपुर की राजपूत वास्तुकला के मुख्य तत्व क्या हैं?",
    # "भारतीय रंगमंच में नाट्यशास्त्र का क्या महत्व है?"
]

class AudioForm(FlaskForm):
    language = SelectField('Language', choices=[('ta-IN', 'Tamil'), ('en-IN', 'English'), ('hi-IN', 'Hindi')], render_kw={"id": "language"})
    voiceInput = StringField('Voice to Text', render_kw={"id": "voiceInput"})
    api = SelectField('GPT API', choices=[('gpt-3.5-turbo', 'ChatGPT 3.5 Turbo'), ('gpt-4', 'ChatGPT 4.0')])
    tts = SelectField('TTS API', choices=[('bhashini', 'BhashiniAI'), ('google', 'Google Cloud TTS')])
    strictness_level = SelectField('Strictness Level', choices=[('medium', STRICTNESS_UI_DISPLAY['medium']), ('low', STRICTNESS_UI_DISPLAY['low']), ('high', STRICTNESS_UI_DISPLAY['high'])])
    choose_assistant = SelectField('Choose Assistant', choices=[(0, 'Female'), (1, 'Male')])
    follow_up = BooleanField('Follow up', render_kw={"id": "follow_up"})
    submit = SubmitField('Submit')

def increment_follow_up_count():
    global follow_up_count
    follow_up_count += 1


@app.route('/', methods=['GET', 'POST'])
def index():
    form = AudioForm()
    response = {
        "prompts": PROMPTS,
    }
    if form.validate_on_submit():
        print("Form submitted")
        language = form.language.data
        voice_input = form.voiceInput.data
        api = form.api.data
        strictness_level = form.strictness_level.data
        tts = form.tts.data
        follow_up = form.follow_up.data
        if not follow_up:
            global chat_history
            chat_history = [
                {"role": "system", "content": f"You are a heritage expert. Take input from wikipedia for educated responses. {strictness_evaluator(strictness_level)}."}
            ]
            global follow_up_count
            follow_up_count = 0   
        else:
            increment_follow_up_count()
        chat_history.append({"role": "user", "content": voice_input})
        output_filename = f"static/audios/audio{follow_up_count}.mp3"
        choose_assistant = form.choose_assistant.data
        response_text = get_response(voice_input, api, strictness_level, chat_history)
        chat_history.append({"role": "system", "content": response_text})
        print(response_text)
        if tts == 'google':
            synthesize_text(response_text, language, output_filename, choose_assistant)
        else:
            get_audio_response(response_text, language, output_filename, assistant=choose_assistant)
        response["response_audio_src"] = "audios/audio.mp3"
        response["response_text"] = response_text
        print(f"Follow up count: {follow_up_count}")
    return render_template("home.html", form=form, prompts=PROMPTS, response=response, chat_history=chat_history, follow_up_count=str(follow_up_count))

if __name__ == '__main__':
    app.run()