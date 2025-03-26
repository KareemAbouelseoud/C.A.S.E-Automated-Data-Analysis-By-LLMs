import streamlit as st
from Project.AutoML import AutoML
from Project.Visualizations import Visualizations
from Project.Dataset import Dataset
from Requests import databaseRequests
import uuid
from Style import general,buttons
class Project:
    
    def backtooverview(self):
        st.session_state['user_data']['projects']['current_project']={}
        


    def selectedProject(self):
        self.home_session=st.session_state['user_data']['projects']['current_project']
        if 'project_details' not in self.home_session or self.home_session['project_details']==None:
            self.home_session['project_details']=databaseRequests.get_project_details(self.home_session['project_id'])
        st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{self.home_session['project_details']['name']}</h1>", unsafe_allow_html=True)     

        

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


if 'project_id' in st.session_state['user_data']['projects']['current_project'] and st.session_state['user_data']['projects']['current_project']['project_id']!=None:
    Project().selectedProject()
    