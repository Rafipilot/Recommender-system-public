#inbuilt modules
import platform
import datetime 
import re

# 3rd party
import streamlit as st
import openai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import datetime 
import re
from googleapiclient.discovery import build
from pytube import YouTube
import numpy as np
#import config


#my modules/ local
from Main import Arch
import ao_core as ao
from preloaded_links import preloaded_links
import config

openai.api_key = config.openai
GoogleApiKey = config.GoogleApiKey

def agentCall(input, pref): 

    #st.session_state.agent.next_state( INPUT=input,Cpos=Cpos, Cneg=Cneg, print_result=True)
    print("input to agent", input)

    st.session_state.agent.next_state( INPUT=input, print_result=False)

    response = st.session_state.agent.story[st.session_state.agent.state-1, st.session_state.agent.arch.Z__flat]




    return response

def agentTrain(input, pref):

    global Cpos
    global Cneg 
    if pref == "l":

        Cpos = True 
        Cneg = False
    if pref =="d": 
        Cneg = True
        Cpos = False

    st.session_state.agent.next_state(INPUT=input, Cpos=Cpos, Cneg=Cneg, print_result=False)






def recommenderVideo(genre, language, time, device, length, Type, Mood, FNF,  pref, NUM):   

    

    #Fiction/ non fiction to binary

    length = round(length/60, 2)

   # print(type(length))
    try:
        length = int(length)
        if length<5:
            length = [0,0]
        if length>=5 and length<20:
            length = [0,1]
        else:
            length = [1,1]
        print(length)
    except Exception:
        pass
    #length= [1,0]


    FNF = str(FNF.upper)
    if "FICTION" in FNF:
        FNF = [1]
    else:
        FNF = [0]


    #Time to bnary
    time = int(time)
    time = bin(time)[2:]

    #Mood to binary#
  
    Mood = Mood.upper()
    #Mood = str(Mood)
 
    if "FUNNY" in Mood:
        Mood = [0,1]
    elif "SERIOUS" in Mood:
        Mood = [0,0]
    elif "RANDOM" in Mood:
        Mood = [1,0]
    else:
        print("error not a classified response in mood")
        Mood = [1,1]

    
    

    category = genre.upper()

    if "VLOGS" in category:
        binary_rep = [0,0,0,1]
    elif "GAMING" in category:
        binary_rep = [0,0,1,0]
    elif "EDUCATIONAL" in category:
        binary_rep = [0,0,1,1]
    elif "TECH REVIEWS" in category:
        binary_rep = [0,1,0,0]
    elif "COMEDY" in category or "SKITS" in category:
        binary_rep = [0,1,0,1]
    elif "BEAUTY" in category or "FASHION" in category:
        binary_rep = [0,1,1,0]
    elif "MUSIC" in category:
        binary_rep = [0,1,1,1]
    elif "FITNESS" in category:
        binary_rep = [1,0,0,0]
    elif "COOKING" in category:
        binary_rep = [1,0,0,1]
    elif "TRAVEL" in category:
        binary_rep = [1,0,1,0]
    elif "ASMR" in category:
        binary_rep = [1,0,1,1]
    elif "CHALLENGES" in category or "PRANK" in category:
        binary_rep = [1,1,0,0]
    else:
        print("error not a classified response in genre")
        binary_rep = [0,0,0,0]

    Bgenre=binary_rep



    Type = Type.upper()

    if "PODCAST" in Type:
        type = [0,0,0,1]
    elif "REVIEW" in Type:
        type = [0,0,1,0]
    elif "NEWS" in Type:
        type = [0,0,1,1]
    elif "VIDEO ESSAY" in Type:
        type = [0,1,0,0]
    elif "SKIT" in Type:
        type = [0,1,0,1]
    elif "PRESENTATION" in Type:
        type = [0,1,1,0]
    elif "ENTERTAINMENT" in Type:
        type = [1,1,1,1]
    else:
        print("error not a classified response in type")
        type = [0,0,0,0]  


    

    Type = Type

    
    #st.write(time, FNF, Mood, Bgenre, type)
    
    INPUT = Bgenre+ length +FNF
    # Call agent

    if NUM == True:

        R = agentCall(INPUT, pref)
        if np.sum(R)>5:
            return True
        else:
            return False



    else:
        R = agentTrain(INPUT, pref)


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

def GetGenre(text):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            {"role": "system", "content": "give a one word answer"},
            {"role": "user", "content": f"what is the genre in one of these options not anything other than the ones given please nothing random just from the list given: Vlogs, Gaming ,Educational, Tech Reviews, Comedy/Skits, Beauty & Fashion, Music, Fitness, Cooking, Travel, ASMR , Challenges/Pranks\n\n{text}"}
        ],
        max_tokens=5,  # adjust based on how concise we want the summary
        temperature=0.1  # Lower temperature for more deterministic output
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

def GetFNF(text):   # get fiction/ non fiction
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  
        messages=[
            #{"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Is this video Fiction or Non Fiction in one or two words \n\n{text}"}
        ],
        max_tokens=10  # adjust based on how concise we want the summary
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
       



        
    

def retrain(pref):

    NUM = False
    try:
        ID = get_youtube_video_id(st.session_state.VR[(0)])
        url = st.session_state.VR[(0)]
        yt = YouTube(url)
        try:
            lengt = yt.length
        except Exception as e:
            print("error in getting length",e)
            lengt = 0

        lang = "en"
        current_time = datetime.datetime.now().strftime("%H")
        machine = platform.machine()
                    #st.write(ID)
        transcript = get_transcript(ID)
        st.session_state.transcripts[st.session_state.links[(0)]] = transcript  # Save transcript
                    #st.write("Summarizing")
        genre = GetGenre(transcript)
        Type =  GetType(transcript)
        mood =  st.session_state.mood_input
        FNF =  GetFNF(transcript)

        recommenderVideo(genre, lang, current_time, machine, lengt, Type, mood, FNF, pref, NUM)
            #st.write(f"Summary for video ID {st.session_state.links[(i)]}:")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


      # would return true if it recommends
        
        
        
def RV(firstV, pref):
    const = 0
    if firstV == True:
        const = 0
    else:
        const = 1
    NUM = True
    
    try:  
        ID = get_youtube_video_id(st.session_state.VR[(const)])
        url = st.session_state.VR[(const)]
        yt = YouTube(url)
        try:
            lengt = yt.length
        except Exception as e:
            print("error in getting length",e)
            lengt = 0
        lang = "en"
        current_time = datetime.datetime.now().strftime("%H")
        machine = platform.machine()

        transcript = get_transcript(ID)
        st.session_state.transcripts[st.session_state.links[(0)]] = transcript  # Save transcript

        genre = GetGenre(transcript)
        Type =  GetType(transcript)
        mood =  st.session_state.mood_input
        FNF = GetFNF(transcript)

        
        st.session_state.recommendationInput = genre, FNF, lengt, lang, current_time, machine, Type, mood

        recommend = recommenderVideo(genre, lang, current_time, machine, lengt, Type, mood, FNF, pref, NUM)  #

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
    except Exception as e:

        print(f"An unexpected error occurred: {e}")
        
        genre = "UNKNOWN" 
        Type = "UNKNOWN"
        mood = "UNKNOWN"
        FNF = "UNKNOWN"
        lang = "UNKNOWN"
        lengt = 0