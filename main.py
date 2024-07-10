from fastapi import FastAPI,HTTPException
from pydantic import BaseModel
import speech_recognition as sr
# Initialize recognizer class                                       
r = sr.Recognizer()

# import whisper
import os

from faster_whisper import WhisperModel

# SpeechToTextModelSize = "tiny.en"

# Run on GPU with FP16
# model = WhisperModel(SpeechToTextModelSize, device="cuda", compute_type="float16")

# or run on GPU with INT8
# model = WhisperModel(SpeechToTextModelSize, device="cuda", compute_type="int8_float16")
# or run on CPU with INT8
# SpeechToTextModel = WhisperModel(SpeechToTextModelSize, device="cpu", compute_type="int8")

#to avoid this error: Initializing libiomp5md.dll, but found libiomp5md.dll already initialized. 
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

#for LLM 
os.environ["GROQ_API_KEY"] = "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"
 
from langchain_groq import ChatGroq
 
llmModel = ChatGroq(model="llama3-8b-8192")
 
from langchain_core.messages import HumanMessage
 
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
 
store = {}



#Request body
class AudioFilePath(BaseModel):
    path:str

#initialize the app
app = FastAPI()



#define the endpoint
@app.post("/transcribe/")
async def transcribe_audio(file_path:AudioFilePath):
    path=file_path.path
    # Check if the file exists
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Audio file not found")

    audio = sr.AudioFile(path)
    result=""
    #read audio object and transcribe
    with audio as source:
        audio = r.record(source)                  
        result = r.recognize_google(audio)



    #remove the file since transcription is completed
    os.remove(path)
    return {"transcription":result}




# Now on to making a llama3 API

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    print(store[session_id])
    return store[session_id]
 
 
with_message_history = RunnableWithMessageHistory(llmModel, get_session_history)

config = {"configurable": {"session_id": "abc2"}}

#Request body 
class Message(BaseModel):
    message: str

@app.post("/caBuddy/")
async def llmResponse(msg: Message):
    message=msg.message

    prompt = "Your name is 'CA AI Buddy for Tally Solutions'. Only answer questions directly related to Chartered Accountancy know-how only. Refrain from answering any other questions about people, companies, etc. kindly."
    prompt+= "Refrain from answering questions about Tally or any other companies or topics unrelated to Chartered Accounting knowledge and know-how."
    # prompt+= "Respond very very kindly to derogatory remarks and foul language and ask them where you can be helpful in a short response."
    prompt+="Respond in a very kind and short one sentence way to derogatory remarks and ask them where you can help them."
    message = prompt + "\n" + message
    response = with_message_history.invoke(
        [HumanMessage(content=message)],
        config=config,
    )
    return response.content




if __name__ == "__main__":
    import uvicorn 
    uvicorn.run(app, host="127.0.0.1", port=8000)
