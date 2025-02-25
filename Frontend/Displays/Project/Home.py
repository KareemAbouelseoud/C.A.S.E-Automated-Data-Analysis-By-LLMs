import streamlit as st
from Project.AutoML import AutoML
from Project.Visualizations import Visualizations
from Requests import databaseRequests
import uuid
class Project:
    
    def backtooverview(self):
        st.session_state['training']=False
        st.session_state['Project']=None
        st.session_state['Visualization']=None
        st.session_state["newProject"] = False
        st.session_state['Project']=None
        st.session_state['Visualization']=None
        st.session_state['viz_data']=[]
        if 'board' in st.session_state:
            st.session_state['board']=None
        if "w"  in st.session_state:
            del st.session_state['w']
        if 'df' in st.session_state:
            del st.session_state['df']
            del st.session_state['autoML_data']
        if 'project_details' in st.session_state:
            del st.session_state['project_details']
        if 'messages' in st.session_state:
            del st.session_state['messages']
        if 'new' in st.session_state:
            del st.session_state['new']
        if 'recommendation' in st.session_state:
            del st.session_state['recommendation']


    def selectedProject(self):
        if 'project_details' not in st.session_state or st.session_state['project_details']==None:
            st.session_state['project_details']=databaseRequests.get_project_details(st.session_state['Project'])
        st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{st.session_state['project_details']['name']}</h1>", unsafe_allow_html=True)     

        

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
        tabs=st.tabs(['Raw Dataset','Processed Dataset','Insights','Visualizations','AutoML'])
        with tabs[0]:
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
            st.markdown("<h1 style='text-align: center; font-size: 50px;'>IRIS</h1>", unsafe_allow_html=True)    
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


if 'Project' in st.session_state and st.session_state['Project']!=None:
    Project().selectedProject()
    