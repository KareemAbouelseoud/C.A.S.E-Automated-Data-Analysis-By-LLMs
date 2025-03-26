import streamlit as st
from streamlit_cookies_controller import CookieController
import os
from Style import buttons,general
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
        
        st.markdown(general.logo, unsafe_allow_html=True) 
        logo_path = os.path.join(os.path.dirname(__file__), "static", "CASE LOGO white.png")
        st.logo(
            logo_path,
        )
        st.markdown(general.background,unsafe_allow_html=True)

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
        st.session_state['loggedIn'] = False
        self.controller.remove(f"user")     
        self.controller.remove(f"user_id")     
        del st.session_state['user_data']


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
        cookies = self.controller.getAll()
        if 'user_data' not in st.session_state:
            st.session_state['user_data'] = {}
            st.session_state['user_data']['projects'] = {}
            st.session_state['user_data']['projects']['current_project'] = {}

        if st.session_state['loggedIn']==False:
            for key in cookies:
                if key=="user_id":
                    st.session_state['user_data']['user_id'] = cookies[key]
                    st.session_state['loggedIn']=True
                    user_first_name=controller.get("user")["first_name"]
                    st.toast(f"Welcome back, {user_first_name}!",icon='🎉')
                    break
                

        if st.session_state['loggedIn']==False:
            self.login()
        else:
            user_first_name=controller.get("user")["first_name"]
            with st.sidebar:
                st.markdown(f"<h1 style='text-align: center; font-size: 30px;'>Hello {user_first_name}</h1>", unsafe_allow_html=True)
            if 'project_id' in st.session_state['user_data']['projects']['current_project'] and st.session_state['user_data']['projects']['current_project']['project_id']!=None:
                
                # if st.session_state['user_data']['projects']['current_project'].get('description_confirmed',False):
                #     st.navigation(self.pages[-2:]).run()
                # else:
                #     #this needs to be here
                #     from Displays.Project.dataDescription import dataDescription
                #     dataDescription()
                st.navigation(self.pages[-2:]).run() #remove this when the above is fixed

                    
            else:  
                pg=st.navigation(self.pages[2:4])
                pg.run()
            st.sidebar.markdown(buttons.sidebar_button,unsafe_allow_html=True,)
            st.sidebar.markdown('<span id="button-sidebar"></span>', unsafe_allow_html=True)
            clicked=st.sidebar.button("Logout",on_click=self.logout)
            if clicked:
                pg=st.navigation(self.pages[:2])
                pg.run()
        



            
if __name__=='__main__':
    st.set_page_config(layout='wide')   
    controller = CookieController()
    full_app = MultiPageApp(controller=controller)
    full_app.add_page('Displays/Login.py',title='Login')
    full_app.add_page('Displays/Signup.py',title='Signup')
    full_app.add_page("Displays/Overview.py",title='Overview',default=True) 
    full_app.add_page("Displays/About.py",title='About') 
    full_app.add_page('Displays/Project/Home.py',title='Home')
    full_app.add_page('Displays/Project/Chatbot.py',title='ZEUS')
    full_app.run()



  