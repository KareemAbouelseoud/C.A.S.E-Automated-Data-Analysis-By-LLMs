"""
This module implements a login interface for a Streamlit application. It includes a 
Login class that handles user authentication and session management.

Classes:
    Login: Handles user login functionalities including input fields for username 
           and password, login button, and session state management.
"""

import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from Requests import databaseRequests
from streamlit_cookies_controller import CookieController

try:
    controller = CookieController()
except:
    pass
class Login:

    def __init__(self) -> None:
        __username=None
        __password=None
        if 'user_id' not in st.session_state['user_data']:
            st.session_state['user_data']['user_id']=''

    
        

    

    def __login(self):
        """
        Private method to authenticate the user based on username and password.
        Updates the session state upon successful login.
        """
        if self.__username and self.__password:
            if databaseRequests.check_login(self.__username,self.__password)=='True':
                st.session_state['loggedIn']=True
                user =databaseRequests.get_user_by_username(self.__username)
                controller.set("user",user)
                controller.set(f"user_id", user["id"])  # set expiration date as needed
                

            else:
                st.error('Incorrect Username or Password.')

    def login_page(self):
        """
        Renders the login page interface with input fields for username and password,
        and a login button.
        """
        st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>Welcome to C.A.S.E</h1>", unsafe_allow_html=True)
        cols=st.columns(3)
        with cols[1]:
            st.info("NOTE: When Logging in, please write your responses in your own words. Using suggested text can sometimes lead to unexpected errors in Streamlit.")

            with st.container(border=True):
                st.header('Login')
                self.__username=st.text_input(label='Username',value='',placeholder='Enter your username')
                self.__password=st.text_input(label='Password',value='',placeholder='Enter your password',type='password')
                LoginButton=st.button('Login',on_click=self.__login)

login=Login()
login.login_page()