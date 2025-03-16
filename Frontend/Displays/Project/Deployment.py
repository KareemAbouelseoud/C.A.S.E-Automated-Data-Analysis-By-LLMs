import streamlit as st
import json
def display_feature_form(features):
    # Wrap everything in a form
    with st.form("feature_form"):
        st.write("Fill out the form below:")

        # Determine number of columns to use per row
        max_cols = 3  # maximum columns per row
        num_features = len(features)
        cols = st.columns(min(num_features, max_cols))

        # Cycle through each feature and assign it to a column.
        for idx, feature in enumerate(features):
            col = cols[idx % max_cols]
            with col:
                name = feature["feature_name"]
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
                    # Call the appropriate function
                    # Ensure label parameter exists
                    if 'label' not in params:
                         params['label'] = name
                    input_funcs[input_type](**params)
                
                elif input_type in ["selectbox", "radio", "multiselect"]:
                    print(f"Processing {input_type} input")
                    print(f"Params: {params}")
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
                    
                    # Call the appropriate function
                    # Ensure label parameter exists
                    if 'label' not in params:
                         params['label'] = name
                    params['options']=options
                    selection = select_inputs[input_type](**params)
                    
                    # Handle "Other" option for all select input types
                    if (input_type != "multiselect" and selection == "Other") or \
                       (input_type == "multiselect" and "Other" in selection):
                        st.text_input(f"Enter custom value for {name}")
        
        # Form submission button
        submitted = st.form_submit_button("Submit")
        
        if submitted:
            st.write("Form submitted!")
            # Process or display the form data as needed.
