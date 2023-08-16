from threading import Thread
import yaml
from yaml.loader import SafeLoader
import streamlit as st
from PIL import Image
from CommonLibrary.Interfaces.interfaces import State
from CommonLibrary.Interfaces.interfaces import Liveliness
import requests
import time

st.header("Self Calibrated Radar BIT")

# Open the configuration yaml file
with open('CommonLibrary/configuration.yaml') as f:
    configuration = yaml.load(f, Loader=SafeLoader)


def is_active(host, port):
    """
    is_active:
    Description:
        send an HTTP get request to get the process liveliness and
        checks if the process is active

    Returns:
        True  - The process is Active
        False - Otherwise
    """
    # get the destenation URL
    url = "http://" + host + ":" + str(port) + "/liveliness"

    try:
        # get the response from the HTTP request
        response = requests.get(url)
        # Raise an exception if the request was not successful (status code >= 400)
        response.raise_for_status() 
        # convert the response to JSON
        data = response.json()

        # convert to state
        state = State(data['state'])

        # return True if active False otherwise 
        return state == State.Active
    
    # The Process is not Active
    except requests.exceptions.RequestException as e:
        return False

on_button_image = Image.open('images\on_button.png')
off_button_image = Image.open('images\off_button.png')

#width = st.slider('What is the width in pixels?', 0, 700, 350)

description = { 'on':  'Powered ON' ,
                'off': 'Powered OFF',
              }

width = { 'on':  250 ,
          'off': 230 ,
        }

on_button_data = { 'image'      : on_button_image,
                   'description': 'Powered ON'   ,
                   'width'      :  250           ,
}

off_button_data = { 'image'      : off_button_image,
                    'description': 'Powered OFF'   ,
                    'width'      :  250            ,
                  }

images = { 'active'  : on_button_data ,
           'inactive': off_button_data,
         }

if 'processes_state' not in st.session_state:
    st.session_state.processes_state = { 'ASP': 'inactive', 'Ranker': 'inactive', 'Feeder': 'inactive' }

processes = { 'ASP'   : { 'state'  : st.session_state.processes_state['ASP']                       ,
                          'caption': images[st.session_state.processes_state['ASP']]['description'],
                          'image'  : images[st.session_state.processes_state['ASP']]['image']
                        },
              'Ranker': { 'state'  : st.session_state.processes_state['Ranker']                    ,
                          'caption': images[st.session_state.processes_state['Ranker']]['description'],
                          'image'  : images[st.session_state.processes_state['Ranker']]['image']
                        },
              'Feeder': { 'state'  : st.session_state.processes_state['Feeder']                    ,
                          'caption': images[st.session_state.processes_state['Feeder']]['description'],
                          'image'  : images[st.session_state.processes_state['Feeder']]['image']
                        },
            }

def check_activity(process):
    if is_active(configuration[process]['ip'], configuration[process]['port']):
        st.session_state.processes_state[process] ='active'
    else:
        st.session_state.processes_state[process] ='inactive'


cols = st.columns(3, gap='large')

for idx, key in enumerate( processes.keys() ):
    with cols[idx]:
        st.header(key)
        st.image( processes[key]['image'],
                  caption = processes[key]['caption'],
                  width   = 200)
        
for process in processes.keys():
    check_activity(process)

st.experimental_rerun()
