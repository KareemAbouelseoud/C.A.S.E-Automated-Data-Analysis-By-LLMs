import streamlit as st
from Requests import databaseRequests
data_session = st.session_state['user_data']['projects']['current_project']
class dataDescription:
    def __init__(self):
        #NOTE: Initial Data Description should contain the generated description of the data
        try:
            self.initial_description = data_session['initial_data_description']
        except:
            self.initial_description = databaseRequests.fetch_datareport(data_session['project_id'])['dataset_description']
        self.display()
    def display(self):
        with st.container(border=True):
            with st.form("Data Description",):
                final_description=st.text_area(label='Initial Data Description. Please make sure that this description is accurate', value=self.initial_description, height=500)
                st.form_submit_button(label='Submit',on_click=self.submit,args=[final_description])

    
    def submit(self,final_description):
        #NOTE: Save the final description to the database
        #NOTE: BEWARE OF PROMPT INJECTION, MAKE SURE TO SANITIZE THE INPUT BEFORE SAVING
        data_session['description_confirmed']=True
        

