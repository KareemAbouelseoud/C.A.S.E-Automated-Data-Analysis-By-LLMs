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
            time.sleep(0.0001)  # Adjust the speed of typing
def desc_confirm():
    st.session_state['user_data']['projects']['current_project']["description_confirmed"] = True
class Project:
    
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
        if st.session_state['user_data']['projects']['current_project']["description_confirmed"]==False:
            col1, col2 = st.columns([1,3])
        
            with col1:
                st.write("Feedback History")
                # Display chat messages from session state
                if 'feedback_history' not in st.session_state:
                    st.session_state.feedback_history = []
                st.markdown(chatbot.assistant_messages, unsafe_allow_html=True)
                st.markdown(chatbot.user_messages, unsafe_allow_html=True)        
                st.markdown(general.dialog_box,unsafe_allow_html=True)
                chat_html = """
                <div class="chat-history-container">
                """
                
                # Add messages to container
                for feedback in st.session_state.feedback_history:
                    chat_html += f"""
                    <div class="chat-message user-message">
                        {feedback}
                    </div>
                    """
                
                chat_html += "</div>"
                
                # Render chat container
                st.html(chat_html)
                
                # Chat input
                if prompt := st.chat_input("Type your message...", key="chat_input"):
                    st.session_state.feedback_history.append(prompt)
                    st.rerun(scope="fragment")
            with col2:
                if st.session_state['user_data']['projects']['current_project']["description_confirmed"]==False:
                    text_generator = stream_text(description,st.session_state['user_data']['projects']['current_project']["description_confirmed"])
                    text_area = st.empty()
                    for text in text_generator:
                        if text == description:
                            output = text_area.text_area('Description Area', value=text,label_visibility="hidden")
                        else:
                            text_area.text_area('Description Area', value=text,label_visibility="hidden")
                        time.sleep(0.0001)  # Adjust the speed of typing
                
                if st.button("Confirm",on_click=desc_confirm):
                    print(output)
                    st.toast("Content confirmed!", icon="✅")
                    time.sleep(3)
                    st.session_state['user_data']['projects']['current_project']["description_confirmed"]=True
                    st.rerun(scope="app")

        else:
            st.rerun(scope="app")

    def selectedProject(self):
        self.home_session=st.session_state['user_data']['projects']['current_project']
        if 'project_details' not in self.home_session or self.home_session['project_details']==None:
            # self.home_session['project_details']=databaseRequests.get_project_details(self.home_session['project_id'])
            self.home_session['project_details']={"name":"Dummy Name to save Backend requests","data_report":""}
        st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>{self.home_session['project_details']['name']}</h1>", unsafe_allow_html=True)     
        
        if st.session_state['user_data']['projects']['current_project']["description_confirmed"]:
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
            # desc, thread_id=insightRequests.get_description(self.home_session['project_id'])
            desc="""
            
                        Column Explanation:
*   **PassengerId:** A unique identifier for each passenger.
*   **Survived:** Indicates whether the passenger survived (0 = No, 1 = Yes).
*   **Pclass:** The passenger's class (1 = 1st class, 2 = 2nd class, 3 = 3rd class).
*   **Name:** The name of the passenger.
*   **Sex:** The gender of the passenger (male or female).
*   **Age:** The age of the passenger in years.
*   **SibSp:** The number of siblings/spouses aboard.
*   **Parch:** The number of parents/children aboard.
*   **Ticket:** The passenger's ticket number.
*   **Fare:** The fare paid by the passenger.
*   **Cabin:** The cabin number of the passenger.
*   **Embarked:** The port where the passenger embarked (C = Cherbourg, Q = Queenstown, S = Southampton).
                        Overview:
The dataset contains information about passengers aboard the Titanic, including their demographics, ticket information, and survival status. It is commonly used for predictive modeling tasks, particularly for predicting passenger survival.
                        Key Patterns:
*   Survival rate appears to be correlated with passenger class and sex.
*   A significant portion of passengers are traveling without siblings/spouses or parents/children.
*   Fare prices vary widely, with some passengers paying significantly more than others.
*   The majority of passengers embarked from Southampton (S).
                        Quality Issues:
*   **Missing Values:** The 'Age' column has a significant number of missing values, which may require imputation or other handling.
    The 'Cabin' column has a large number of missing values, potentially indicating that this information was not recorded for many passengers, or the passengers didn't have a cabin.
    The 'Embarked' column has some missing values.
*   **Data Types:** The 'Age' column is numerical but contains null values, which might need to be addressed before certain analyses.
*   **Inconsistent Data:** There might be inconsistencies in the 'Name' column (e.g., titles, nicknames) that could affect analysis if not handled properly.
                
            """
            st.markdown(buttons.back_button,unsafe_allow_html=True)
            st.markdown(f'<span id="button-back"></span>', unsafe_allow_html=True)
            st.button('',icon=":material/arrow_back:",on_click=self.backtooverview,key=f"back_{uuid.uuid4()}")
            
            self.Confirm_data_description( description=desc)


if 'project_id' in st.session_state['user_data']['projects']['current_project'] and st.session_state['user_data']['projects']['current_project']['project_id']!=None:
    
    Project().selectedProject()
    