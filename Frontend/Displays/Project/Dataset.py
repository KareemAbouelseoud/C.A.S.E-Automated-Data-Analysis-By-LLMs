import streamlit as st
from Requests import databaseRequests,visualizationRequests
import plotly.express as px
import plotly.io as pio
import streamlit_nested_layout # Leave it here, dont remove it.

dataset_session=st.session_state['user_data']['projects']['current_project']
class Dataset:
    def __init__(self):
        if 'dataset_session' not in dataset_session:
            dataset_session['dataset_session']={}
            dataset_session['dataset_session']['Insights']=False
            dataset_session['dataset_session']['raw_data_report']=databaseRequests.fetch_datareport(dataset_session['project_id'])
            #NOTE: CHANGE THIS TO FETCH PROCESSED DATA REPORT
            dataset_session['dataset_session']['processed_data_report']=databaseRequests.fetch_datareport(dataset_session['project_id'])

        self.run()

    def InsightsShown(self):
        dataset_session['dataset_session']['Insights']=True
    def run(self):
        if dataset_session['dataset_mode']=='Raw':
            data_report=dataset_session['dataset_session']['raw_data_report']
        else:
            data_report=dataset_session['dataset_session']['processed_data_report']
        st.markdown("""
        <style>
    .stExpander {
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
                    font-size: 50px;
                    cursor: pointer;
                    padding: 0px;
                    justify-content: center;
                    align-items: center;
                    margin-bottom: 5px; /* Adds vertical space if wrapping occurs */
                    transition: box-shadow 0.3s ease; /* Smooth transition */
                    border: none; /* Explicitly remove any border */
    }
    .stExpander:hover {
        box-shadow: 
            0 0 10px rgba(255, 255, 255, 0.6), 
            0 0 20px rgba(255, 255, 255, 0.5), 
            0 0 30px rgba(255, 255, 255, 1); /* Stronger glow on hover */
    }
    .st-emotion-cache-8s6zi3.enj44ev3:hover {
        color: white;
        text-shadow: 
            0 0 10px rgba(255, 255, 255, 0.6), 
            0 0 20px rgba(255, 255, 255, 0.5), 
            0 0 30px rgba(255, 255, 255, 1); /* Stronger glow on hover */
    }
    .e14lo1l1.st-emotion-cache-1b2ybts.ex0cdmw0:hover svg {
        fill: white;
        transition: fill 0.3s ease; /* Smooth transition */
    }
</style>
""",unsafe_allow_html=True)
        cols=st.columns(2)
        with cols[0]:
            with st.expander("Dataset Description"):
                        st.write(data_report['dataset_description'])
        with cols[1]:
                with st.expander("Statistical Representation"):
                    overview=data_report['dataset_profile']['overview']
                    st.write(f"Number of Rows: {overview['n']}")
                    st.write(f"Number of Features: {overview['n_var']}")
                    try:
                        plot_data=visualizationRequests.plot_column_types(dataset_session['project_id'])
                         
                        with st.expander("Column Types"):
                            if plot_data:
                                # Convert the JSON string to a plotly figure
                                fig = pio.from_json(plot_data)
                                # Display the plot in Streamlit
                                st.plotly_chart(fig, use_container_width=True)

                    except:
                         print('Error in visualizing column types')
                        
                    st.write(f"Number of Missing Cells: {overview['n_cells_missing']}")
                    st.write(f"Number of Duplicate Rows: {overview['n_duplicates']}")

        st.write('\n\n\n')
        st.markdown("<h1 style='text-align: center; font-size: 50px;'>Feature Overview</h1>", unsafe_allow_html=True)  
        st.write('---')  

            
        
                