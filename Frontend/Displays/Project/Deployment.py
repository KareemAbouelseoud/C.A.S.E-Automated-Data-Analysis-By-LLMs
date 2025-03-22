import streamlit as st
import json
import uuid
import hydralit_components as hc
from Requests import automlRequests

def display_feature_form(features, model_name, project_id,feature_columns=None,encoder_mapping=None):
    # Wrap everything in a form
    with st.form(key=f"feature_form_{model_name}"):
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
    if f"FormSubmitter:feature_form_{model_name}-Submit" in st.session_state and st.session_state[f'FormSubmitter:feature_form_{model_name}-Submit']:
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

            predictions=submitted(model_name, project_id,feature_columns,feature_values)
            if isinstance(predictions,list):
                    print(model_name)
                    st.session_state[f"{model_name}_predictions"]=predictions[0]
            else:
                st.toast("Failed to predict", icon=":material/error:")
                    
            
    return None

    
def submitted( model_name, project_id,feature_columns,feature_values): 
    predictions = automlRequests.predict(project_id, model_name, [feature_values],feature_columns)
    return predictions