import streamlit as st
from Objects import Dashboard,Plot
from streamlit_elements import elements,event,sync,lazy
from types import SimpleNamespace
from Requests import visualizationRequests

class Visualizations:
    def __init__(self):
        st.markdown("<h1 style='text-align: center; font-size: 50px;'>IRIS</h1>", unsafe_allow_html=True)
        self.run()

    def create(self,fig_dict):
        if isinstance(fig_dict,dict):
            plot=Plot.Plots(st.session_state.board, 12,  7, w=5, h=7, minW=2, minH=4,fig=fig_dict)
            return plot
        else:
            for i in fig_dict:
                return self.create(i)
    
    def visualizationShown(self):
        st.session_state['Visualization']=True
        
    def run(self):
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
            if not st.session_state['Visualization']:
                st.button("Begin Generation",on_click=self.visualizationShown)
        print(st.session_state['Visualization'])
        if st.session_state['Visualization']:
            if "w" not in st.session_state:
                st.session_state.board = Dashboard.Dashboard()
                w = SimpleNamespace(
                    visualizations=[]
                )
                st.session_state.w = w

            else:
                w = st.session_state.w
            with elements("demo"):
                event.Hotkey("ctrl+s", sync(), bindInputs=True, overrideDefault=True)
                vizs=visualizationRequests.fetch_visualizations(st.session_state.Project)
                print(vizs) 
                for i in vizs:
                    w.visualizations.append(self.create((i)))
                

                with st.session_state.board(rowHeight=57):
                    for i in w.visualizations:
                        i()