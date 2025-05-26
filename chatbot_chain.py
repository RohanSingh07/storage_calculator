from langchain.memory import ConversationSummaryMemory
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("open_ai_key")

os.environ["OPENAI_API_KEY"] = api_key

# LLM for both conversation and summarization
llm = ChatOpenAI(temperature=0, model_name="gpt-4o",max_tokens=1000)

# Memory that summarizes the conversation
summary_memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", return_messages=True)

# System + human prompt
template = ChatPromptTemplate.from_messages([
    ("system", 
     "Your name is Selena and you are a helpful assistant for calculating video surveillance storage and system requirements for a company named Aeroskop."
     "Only answer questions related to the surveillance setup including: camera configuration, stream settings, compression, bitrate, bandwidth, RAM/CPU/storage needs, and system design. "
     "Keep the response as short to save tokens."
     "If the user asks unrelated questions (like news, jokes, or programming), politely refuse."),
    ("human", "{input}")
])

# Chain with summary memory
chain = LLMChain(
    llm=llm,
    prompt=template,
    memory=summary_memory,
    verbose=True
)

# In-memory request log
user_request_log = {}

# Configurable limits
MAX_REQUESTS = 10
TIME_WINDOW = timedelta(hours=24)  # Allow 10 requests per IP per 24 hour

def get_chatbot_response(user_input: str, user_ip: str) -> str:
    now = datetime.now()
    requests = user_request_log.get(user_ip, [])

    # Remove old timestamps
    requests = [ts for ts in requests if now - ts < TIME_WINDOW]

    if len(requests) >= MAX_REQUESTS:
        return "Rate limit exceeded. Try again later."

    # Log the current request
    requests.append(now)
    user_request_log[user_ip] = requests

    # Run the LLM chain
    response = chain.invoke({"input": user_input})
    
    return response['text']

