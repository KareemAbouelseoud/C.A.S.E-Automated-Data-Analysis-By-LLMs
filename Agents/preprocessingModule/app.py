import streamlit as st
import pandas as pd
from pipeline import preprocess_data
import json
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Data Preprocessing Module",
    page_icon="🔧",
    layout="wide"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'preprocessing_steps' not in st.session_state:
    st.session_state.preprocessing_steps = []
if 'project_id' not in st.session_state:
    st.session_state.project_id = None
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'result' not in st.session_state:
    st.session_state.result = None
if 'iterations' not in st.session_state:
    st.session_state.iterations = 0

async def main():
    # Title
    st.title("Data Preprocessing Module")

    # File upload
    uploaded_file = st.file_uploader("Upload your dataset", type=['csv', 'xlsx'])

    if uploaded_file is not None:
        # Read the file
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)
        
        st.session_state.data = data
        
        # Display the data
        st.subheader("Dataset Preview")
        st.dataframe(data.head())
        
        # Column selection
        st.subheader("Select Column for Preprocessing")
        column = st.selectbox("Select a column", data.columns)
        
        # Preprocessing options
        st.subheader("Preprocessing Options")
        preprocessing_type = st.selectbox(
            "Select preprocessing type",
            ["Handle Missing Values", "Remove Outliers", "Change Column Type"]
        )
        
        # Parameters based on preprocessing type
        if preprocessing_type == "Handle Missing Values":
            strategy = st.selectbox(
                "Select strategy",
                ["mean", "median", "mode", "drop"]
            )
            preprocessing_task = f"handle_missing_values"
            
        elif preprocessing_type == "Remove Outliers":
            method = st.selectbox(
                "Select method",
                ["zscore", "iqr"]
            )
            threshold = st.number_input("Threshold", value=3.0)
            preprocessing_task = f"remove_outliers"
            
            
        elif preprocessing_type == "Change Column Type":
            target_type = st.selectbox(
                "Select target type",
                ["datetime", "int", "float", "string"]
            )
            format_string = None
            if target_type == "datetime":
                format_string = st.text_input("Enter datetime format (e.g. %Y-%m-%d)", "%Y-%m-%d")
            preprocessing_task = f"change_column_type"
        
        # Apply preprocessing
        if st.button("Apply Preprocessing") and not st.session_state.processing:
            st.session_state.processing = True
            st.rerun()
        
        if st.session_state.processing:
            with st.spinner("Processing..."):
                try:
                    # Run the preprocessing pipeline
                    result = await preprocess_data(project_id=st.session_state.project_id,
                                                dataframe=st.session_state.data,
                                                preprocessing_task=preprocessing_task,
                                                target_column=column,
                                                strategy=strategy)
                    
                    st.session_state.result = result
                    st.session_state.iterations += 1
                    st.session_state.processing = False
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.session_state.processing = False
                    st.rerun()
        
        if st.session_state.result is not None:
            result = st.session_state.result
            processed_df = result["preprocessed_dataframe"]
            
            # Display the result
            st.subheader("Processed Dataset")
            st.dataframe(processed_df)
            
            # Download button
            csv = processed_df.to_csv(index=False)
            st.download_button(
                label="Download processed data",
                data=csv,
                file_name="processed_data.csv",
                mime="text/csv"
            )
        else:
            if st.session_state.iterations > 0:
                st.error("Preprocessing failed. Please check the error messages.")

if __name__ == "__main__":
    asyncio.run(main())