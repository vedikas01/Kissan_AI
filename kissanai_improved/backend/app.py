from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
import os
import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator
import tempfile
import uuid
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")

SECRET_KEY = os.getenv("SECRET_KEY")

app.config["SECRET_KEY"] = SECRET_KEY
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
Session(app)

LANGUAGES = {
    "English": "en",
    "Hindi": "hi",
    "Punjabi": "pa",
    "Bengali": "bn",
    "Tamil": "ta",
    "Telugu": "te"
}

GROQ_API_KEY = os.getenv("GROQ_API")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-70b-8192"

if not os.path.exists("static/audio"):
    os.makedirs("static/audio")

@app.route("/")
def index():
    """Render the language selection page"""
    return render_template("index.html", languages=LANGUAGES)

@app.route("/set_language", methods=["POST"])
def set_language():
    """Set the user's preferred language"""
    language = request.form.get("language")
    if language in LANGUAGES.values():
        session["language"] = language
        return redirect(url_for("chat"))
    return redirect(url_for("index"))

@app.route("/chat")
def chat():
    """Render the chat interface"""
    language = session.get("language", "en")
    return render_template("chat.html", language=language, language_name=get_language_name(language))

def get_language_name(code):
    """Get language name from language code"""
    for name, lang_code in LANGUAGES.items():
        if lang_code == code:
            return name
    return "English"  

@app.route("/process_text", methods=["POST"])
def process_text():
    """Process text input"""
    text = request.form.get("text", "")
    language = session.get("language", "en")
    
    if language != "en":
        translator = Translator()
        translated = translator.translate(text, src=language, dest="en")
        text_for_processing = translated.text
    else:
        text_for_processing = text
  
    response = get_llama_response(text_for_processing, language)
    
    return jsonify({"response": response})

@app.route("/process_voice", methods=["POST"])
def process_voice():
    """Process voice input"""
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400
    
    audio_file = request.files["audio"]
    language = session.get("language", "en")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio_file.save(temp_file.name)
    temp_file.close()
    
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(temp_file.name) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data, language=language)
    except Exception as e:
        os.unlink(temp_file.name)
        return jsonify({"error": str(e)}), 500
    
    os.unlink(temp_file.name)

    if language != "en":
        translator = Translator()
        translated = translator.translate(text, src=language, dest="en")
        text_for_processing = translated.text
    else:
        text_for_processing = text
    
    response_text = get_llama_response(text_for_processing, language)

    audio_filename = generate_audio_response(response_text, language)
    
    return jsonify({
        "recognized_text": text,
        "response": response_text,
        "audio_url": audio_filename
    })

def get_llama_response(query, language):
    """Get a response from Llama model via Groq API and translate it if needed"""
    try:
        prompt = f"""You are a helpful farming assistant. The farmer asks: {query}"""
        
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": "You are a helpful farming assistant that provides concise advice to farmers."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        
        if response.status_code == 200:
            response_data = response.json()
            answer = response_data["choices"][0]["message"]["content"].strip()
            
            if language != "en":
                translator = Translator()
                translated = translator.translate(answer, src="en", dest=language)
                return translated.text
            
            return answer
        else:
            return f"API Error: {response.status_code}"
            
    except Exception as e:
        print(f"Error calling Groq API: {str(e)}")
        return f"Error: {str(e)}"

def generate_audio_response(text, language):
    """Generate an audio response in the specified language"""
    filename = f"response_{uuid.uuid4()}.mp3"
    filepath = os.path.join("static/audio", filename)
    
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save(filepath)
    
    return f"/static/audio/{filename}"

if __name__ == "__main__":
    app.run(debug=True)