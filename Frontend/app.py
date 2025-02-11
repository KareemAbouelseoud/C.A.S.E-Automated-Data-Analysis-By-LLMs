import streamlit as st
from streamlit_cookies_controller import CookieController
import os
import pandas as pd
import requests
from Requests import databaseRequests
class MultiPageApp():
    """
    A class to create a multi-page Streamlit application.
    
    Attributes
    ----------
    pages : list
        A list to store the pages of the application.
    
    Methods
    -------
    add_page(directory, title, default=False)
        Adds a new page to the application.
    
    run()
        Runs the Streamlit application with the configured pages and layout.
    """
    def __init__(self,controller) -> None:
        self.pages=[]
        self.auth_pages={}
        self.controller=controller
        
        # st.session_state['cookie_man']=True
        bg = '''
        <style>
        [data-testid="stHeader"] {
            background-color: rgba(0,0,0,0);
        }
        [data-testid="stAppViewContainer"] {
            background-color: #908d8d;
            opacity: 1;
            background-image: radial-gradient(circle at center center, #000000, #908d8d), repeating-radial-gradient(circle at center center, #000000, #000000, 40px, transparent 100px, transparent 40px);
            background-blend-mode: multiply;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.5), 0 0 20px rgba(255, 255, 255, 0.5), 0 0 30px rgba(255, 255, 255, 0.5);
        }
        .st-emotion-cache-lr2bj0.eiemyj5 {
            border-radius: 16px;
            background: rgba(0,0,0,0.5);
            z-index: 2;
            box-shadow: 0 0 10px rgba(255, 255, 255, 0.5), 0 0 20px rgba(255, 255, 255, 0.5), 0 0 30px rgba(255, 255, 255, 0.5);
        }
        </style>
        '''
        st.markdown("""
                    <style>
                    [data-testid="stLogo"] {
                        width: 800;  /* Adjust width as needed */
                        height: auto;  /* Maintain aspect ratio *

                """, unsafe_allow_html=True) 
        st.logo(
            "Static\CASE LOGO.png",
        )
        st.markdown(bg,unsafe_allow_html=True)

        if 'loggedIn' not in st.session_state:
            st.session_state['loggedIn']=False


        if 'signUp_Page' not in st.session_state:
            st.session_state['signUp_Page']=False
        

    def add_page(self,directory,title,default=False):
        """
        Adds a new page to the application.
        
        Parameters
        ----------
        directory : str
            The directory path of the page script.
        title : str
            The title of the page.
        default : bool, optional
            Indicates if this page is the default page (default is False).
        
        Returns
        -------
        None
        """
        self.pages.append(st.Page(directory,title=title,default=default))
        
    def login(self):
        st.session_state['loggedIn']=False
        pg=st.navigation(self.pages[:2])
        pg.run()

    def logout(self):
        st.empty()
        st.session_state['loggedIn'] = False
        self.controller.remove(f"user_{st.session_state['user_id']}_session")        


    def run(self):
        """
        Runs the Streamlit application with the configured pages and layout.
        
        Sets up the page configuration and sidebar, and navigates to the selected page.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        """
        # st.logo(
        #     "Static\CASE LOGO.png",
        # )
        cookies = self.controller.getAll()
        if st.session_state['loggedIn']==False:
            for key in cookies:
                if key.startswith("user_"):
                    st.session_state['user_id'] = cookies[key]
                    st.session_state['loggedIn']=True
                    st.toast(f"Welcome back, {databaseRequests.get_name(st.session_state.user_id)}!",icon='🎉')
                    break
                

        if st.session_state['loggedIn']==False:
            self.login()
        else:
            st.sidebar.title(f"Hello {databaseRequests.get_name(st.session_state.user_id)}")    
            pg=st.navigation([self.pages[-1]])
            pg.run()
            clicked=st.sidebar.button("Logout",on_click=self.logout)
            if not clicked:
                pg=st.navigation(self.pages[2:])
                pg.run()

            
if __name__=='__main__':
    st.set_page_config(layout='wide')   
    controller = CookieController()
    full_app = MultiPageApp(controller=controller)
    # full_app.add_page("pages/About/about.py", title='Home')
    full_app.add_page('Displays/Login.py',title='Login')
    full_app.add_page('Displays/Signup.py',title='Signup')
    full_app.add_page("Displays/Projects/Projects.py",title='Projects') 
    full_app.add_page("Displays/About.py",title='About') 
    full_app.run()



  