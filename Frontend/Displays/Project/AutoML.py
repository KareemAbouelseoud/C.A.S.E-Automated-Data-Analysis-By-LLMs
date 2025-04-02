import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import streamlit_nested_layout # Leave it here, dont remove it.
from Requests import databaseRequests,automlRequests,visualizationRequests
import plotly.io as pio
import hydralit_components as hc
import json
from .Deployment import display_feature_form
import uuid
from Style import buttons,general



class AutoML:

    def __init__(self):
        self.status_keys={
            'splitter_node':"Finished Splitting",
            "preprocessing_node":"Finished Preprocessing",
            "model_evaluator_node":"Finished Evaluation",
            "model_trainer_node":"Finished Training",
            "model_selector_node":"Finished Model Selection",
            "model_tuner_node":"Finished Tuning",
        }
        st.markdown(general.select_box,unsafe_allow_html=True)
        self.autoML_session = st.session_state['user_data']['projects']['current_project']
        if 'autoML' not in self.autoML_session:
            self.autoML_session['autoML']={}            
            self.autoML_session['autoML']['training']=False
            self.autoML_session['autoML']['autoML_data']={}
            self.autoML_session['autoML']['eval_report']=None
        self.placeholder=st.empty()
        if not self.autoML_session['autoML']['eval_report']:
            self.autoML_session['autoML']['eval_report']=automlRequests.fetch_evaluation_report(self.autoML_session['project_id'])
           
        self.run()


    def trainingStarted(self):
        self.autoML_session['autoML']['training']=True

    def run(self):
        st.write("\n\n\n\n\n")
        if 'raw_dataset' not in self.autoML_session['dataset_session'] or self.autoML_session['dataset_session']['raw_dataset'] is None:
            df=databaseRequests.fetch_dataset(self.autoML_session['project_id'])
            self.autoML_session['dataset_session']['raw_dataset']=df
        else:
            df=self.autoML_session['dataset_session']['raw_dataset']
        
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
                    feature_selection_mode = st.radio('Feature selection mode', ['Exclude', 'Include'], horizontal=True)
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
                mode = st.selectbox('Select the mode', ['⚡ HERMES', '⚖️ ATHENA', '🔨 HEPHAESTUS'],help='HERMES is extremely fast, but sacrifices accuracy\n\n ATHENA is the balanced mode\n\n HEPHAESTUS is the slowest, but guarantess the highest accuracy')
                self.autoML_session['autoML']['mode'] = mode
            c=st.columns([1,2,1])
            # with c[-1]:
                # if st.session_state['mode'] == '⚡HERMES':
                #     st.info('**⚡ HERMES**: Results before you blink!\n\n  Hermes is that intern who drinks five espressos before 9 AM and delivers results before you even finish explaining the problem.\n\nIt might cut a few corners, make some wild assumptions, and occasionally hallucinate correlations, but hey—speed is the name of the game!')
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
                    st.markdown(buttons.primary_button,unsafe_allow_html=True,)
                    st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)
                    if not self.autoML_session['autoML']['training']:
                        st.form_submit_button("Begin Training",on_click=self.trainingStarted)
                    else:
                        st.form_submit_button("Retrain",on_click=self.trainingStarted)
        
        if self.autoML_session['autoML']['training']:
            self.trainPage(**self.autoML_session['autoML']['autoML_data'])
        if 'eval_report' in self.autoML_session['autoML'] and self.autoML_session['autoML']['eval_report']:
                with self.placeholder.container(border=False):
                    self.visualize()

    def visualize(self):
            print(self.autoML_session['autoML']['eval_report'])
            # st.write(self.autoML_session['autoML']['eval_report'])
            if self.autoML_session['autoML']['eval_report']['mode']=='HERMES':
                mode='⚡ HERMES'
            elif self.autoML_session['autoML']['eval_report']['mode']=='ATHENA':
                mode='⚖️ ATHENA'
            elif self.autoML_session['autoML']['eval_report']['mode']=='HEPHAESTUS':
                mode='🔨 HEPHAESTUS'
                
            st.markdown(f"<h1 style='text-align: center; font-size: 65px;'>{mode}</h1>", unsafe_allow_html=True)    
            model_evaluation_reports=self.autoML_session['autoML']['eval_report']['evaluation_reports']
            
            if 'splitting_logic' in self.autoML_session['autoML']['eval_report']:
                st.markdown(f"<h1 font-size: 30px;'>Splitting</h1>", unsafe_allow_html=True)
                with st.expander('Splitting Agent Logic'):
                    st.write(self.autoML_session['autoML']['eval_report']['splitting_logic'])
                split_col=st.columns([1,2])
                with split_col[0]:
                    with st.expander('Splitting Parameters'):
                        cols=st.columns([1,1,1])
                        with cols[0]:
                            train_size=1-self.autoML_session['autoML']['eval_report']['test_size'][0]
                            if 'val_size' in self.autoML_session['autoML']['eval_report'] and self.autoML_session['autoML']['eval_report']['val_size'] is not None:
                                train_size-=self.autoML_session['autoML']['eval_report']['val_size']
                            st.write(f"**Train Percentage:\n {train_size*100}%**")
                        with cols[1]:
                            if self.autoML_session['autoML']['eval_report']['cross_validation']: 
                                st.write(f"**Cross Validation:\n {self.autoML_session['autoML']['eval_report']['n_splits']} Split(s)**")
                            else:
                                st.write(f"**Validation Percentage:\n {self.autoML_session['autoML']['eval_report']['val_size']*100}%**")
                        with cols[2]:
                            st.write(f"**Test Percentage:\n {self.autoML_session['autoML']['eval_report']['test_size'][0]*100}%**")
                        st.write("---")
                        if self.autoML_session['autoML']['eval_report']['shuffle']:
                            st.write("**The Data was shuffled before training**")
                        else:
                            st.write("**The Data was not shuffled before training**")
                        if self.autoML_session['autoML']['eval_report']['stratify']:
                            st.write("**The Data was stratified before training**")
                        else:
                            st.write("**The Data was not stratified before training**")
                        st.write('---')
                        with st.expander('Training Feature'):
                            for idx,feature in enumerate(self.autoML_session['autoML']['eval_report']['X_columns']):
                                st.write(f"**{idx+1}. {feature}**")
                        st.write(f"**Target Feature: {self.autoML_session['autoML']['eval_report']['y_column']}**")
                with split_col[1]:
                    try:
                        total_rows=self.autoML_session['dataset_session']['raw_data_report']['dataset_profile']['overview']['n']
                    except:
                        total_rows=None

                    fig_data=visualizationRequests.plot_split_distribution(self.autoML_session['project_id'],
                                                                        train_size=self.autoML_session['autoML']['eval_report']['train_count'],
                                                                        test_size=model_evaluation_reports[0]['test_count'],
                                                                        val_size=self.autoML_session['autoML']['eval_report']['val_count'] if not self.autoML_session['autoML']['eval_report']['cross_validation'] else None,
                                                                        total_rows=total_rows)
                    if fig_data is not None:
                        with st.expander('Split Distribution'):
                            fig = pio.from_json(fig_data)
                            st.plotly_chart(fig,use_container_width=True,key=f"split_distribution_{uuid.uuid4()}")
                        

            
                st.write('\n---')

            if 'X_preprocessing_logic' in self.autoML_session['autoML']['eval_report'] or 'Y_preprocessing_logic' in self.autoML_session['autoML']['eval_report']:
                st.markdown(f"<h1 font-size: 30px;'>Preprocessing</h1>", unsafe_allow_html=True)
                # Determine how many columns based on available preprocessing logic
                has_X_preprocessing = 'X_preprocessing_logic' in self.autoML_session['autoML']['eval_report'] and self.autoML_session['autoML']['eval_report']['X_preprocessing_logic'] is not None
                has_Y_preprocessing = 'Y_preprocessing_logic' in self.autoML_session['autoML']['eval_report'] and self.autoML_session['autoML']['eval_report']['Y_preprocessing_logic'] is not None
                
                if has_X_preprocessing and has_Y_preprocessing:
                    pre_col = st.columns([1, 1])
                    with pre_col[0]:
                        with st.expander('Train Preprocessing Agent Logic'):
                            st.write(self.autoML_session['autoML']['eval_report']['X_preprocessing_logic'])

                    with pre_col[1]:
                        with st.expander('Target Preprocessing Agent Logic'):
                            st.write(self.autoML_session['autoML']['eval_report']['Y_preprocessing_logic'])
                        
                
                elif has_X_preprocessing:
                    with st.expander('Train Preprocessing Agent Logic'):
                        st.write(self.autoML_session['autoML']['eval_report']['X_preprocessing_logic'])

                elif has_Y_preprocessing:
                    with st.expander('Target Preprocessing Agent Logic'):
                        st.write(self.autoML_session['autoML']['eval_report']['Y_preprocessing_logic'])
                
                # Display preprocessing HTML if available
                has_X_pipeline_html = 'X_pipeline_html' in self.autoML_session['autoML']['eval_report'] and self.autoML_session['autoML']['eval_report']['X_pipeline_html'] is not None
                has_Y_pipeline_html = 'Y_pipeline_html' in self.autoML_session['autoML']['eval_report'] and self.autoML_session['autoML']['eval_report']['Y_pipeline_html'] is not None
                
                if has_X_pipeline_html and has_Y_pipeline_html:
                    pre_cols = st.columns([1, 1])
                    with pre_cols[0]:
                        with st.expander('Train Preprocessing Steps'):
                            st.components.v1.html(self.autoML_session['autoML']['eval_report']['X_pipeline_html'],height=210,scrolling=True)
                    with pre_cols[1]:
                        with st.expander('Target Preprocessing Steps'):
                            st.components.v1.html(self.autoML_session['autoML']['eval_report']['Y_pipeline_html'],height=210,scrolling=True)
                elif has_X_pipeline_html:
                    with st.expander('Train Preprocessing Steps'):
                        st.components.v1.html(self.autoML_session['autoML']['eval_report']['X_pipeline_html'],height=210,scrolling=True)
                elif has_Y_pipeline_html:
                    with st.expander('Target Preprocessing Steps'):
                        st.components.v1.html(self.autoML_session['autoML']['eval_report']['Y_pipeline_html'],height=210,scrolling=True)
                
                st.write('\n---')
                

            st.markdown(f"<h1 style='text-align: center; font-size: 50px;'>Modeling</h1>", unsafe_allow_html=True)    

            for model_evaluation,model_info in zip(model_evaluation_reports,self.autoML_session['autoML']['eval_report']['models']):
                st.markdown(f"<h1 font-size: 25px;'>{model_info['model']}</h1>", unsafe_allow_html=True)
                if 'params_distribution' in model_info and  model_info['params_distribution'] is not None:
                    cols=2
                else:
                    cols=1
                info_cols=st.columns(cols)
                with info_cols[0]:
                    with st.expander('Reasoning'):
                        st.write(model_info['reasoning'])
                if cols==2:
                    with info_cols[1]:
                        with st.expander('Parameter Distribution'):
                            st.write(model_info['params_distribution'])
                
                if model_evaluation['problem_type']=='classification':
                    self.visualize_classification(model_evaluation,)
                elif model_evaluation['problem_type']=='regression':
                    self.visualize_regression(model_evaluation)
                with st.expander('Test Model'):
                    display_feature_form(model_info['deployment'],model_info['model'],self.autoML_session['project_id'],feature_columns=model_info['X_columns'] if 'X_columns' in model_info else None)
                    if f"{model_info['model']}_predictions" in st.session_state:
                        text=f"Prediction(s):"
                        predictions=str(st.session_state[f'{model_info["model"]}_predictions'])
                        if 'encoder_mapping' in model_info and model_info['encoder_mapping']:
                            predictions=model_info['encoder_mapping'].get(predictions, predictions)
                        text+=predictions
                        st.success(text)
                        # del st.session_state[f"{model_info['model']}_predictions"]
                        
                st.write('\n---')




    def trainPage(self,target_feature,features,model_preferences=None):
        self.placeholder.empty()
        finish=False
        eval_report=''
        with hc.HyLoader("", hc.Loaders.pulse_bars, index=[0]):
            response=automlRequests.train(self.autoML_session['project_id'],target_feature,features,self.autoML_session['autoML']['mode'][2:].strip(),model_preferences)
            for word in response:
                decoded=word.decode("utf-8")
                if "{" not in decoded and not finish:
                    status=self.status_keys.get(decoded, None)
                    if status:
                        st.toast(status,icon=":material/check_circle:")
                else:
                    finish=True
                    eval_report+=decoded
        self.autoML_session['autoML']['eval_report']=json.loads(eval_report)
        self.autoML_session['autoML']['training']=False
            
    

    def visualize_classification(self,model_evaluation):
        with st.expander('Metrics'):
            # Create a 3-column layout
            col1, col2, col3 = st.columns([1, 2, 1])  # Middle column is wider for Accuracy

            with col1:
                st.components.v1.html(visualizationRequests.render_gauge(model_evaluation['metrics']["precision"]*100, "Precision","#008000" ), height=400,)
                st.components.v1.html(visualizationRequests.render_gauge(model_evaluation['metrics']["recall"]*100, "Recall","#008000" ), height=250)

            with col2:
                # Make Accuracy larger
                st.components.v1.html(visualizationRequests.render_gauge(model_evaluation['metrics']["accuracy"]*100, "Accuracy","#008000" , size=500), height=600)
                # Add text showing correct and incorrect predictions
                if 'confusion_matrix' in model_evaluation['metrics']:
                    confusion_matrix = model_evaluation['metrics']['confusion_matrix']
                    cols=st.columns(2)
                    with cols[0]:
                        st.markdown(f"<h1 style='text-align: center; font-size: 30px;'>Correct Predictions: \n\n{confusion_matrix[0][0]+confusion_matrix[1][1]}</h1>", unsafe_allow_html=True)    

                    with cols[1]:
                        st.markdown(f"<h1 style='text-align: center; font-size: 30px;'>Incorrect Predictions: \n\n{confusion_matrix[0][1]+confusion_matrix[1][0]}</h1>", unsafe_allow_html=True)    

            with col3:
                st.components.v1.html(visualizationRequests.render_gauge(model_evaluation['metrics']["f1_score"]*100, "F1 Score","#008000"), height=400)
                st.components.v1.html(visualizationRequests.render_gauge(model_evaluation['metrics']["roc_auc"]*100, "ROC-AUC Score","#008000"), height=250)
        if 'feature_importance' in model_evaluation['metrics']:
            col_number=2
        else:
            col_number=1
        cols=st.columns(col_number)
        with cols[0]:
            if 'confusion_matrix' in model_evaluation['metrics']:
                with st.expander('Confusion Matrix'):
                    st.plotly_chart(visualizationRequests.plot_confusion_matrix(model_evaluation['metrics']['confusion_matrix']),use_container_width=True,key=f"confusion_matrix_{uuid.uuid4()}")
        if col_number==2:
            with cols[1]:
                with st.expander('Feature Importance'):
                    st.plotly_chart(visualizationRequests.plot_feature_importance(model_evaluation['metrics']['feature_importance']),use_container_width=True,key=f"feature_importance_{uuid.uuid4()}")
        cols=st.columns(2)
        with cols[1]:
            with st.expander('Precision-Recall Curve'):
                st.plotly_chart(visualizationRequests.plot_precision_recall_curve(model_evaluation['metrics']['precision_recall_curve']),use_container_width=True,key=f"precision_recall_curve_{uuid.uuid4()}")
        with cols[0]:
            with st.expander('ROC Curve'):
                st.plotly_chart(visualizationRequests.plot_roc_curve(model_evaluation['metrics']['roc_curve']),use_container_width=True,key=f"roc_curve_{uuid.uuid4()}")
            
            
    def visualize_regression(self,model_evaluation):
            pass
