import time
import datetime
import streamlit as st
# from transformers import pipelineimport os
import sys
from pathlib import Path
import aiohttp
import uuid
import os
import json
import asyncio
import plotly.graph_objects as go

modules_path = Path("/home/robo/Modules")

import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


# from req import clear_history,get_st_history,create_new_chat,update_user_st_history,get_model_history,chat,recommender
from Requests import chatbotRequests,databaseRequests,visualizationRequests
from dataModels.visualization import visualizations,ChatViz
st.empty()

#GenRobo class for creating and managing the Robo Advisor application.
#This chatbot assists users with financial queries using a conversational interface.
#It maintains chat history, and responds with financial insights.
###
from streamlit_cookies_controller import CookieController
controller=CookieController()
viz_count=0

class Chatbot:
    def __init__(self):
        st.markdown(
    """
    <style>
    div[data-testid="stChatInput"] textarea {
        box-sizing: border-box;
        bottom: 10px ;
        position: fixed;
        z-index: 1000; 
    }
    div[data-baseweb="textarea"] {
        box-sizing: border-box;
        bottom: 10px ;
        position: fixed;
        z-index: 1000;
        background-color: #222222; 
    }
    button[data-testid="stChatInputSubmitButton"] {
        bottom: 10px ;
        position: fixed;
        z-index: 1000;
    }
    </style>
    """,
    unsafe_allow_html=True
)
        st.markdown( f"""
        <style>
        div.stButton > button:first-child {{ border-radius:15px 15px 15px 15px;}}

        <style>
        """, unsafe_allow_html=True)
        self.intialize_chat_history()
        self.setup_app_interface()
        
    def setup_app_interface(self):
        """
        Sets up the main interface of the Zeus application, including:
        - Displaying the title and warnings.
        - Setting up the buttons and event handlers.
        - Displaying the chat history.
        """

        st.markdown("<h1 style='text-align: center; font-size: 50px;'>ZEUS</h1>", unsafe_allow_html=True)
        # Apply CSS to all elements with the class `.st-emotion-cache-4oy321`
        st.markdown("""
            <style>
            .st-emotion-cache-4oy321 {
                border : 1px solid transparent;
                border-radius : 10px
                color: #ffffff;
                padding: 10px 10px;
                margin: 0px 7px;
                min-width: 10%
                width:auto;
                max-width: 90%;
                text-align: left;
                background: rgba(50, 50, 50, 0.4);
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("""
            <style>
            .st-emotion-cache-janbn0 { 
                        display: flex;
                        margin: 5px;
                        min-width: 10%;
                        max-width: 70%;
                        flex-direction: row-reverse;
                        font-family: "Source Sans Pro", sans-serif, "Segoe UI", "Roboto", sans-serif;
                        border: 1px solid transparent;
                        padding: 5px 10px;
                        color: white;
                        border-radius: 20px;
                        text-align: right;
                        margin-left: auto; /* Align to the right */
                    }
            </style>
        """, unsafe_allow_html=True)

        if st.sidebar.button('Clear History'):
            chatbotRequests.clear_history(st.session_state.Project,controller.get("user_id"))
            del st.session_state.messages
            del st.session_state.new
            if 'recommendation' in st.session_state:
                del st.session_state.recommendation
            self.intialize_chat_history()
            st.rerun()
        self.display_chat_history()
        self.accept_user_input()
        
   

    def display_chat_history(self):
        """
        Displays the conversation history, showing each message sent by the user and the assistant.
        """
        for message in st.session_state.messages:
            if message['role'] == 'user':
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            elif message['role'] == 'assistant':
                with st.chat_message(message["role"],avatar='👸🏼'):
                    st.markdown(message["content"])
            if message['role'] == 'visualizer':
                with st.chat_message(message["role"],avatar='📈'):
                    for visual in message['content']:
                        self.get_visuals(visual)
    def save_plot(self,fig):
        pass  
    def get_visuals(self,visuals):
        if isinstance(visuals,list):
            for v in visuals:
                self.get_visuals(v)
                pass
        try:
            fig = go.Figure(data=visuals['data'], layout=visuals['layout'])
            st.plotly_chart(fig)
            st.button("Save Plot in Dashboard",on_click=self.save_plot,args=[fig],key=f"plot_{str(uuid.uuid4())}")
        except:
            if isinstance(visuals,dict):
                for key,value in visuals.items():
                    if isinstance(value,dict):
                        self.get_visuals(value)
                    elif isinstance(value,list):
                        for v in value:
                            self.get_visuals(v)
            else:
                if isinstance(visuals,str):
                    json.loads(visuals)
                

        
    def accept_user_input(self):
        """
        Accepts user input and processes the query. It generates responses and handles recommendations.
        """
        st.empty()

        if prompt := st.chat_input("Enter your query:"):
            st.empty()
            st.session_state.new=False
            sanitized_input = self.sanitize_user_input(prompt)
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # if len(st.session_state.messages)<=2:
            #      chatbotRequests.create_new_chat(st.session_state['Project'])

            st.session_state.messages.append({"role": "user", "content": sanitized_input,})

            self.generate_response(sanitized_input)
            self.recommend(sanitized_input)
            try:
                chatbotRequests.update_user_st_history(str(st.session_state['Project']),st.session_state.messages,controller.get("user_id"))
            except:
                messages=st.session_state.messages[-1:]
                messages.append({"role": "assistant", "content": 'news_dataframe'})
                chatbotRequests.update_user_st_history(str(st.session_state['Project']),messages,controller.get("user_id"))
                

        if 'recommendation' in st.session_state:
            with st.chat_message("user"):
                st.markdown(st.session_state.recommendation)
            st.session_state.new=False
            
            # if len(st.session_state.messages)<=2:
            #     chatbotRequests.create_new_chat(st.session_state['Project'])
                
            st.session_state.messages.append({"role": "user", "content": st.session_state.recommendation})
            self.generate_response(st.session_state.recommendation)
            chatbotRequests.update_user_st_history(str(st.session_state['Project']),st.session_state.messages,controller.get("user_id"))
            self.recommend(st.session_state.recommendation)
            del st.session_state.recommendation


        if len(st.session_state.messages)==1:
            self.recommend()
            pass
    
 

    def generate_response(self, user_input):
        """
        Generates a response from the assistant using the chat model (Claude).
        """
        with st.spinner("Generating response..."):
            try:
                
                response =chatbotRequests.chat(user_input,project_id=st.session_state.Project)
                self.display_assistant_response(response)

            except Exception as e:
                raise e
                error_message = f"An error occurred: {str(e)}"
                st.warning(error_message)
                self.display_assistant_response("Sorry,I don't have this functionality, Can't provide an answer.\n Ask another question please.",stream=False)

    def sanitize_user_input(self, user_input):
        # Remove any potentially harmful characters or sequences        
        sanitized = user_input.replace('<', '&lt;').replace('>', '&gt;')
        # Limit input length
        max_length = 500
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            st.warning(f"Input truncated to {max_length} characters.")
        return sanitized

    def display_assistant_response(self, response,stream=True):
        """
        Display the output of claude
        """
        with st.chat_message("assistant", avatar='👸🏼'):
            visuals=[]
            if stream:
                escaped_response=st.write_stream((self.stream_ans(response,visuals)))
            else:
                escaped_response=response
                st.write(escaped_response)
        st.session_state.messages.append({"role": "assistant", "content": escaped_response})

        if len(visuals)>0:
            with st.chat_message('visualizer',avatar='📈'):
                for visual in visuals:
                    self.get_visuals(visual)
                    
                    new_chat_viz=ChatViz(viz=visual)
                    visualizationRequests.save_chat_visualizations(st.session_state['Project'],new_chat_viz)
                    st.session_state.messages.append({'role':'visualizer','content':viz_count})
        chatbotRequests.update_user_st_history(str(st.session_state['Project']),st.session_state.messages,controller.get("user_id"))
            
    


    def intialize_chat_history(self):
        """
        Called at the beginning of any chat
        """
        chat_history,viz_count = chatbotRequests.get_streamlit_chat_history(st.session_state['Project'])
        if chat_history!=[]:
            st.session_state.messages = chat_history
            st.session_state['conv_change']=''
            st.session_state['new']=False
            st.session_state['Bot_Clicked']=False
            welcome_message = "Welcome back. How can I assist you today?"
            st.session_state.messages.append({"role": "assistant", "content": welcome_message})
        else:
            if 'messages' in st.session_state:
                del st.session_state.messages
        if "messages" not in st.session_state:
            st.session_state['conv_change']=''
            st.session_state['new']=True
            st.session_state.messages = []
            st.session_state['Bot_Clicked']=False
            # Add greeting message to chat history
            first_message = "Good Morning. I am Zeus, a Smart Assistant for C.A.S.E. How can I assist you today?"
            st.session_state.messages.append({"role": "assistant", "content": first_message})

    def stream_ans(self,response,visuals):
        """
    Response of claude is streamed so this function handles it
        """
        tag_flag = False
        buffer = ""
        try:
            for word in response:
                word = word.decode('utf-8')
                buffer += word
                try:
                    if buffer[0] == '{' or buffer[0] == '[':
                        json_obj = json.loads(buffer)
                        if isinstance(json_obj, list):
                            visuals.append(json_obj)
                            buffer = ""
                    else:
                        for w in buffer:
                            if w == '<':
                                tag_flag = True
                            elif w == '>':
                                tag_flag = False
                            if not tag_flag:

                                w = w.replace("$", "\$")
                                yield w
                                time.sleep(0.007)
                        buffer = ""
                except json.JSONDecodeError:
                    # Continue accumulating chunks until a complete JSON object is formed
                    continue
        except Exception as e:
            raise e
        

    def recommend_response(self,prompt):
        """
        Function Helper for recommend()
        """
        st.session_state.recommendation=prompt

    def recommend(self,prompt=None):
        """
        Provides personalized prompt recommendations based on the user's input.
        """
        if prompt:
            chat_hist,viz_count = chatbotRequests.get_streamlit_chat_history(st.session_state['Project'])
            if len(chat_hist)>0:
                chat_hist.extend([{'role':'user','content':"Don't answer the user prompt, just choose the prompts and generate them in a PYTHON LIST of strings as requested in the system instruction. Give different SIMPLE functionality than what the user and you have already gave. You are restricted to the prompts listed in the system instruction do not get creative. The stocks that you can use to generate the prompts are from the list given to you use them:\n"+prompt}])
                recommendations=chatbotRequests.recommender(chat_hist,project_id=st.session_state.Project)
            else:
                recommendations=chatbotRequests.recommender([{'role':'user','content':"Don't answer the user prompt, just choose the prompts and generate them in a PYTHON LIST of strings as requested in the system instruction. Give different SIMPLE functionality than what the user and you have already gave. You are restricted to the prompts listed in the system instruction do not get creative. The stocks that you can use to generate the prompts are from the list given to you use them:\n"+prompt}],st.session_state.Project)
        else:
            recommendations=['What are your features']
            
        for i in range(len(recommendations)):
            if i>6:
                break
            if recommendations[i]!=' ':
                recommendations[i]=recommendations[i].replace('"','')
                st.button(recommendations[i],on_click=self.recommend_response,args=[recommendations[i]])
    

    # def checkQueryRequest(self,prompt):
    #     classifier = pipeline("zero-shot-classification",model="facebook/bart-large-mnli")
    #     sequence_to_classify = prompt
    #     candidate_labels = ['Question','Table','Plot']
    #     result = classifier(sequence_to_classify, candidate_labels)
    #     print(result)
    # print("HISTORY: ",messages)
    