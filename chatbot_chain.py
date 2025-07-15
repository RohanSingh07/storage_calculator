from langchain.memory import ConversationBufferWindowMemory,CombinedMemory, ConversationBufferMemory
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

summary_memory = ConversationBufferMemory(llm=llm, memory_key="chat_history")

# System + human prompt
template = ChatPromptTemplate.from_messages([
    ("system",
     "You are Selena, an AI chatbot assistant and AI calculator for Aeroskop."  
    "You need to accurately calculate the total storage (in TB), total bandwidth (in Mbps), and total bitrate (in Kbps) based on a list of camera configurations provided to you."  
    "The input will be a structured object with keys like model1, model2, etc. Each modelx defines one type of camera configuration."  
    "Each modelx contains the following keys:"  
    "  - modelx: the name or type of the camera model."  
    "  - camera-countx: total number of cameras of this configuration."  
    "  - stream-modex: either 'single' or 'dual', indicating how many streams are used for recording and viewing."  
    "  - resolutionxA / resolutionxB: resolution in pixels for stream A and B respectively (only A if mode is single)."  
    "  - fpsxA / fpsxB: frame rate (frames per second) for each stream."  
    "  - compressionxA / compressionxB: compression format used for each stream (e.g., H.264, H.265)."  
    "  - qualityxA / qualityxB: video quality level for each stream (values can be LOW, GOOD, VGOOD, HIGH, EXCELLENT)."  
    "  - bitrate-modexA / bitrate-modexB: mode of bitrate for each stream (CBR or VBR)."  
    "  - recording-hoursxA / recording-hoursxB: number of hours the camera records each day."  
    "  - retentionxA / retentionxB: number of days video must be stored."  

    "Your task is to calculate:"  
    "  - total_storage in TB (terabytes), calculated from all camera streams and configurations."  
    "  - total_bandwidth in Mbps, based on the live streaming requirements of all cameras."  
    "  - total_bitrate in Kbps, which is the sum of the bitrates of all active streams."  

    "The output must be returned as a JSON object with only these three fields:"  
    "total_storage: , total_bandwidth: ,total_bitrate"  
    "Do not include any explanation, notes, or text other than this JSON unless the input is conversational."  

    "If the input is a chat or conversational message, respond like a helpful chatbot but keep the reply short and focused on calculation."  
    "If the user refers to a previous calculation or does not provide full context, use your memory and build upon the last camera data."  
    "If the user gives a fresh and complete list of camera configurations, ignore memory and use only the new input."  

    "Make sure to vary bitrate based on the video quality:"  
    "  - Use higher bitrate for higher quality (e.g., EXCELLENT > HIGH > VGOOD > GOOD > LOW)."  
    "  - Apply appropriate adjustments whether the bitrate mode is CBR or VBR."  

    "If the user asks anything unrelated to storage or system calculations or configurations of cameras, politely decline and say: 'I am only here to assist you with storage calculation and system requirements.'"  

     ),
    ("system", "{chat_history}"),
    ("human", "{input}")
])



# Chain without memory
predict_chain = LLMChain(
    llm=llm,
    prompt=template,
    memory=summary_memory,
    verbose=True,
)
# last_user_input = None
# last_ai_output = None 

def get_requirements_response(user_input: str, user_ip: str) -> str:
    # global last_user_input, last_ai_output 
    # Run the LLM chain
    response = predict_chain.invoke({"input": user_input})
    # last_user_input = user_input
    # last_ai_output = response['text']
    return response['text']


# combined memory
# summary_memory2 = ConversationBufferWindowMemory(llm=llm, memory_key="chat_history2", k=2)
# combined_memory = CombinedMemory(
#     memories=[summary_memory1,summary_memory2]
# )

# System + human prompt
template2 = ChatPromptTemplate.from_messages([
    ("system",
     """
     "You are Selena, an AI chatbot assistant for Aeroskop" 
     "You need to accurately calculate the total storage, total bandwidth, bitrate as well as system requirements based on the input provided by the User"
     "The configurations could be as follows:- modelx: model of the camera, camera-countx: total number of cameras of this configuration, stream-modex: single or dual mode of camera streaming as well as for recording, resolutionxA and resolutionxB: The resolutions of the cameras in pixels in both the modes or only for one mode if the mode is single, fpsxA/fpsxB: Frame per second for camera in single/dual mode, compressionxA/compressionxB: camera compression for storage, like H.264 or H.265, qualityxA/qualityxB: The quality of video streaming and recording, bitratexA/bitratexB mode: CBR or VBR, recording-hoursxA/recording-hoursxB: number of hours the camera would record everyday, retentionxA/retentionxB: For how many days the videos will be stored in storage, etc."
     "You might get your last calculation details from the memory, build on top of it if the User refers to the above calculation or does not provide proper conext of the cameras and starts providing additional information. You should say things like based on the above camera description or list of cameras, if you take the last calculations into consideration. If the User is providing detailed list of cameras along with description, ignore the calculation from the memory"
     "Predict the total storage needed for all the cameras in total in TB, the total bandwidth needed to stream and store the videos and the estimated bitrate for each camera setting and total bitrate."     
     "Take into consideration the quality of the camera, LOW, GOOD, VGOOD, HIGH and EXCELLENT and adjust the bitrate accordingly. Bitrate should not be same for all the quality settings and should increase with increase of quality."
     "If the User asks anything not related to the calculation, politely refuse and say things like 'I am only here to assist you related to your storage calculation and system requirements'."
     """),
    ("human", "{input}"),
])

# Chain with memory
# chatChain = LLMChain(
#     llm=llm,
#     prompt=template2,
#     memory=summary_memory1,
#     verbose=True
# )

def chatbot(user_input):
    response = predict_chain.invoke({"input": user_input})
    return response["text"]




