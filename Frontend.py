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
import config
from functions import RV, retrain, get_youtube_video_id

openai.api_key = config.openai
GoogleApiKey = config.GoogleApiKey

st.set_page_config(page_title="DemoRS", layout="wide")

running = False
counter = 0



try:
    youtube = build('youtube', 'v3', developerKey=GoogleApiKey)
except Exception as e:
    pass


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
                    RV(firstV, pref)
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
                    RV(firstV, pref)

                else:
                    print("First Vid")
                    retrain(pref) 
                    print("RV----------------------------------------------------------------------------")
                    RV(firstV, pref)



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
                    RV(firstV, pref)

                else:
                    print("First Vid ")
                    retrain(pref) 
                    print("RV----------------------------------------------------------------------------")
                    RV(firstV, pref)



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
        st.write("Select where to get the secrets from")
        if st.button("Local"):
            openai.api_key = config.openai
            GoogleApiKey = config.GoogleApiKey
        if st.button("Cloud"):
            openai.api_key = st.secrets.openai
            GoogleApiKey = st.secrets.GoogleApiKey
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
                    st.session_state.count +=1
                    title =("No title" + str(st.session_state.count))
                if title not in st.session_state.video_name:
                    st.session_state.video_name.append(title)
                    #st.write("No title found for this video")

            if len(st.session_state.Trained)>0:
                st.session_state.training_history = np.zeros([ len(st.session_state.result), 4  ], dtype="O")
                st.session_state.training_history[:, 0] = st.session_state.result
                st.session_state.training_history[:, 1] = st.session_state.likedislike
                st.session_state.training_history[:, 2] = st.session_state.Trained
                try:
                    st.session_state.training_history[:, 3] = st.session_state.video_name[:len(st.session_state.training_history)]
                except Exception as e:
                    print(st.session_state.video_name)
                    print(e)

                st.write(np.flip(st.session_state.training_history, 0))    
                if len(st.session_state.training_history) != 0:
            
                    st.session_state.pleasure_percentage = np.count_nonzero(st.session_state.training_history == "pleasure")/len(st.session_state.training_history)
                    st.write("percentage of response which is pleasure: ",st.session_state.pleasure_percentage)

        else:
            pass

        # st.write(st.session_state.Trained, st.session_state.likedislike)
        








