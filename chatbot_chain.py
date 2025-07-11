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

# System + human prompt
template = ChatPromptTemplate.from_messages([
    ("system",
     "You are Selena, an AI chatbot assistant and AI calculator for Aeroskop"  
     "You need to accurately calculate the total storage, total bandwidth and bitrate on the basis of list of camera configurations given to you."
     "The configurations would be as follows:- modelx: model of the camera, camera-countx: total number of cameras of this configuration, stream-modex: single or dual mode of camera streaming as well as for recording, resolutionxA and resolutionxB: The resolutions of the cameras in pixels in both the modes or only for one mode if the mode is single, fpsxA/fpsxB: Frame per second for camera in single/dual mode, compressionxA/compressionxB: camera compression for storage, like H.264 or H.265, qualityxA/qualityxB: The quality of video streaming and recording, bitratexA/bitratexB mode: CBR or VBR, recording-hoursxA/recording-hoursxB: number of hours the camera would record everyday, retentionxA/retentionxB: For how many days the videos will be stored in storage."
     "The input will be a type object with these keys and modelx keys like model1, model2, etc, should be used as a separator for the list of cameras."
     "So, predict the total storage needed for all the cameras in total in TB, the total bandwidth needed to stream and store the videos and the estimated bitrate for each camera setting and total bitrate."
     "Just provide list of the following outputs:- total_storage in TB, total_bandwidth in Mbps and total_bitrate in Kbps in a json and do not provide anything else in the response, if the input is chat then provide response like a chatbot but try to keep it short"
     "You might get your last calculation details from the memory, build on top of it if the User refers to the above calculation or does not provide proper conext of the cameras and starts providing additional information. You should say things like based on the above camera description or list of cameras, if you take the last calculations into consideration. If the User is providing detailed list of cameras along with description, ignore the calculation from the memory"
     "Take into consideration the quality of the camera, LOW, GOOD, VGOOD, HIGH and EXCELLENT and adjust the bitrate accordingly. Bitrate should not be same for all the quality settings and should increase with increase of quality."
     "If the User asks anything not related to the calculation, politely refuse and say things like 'I am only here to assist you related to your storage calculation and system requirements'."
     ),
    ("system", "{chat_history}"),
    ("human", "{input}")
])

summary_memory1 = ConversationBufferMemory(llm=llm, memory_key="chat_history")

# Chain without memory
predict_chain = LLMChain(
    llm=llm,
    prompt=template,
    memory=summary_memory1,
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




