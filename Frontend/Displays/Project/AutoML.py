import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Requests import databaseRequests,automlRequests





class AutoML:

    def __init__(self):
        self.autoML_session = st.session_state['user_data']['projects']['current_project']
        if 'autoML' not in self.autoML_session:
            self.autoML_session['autoML']={}            
            self.autoML_session['autoML']['training']=False
            self.autoML_session['autoML']['autoML_data']={}
        
        self.run()


    def trainingStarted(self):
        self.autoML_session['autoML']['training']=True
        self.trainPage(**self.autoML_session['autoML']['autoML_data'])

    def run(self):
        st.write("\n\n\n\n\n")
        if 'df' not in self.autoML_session['autoML'] or self.autoML_session['autoML']['df'] is None:
            df=databaseRequests.fetch_dataset(self.autoML_session['project_id'])
            self.autoML_session['autoML']['df']=df
        else:
            df=self.autoML_session['autoML']['df']
        
        if 'autoML_data' not in self.autoML_session['autoML']:
            self.autoML_session['autoML']['autoML_data']={}
        
            
        with st.form('AutoML'):
            cols=st.columns([1,2,1])
            with cols[0]:
                c=st.columns([9,1])
                with c[0]:
                    if df is not None:
                        columns = df.columns.tolist()
                        target_feature = st.selectbox('Select the target feature', columns)
                        self.autoML_session['autoML']['autoML_data']['target_feature']=target_feature
            with cols[1]:
                c=st.columns([2,1])
                with c[1]:
                    feature_selection_mode = st.radio('Feature selection mode', ['Include', 'Exclude'], horizontal=True)
                with c[0]:
                    if df is not None:
                        if feature_selection_mode == 'Include':
                            features = st.multiselect('Select the features to include', [col for col in df.columns.tolist() if col != target_feature])
                            self.autoML_session['autoML']['autoML_data']['features']=features
                        else:
                            features = st.multiselect('Select the features to exclude', [col for col in df.columns.tolist() if col != target_feature])
                            features = [feature for feature in df.columns.tolist() if feature not in features and feature != target_feature]
                            self.autoML_session['autoML']['autoML_data']['features']=features
            with cols[2]:
                mode = st.selectbox('Select the mode', ['⚡HERMES', '⚖️ ATHENA', '🔨 HEPHAESTUS'],help='HERMES is extremely fast, but sacrifices accuracy\n\n ATHENA is the balanced mode\n\n HEPHAESTUS is the slowest, but guarantess the highest accuracy')
                self.autoML_session['autoML']['mode'] = mode
            c=st.columns([1,2,1])
            # with c[-1]:
                # if st.session_state['mode'] == '⚡HERMES':
                #     st.info('**⚡HERMES**: Results before you blink!\n\n  Hermes is that intern who drinks five espressos before 9 AM and delivers results before you even finish explaining the problem.\n\nIt might cut a few corners, make some wild assumptions, and occasionally hallucinate correlations, but hey—speed is the name of the game!')
                # elif st.session_state['mode'] == '⚖️ ATHENA':
                #     st.warning('**⚖️ ATHENA**: Smart, steady, and allergic to bad decisions. \n\n Athena balances speed and accuracy like a pro—quick enough to be useful, careful enough to avoid embarrassing mistakes. The safe bet, unless you enjoy chaos.')
                # elif st.session_state['mode'] == '🔨 HEPHAESTUS':
                #     st.error('**🔨 HEPHAESTUS**: Quality takes time. Go touch grass.\n\n Hephaestus doesn’t do “rush jobs.” You need a model? He’s forging it with the patience of a monk and the precision of an elven master craftsman.\n\nSure, by the time he’s done, technology itself might have advanced, but hey—when your results finally arrive, they’ll be the statistical equivalent of a legendary Excalibur.')
                
            with c[0]:
                model_preferences = st.text_input('Model Preferences (Optional)', help='Specify any preferences or constraints for the model.\n\nE.g., "High recall for detecting fraud" or "High precision for medical diagnosis".')
                self.autoML_session['autoML']['autoML_data']['model_preferences']=model_preferences
            with c[1]:
                cc=st.columns([1,2,1])
                with cc[1]:
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
                    if not self.autoML_session['autoML']['training']:
                        st.form_submit_button("Begin Training",on_click=self.trainingStarted)
                    else:
                        st.form_submit_button("Retrain",on_click=self.trainingStarted)




    def trainPage(self,target_feature,features,model_preferences=None):
        print( target_feature,features,model_preferences)
        print(self.autoML_session['project_id'])
        print(self.autoML_session['mode'])
        # automlRequests.train(st.session_state['Project'],target_feature,training_features,st.session_state['mode'],user_input)

        
            