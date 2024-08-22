#inbuilt modules
import platform
import datetime 
import re
import time

# 3rd party
import streamlit as st
import openai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import datetime 
import re
from googleapiclient.discovery import build
import requests
from bs4 import BeautifulSoup
from pytube import YouTube
import numpy as np
#import config
import sys
import subprocess


#my modules/ local
from Main import Arch
import ao_core as ao
from preloaded_links import preloaded_links



st.set_page_config(page_title="DemoRS", layout="wide")

running = False
counter = 0
openai.api_key = st.secrets.openai
GoogleApiKey = st.secrets.GoogleApiKey
youtube = build('youtube', 'v3', developerKey=GoogleApiKey)


st.session_state.recommendationInput = ""
st.session_state.recommendationResult = ""
st.session_state.mood_input = ""
st.session_state.pleasure_percentage = 0
#st.session_state.training_history = None


try:
  # replace "yourpackage" with the package you want to import
  import ao_core

# This block executes only on the first run when your package isn't installed
except ModuleNotFoundError as e:
  subprocess.Popen([f'{sys.executable} -m pip install git+https://:{st.secrets.GITHUB_PAT}@github.com/aolabsai/ao_core'], shell=True)
  # wait for subprocess to install package before running your actual code below
  time.sleep(90)

import ao_core as ao


if "agent" not in st.session_state:
    print("-------creating agent-------")
    st.session_state.agent = ao.Agent(Arch, notes=[])

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
    try:
        length = round(length/60, 2)

        length = int(length)
        if length<5:
            length = [0,0]
        if length>5 and length<20:
            length = [0,1]
        else:
            length = [1,1]
    except Exception as e:
        length= [1,0]
        print(f"An unexpected error occurred:  in the length getting {e}")


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


    

    Type = type

    
    #st.write(time, FNF, Mood, Bgenre, type)
    
    INPUT = Bgenre+ length+ FNF
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
        
        
        
def RV(firstV):
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

    # Assuming you want to proceed even if there was an exception
       

 
if 'urls' not in st.session_state:
    st.session_state.urls = []
# Initialize session state for links if it doesn't exist
if 'links' not in st.session_state:
    st.session_state.links = []  # Creating the array of links the user "likes"

# Initialize session state for VR( videos to recommend) if it doesn't exist
if 'VR' not in st.session_state:
    st.session_state.VR = []  # Creating the array of links of the videos to recommend

# Initialize session state for transcripts if it doesn't exist
if 'transcripts' not in st.session_state:
    st.session_state.transcripts = {}  # Storing transcripts with video ID as ke

if 'Trained' not in st.session_state:
    st.session_state.Trained = []

if 'likedislike' not in st.session_state:
    st.session_state.likedislike = []

if 'result' not in st.session_state:
    st.session_state.result = []

if 'array' not in st.session_state:
    st.session_state.array = []

if 'video_name' not in st.session_state:
    st.session_state.video_name = []




st.title('Recommender System', anchor='center')

###Frontend

# Create columns
main_col, vid_col = st.columns([1, 1.25])

with main_col:

    user_input = st.text_input('Enter a YouTube URL for the video that you like:')
    st.session_state.mood_input = st.selectbox("Pick your mood!: ",(" Random" , "Serious", "Funny"))


    if user_input:
        if user_input not in st.session_state.urls:
            st.session_state.urls.insert(0, user_input)
        VID = get_youtube_video_id(user_input)
        if VID and VID not in st.session_state.links:
            st.session_state.links.insert(0, VID)
            st.session_state.VR.insert(0, user_input)
        st.write('You entered:', VID)   
    preload_col, run_col, reset_col = st.columns(3)

    

    #preloading of the links
    with preload_col:
        if  st.button("preload links", type="primary"):
            for i in range(len(preloaded_links)):
                st.session_state.urls.append(preloaded_links[i-1])
                vid = get_youtube_video_id(st.session_state.urls[i-1])
                st.session_state.links.append(vid)
            st.success(f'Preloaded {len(st.session_state.urls)} links.')

            
            for i in range(len(st.session_state.links)):
                with vid_col:
                    st.session_state.VR.append(st.session_state.urls[i-1])            


    # Handle the RUN button
    with run_col:
        if st.button("RUN" , type="primary"):
            if len(st.session_state.VR) > 0:
                pref= "none"

                print("Start----------------------------------------")
                

                if len(st.session_state.links) !=0:
                #st.write("Running")
                    running = True

                    # retrain(pref)
                    firstV = True
                    RV(firstV)
                    firstV = False

    
