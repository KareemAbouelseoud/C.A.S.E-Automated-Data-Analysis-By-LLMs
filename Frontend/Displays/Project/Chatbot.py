import time
import datetime
import streamlit as st
import sys
from pathlib import Path
import uuid
import os
import json
import plotly.graph_objects as go
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

# from req import clear_history,get_st_history,create_new_chat,update_user_st_history,get_model_history,chat,recommender
from Requests import chatbotRequests,visualizationRequests
from dataModels.visualization import visualizations,ChatViz
from streamlit_cookies_controller import CookieController
controller=CookieController()

class Chatbot:
    def __init__(self):  
        self.chatbot_session=st.session_state['user_data']['projects']['current_project']
        try:
            print("at the beginning of chatbot",self.chatbot_session['chatbot']['messages'])
        except:
            pass

        if 'chatbot' not in self.chatbot_session:
            self.chatbot_session['chatbot']={}
        self.logo_path = "/app/static/ZEUS.png"
        st.markdown(
    """
    <style>
    div[data-testid="stChatInput"] textarea {
        box-sizing: border-box;
        bottom: 5px ;
        position: fixed;
        z-index: 1000; 
    }
    div[data-baseweb="textarea"] {
        box-sizing: border-box;
        bottom: 5px ;
        position: fixed;
        z-index: 1000;
        background-color: #222222; 
    }
    button[data-testid="stChatInputSubmitButton"] {
        bottom: 5px ;
        position: fixed;
        z-index: 1000;
    }
    .st-emotion-cache-1pqiyj1.ekr3hml7 {
        background: url("app/static/imagemeshgradient.png") no-repeat center center fixed;
        background-position: center 200px;
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
            st.markdown("""
                <style>
                .element-container:has(#button-back) + div button {
                    justify-content: center;
                    align-items: center;
                    width: 100%; /* Ensure the container takes up full width */
                    height: 100%; /* Optional: to ensure vertical centering */
                    border-radius: 16px;
                    background: rgba(0, 0, 0, 0.4);
                    z-index: 2;
                    box-shadow: 
                        0 0 6px rgba(255, 255, 255, 0.3), 
                        0 0 12px rgba(255, 255, 255, 0.2), 
                        0 0 18px rgba(255, 255, 255, 0.2);
                    color: white;
                    font-size: 50px;
                    text-align: center;
                    cursor: pointer;
                    padding: 0px;
                    justify-content: center;
                    align-items: center;
                    margin-bottom: 5px; /* Adds vertical space if wrapping occurs */
                    transition: box-shadow 0.3s ease; /* Smooth transition */
                    border: none; /* Explicitly remove any border */

                    }
                    .element-container:has(#button-back) + div button:hover {
                    box-shadow: 
                        0 0 10px rgba(255, 255, 255, 0.6), 
                        0 0 20px rgba(255, 255, 255, 0.5), 
                        0 0 30px rgba(255, 255, 255, 1); /* Stronger glow on hover */
                }
                </style>
            """,unsafe_allow_html=True)
            st.markdown(f'<span id="button-back"></span>', unsafe_allow_html=True)
            st.button('← Back',on_click=self.backtooverview,key=f"back_{uuid.uuid4()}")
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
            self.chatbot_session['thread_id']=chatbotRequests.clear_history(self.chatbot_session['project_id'],controller.get("user_id"))
            self.chatbot_session['chatbot']['messages']=[]
            self.chatbot_session['chatbot']['new']=None
            if 'recommendation' in self.chatbot_session['chatbot']:
                self.chatbot_session['chatbot']['recommendation']=None
            self.intialize_chat_history()
            print("History Cleared")
            st.rerun()
        self.display_chat_history()
        self.accept_user_input()
        
   

    def display_chat_history(self):
        """
        Displays the conversation history, showing each message sent by the user and the assistant.
        """
        print("Before Displaying Chat History",self.chatbot_session['chatbot']['messages'])
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
        print("After Displaying Chat History",self.chatbot_session['chatbot']['messages'])
    def save_plot(self,fig):        
        pass  
    
    
    def get_visuals(self, visuals,save=False):
        if isinstance(visuals, list):
            for v in visuals:
                self.get_visuals(v,save)
                return
        try:
            fig = go.Figure(data=visuals['data'], layout=visuals['layout'])
            st.plotly_chart(fig)
            st.button("Save Plot in Dashboard", on_click=self.save_plot, args=[fig], key=f"plot_{str(uuid.uuid4())}")
            
            # Convert the visuals to serializable format before saving
            if save:
                serializable_visuals = visualizationRequests.make_serializable(visuals)
                new_chat_viz = ChatViz(viz=[serializable_visuals])
                visualizationRequests.save_chat_visualizations(self.chatbot_session['project_id'], new_chat_viz)
                self.chatbot_session['chatbot']['messages'].append({'role':'visualizer','content':visuals})
                print("VISUALS SAVED")
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
                    json.loads(visuals)
                

        
    def accept_user_input(self):
        """
        Accepts user input and processes the query. It generates responses and handles recommendations.
        """
        print('Before Accepting User Input',self.chatbot_session['chatbot']['messages'])
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
            pass
        print('After Accepting User Input',self.chatbot_session['chatbot']['messages'])
 

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
        print("After Generating Response",self.chatbot_session['chatbot']['messages'])

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
        print("Before Displaying Assistant Response",self.chatbot_session['chatbot']['messages'])

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
        print("After Displaying Assistant Response",self.chatbot_session['chatbot']['messages'])
    


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
            print("FETCHED HISTORY")
            self.chatbot_session['chatbot']['messages'].extend(chatbotRequests.get_streamlit_chat_history(self.chatbot_session['project_id']))
        else:
            print("HISTORY ALREADY EXISTS")
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
    

    # def checkQueryRequest(self,prompt):
    #     classifier = pipeline("zero-shot-classification",model="facebook/bart-large-mnli")
    #     sequence_to_classify = prompt
    #     candidate_labels = ['Question','Table','Plot']
    #     result = classifier(sequence_to_classify, candidate_labels)
    #     print(result)
    # print("HISTORY: ",messages)
if 'project_id' in st.session_state['user_data']['projects']['current_project'] and st.session_state['user_data']['projects']['current_project']['project_id']!=None:
    Chatbot()