#inbuilt modules
import platform
import datetime 
import re
import random

# 3rd party
import streamlit as st
import openai
from openai import AsyncOpenAI
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import datetime 
import re
from googleapiclient.discovery import build
from pytube import YouTube
import numpy as np
#import config
import asyncio

#my modules/ local
from Arch import Arch
import ao_core as ao
from preloaded_links import preloaded_links
import config

openai.api_key = config.openai
Google_api_list = [config.GoogleApiKey1, config.GoogleApiKey2]

GoogleApiKey = ""
client = AsyncOpenAI(api_key=openai.api_key)

#local_genre = ""

## call gpt
async def get_genre(text):
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": "give a one word answer"},
            {"role": "user", "content": f"What is the genre in one of these options, not anything other than the ones given: Vlogs, Gaming, Educational, Tech Reviews, Comedy/Skits, Beauty & Fashion, Music, Fitness, Cooking, Travel, ASMR, Challenges/Pranks\n\n{text}"}
        ],
         max_tokens=5,
        temperature=0.1
    )
    local_genre = response.choices[0].message.content
    return local_genre 

    # Get Fiction/Non-Fiction classification
async def get_fnf(text):
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "user", "content": f"Is this video Fiction or Non Fiction in one or two words?\n\n{text}"}
        ],
        max_tokens=10
    )
    local_FNF = response.choices[0].message.content
    return local_FNF



async def call_inputs(text):
    batch = await asyncio.gather(get_fnf(text), get_genre(text))
    local_fnf, local_genre = batch
    return local_fnf, local_genre

##encode to binary
def llm_inputs():
    print("running")
    
    ID = get_youtube_video_id(st.session_state.VR[0])
    text = get_transcript(ID)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    local_fnf, local_genre = loop.run_until_complete(call_inputs(text))
    loop.close()



    # Get video length
    url = st.session_state.VR[0]
    yt = YouTube(url)
    try:
        length = yt.length
    except Exception as e:
        print("error in getting length", e)
        length = 0

    length = round(length / 60, 2)
    if length < 5:
        length = [0, 0]
    elif length >= 5 and length < 20:
        length = [0, 1]
    else:
        length = [1, 1]

    # Determine if Fiction or Non-Fiction
    local_fnf.upper()
    if local_fnf == "FICTON":
        FNF = [1]
    else:
        FNF = [0]

    # Map genre to binary representation
    genre_map = {
        "VLOGS": [0, 0, 0, 1],
        "GAMING": [0, 0, 1, 0],
        "EDUCATIONAL": [0, 0, 1, 1],
        "TECH REVIEWS": [0, 1, 0, 0],
        "COMEDY": [0, 1, 0, 1],
        "SKITS": [0, 1, 0, 1],
        "BEAUTY": [0, 1, 1, 0],
        "FASHION": [0, 1, 1, 0],
        "MUSIC": [0, 1, 1, 1],
        "FITNESS": [1, 0, 0, 0],
        "COOKING": [1, 0, 0, 1],
        "TRAVEL": [1, 0, 1, 0],
        "ASMR": [1, 0, 1, 1],
        "CHALLENGES": [1, 1, 0, 0],
        "PRANKS": [1, 1, 0, 0]
    }
    local_genre = genre_map.get(local_genre.upper(), [0, 0, 0, 0])

    # Combine results into a single list
    local_input_agent = local_genre + FNF + length

    print("local input:", local_input_agent)

    return local_input_agent








#agent call to get response
def agentCall(input, pref): 

    #st.session_state.agent.next_state( INPUT=input,Cpos=Cpos, Cneg=Cneg, print_result=True)
    print("input to agent", input)

    st.session_state.agent.next_state( INPUT=input, print_result=False)

    response = st.session_state.agent.story[st.session_state.agent.state-1, st.session_state.agent.arch.Z__flat]

    return response

#agent call to train agent 
def agentTrain(input, pref):

    global Cpos
    global Cneg 
    if pref == "l":

        Cpos = True 
        Cneg = False
    if pref =="d": 
        Cneg = True
        Cpos = False

    print("input to agent in agent call:", input)

    st.session_state.agent.next_state(INPUT=input, Cpos=Cpos, Cneg=Cneg, print_result=False)





#decide when to call what
def recommenderVideo(llm_input,  pref, NUM):   

    if NUM == True:
        print("recommenderVideoInput:", llm_input)
        R = agentCall(llm_input, pref)
        if np.sum(R)>5:
            return True
        else:
            return False
    else:
        print("input:",llm_input)

        R = agentTrain(llm_input, pref)


def GetType(text):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": "Give a one word answer from only one of the options provided, with no puctionation"},
            {"role": "user", "content": f"what is the Type in one of these options: Podcast, Review, News, Video Essay, Skit, Presentation, entertainment \n\n{text}"}
        ],
        max_tokens=10  # adjust based on how concise we want the summary
    )
    summary = response.choices[0].message.content
    return summary

def GetMood(text):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            #{"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"what is the mood in one of these options not anything else: funny, serious, or random \n\n{text}"}
        ]  # adjust based on how concise we want the summary
    )
    summary = response.choices[0].message.content
    return summary

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_transcript = ' '.join([entry['text'] for entry in transcript])
        return full_transcript
    
    except TranscriptsDisabled:
        print(f"Subtitles are disabled for this video: {video_id}")
    
    except NoTranscriptFound:
        print(f"No transcript found for this video: {video_id}")
    
    except VideoUnavailable:
        print(f"Video is unavailable: {video_id}")
    
    except Exception as e:
        print(f"An unexpected error occurred in getting transcript: {e}", video_id)

def get_youtube_video_id(url):
    # Define the regular expression pattern to match YouTube URLs
    pattern = re.compile(
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    

    match = pattern.search(url)
    

    if match:
        return match.group(6)
    return None
                  
def get_language(video_id):

   # Build the YouTube service
   try:
        x = random.randint(0,1)
        print("key getting used", x)
        GoogleApiKey = Google_api_list[x]
        youtube = build('youtube', 'v3', developerKey=GoogleApiKey)

        # Request the video details
        request = youtube.videos().list(
            part="snippet,recordingDetails",
            id=video_id
        )
        response = request.execute()

        
        video_info = response.get("items", [])[0]


        language = video_info.get("snippet", {}).get("defaultLanguage")
        if language:

            return language
        else:

            audio_language = video_info.get("snippet", {}).get("defaultAudioLanguage")
            if audio_language:

                return audio_language
            else:

                return ("no data")
            
   except Exception as e:

    print(f"An unexpected error occurred in get lang: {e}")

def retrain(llm_input, pref):

    NUM = False



    recommenderVideo(llm_input, pref, NUM)



      # would return true if it recommends
              
def RV(firstV, pref, llm_input):
    NUM = True
    print("input in RV:", llm_input)
    

    recommend = recommenderVideo(llm_input, pref, NUM)
        
    st.session_state.recommendationInput = llm_input

       # recommend = recommenderVideo(genre, lang, current_time, machine, lengt, Type, mood, FNF, pref, NUM)  #

    if  recommend:
            #st.write("Recommended for you")
        st.session_state.recommendationResult = "Recommended for you"
            
        pass # do nothing as it has been recommended again in the retrain
    else:
            #st.write("Not recommended for you")
        st.session_state.recommendationResult = "Not recommended for you"
            #st.session_state.VR.pop(0)   # if we only wanted to show the recommended vids then we would incude this line
        
    if firstV:
        pass
    else:
        st.session_state.result.append(st.session_state.recommendationResult)
