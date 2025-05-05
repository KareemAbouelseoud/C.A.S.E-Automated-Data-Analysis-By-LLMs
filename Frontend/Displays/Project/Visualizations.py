import streamlit as st
from Objects import Dashboard,Plot
from streamlit_elements import elements,event,sync,lazy
from types import SimpleNamespace
from Requests import visualizationRequests
import hydralit_components as hc
from Style import buttons
import uuid
class Visualizations:
    def __init__(self):
        self.dimensions={
            "Pair":{'w':12,'h':10},
            "Bar":{'w':6,'h':9},
            "Histogram":{'w':6,'h':9},
            "Violin":{'w':6,'h':9},
            "Box":{'w':6,'h':9},
            "Line":{'w':7.5,'h':7},
            "Pie":{'w':4.5,'h':7},

        }
        self.placeholder=st.empty()
        self.viz_session=st.session_state['user_data']['projects']['current_project']

        if 'viz' not in self.viz_session:
            self.viz_session['viz']={}
            self.viz_session['viz']['Visualization']=False

        if 'w' not in self.viz_session['viz']:
            self.viz_session['viz']['board'] = Dashboard.Dashboard()
            w = SimpleNamespace(
                visualizations=[]
            )
            vizs=visualizationRequests.fetch_visualizations(self.viz_session['project_id'])
            if vizs:
                for i in vizs:
                    w.visualizations.append(self.create((i)))
            self.viz_session['viz']['w'] = w
            self.visualize(self.viz_session['viz']['w'])
        else:
            if self.viz_session['viz']['w'].visualizations:
                self.visualize(self.viz_session['viz']['w'])
        self.run()

    def create(self,fig_dict):
        if isinstance(fig_dict,dict):
            try:
                plot=Plot.Plots(self.viz_session['viz']['board'], 0,  0, w=6, h=6,fig=fig_dict['figure_data'],name=fig_dict['name'])
            except:
                plot=Plot.Plots(self.viz_session['viz']['board'], 0,  0, w=6, h=6,fig=fig_dict)

            return plot
        else:
            for i in fig_dict:
                return self.create(i)
    
    def visualizationShown(self):
        self.viz_session['viz']['Button_clicked']=True
        
    def run(self):
        cols=st.columns(3)
        with cols[1]:
            st.markdown(
                buttons.primary_button,
                unsafe_allow_html=True,
            )
            st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
            placeholder = st.empty()
            placeholder.button("Regenerate Visualizations" if self.viz_session['viz']['w'].visualizations else "Begin Generation",on_click=self.visualizationShown)
            if 'Button_clicked' in self.viz_session['viz'] and self.viz_session['viz']['Button_clicked']:
                placeholder2=st.empty()
                with placeholder2.container(border=True):
                    df=self.viz_session['dataset_session']['raw_dataset']
                    with st.form(key='viz_form',border=False):
                        features = st.multiselect('Select the features to focus on. (Optional)',df.columns.to_list())
                        if st.form_submit_button("Generate"):
                            if features:
                                self.viz_session['viz']['features']=features
                            self.viz_session['viz']['Visualization']=True
        
        if self.viz_session['viz']['Visualization']:
            placeholder2.empty()
            self.viz_session['viz']['w']=self.generate_visuals(self.viz_session['viz']['w'])
            self.viz_session['viz']['Visualization']=False
            self.viz_session['viz']['Button_clicked']=False
            st.rerun()
            
    def generate_visuals(self,w):
            with hc.HyLoader("",hc.Loaders.pulse_bars,index=[0]):
                features=[]
                if 'features' in self.viz_session['viz']:
                    features=self.viz_session['viz']['features']
                vizs=visualizationRequests.create_visualizations(self.viz_session['project_id'],features)
                w.visualizations=[]
                for i in vizs:
                    w.visualizations.append(self.create((i)))
            return w            

    def visualize(self,w):
        with self.placeholder.container(border=True):
            with elements(f"demo"):
                event.Hotkey("ctrl+s", sync(), bindInputs=True, overrideDefault=True)
                with self.viz_session['viz']['board'](compactType='horizontal',rowHeight=57):
                    for i in w.visualizations:
                        i()