"""
This module implements a sign-up interface for a Streamlit application. It includes a 
SignUp class that handles user registration and session management.

Classes:
    SignUp: Handles user sign-up functionalities including input fields for first name, 
            last name, username, password, email, and a sign-up button, along with session 
            state management.
"""
import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from Requests import databaseRequests
from streamlit_cookies_controller import CookieController
controller = CookieController()

class SignUp:
    def __init__(self) -> None:
        self.__first_name=None
        self.__last_name=None
        self.__username=None
        self.__password=None
        self.__email=None
        if 'user_id' not in st.session_state['user_data']:
            st.session_state['user_data']['user_id']=''

    def __signup(self)->None:
        """
        Private method to register a new user based on the provided information.
        Updates the session state upon successful sign-up.
        """
        if self.__username and self.__last_name and self.__first_name and self.__password and self.__email:
            response=databaseRequests.check_signup(self.__first_name,self.__last_name,self.__email,self.__username,self.__password)
            if response=="Email already exists.":
                st.toast(response)
            elif response=="Username already exists.":
                st.toast(response)
            elif response== "Signup successful!":
                # st.session_state['user_id']=databaseRequests.get_user_id(self.__username)
                user =databaseRequests.get_user_by_username(self.__username)
                st.session_state['loggedIn']=True
                controller.set("user",user)
                controller.set(f"user_id", user["id"])  # set expiration date as needed

                
            else:
                st.error('An error occured, please try again later.')
            


    def signUp(self)-> None:
        """
        Renders the sign-up page interface with input fields for first name, last name, username, 
        password, email, and a sign-up button.
        """
        st.markdown(f"<h1 style='text-align: center; font-size: 80px;'>Welcome to C.A.S.E</h1>", unsafe_allow_html=True)
        cols=st.columns(3)
        with cols[1]:
            st.info("NOTE: When signing up, please write your responses in your own words. Using suggested text can sometimes lead to unexpected errors in Streamlit.")

            with st.container(border=True):
                st.header('Signup')
                cols=st.columns(2)
                with cols[0]:
                    self.__first_name=st.text_input(label='First Name',value='',placeholder='Enter your First Name')
                with cols[1]:
                    self.__last_name=st.text_input(label='Last Name',value='',placeholder='Enter your Last Name')
                self.__email=st.text_input(label='Email',value='',placeholder='Enter your Email')
                cols=st.columns(2)
                with cols[0]:
                    self.__username=st.text_input(label='Username',value='',placeholder='Enter your username')
                with cols[1]:
                    self.__password=st.text_input(label='Password',value='',placeholder='Enter your password',type='password')
                SignUpButton=st.button('Sign Up',on_click=self.__signup)



SignUp().signUp()