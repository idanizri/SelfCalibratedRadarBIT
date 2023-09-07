from threading import Thread
import yaml
from yaml.loader import SafeLoader
import streamlit as st
from PIL import Image
from CommonLibrary.Interfaces.interfaces import State
from CommonLibrary.Interfaces.interfaces import Liveliness
import requests
import time
import json

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

if 'parameters' not in st.session_state:
    st.session_state.parameters = {}

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

def parameters_modifications():
    print(st.session_state.parameters)


cols = st.columns(3, gap='large')

for idx, key in enumerate( processes.keys() ):
    with cols[idx]:
        if key == 'ASP':
            st.header('Server')
        else:
            st.header(key + "\n" )
        st.image( processes[key]['image'],
                  caption = processes[key]['caption'],
                  width   = 200)
        
st.header("System Parameters")

st.subheader("Simulator Server Parameters")

# Use a callback to display the current value of the slider when changed
def change_value(slider_key, destination):
    st.session_state['parameters'][slider_key] = st.session_state[slider_key]
    print(st.session_state['parameters'][slider_key])
    
    host = configuration[destination]['ip'] 
    port = configuration[destination]['port']

    url = "http://" + host + ":" + str(port) + "/modify_parameters"


    result = json.dumps(st.session_state['parameters'])

    my_json = 'parameters=' + result

    x = requests.post(url,params= my_json)


st.slider("Azimuth Difference Threshold",
           0.0, 100.0, 60.0, step=1.0, key="az_diff_threshold"        , on_change=change_value,args=('az_diff_threshold'        ,'ASP') )

st.slider("Elevation Difference Threshold",
           0.0, 100.0, 40.0, step=1.0, key="el_diff_threshold"        , on_change=change_value,args=('az_diff_threshold'        ,'ASP') )

st.slider("Time Until Target is Not Valid",
           0.0, 60.0 , 2.0 , step=1.0, key="time_difference_threshold", on_change=change_value,args=('time_difference_threshold','ASP') )

st.slider("Adam Algorithm Number of Optimizer Steps",
           0, 1000, 250, step=1, key="adam_num_of_optimizer_steps", on_change=change_value,args=('adam_num_of_optimizer_steps', 'ASP') )

st.number_input("Optimizer Epsilon",
                 value=0.00001, step=0.00001, format="%.5f", key="optimizer_epsilon", on_change=change_value,args=('optimizer_epsilon', 'ASP'))

st.slider("Brute Force Algorithm Number Iterations",
           0, 100, 1, step=1, key="brute_force_number_of_iterations", on_change=change_value,args=('brute_force_number_of_iterations', 'ASP') )

brute_force_optimizer_type = ["snr", "gain"]
st.selectbox( "Brute Force Algorithm Optimizer Type",
              options=brute_force_optimizer_type, key="brute_force_optimizer_type", on_change=change_value,args=('brute_force_optimizer_type', 'ASP'),
            )

st.slider("Heuristic Algorithm Gain Threshold",
           0.0, 1.0 , 0.01, step=0.01, key="heuristic_gain_threshold", on_change=change_value,args=('heuristic_gain_threshold','ASP') )

st.slider("Heuristic Algorithm Phase Threshold",
           0.0, 10.0 , 1.0, step=0.5, key="heuristic_phase_threshold", on_change=change_value,args=('heuristic_phase_threshold','ASP') )

st.slider("Heuristic Algorithm Amount Of Beams",
           0, 100 , 10, step=1, key="heuristic_number_of_beams", on_change=change_value,args=('heuristic_number_of_beams','ASP') )

for process in processes.keys():
    check_activity(process)
    time.sleep(1)

st.experimental_rerun()
