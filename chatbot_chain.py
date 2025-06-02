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

# System + human prompt
template = ChatPromptTemplate.from_messages([
    ("system", 
     "You need to accurately calculate the total storage, total bandwidth and bitrate on the basis of list of camera configurations given to you."
     "The configurations would be as follows:- modelx: model of the camera, camera-countx: total number of cameras of this configuration, stream-modex: single or dual mode of camera streaming as well as for recording, resolutionxA and resolutionxB: The resolutions of the cameras in pixels in both the modes or only for one mode if the mode is single, fpsxA/fpsxB: Frame per second for camera in single/dual mode, compressionxA/compressionxB: camera compression for storage, like H.264 or H.265, qualityxA/qualityxB: The quality of video streaming and recording, bitratexA/bitratexB: CBR or VBR, recording-hoursxA/recording-hoursxB: number of hours the camera would record everyday, retentionxA/retentionxB: For how many days the videos will be stored in storage."
     "The input will be a type object with these keys and modelx keys like model1, model2, etc, should be used as a separator for the list of cameras."
     "So, predict the total storage needed for all the cameras in total in TB, the total bandwidth needed to stream and store the videos and the estimated bitrate for each camera setting and total bitrate."
     "Just provide list of the following outputs:- total_storage in TB, total_bandwidth in Mbps and total_bitrate in Kbps in a json and do not provide anything else in the response"
     "Take into consideration the quality of the camera, LOW, GOOD, VGOOD, HIGH and EXCELLENT and adjust the bitrate accordingly. Bitrate should not be same for all the quality settings and should increase with increase of quality."
     ),
    ("human", "{input}")
])

# Memory that summarizes the conversation
summary_memory = ConversationSummaryMemory(llm=llm, memory_key="chat_history", return_messages=True)


# Chain with summary memory
predict_chain = LLMChain(
    llm=llm,
    prompt=template,
    verbose=True
)

# chain = LLMChain(
#     llm=llm,
#     prompt=template,
#     memory=summary_memory,
#     verbose=True
# )

# In-memory request log
user_request_log = {}

# Configurable limits
MAX_REQUESTS = 10
TIME_WINDOW = timedelta(hours=24)  # Allow 10 requests per IP per 24 hour

def get_requirements_response(user_input: str, user_ip: str) -> str:
    now = datetime.now()
    requests = user_request_log.get(user_ip, [])

    # Remove old timestamps
    requests = [ts for ts in requests if now - ts < TIME_WINDOW]

    # if len(requests) >= MAX_REQUESTS:
    #     return "Rate limit exceeded. Try again later."

    # Log the current request
    requests.append(now)
    user_request_log[user_ip] = requests

    # Run the LLM chain
    response = predict_chain.invoke({"input": user_input})
    
    return response['text']

