from fastapi import FastAPI, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from openai import OpenAI
import os
from typing import List
import pdfplumber

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://jeromejaya.github.io/Ai-counslling"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="template")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="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"
)

class ChatMessage(BaseModel):
    message: str

class Conversation(BaseModel):
    messages: List[dict] = []

def read_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()
file_content = read_file_content("counslling dataset.txt")

def append_to_aboutme(content):
    with open("about.txt", "a") as file:
        file.write(content + "\n")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(chat_message: ChatMessage):

    if not hasattr(app, 'conversation'):
        app.conversation = Conversation()
    manipulated_prompt = f"Answer the question only from the following content allways give only less content only: {file_content}\n\nThe question is: {chat_message.message}"

    app.conversation.messages.append({"role": "user", "content": manipulated_prompt})
    append_to_aboutme(f"User: {chat_message.message}")

    completion = client.chat.completions.create(
        model="nvidia/llama-3.1-nemotron-70b-instruct",
        messages=app.conversation.messages,
        temperature=1,
        top_p=1,
        max_tokens=2000,
        stream=True
    )

    response = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content is not None:
            response += chunk.choices[0].delta.content
    app.conversation.messages.append({"role": "assistant", "content": response})

    append_to_aboutme(f"AI: {response}")

    return {"response": response}

@app.post("/predictcourse")
async def chat(chat_message: ChatMessage):
    aboutme = read_file_content("about.txt")
    coursepredicter = read_file_content("availablecourses.txt")
    if not hasattr(app, 'conversation'):
        app.conversation = Conversation()
    careerresult = f"this is my career counslling conversation {aboutme}\n\n now suggest me only 5 courses from the following listed courses{coursepredicter}. after giving me the 5 course, say me in very precise manner about why did you that 5 course, say me about sallary packages available in different country. do not  give the responce in tables(rows,columns)"

    app.conversation.messages.append({"role": "user", "content":careerresult})

    completion = client.chat.completions.create(
        model="nvidia/llama-3.1-nemotron-70b-instruct",
        messages=app.conversation.messages,
        temperature=1,
        top_p=0.8,
        max_tokens=6000,
        stream=True
    )

    response2 = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content is not None:
            response2 += chunk.choices[0].delta.content
    app.conversation.messages.append({"role": "assistant", "content": response2})

    return {"response": response2}

@app.post("/analyzeresume")
async def chat(chat_message: ChatMessage):
    with pdfplumber.open("example.pdf") as pdf:
        resumeData=""
        for page in pdf.pages:
           resumeData += page.extract_text()
        
    resumeAnalyze = f"you are a resume analyser, based on the instruction {resumeData} analyze the following resume ' {aboutme}' "

    app.conversation.messages.append({"role": "user", "content":resumeAnalyze})

    completion = client.chat.completions.create(
        model="nvidia/llama-3.1-nemotron-70b-instruct",
        messages=app.conversation.messages,
        temperature=1,
        top_p=0.8,
        max_tokens=6000,
        stream=True
    )

    response3 = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content is not None:
            response2 += chunk.choices[0].delta.content
    app.conversation.messages.append({"role": "assistant", "content": response3})

    return {"response": response3}

