import os
import streamlit as st
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import subprocess
from datetime import datetime

# Replace this with your actual Google API key
GOOGLE_API_KEY = "Google API Key"

# Initialize recognizer and text-to-speech engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Set up custom CSS for styling
st.markdown(
    """
    <style>
    body {
        background-color: #f0f2f6;
    }
    .chat-history {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .you {
        color: #1e88e5;
        font-weight: bold;
    }
    .bot {
        color: #388e3c;
        font-weight: bold;
    }
    .button {
        background-color: #1e88e5;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        border: none;
    }
    .button:hover {
        background-color: #1565c0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for chat history if not already present
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def llm(text):
    if "time" in text.lower():
        return f"The current time is {datetime.now().strftime('%H:%M:%S')}"
    elif "name" in text.lower():
        return "I am your voice assistant."
    elif "notepad" in text.lower():
        os.system("notepad.exe")
        return "Opening Notepad."
    elif "chrome" in text.lower():
        os.system("start chrome")
        return "Opening Chrome."
    
    # Handle other LLM responses
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(text)
    return response.text.lower()

def recognize_speech_from_microphone(listening_placeholder):
    with sr.Microphone() as source:
        listening_placeholder.info("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for background noise
        try:
            # Capture audio for a fixed duration (e.g., 5 seconds)
            audio = recognizer.record(source, duration=5)
            text = recognizer.recognize_google(audio)
            st.session_state.chat_history.append(f"You: {text}")
            listening_placeholder.empty()  # Clear the "Listening..." message
            return text
        except sr.UnknownValueError:
            listening_placeholder.error("Could not understand the audio")
        except sr.RequestError:
            listening_placeholder.error("Could not request results from the service")
        return None

def speak_text(text):
    if tts_engine._inLoop:  # Check if the event loop is already running
        tts_engine.endLoop()  # End the loop if it's   running
    tts_engine.say(text)
    tts_engine.runAndWait()

# Streamlit app UI
st.title("Voice-to-Voice Conversation")
st.write("Click the button below to start speaking.")

if st.button("Start Talking", key="start_button", help="Click to start talking", use_container_width=True):
    listening_placeholder = st.empty()  # Create a placeholder for the "Listening..." message
    recognized_text = recognize_speech_from_microphone(listening_placeholder)
    if recognized_text:
        with st.spinner("Processing..."):
            processed_text = llm(recognized_text)
            st.session_state.chat_history.append(f"Bot: {processed_text}")
        
        st.subheader("Chat History")
        for message in st.session_state.chat_history:
            if message.startswith("You:"):
                st.markdown(f"<div class='chat-history you'>{message}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-history bot'>{message}</div>", unsafe_allow_html=True)
        speak_text(processed_text)

# Adding a manual text input option
st.write("Or, type your message below:")

user_input = st.text_input("Enter your text here", key="text_input")
if st.button("Add Text", key="text_button", help="Click to add your text", use_container_width=True):
    if user_input:
        st.session_state.chat_history.append(f"You: {user_input}")
        with st.spinner("Processing..."):
            processed_text = llm(user_input)
            st.session_state.chat_history.append(f"Bot: {processed_text}")
        
        st.subheader("Chat History")
        for message in st.session_state.chat_history:
            if message.startswith("You:"):
                st.markdown(f"<div class='chat-history you'>{message}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-history bot'>{message}</div>", unsafe_allow_html=True)
        speak_text(processed_text)
