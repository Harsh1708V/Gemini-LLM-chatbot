import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from gtts import gTTS
import base64

load_dotenv()

st.set_page_config(
    page_title='Gemini LLM Chatbot',
    page_icon='🤖',
    layout='centered',
    initial_sidebar_state='auto'
)

st.markdown(
    """
    <style>
    .user-avatar { width: 50px; height: 50px; border-radius: 50%; }
    .bot-avatar { width: 50px; height: 50px; border-radius: 50%; }
    </style>
    """,
    unsafe_allow_html=True
)

api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API key not found. Please set the GOOGLE_API_KEY environment variable.")

try:
    model = genai.GenerativeModel("gemini-1.5-pro")
    chat = model.start_chat(history=[])
except Exception as e:
    st.error(f"Failed to initialize the generative model: {e}")

def get_gemini_response(prompt):
    try:
        with st.spinner("Getting response..."):
            response = chat.send_message(prompt)
        return response
    except Exception as e:
        st.error(f"Failed to get response from Gemini: {e}")
        return None

def text_to_speech(message):
    tts = gTTS(message)
    tts.save("response.mp3")
    with open("response.mp3", "rb") as audio_file:
        audio_bytes = audio_file.read()
        b64_audio = base64.b64encode(audio_bytes).decode()
    audio_link = f'<audio controls><source src="data:audio/mp3;base64,{b64_audio}" type="audio/mp3"></audio>'
    return audio_link

st.header("Gemini LLM Chatbot 🤖")

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

user_input = st.text_input("Type your message here...", key='input_text')
submit = st.button("Send")

if submit and user_input:
    response = get_gemini_response(user_input)
    if response:
        tts_audio_link = text_to_speech(response.text)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Bot", response.text, tts_audio_link))
    else:
        st.error("Failed to get a response from the model.")

st.subheader("Chat History")
for sender, message, *tts_audio_link in st.session_state.chat_history:
    if sender == "You":
        st.markdown(f"![User Avatar](user_avatar_url) *You*: {message}")
    else:
        st.markdown(f"![Bot Avatar](bot_avatar_url) *Bot*: {message}")
        if tts_audio_link:
            st.markdown(tts_audio_link[0], unsafe_allow_html=True)

if st.button("Clear Chat History"):
    st.session_state.chat_history = []

st.sidebar.subheader("Usage Analytics")
st.sidebar.write(f"Total Messages: {len(st.session_state.chat_history)}")

st.sidebar.subheader("Feedback")
feedback = st.sidebar.text_area("Your Feedback", placeholder="Provide your feedback here...")
if st.sidebar.button("Submit Feedback"):
    st.sidebar.success("Thank you for your feedback!")

st.sidebar.subheader("Help")

st.sidebar.write("""
    *How to use this chatbot:*
    - Type your message in the input box and click "Send".
    - The bot will respond to your message.
    - View the chat history on the main page.
""")

user_avatar_url = ""
bot_avatar_url = "https://www.shutterstock.com/image-vector/chatbot-robo-advisor-adviser-chat-600nw-1222464061.jpg"