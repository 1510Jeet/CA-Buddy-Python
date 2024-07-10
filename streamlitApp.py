import streamlit as st
import requests
from gtts import gTTS
from io import BytesIO
from streamlit_mic_recorder import mic_recorder
import json

st.title("CA Assistant")



# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []



def text_to_speech_and_display(text):
    # Convert text to speech
    tts = gTTS(text=text, lang='en')
    audio_fp = BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
   
    # Display the audio file in Streamlit
    st.audio(audio_fp, format="audio/mp3")
 


# Display chat messages from history 
def displayChat():
    for message in st.session_state.messages:
        if message["content"] != "":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"]=="assistant":
                    text_to_speech_and_display(message["content"])




def callback():
    if st.session_state.my_recorder_output:
        audio_bytes = st.session_state.my_recorder_output['bytes']


def llmCall(prompt):
    url = "http://127.0.0.1:8000/caBuddy/"
    requestParams = {
        "message": prompt,
    }
    response = requests.post(url=url,json=requestParams)
    return response




transcribedText=""
audioBytes = mic_recorder(key='my_recorder', callback=callback, format="wav")
try:
    audioBytes=audioBytes["bytes"]
    ##Save the Recorded File
    audio_location = "Test.wav"
    with open(audio_location, "wb") as f:
        f.write(audioBytes)

    transcribeURL = "http://127.0.0.1:8000/transcribe/"
    requestParams = {"path": audio_location}
    response = requests.post(url=transcribeURL,json=requestParams)
    response_dict = json.loads(response.text)
    transcribedText = response_dict["transcription"]
except:
    pass
prompt = st.chat_input("Ask your CA Buddy") 


if prompt is not None:
    st.session_state.messages.append({"role": "user", "content": prompt})
    response=llmCall(prompt)
    if response.status_code == 200:
        # Display the response from FastAPI
        st.session_state.messages.append({"role": "assistant", "content":  response.text})
    else:
        st.write("Error:", response)

if transcribedText !="":

    st.session_state.messages.append({"role": "user", "content": transcribedText})
    response=llmCall(transcribedText)
    if response.status_code == 200:
        # Display the response from FastAPI
        st.session_state.messages.append({"role": "assistant", "content":  response.text})
    else:
        st.write("Error:", response)

displayChat()

    

        

