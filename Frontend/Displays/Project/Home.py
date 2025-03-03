import streamlit as st
from Project.AutoML import AutoML
from Project.Visualizations import Visualizations
from Project.Dataset import Dataset
from Requests import databaseRequests
import uuid
class Project:
    
    def backtooverview(self):
        st.session_state['user_data']['projects']['current_project']={}
        print("AFTER BACK", st.session_state['user_data'])
        


    def selectedProject(self):
        self.home_session=st.session_state['user_data']['projects']['current_project']
        if 'project_details' not in self.home_session or self.home_session['project_details']==None:
            self.home_session['project_details']=databaseRequests.get_project_details(self.home_session['project_id'])
        st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{self.home_session['project_details']['name']}</h1>", unsafe_allow_html=True)     

        

        st.markdown("""
                    <style>
        [data-baseweb="tab-highlight"] {
            background-color: rgba(255, 240, 200, 0.4);
            box-shadow: 
                    0 0 6px rgba(255, 255, 255, 1), 
                    0 0 12px rgba(255, 255, 255, 1), 
                    0 0 18px rgba(255, 255, 255, 1); /* Initial glow */

                            }

	.stTabs [data-baseweb="tab"] {
        color: white;
        text-shadow: 0 0 1px white, 0 0 1px white, 0 0 1px white;

    }
                    
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center; /* Center horizontally */
        align-items: center; /* Center vertically */
    }

    </style>
""",unsafe_allow_html=True)
        tabs=st.tabs(['Dataset','Processing','Insights','Visualizations','AutoML'])
        with tabs[0]:
            col=[4]+[1]*18
            cols=st.columns(col)
            with cols[-1]:
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
            with cols[0]:
                st.markdown("""
                    <style>
                    .element-container:has(#button-segmented) + div button {
                        justify-content: center;
                        align-items: center;
                        background: rgba(0, 0, 0, 0.4);
                        z-index: 2;
                        color: white;
                        font-size: 50px;
                        text-align: center;
                        cursor: pointer;
                        transition: box-shadow 0.3s ease; /* Smooth transition */
                        border: none; /* Explicitly remove any border */
                        }
                        .element-container:has(#button-segmented) + div button:hover {
                        box-shadow: 
                            0 0 10px rgba(255, 255, 255, 0.6), 
                            0 0 20px rgba(255, 255, 255, 0.5), 
                            0 0 30px rgba(255, 255, 255, 1); /* Stronger glow on hover */
                    }
                    .st-emotion-cache-1u8vu9t {
                                box-shadow: 
                                    0 0 10px rgba(0, 255, 255, 0.6), 
                                    0 0 20px rgba(0, 255, 255, 0.5), 
                                    0 0 30px rgba(0, 255, 255, 1); /* Electric blue on click */
                                border: none; /* Explicitly remove any border */
                            }
                    </style>
                """,unsafe_allow_html=True)
                st.markdown(f'<span id="button-segmented"></span>', unsafe_allow_html=True)
                self.home_session['dataset_mode'] = st.segmented_control(
                    "Displayed values", 
                    ["Raw", "Processed"], 
                    default=self.home_session.get('dataset_mode', 'Raw'), 
                    label_visibility="collapsed", 
                    selection_mode='single'
                )
            print(self.home_session['dataset_mode'])
            Dataset()
        with tabs[2]:
            st.markdown("<h1 style='text-align: center; font-size: 65px;'>ODIN</h1>", unsafe_allow_html=True)    
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
        with tabs[3]:
            st.markdown("<h1 style='text-align: center; font-size: 65px;'>IRIS</h1>", unsafe_allow_html=True)    
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
            Visualizations()

        with tabs[-1]:
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
            AutoML()


if 'project_id' in st.session_state['user_data']['projects']['current_project'] and st.session_state['user_data']['projects']['current_project']['project_id']!=None:
    Project().selectedProject()
    