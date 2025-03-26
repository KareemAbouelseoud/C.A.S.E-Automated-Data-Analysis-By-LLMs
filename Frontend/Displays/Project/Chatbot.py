import time
import streamlit as st
import sys
import uuid
import os
import json
import plotly.graph_objects as go
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Requests import chatbotRequests,visualizationRequests
from dataModels.visualization import ChatViz
from streamlit_cookies_controller import CookieController
from Style import buttons,chatbot
controller=CookieController()

class Chatbot:
    def __init__(self):  
        self.chatbot_session=st.session_state['user_data']['projects']['current_project']

        if 'chatbot' not in self.chatbot_session:
            self.chatbot_session['chatbot']={}
        self.logo_path = "/app/static/ZEUS.png"
        st.markdown(chatbot.text_box,unsafe_allow_html=True)
        st.markdown(buttons.rounded_button, unsafe_allow_html=True)
        
        self.intialize_chat_history()
        self.setup_app_interface()
    
    def backtooverview(self):
        st.session_state['user_data']['projects']['current_project']={}
            
    
    def setup_app_interface(self):
        """
        Sets up the main interface of the Zeus application, including:
        - Displaying the title and warnings.
        - Setting up the buttons and event handlers.
        - Displaying the chat history.
        """

        st.markdown("<h1 style='text-align: center; font-size: 100px;'>ZEUS</h1>", unsafe_allow_html=True)
        with st.columns(19)[-1]:
            st.markdown(buttons.back_button,unsafe_allow_html=True)
            st.markdown(f'<span id="button-back"></span>', unsafe_allow_html=True)
            st.button('',icon=":material/arrow_back:",on_click=self.backtooverview,key=f"back_{uuid.uuid4()}")

        st.markdown(chatbot.assistant_messages, unsafe_allow_html=True)
        st.markdown(chatbot.user_messages, unsafe_allow_html=True)

        st.sidebar.markdown(buttons.sidebar_button,unsafe_allow_html=True,)
        st.sidebar.markdown('<span id="button-sidebar"></span>', unsafe_allow_html=True)
        if st.sidebar.button('Clear History'):
            self.chatbot_session['thread_id']=chatbotRequests.clear_history(self.chatbot_session['project_id'],controller.get("user_id"))
            self.chatbot_session['chatbot']['messages']=[]
            self.chatbot_session['chatbot']['new']=None
            if 'recommendation' in self.chatbot_session['chatbot']:
                self.chatbot_session['chatbot']['recommendation']=None
            self.intialize_chat_history()
            st.rerun()
        self.display_chat_history()
        self.accept_user_input()
        
   

    def display_chat_history(self):
        """
        Displays the conversation history, showing each message sent by the user and the assistant.
        """
        for message in self.chatbot_session['chatbot']['messages']:
            if message['role'] == 'user':
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            elif message['role'] == 'assistant':
                with st.chat_message(message["role"],avatar=self.logo_path):
                    st.markdown(message["content"])
            if message['role'] == 'visualizer':
                with st.chat_message(message["role"],avatar='📈'):
                    for visual in message['content']:
                        self.get_visuals(visual)

    def save_plot(self,fig):        
        pass  
    
    
    def get_visuals(self, visuals,save=False):
        if isinstance(visuals, list):
            for v in visuals:
                self.get_visuals(v,save)
        try:
            fig = go.Figure(data=visuals['data'], layout=visuals['layout'])
            st.plotly_chart(fig)
            st.button("Save Plot in Dashboard", on_click=self.save_plot, args=[fig], key=f"plot_{str(uuid.uuid4())}")
            
            # Convert the visuals to serializable format before saving
            if save:
                serializable_visuals = visualizationRequests.make_serializable(visuals)
                new_chat_viz = ChatViz(viz=[serializable_visuals])
                visualizationRequests.save_chat_visualizations(self.chatbot_session['project_id'], new_chat_viz)
                self.chatbot_session['chatbot']['messages'].append({'role':'visualizer','content':[visuals]})

        except Exception as e:
            print(f"Error in get_visuals: {str(e)}")
            if isinstance(visuals, dict):
                for key, value in visuals.items():
                    if isinstance(value, dict):
                        self.get_visuals(value,save)
                    elif isinstance(value, list):
                        for v in value:
                            self.get_visuals(v,save)
            else:
                if isinstance(visuals, str):
                    if visuals == None:
                        return
                    self.get_visuals(json.loads(visuals),save)
                

        
    def accept_user_input(self):
        """
        Accepts user input and processes the query. It generates responses and handles recommendations.
        """
        if prompt := st.chat_input("Enter your query:"):
            self.chatbot_session['chatbot']['new']=False
            sanitized_input = self.sanitize_user_input(prompt)
            with st.chat_message("user"):
                st.markdown(prompt)

            self.chatbot_session['chatbot']['messages'].append({"role": "user", "content": sanitized_input,})

            self.generate_response(sanitized_input)
            self.recommend(sanitized_input)
            chatbotRequests.update_user_st_history(str(self.chatbot_session['project_id']),self.chatbot_session['chatbot']['messages'],controller.get("user_id"))

                

        if 'recommendation' in self.chatbot_session['chatbot']:
            with st.chat_message("user"):
                st.markdown(self.chatbot_session['chatbot']['recommendation'])
            self.chatbot_session['chatbot']['new']=False
                
            self.chatbot_session['chatbot']['messages'].append({"role": "user", "content": self.chatbot_session['chatbot']['recommendation']})
            self.generate_response(self.chatbot_session['chatbot']['recommendation'])
            chatbotRequests.update_user_st_history(str(self.chatbot_session['project_id']),self.chatbot_session['chatbot']['messages'],controller.get("user_id"))
            self.recommend(self.chatbot_session['chatbot']['recommendation'])
            del self.chatbot_session['chatbot']['recommendation']


        if len(self.chatbot_session['chatbot']['messages'])==1:
            self.recommend()
 

    def generate_response(self, user_input):
        """
        Generates a response from the assistant using the chat model (Claude).
        """
        print("Before Generating Response",self.chatbot_session['chatbot']['messages'])
        with st.spinner("Generating response..."):
            try:
                response =chatbotRequests.chat(user_input,project_id=self.chatbot_session['project_id'],thread_id=self.chatbot_session['thread_id'])
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

        with st.chat_message("assistant", avatar=self.logo_path):
            visuals=[]
            if stream:
                escaped_response=st.write_stream((self.stream_ans(response,visuals)))
            else:
                escaped_response=response
                st.write(escaped_response)
        self.chatbot_session['chatbot']['messages'].append({"role": "assistant", "content": escaped_response})

        if len(visuals)>0:
            with st.chat_message('visualizer',avatar='📈'):
                for visual in visuals:
                    self.get_visuals(visual,save=True)
    


    def intialize_chat_history(self):
        """
        Called at the beginning of any chat
        """ 
        
        if "messages" not in self.chatbot_session['chatbot'] or self.chatbot_session['chatbot']['messages']==[]:
            self.chatbot_session['chatbot']['conv_change']=''
            self.chatbot_session['chatbot']['new']=True
            self.chatbot_session['chatbot']['Bot_Clicked']=False
            first_message = "Good Morning. I am Zeus, a Smart Assistant for C.A.S.E. How can I assist you today?"
            self.chatbot_session['chatbot']['messages']=[{"role": "assistant", "content": first_message}]
            self.chatbot_session['chatbot']['messages'].extend(chatbotRequests.get_streamlit_chat_history(self.chatbot_session['project_id']))

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
        self.chatbot_session['chatbot']['recommendation']=prompt

    def recommend(self,prompt=None):
        """
        Provides personalized prompt recommendations based on the user's input.
        """
        if prompt:
                recommendations=chatbotRequests.recommender([{'role':'user','content':"Don't answer the user prompt, just choose the prompts and generate them in a PYTHON LIST of strings as requested in the system instruction. Give different SIMPLE functionality than what the user and you have already gave. You are restricted to the prompts listed in the system instruction do not get creative. The stocks that you can use to generate the prompts are from the list given to you use them:\n"+prompt}],self.chatbot_session['project_id'],self.chatbot_session['thread_id'])
        else:
            recommendations=['What are your features',"Suggest interesting visualizations","Find outliers in this dataset and explain their impact","Create a Machine Learning Model","Summarize key insights from this dataset"]
            
        for i in range(len(recommendations)):
            if i>6:
                break
            if recommendations[i]!=' ':
                recommendations[i]=recommendations[i].replace('"','')
                st.button(recommendations[i],on_click=self.recommend_response,args=[recommendations[i]])
    

if 'project_id' in st.session_state['user_data']['projects']['current_project'] and st.session_state['user_data']['projects']['current_project']['project_id']!=None:
    Chatbot()