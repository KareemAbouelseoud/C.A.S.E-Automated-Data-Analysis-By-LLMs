import time
import streamlit as st
import sys
import uuid
import os
import json
import plotly.graph_objects as go
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from Requests import chatbotRequests,visualizationRequests
from dataModels.visualization import ChatViz
from streamlit_cookies_controller import CookieController
from Style import buttons,chatbot
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from Deployment import submitted

try:
    controller=CookieController()
except:
    pass

class Chatbot:
    def __init__(self):  

        self.status_keys={
            'splitter_node':"Finished Splitting",
            "preprocessing_node":"Finished Preprocessing",
            "model_evaluator_node":"Finished Evaluation",
            "model_trainer_node":"Finished Training",
            "model_selector_node":"Finished Model Selection",
            "model_tuner_node":"Finished Tuning",
        }
        self.chatbot_session=st.session_state['user_data']['projects']['current_project']
        self.recommender_placeholder=None
        if 'chatbot' not in self.chatbot_session:
            self.chatbot_session['chatbot']={}
        self.chatbot_session['chatbot']['refreshed']=True
        self.logo_path = "/app/static/ZEUS.png"
        st.markdown(chatbot.text_box,unsafe_allow_html=True)
        st.markdown(buttons.rounded_button, unsafe_allow_html=True)
        
        self.initialize_chat_history()
        self.setup_app_interface()

    
    def backtooverview(self):
        st.session_state['user_data']['projects']['current_project']={}
            
    
    def setup_app_interface(self):
        """
        Sets up the main interface of the Zeus application, including:
        - Displaying the title and warnings.
        - Setting up the buttons and event handlers.
        - Displaying the chat history.
        """

        st.markdown("<h1 style='text-align: center; font-size: 100px;'>ZEUS</h1>", unsafe_allow_html=True)
        with st.columns(19)[-1]:
            st.markdown(buttons.back_button,unsafe_allow_html=True)
            st.markdown(f'<span id="button-back"></span>', unsafe_allow_html=True)
            st.button('',icon=":material/arrow_back:",on_click=self.backtooverview,key=f"back_{uuid.uuid4()}")

        st.markdown(chatbot.assistant_messages, unsafe_allow_html=True)
        st.markdown(chatbot.user_messages, unsafe_allow_html=True)

        st.sidebar.markdown(buttons.sidebar_button,unsafe_allow_html=True,)
        st.sidebar.markdown('<span id="button-sidebar"></span>', unsafe_allow_html=True)
        if st.sidebar.button('Clear History'):
            self.chatbot_session['thread_id']=chatbotRequests.clear_history(self.chatbot_session['project_id'],controller.get("user_id"))
            self.chatbot_session['chatbot']['messages']=[]
            self.chatbot_session['chatbot']['new']=None
            if 'recommendation' in self.chatbot_session['chatbot']:
                self.chatbot_session['chatbot']['recommendation']=None
            self.initialize_chat_history()
            st.rerun()
        self.display_chat_history()
        self.accept_user_input()

        if self.chatbot_session['chatbot']['recommendations']!=None:
            self.recommend()
        
   

    def display_chat_history(self):
        """
        Displays the conversation history, showing each message sent by the user and the assistant.
        """
        for message in self.chatbot_session['chatbot']['messages']:
            if message['role'] == 'user':
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            elif message['role'] == 'assistant':
                with st.chat_message(message["role"],avatar=self.logo_path):
                    st.markdown(message["content"])
            if message['role'] == 'visualizer':
                with st.chat_message(message["role"],avatar='📈'):
                    for visual in message['content']:
                        self.get_visuals(visual)

    def save_plot(self,fig):        
        pass  
    
    
    def get_visuals(self, visuals,save=False):
        print(visuals)
        if isinstance(visuals, list):
            for v in visuals:
                self.get_visuals(v,save)
        if isinstance(visuals, str):
            print("STRING")
            visuals = json.loads(visuals)
        try:
            if isinstance(visuals,dict):
                if 'data' in visuals and 'layout' in visuals:
                    fig = go.Figure(data=visuals['data'], layout=visuals['layout'])
                    st.plotly_chart(fig)
                    st.button("Save Plot in Dashboard", on_click=self.save_plot, args=[fig], key=f"plot_{str(uuid.uuid4())}")
                elif 'model' in visuals:
                    if visuals['problem_type'] == 'classification':
                        self.visualize_classification(visuals)
                    elif visuals['problem_type'] == 'regression':
                        self.visualize_regression(visuals)
                elif 'deployment' in visuals:
                    model_names= list(visuals['deployment'].keys())
                    key=f"model_select_{uuid.uuid4()}"
                    st.selectbox("Select Model",model_names,key=key)                        
                    self.display_feature_form(visuals['deployment'],key)   
                # Convert the visuals to serializable format before saving
                if save:
                    serializable_visuals = visualizationRequests.make_serializable(visuals)
                    new_chat_viz = ChatViz(viz=[serializable_visuals])
                    visualizationRequests.save_chat_visualizations(self.chatbot_session['project_id'], new_chat_viz)
                    self.chatbot_session['chatbot']['messages'].append({'role':'visualizer','content':[visuals]})

        except Exception as e:
            raise e
            print(f"Error in get_visuals: {str(e)}")
            if isinstance(visuals, dict):
                for key, value in visuals.items():
                    if isinstance(value, dict):
                        self.get_visuals(value,save)
                    elif isinstance(value, list):
                        for v in value:
                            self.get_visuals(v,save)
            else:
                if isinstance(visuals, str):
                    if visuals == None:
                        return
                    self.get_visuals(json.loads(visuals),save)
                

        
    def accept_user_input(self):
        """
        Accepts user input and processes the query. It generates responses and handles recommendations.
        """
        if prompt := st.chat_input("Enter your query:"):
            self.chatbot_session['chatbot']['new']=False
            sanitized_input = self.sanitize_user_input(prompt)
            with st.chat_message("user"):
                st.markdown(prompt)

            self.chatbot_session['chatbot']['messages'].append({"role": "user", "content": sanitized_input,})   
            self.generate_response(sanitized_input)
            self.recommend(sanitized_input)
            chatbotRequests.update_user_st_history(str(self.chatbot_session['project_id']),self.chatbot_session['chatbot']['messages'],controller.get("user_id"))

                

        if 'recommendation' in self.chatbot_session['chatbot']:
            with st.chat_message("user"):
                st.markdown(self.chatbot_session['chatbot']['recommendation'])
            self.chatbot_session['chatbot']['new']=False

            self.chatbot_session['chatbot']['messages'].append({"role": "user", "content": self.chatbot_session['chatbot']['recommendation']})
            self.generate_response(self.chatbot_session['chatbot']['recommendation'])
            chatbotRequests.update_user_st_history(str(self.chatbot_session['project_id']),self.chatbot_session['chatbot']['messages'],controller.get("user_id"))
            self.recommend(self.chatbot_session['chatbot']['recommendation'])
            del self.chatbot_session['chatbot']['recommendation']


        if len(self.chatbot_session['chatbot']['messages'])==1:
            self.recommend()


    def generate_response(self, user_input):
        """
        Generates a response from the assistant using the chat model (Claude).
        """
        print("Before Generating Response",self.chatbot_session['chatbot']['messages'])
        with st.spinner("Generating response..."):
            try:
                response =chatbotRequests.chat(user_input,project_id=self.chatbot_session['project_id'],thread_id=self.chatbot_session['thread_id'])
                self.display_assistant_response(response)

            except Exception as e:
                # raise e
                error_message = f"An error occurred: {str(e)}"
                st.warning(error_message)
                self.display_assistant_response("Sorry,I don't have this functionality, Can't provide an answer.\n Ask another question please.",stream=False)

    def sanitize_user_input(self, user_input):
        # Remove any potentially harmful characters or sequences        
        sanitized = user_input.replace('<', '&lt;').replace('>', '&gt;')
        # Limit input length
        max_length = 500
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            st.warning(f"Input truncated to {max_length} characters.")
        return sanitized

    def display_assistant_response(self, response,stream=True):
        """
        Display the output of claude
        """

        with st.chat_message("assistant", avatar=self.logo_path):
            visuals=[]
            if stream:
                escaped_response=st.write_stream((self.stream_ans(response,visuals)))
            else:
                escaped_response=response
                st.write(escaped_response)
        self.chatbot_session['chatbot']['messages'].append({"role": "assistant", "content": escaped_response})

        if len(visuals)>0:
            with st.chat_message('visualizer',avatar='📈'):
                for visual in visuals:
                    self.get_visuals(visual,save=True)
    


    def initialize_chat_history(self):
        """
        Called at the beginning of any chat
        """ 
        
        if "messages" not in self.chatbot_session['chatbot'] or self.chatbot_session['chatbot']['messages']==[]:
            self.chatbot_session['chatbot']['conv_change']=''
            self.chatbot_session['chatbot']['new']=True
            self.chatbot_session['chatbot']['Bot_Clicked']=False
            first_message = "Good Morning. I am Zeus, a Smart Assistant for C.A.S.E. How can I assist you today?"
            self.chatbot_session['chatbot']['messages']=[{"role": "assistant", "content": first_message}]
            self.chatbot_session['chatbot']['messages'].extend(chatbotRequests.get_streamlit_chat_history(self.chatbot_session['project_id']))
            self.chatbot_session['chatbot']['recommendations']=None
    def stream_ans(self,response,visuals):
        """
    Response of claude is streamed so this function handles it
        """
        tag_flag = False
        buffer = ""
        try:
            for word in response:
                word = word.decode('utf-8')
                buffer += word
                try:
                    if buffer[0] == '{' or buffer[0] == '[':
                        json_obj = json.loads(buffer)
                        if isinstance(json_obj, list):
                            visuals.append(json_obj)
                            buffer = ""
                        elif isinstance(json_obj, dict):
                            if 'data' in json_obj and 'layout' in json_obj or 'deployment' in json_obj:
                                visuals.append(json_obj)
                                buffer = ""
                            elif 'status' in json_obj:
                                status = json_obj['status']
                                status=self.status_keys.get(status, None)
                                if status:
                                    st.toast(status,icon=":material/check_circle:")
                                buffer = ""
                    else:
                        for w in buffer:
                            if w == '<':
                                tag_flag = True
                            elif w == '>':
                                tag_flag = False
                            if not tag_flag:

                                w = w.replace("$", "\$")
                                yield w
                                time.sleep(0.007)
                        buffer = ""
                except json.JSONDecodeError:
                    # Continue accumulating chunks until a complete JSON object is formed
                    continue
        except Exception as e:
            raise e
        

    def recommend_response(self,prompt):
        """
        Function Helper for recommend()
        """
        self.chatbot_session['chatbot']['recommendation']=prompt
        self.recommender_placeholder.empty()

    def recommend(self,prompt=None):
        """
        Provides personalized prompt recommendations based on the user's input.
        """
        if prompt:
                recommendations=chatbotRequests.recommender([{'role':'user','content':"Don't answer the user prompt, just choose the prompts and generate them in a PYTHON LIST of strings as requested in the system instruction. Give different SIMPLE functionality than what the user and you have already gave. You are restricted to the prompts listed in the system instruction do not get creative. The stocks that you can use to generate the prompts are from the list given to you use them:\n"+prompt}],self.chatbot_session['project_id'],self.chatbot_session['thread_id'])
        
        elif self.chatbot_session['chatbot']['recommendations']!=None:
            recommendations=self.chatbot_session['chatbot']['recommendations']
            if not self.chatbot_session['chatbot']['refreshed']:
                return
        
        else:
            recommendations=['What are your features',"Suggest interesting visualizations","Find outliers in this dataset and explain their impact","Create a Machine Learning Model","Summarize key insights from this dataset"]
        
        self.recommender_placeholder = st.empty()
        with self.recommender_placeholder.container(border=False):
            for i in range(len(recommendations)):
                if i>6:
                    break
                if recommendations[i]!=' ':
                    recommendations[i]=recommendations[i].replace('"','')
                    st.button(recommendations[i],on_click=self.recommend_response,args=[recommendations[i]])
            self.chatbot_session['chatbot']['recommendations']=recommendations
            self.chatbot_session['chatbot']['refreshed']=False
            
    
    def visualize_classification(self,model_evaluation):
        with st.expander(list(model_evaluation.keys())[0]):
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
    
    def display_feature_form(self,deployment_data,key):
        # Wrap everything in a form
        model_name=st.session_state[key]
        features=deployment_data[model_name]['features']
        feature_columns=deployment_data[model_name]['feature_columns']
        if 'encoder_mapping' in deployment_data[model_name]:
            encoder_mapping=deployment_data[model_name]['encoder_mapping']
        else:
            encoder_mapping=None
        print(model_name,features,feature_columns)
        with st.form(key=f"chatbot_form_{model_name}"):
            st.write("Fill out the form below:")
            # Determine number of columns to use per row
            max_cols = 3  # maximum columns per row
            num_features = len(features)
            cols = st.columns(min(num_features, max_cols))
            
            names=[]

            # Cycle through each feature and assign it to a column.
            for idx, feature in enumerate(features):
                col = cols[idx % max_cols]
                with col:
                    name = feature["feature_name"]
                    names.append(name)
                    input_type = feature["streamlit_input"]

                    # Dictionary mapping for different input types
                    input_funcs = {
                        "number_input": st.number_input,
                        "text_input": st.text_input,
                        "text_area": st.text_area,
                        "slider": st.slider,
                        "checkbox": st.checkbox
                    }
                    try:
                        params = json.loads(feature["streamlit_parameters"])
                    except json.JSONDecodeError:
                        params = {}
                    
                    # If input_type is in the dictionary, call the corresponding function
                    if input_type in input_funcs:
                        # Ensure label parameter exists
                        if 'label' not in params:
                            params['label'] = name
                        # Store the returned value
                        input_funcs[input_type](**params,key=f"{model_name}_{name}")
                    
                    elif input_type in ["selectbox", "radio", "multiselect"]:
                        # Retrieve options for categorical inputs
                        options = params.get("options", [])
                        if "Other" not in options:
                            options.append("Other")
                        
                        # Create mapping for different select inputs
                        select_inputs = {
                            "selectbox": st.selectbox,
                            "radio": st.radio,
                            "multiselect": st.multiselect
                        }
                        
                        # Ensure label parameter exists
                        if 'label' not in params:
                            params['label'] = name
                        params['options'] = options
                        # Store the returned value
                        selection = select_inputs[input_type](**params,key=f"{model_name}_{name}")
            
            # Form submission button
            st.form_submit_button("Submit")
        # print(st.session_state)
        if f"FormSubmitter:chatbot_form_{model_name}-Submit" in st.session_state and st.session_state[f'FormSubmitter:chatbot_form_{model_name}-Submit']:
            with st.spinner("Predicting..."):
                # Create a copy of session state keys to iterate over
                session_keys = list(st.session_state.keys())
                
                # Initialize dictionary to store feature values
                feature_values = {}
                
                # Iterate over the copied keys
                for key in session_keys:
                    # Check if key corresponds to a feature input
                    if key.startswith(f"{model_name}_"):
                        # Extract feature name (remove model_name_ prefix)
                        feature_name = key[len(f"{model_name}_"):]
                        if feature_name in names:
                            # Store the value in our dictionary
                            feature_values[feature_name] = st.session_state[key]
                            # Delete the key from session state after capturing its value
                            del st.session_state[key]

                predictions=submitted(model_name, self.chatbot_session['project_id'],feature_columns,feature_values)
                if isinstance(predictions,list):
                        print(model_name)
                        text=f"Prediction(s):"
                        if encoder_mapping:
                            predictions=encoder_mapping.get(predictions[0], predictions[0])
                        else:
                            predictions=predictions[0]
                        text+=str(predictions)
                        st.success(text)
                else:
                    st.error("This model is outdated, please access recent models in the AutoML tab or ask ZEUS.", icon=":material/error:")
                        
                
        return None
if 'project_id' in st.session_state['user_data']['projects']['current_project'] and st.session_state['user_data']['projects']['current_project']['project_id']!=None:
    Chatbot()



