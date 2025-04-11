import time
import streamlit as st
from Style import chatbot
from Project.AutoML import AutoML
from Project.Visualizations import Visualizations
from Project.Dataset import Dataset
from Project.Insights import Insights
from Requests import databaseRequests,insightRequests
import uuid
from Style import general,buttons

def stream_text(text_area_value,lock):
    if ~lock:
        current_text = ""
        for char in text_area_value:
            current_text += char
            yield current_text
            time.sleep(0.00001)  # Adjust the speed of typing
class Project:
    
    def desc_confirm(self):
        self.home_session["description_confirmed"] = True
        final_feedback=self.home_session['project_details']["dataset_description"]["feedback_history"]+["done"]
        insightRequests.modify_on_user_input(
            project_id=self.home_session['project_id'],
            user_input=final_feedback, 
            description=self.home_session['project_details']["dataset_description"]['description'],
            thread_id=self.home_session['project_details']["dataset_description"]["thread_id"]
        )
        st.toast("Content confirmed!", icon="✅")
    def sanitize_user_input(self, user_input):
        # Remove any potentially harmful characters or sequences        
        sanitized = user_input.replace('<', '&lt;').replace('>', '&gt;')
        # Limit input length
        max_length = 500
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            st.warning(f"Input truncated to {max_length} characters.")
        return sanitized
    
    def backtooverview(self):
        st.session_state['user_data']['projects']['current_project']={}
    
    @st.fragment
    @st.dialog("Confirm Data Description", width="large") 
    def Confirm_data_description(self,description=None, thread_id:str=None):
        description = self.home_session['project_details']["dataset_description"]['description']
        thread_id = self.home_session['project_details']["dataset_description"]['thread_id']
        if self.home_session["description_confirmed"]==False:
            col1, col2 = st.columns([1,3])
            chat_area = col1.container(key="chat_area")
            description_area = col2.container(key="description_area")
            with chat_area:
                st.write("Feedback History")
                # Display chat messages from session state
                if 'feedback_history' not in self.home_session['project_details']["dataset_description"]:
                    self.home_session['project_details']["dataset_description"]["feedback_history"] = []
                st.markdown(chatbot.assistant_messages, unsafe_allow_html=True)
                st.markdown(chatbot.user_messages, unsafe_allow_html=True)        
                st.markdown(general.dialog_box,unsafe_allow_html=True)
                with st.container(key="chat-history-container"):
                    for feedback in self.home_session['project_details']["dataset_description"]["feedback_history"]:
                        with st.chat_message("user"):
                            st.markdown(feedback, unsafe_allow_html=True)
                
                
                # Add messages to container
                
                
                # Chat input
                if prompt := st.chat_input("Type your message...", key="chat_input"):
                    sanitized_input = self.sanitize_user_input(prompt)
                    self.home_session['project_details']["dataset_description"]["feedback_history"].append(sanitized_input)
                    self.home_session['project_details']["dataset_description"]['description'], self.home_session['project_details']["dataset_description"]['description_thread_id'] = insightRequests.modify_on_user_input(self.home_session['project_id'],self.home_session['project_details']["dataset_description"]["feedback_history"], thread_id)
                    st.rerun(scope="fragment")
            with description_area:
                if self.home_session['project_details']["description_confirmed"]==False:
                    text_generator = stream_text(description,self.home_session['project_details']["description_confirmed"])
                    text_area = st.empty()
                    for text in text_generator:
                        if text == description:
                            output = text_area.text_area('Description Area', value=text,label_visibility="hidden")
                        else: 
                            text_area.text_area('Description Area', value=text,label_visibility="hidden")
                        time.sleep(0.00001)  # Adjust the speed of typing
                
                if st.button("Confirm"):
                    self.desc_confirm()
                    
                    
                    self.home_session['project_details']["description_confirmed"]=True
                    st.rerun(scope="app")

        else:
            st.rerun(scope="app")

    def selectedProject(self):
        self.home_session=st.session_state['user_data']['projects']['current_project']
        if self.home_session["description_confirmed"]==True:
            if 'project_details' not in self.home_session or self.home_session['project_details']==None:
                self.home_session['project_details']=databaseRequests.get_project_details(self.home_session['project_id'])
                st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{self.home_session['project_details']['name']}</h1>", unsafe_allow_html=True)     
        else:
            self.home_session['project_details']=databaseRequests.get_Incomplete_project_details(self.home_session['project_id'])
            st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{self.home_session['name']}</h1>", unsafe_allow_html=True)     
        
        if self.home_session['project_details']["description_confirmed"]:
            st.markdown(general.tab_design,unsafe_allow_html=True)
            tabs=st.tabs(['Dataset','Processing','Insights','Visualizations','AutoML'])
            with tabs[0]:
                col=[4]+[1]*18
                cols=st.columns(col)
                with cols[-1]:
                    st.markdown(buttons.back_button,unsafe_allow_html=True)
                    st.markdown(f'<span id="button-back"></span>', unsafe_allow_html=True)
                    st.button('',icon=":material/arrow_back:",on_click=self.backtooverview,key=f"back_{uuid.uuid4()}")
                with cols[0]:
                    st.markdown(buttons.segmented_button,unsafe_allow_html=True)
                    st.markdown(f'<span id="button-segmented"></span>', unsafe_allow_html=True)
                    self.home_session['dataset_mode'] = st.segmented_control(
                        "Displayed values", 
                        ["Raw", "Processed"], 
                        default=self.home_session.get('dataset_mode', 'Raw'), 
                        label_visibility="collapsed", 
                        selection_mode='single'
                    )
                Dataset()
            with tabs[2]:
                st.markdown("<h1 style='text-align: center; font-size: 65px;'>ODIN</h1>", unsafe_allow_html=True)    
                with st.columns(19)[-1]:
                    st.markdown(buttons.back_button,unsafe_allow_html=True)
                    st.markdown(f'<span id="button-back"></span>', unsafe_allow_html=True)
                    st.button('',icon=":material/arrow_back:",on_click=self.backtooverview,key=f"back_{uuid.uuid4()}")
                Insights()
            with tabs[3]:
                st.markdown("<h1 style='text-align: center; font-size: 65px;'>IRIS</h1>", unsafe_allow_html=True)    
                with st.columns(19)[-1]:
                    st.markdown(buttons.back_button,unsafe_allow_html=True)
                    st.markdown(f'<span id="button-back"></span>', unsafe_allow_html=True)
                    st.button('',icon=":material/arrow_back:",on_click=self.backtooverview,key=f"back_{uuid.uuid4()}")
                Visualizations()

            with tabs[-1]:
                with st.columns(19)[-1]:
                    st.markdown(buttons.back_button,unsafe_allow_html=True)
                    st.markdown(f'<span id="button-back"></span>', unsafe_allow_html=True)
                    st.button('',icon=":material/arrow_back:",on_click=self.backtooverview,key=f"back_{uuid.uuid4()}")
                AutoML()

        else:
            if self.home_session['project_details']['dataset_description']==None or self.home_session['project_details']['dataset_description']=={}:
                self.home_session['project_details']["dataset_description"]={}
                self.home_session['project_details']["dataset_description"]['description'], self.home_session['project_details']["dataset_description"]['thread_id']=insightRequests.get_description(self.home_session['project_id'])
            with st.columns(19)[-1]:
                    st.markdown(buttons.back_button,unsafe_allow_html=True)
                    st.markdown(f'<span id="button-back"></span>', unsafe_allow_html=True)
                    st.button('',icon=":material/arrow_back:",on_click=self.backtooverview,key=f"back_{uuid.uuid4()}")
            cols=st.columns(3)
            with cols[1]:
                st.markdown(
                    buttons.primary_button,
                    unsafe_allow_html=True,
                )
                st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
                placeholder = st.empty()
                if placeholder.button("Confirm Data Description"):
                    self.Confirm_data_description()
                else:
                    self.Confirm_data_description()

if 'project_id' in st.session_state['user_data']['projects']['current_project'] and st.session_state['user_data']['projects']['current_project']['project_id']!=None:
    
    Project().selectedProject()
    