with vid_col:
    pain_col, pleasure_col = st.columns([1,1])
    
    with pain_col:
        if st.button("Pain" , type="primary"):
            if len(st.session_state.VR) !=1:
                

                pref  = "d"
                firstV = False
                st.session_state.Trained.append(st.session_state.VR[0])
                st.session_state.likedislike.append("pain")
                if "C_dNt4UEVZQ" not in st.session_state.VR[0]:
                    print("Retrain------------------------------------------------------------------------")
                    retrain(pref)  
                    print("RV----------------------------------------------------------------------------")
                    RV(firstV)

                else:
                    print("First Vid")
                    retrain(pref) 
                    print("RV----------------------------------------------------------------------------")
                    RV(firstV)



                st.session_state.VR.pop(0)#
                st.session_state.links.pop(0)
                st.session_state.urls.pop(0)
                #st.session_state.transcripts.pop(0)
                #assuming we would need to retrain here so calling agent function
        
                counter = int(counter)
                running = True
            # counter  = counter+1

            else:
                if len(st.session_state.VR) ==1:
                    st.session_state.VR.pop(0)
                st.write("No more videos in list")

        
    with pleasure_col:
        if st.button("Pleasure", type="primary"):
            if len(st.session_state.VR) !=1:
                

                pref  = "l"
                print(st.session_state.VR[0])
                firstV = False
                st.session_state.Trained.append(st.session_state.VR[0])
                st.session_state.likedislike.append("pleasure")
                if "C_dNt4UEVZQ" not in st.session_state.VR[0]:
                    print("Retrain------------------------------------------------------------------------")
                    retrain(pref)  
                    print("RV----------------------------------------------------------------------------")
                    RV(firstV)

                else:
                    print("First Vid ")
                    retrain(pref) 
                    print("RV----------------------------------------------------------------------------")
                    RV(firstV)



                st.session_state.VR.pop(0)
                #assuming we would need to retrain here so calling agent function
        
                counter = int(counter)
                running = True
            # counter  = counter+1

            else:
                if len(st.session_state.VR) ==1:
                    st.session_state.VR.pop(0)
                st.write("No more videos in list")


      #   st.button("Next+Dislike")
    while running == True:
      #  st.write(st.session_state.VR)

     
            st.write("Videos left in list:"+ str(len(st.session_state.VR)-1))
            st.write("Input to agent( We are only using the first 3 inputs for the demo): ",st.session_state.recommendationInput)
            st.write("Agent output: ", st.session_state.recommendationResult)

            #st.write(st.session_state.VR[counter])
            st.video(st.session_state.VR[0])
            running = False
st.session_state.count = 0
with main_col:
        if len(st.session_state.VR) != 0:
           # try:
            st.write("agent trained on ", len(st.session_state.Trained), " videos")
            st.write("Agent history:")


#### very ducktape fix  getting everyvid name not nessacary
            for i in range(len(st.session_state.Trained)):
                
                try:
                    yt = YouTube(st.session_state.Trained[i-1])
                    title = yt.title              
                except Exception as e:  # backup incase pytube down
                    print(e)
                    response = requests.get(str(st.session_state.Trained[i-1]))
                    soup = BeautifulSoup(response.text, 'html.parser')
                    title = soup.title.string
                    title = title.replace(" - YouTube", "")                      
                if title  == "":  # if no title found then write
                    st.secrets.count +=1
                    title =("No title" + str(st.session_state.count))
                if title not in st.session_state.video_name:
                    st.session_state.video_name.append(title)
                    #st.write("No title found for this video")

            if len(st.session_state.Trained)>0:
                st.session_state.training_history = np.zeros([ len(st.session_state.result), 4  ], dtype="O")
                st.session_state.training_history[:, 0] = st.session_state.result
                st.session_state.training_history[:, 1] = st.session_state.likedislike
                st.session_state.training_history[:, 2] = st.session_state.Trained
                st.session_state.training_history[:, 3] = st.session_state.video_name[:len(st.session_state.training_history)]

                st.write(np.flip(st.session_state.training_history, 0))    
                if len(st.session_state.training_history) != 0:
            
                    st.session_state.pleasure_percentage = np.count_nonzero(st.session_state.training_history == "pleasure")/len(st.session_state.training_history)
                    st.write("percentage of response which is pleasure: ",st.session_state.pleasure_percentage)

        else:
            pass

        # st.write(st.session_state.Trained, st.session_state.likedislike)
        








