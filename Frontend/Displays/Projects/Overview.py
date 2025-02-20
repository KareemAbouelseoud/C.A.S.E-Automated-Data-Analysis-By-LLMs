import sys
import os
# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from Requests import databaseRequests
from Projects.Chatbot import Chatbot
from Projects.AutoML import AutoML
from Projects.Visualizations import Visualizations
class Projects:

    def __init__(self) -> None:
        if "newProject" not in st.session_state:
            st.session_state["newProject"] = False
            st.session_state['Project']=None
            st.session_state['Visualization']=None
            st.session_state['viz_data']=[]

            st.session_state['DASHBOARD_WIDTH'] = 12  # Full width of the dashboard in grid units
            st.session_state['PLOT_WIDTH'] = 6  # Full width of the dashboard in grid units
            st.session_state['PLOT_HEIGHT'] = 4  # Full width of the dashboard in grid units
        
        self.projects=databaseRequests.read_projects(st.session_state.user_id)
        self.max_columns = 3
        self.columns = None
    
    def new_project_clicked(self):
        st.session_state["newProject"] = True
    
    def project_clicked(self,project_id):
        st.session_state['Project']=str(project_id)
  
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


    def selectedProject(self):
        project=databaseRequests.get_project_details(st.session_state['Project'])
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
            st.button('← Back',on_click=self.backtooverview)

        st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{project['name']}</h1>", unsafe_allow_html=True)     
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

    </style>
""",unsafe_allow_html=True)
        tabs=st.tabs(['Raw Dataset','Processed Dataset','Insights','Visualizations','AutoML'])
        with tabs[0]:
            Chatbot()
        
        with tabs[3]:
            Visualizations()

        with tabs[-1]:
            AutoML()
    
    def projectOverview(self):
        st.title("My Projects")
        for idx,(project_id, project_data) in enumerate(self.projects.items()):
            
            if idx % self.max_columns == 0:  # Create a new row every 3 projects
                columns = st.columns(self.max_columns)
           
            with columns[idx % self.max_columns]:  # Add project to the appropriate column
                st.markdown(
                            f"""
                            <style>
                            .element-container:has(#button-after-{idx}) + div button {{
                                border-radius: 16px;
                            background: rgba(0, 0, 0, 0.4);
                            z-index: 2;
                            box-shadow: 
                                0 0 6px rgba(255, 255, 255, 0.3), 
                                0 0 12px rgba(255, 255, 255, 0.2), 
                                0 0 18px rgba(255, 240, 200, 0.4); /* Initial glow */
                            color: white;
                            width: 100%; /* Ensure the container takes up full width */
                            height: 100%; /* Optional: to ensure vertical centering */
                            padding: 50px;
                            font-size: 20px;
                            text-align: center;
                            cursor: pointer;
                            justify-content: center;
                            align-items: center;
                            text-align: center;
                            margin-top: 20px;
                            transition: box-shadow 0.3s ease; /* Smooth transition */
                            border: none; /* Explicitly remove any border */
                                }}
                                .element-container:has(#button-after-{idx}) + div button:hover {{
                                box-shadow: 
                                0 0 10px rgba(255, 255, 255, 0.6), 
                                0 0 20px rgba(255, 255, 255, 0.5), 
                                0 0 30px rgba(255, 240, 130, 1); /* Initial glow */
                            }}
                            </style>
                            """,
                            unsafe_allow_html=True)
                st.markdown(f'<span id="button-after-{idx}"></span>', unsafe_allow_html=True)
                st.button(f"{project_data['name']}\n\n{project_data['date']}",on_click=self.project_clicked,args=[project_id])
        
        cols=st.columns(3)
        with cols[1]:
            st.markdown(
                """
                <style>
                .element-container:has(#button-after) + div button {
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
                    padding: 30px;
                    font-size: 50px;
                    text-align: center;
                    cursor: pointer;
                    justify-content: center;
                    align-items: center;
                    margin-bottom: 20px; /* Adds vertical space if wrapping occurs */
                    transition: box-shadow 0.3s ease; /* Smooth transition */
                    border: none; /* Explicitly remove any border */

                    }
                    .element-container:has(#button-after) + div button:hover {
                    box-shadow: 
                        0 0 10px rgba(255, 255, 255, 0.6), 
                        0 0 20px rgba(255, 255, 255, 0.5), 
                        0 0 30px rgba(255, 255, 255, 1); /* Stronger glow on hover */
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
            st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
            st.button(" \+ Create a new Project",on_click=self.new_project_clicked)
            
            
            if st.session_state['newProject']:
                
                with st.container(border=True):
                    st.header("New Project")
                    project_name = st.text_input("Enter a name for your project:", key="project_name")

                    uploaded_file = st.file_uploader(
                        "Upload a CSV file", type=["csv"], key="uploader"
                    )
                    if st.button('Confirm'):
                        
                        if uploaded_file:
                            # Ask for the project name
                            
                            if project_name:
                                # Save or process the uploaded file
                                st.toast(f"Project '{project_name}' has been created!")
                                databaseRequests.create_project(st.session_state['user_id'],project_name,uploaded_file)
                                st.session_state['newProject']=False
                                st.rerun()
                            
                            else:
                                st.toast('Please choose a unique name for the project')
                        else:
                            st.toast('Please upload a dataset')
                                                      
    def projectsPage(self):
        if not st.session_state['Project']:
            self.projectOverview()
        else:
            st.session_state["newProject"] = False
            self.selectedProject()

projects=Projects()
projects.projectsPage()