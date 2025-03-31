from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import os
from groq import Groq
from bs4 import BeautifulSoup as bs
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class url(BaseModel):
    url: str

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/check")
async def verifyNews(usrr: url):
    def getNews(url):
        response = requests.get(url)
        soup = bs(response.text, 'html.parser')
        return soup.get_text(strip=True)

    STREAM_SEARCH_URL = os.getenv("STREAM_SEARCH_URL")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    if "https://" in usrr.url:
        news = getNews(usrr.url)
    else:
        news = usrr.url

    response = requests.post(STREAM_SEARCH_URL, json={"user_prompt": news})
    data = response.text

    client = Groq(api_key=GROQ_API_KEY)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                 "content": f"""{data} You are an AI assistant that verifies the authenticity of news articles. You will analyze text data from Google Custom Search API, which contains search results related to a news claim.

 To determine if the news is genuine, follow these rules:

 Check if the news is reported by high-profile media outlets such as Times of India, The Hindu, BBC, CNN, Reuters, The Guardian, NY Times, The Washington Post, Al Jazeera, etc. 

If the news appears in multiple reputable sources, it is more likely to be true.

If the results come from unknown, unreliable, or satirical websites, the news is likely fake.

If no major media outlets report the news, assume it is likely fabricated or exaggerated.
The news will be rated 10 if big media powers reports the same
Output:

Return an integer rating between 1 and 10 to represent authenticity:

1-3 → Likely Fake (No credible sources found)

4-6 → Unverified (Few sources, but not high-profile)

7-10 → Genuine (Reported by multiple trusted media sources)

Only return the rating as an integer, without explanations or additional text.""",
            }
        ],
        model="deepseek-r1-distill-qwen-32b",
    )

    return {
        "rating": chat_completion.choices[0].message.content.strip(),
        "link": news
    }
