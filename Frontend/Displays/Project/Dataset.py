import streamlit as st
from Requests import databaseRequests,visualizationRequests
import plotly.io as pio
import streamlit_nested_layout # Leave it here, dont remove it.
import hydralit_components as hc
dataset_session=st.session_state['user_data']['projects']['current_project']
class Dataset:
    def __init__(self):
        if 'dataset_session' not in dataset_session:
            with hc.HyLoader("",hc.Loaders.pretty_loaders,index=[3]):
                dataset_session['dataset_session']={}
                dataset_session['dataset_session']['Insights']=False
                #NOTE: Only fetch a certain number of rows for the dataset description to avoid large payloads
                dataset_session['dataset_session']['raw_data_report']=databaseRequests.fetch_datareport(dataset_session['project_id'])
                dataset_session['dataset_session']['raw_dataset']=databaseRequests.fetch_dataset(dataset_session['project_id'])
                #NOTE: CHANGE THIS TO FETCH PROCESSED DATA REPORT
                dataset_session['dataset_session']['processed_data_report']=databaseRequests.fetch_datareport(dataset_session['project_id'])
                dataset_session['dataset_session']['processed_dataset']=databaseRequests.fetch_dataset(dataset_session['project_id'])


        self.viz_types={
            visualizationRequests.plot_missing_column.__name__:visualizationRequests.plot_missing_column,
            visualizationRequests.plot_distribution.__name__:visualizationRequests.plot_distribution,
            visualizationRequests.plot_top_n.__name__:visualizationRequests.plot_top_n,
            visualizationRequests.plot_word_cloud.__name__:visualizationRequests.plot_word_cloud
        }
        self.viz_names={
            visualizationRequests.plot_missing_column.__name__:'Missing Values',
            visualizationRequests.plot_distribution.__name__:'Distribution',
            visualizationRequests.plot_top_n.__name__:'Text Frequency',
            visualizationRequests.plot_word_cloud.__name__:'Word Cloud'
        }
        self.viz_options={
            'Categorical':
             {
                 visualizationRequests.plot_missing_column.__name__:['Pie Chart','Bar Chart'],
                 visualizationRequests.plot_distribution.__name__:['Bar Chart','Pie Chart']
             },
             'Numeric':
             {
                 visualizationRequests.plot_missing_column.__name__:['Pie Chart','Bar Chart'],
                 visualizationRequests.plot_distribution.__name__:['Histogram','Box Plot','Violin Plot','Density Plot']
             },
            'Text':
            {
                visualizationRequests.plot_missing_column.__name__:['Pie Chart','Bar Chart'],
                visualizationRequests.plot_top_n.__name__:['Word Frequency','Character Frequency']
            }
            
            
        }
        self.run()

    def InsightsShown(self):
        dataset_session['dataset_session']['Insights']=True
    def run(self):
        with hc.HyLoader("",hc.Loaders.pretty_loaders,index=[3]):

            if dataset_session['dataset_mode']=='Raw':
                data_report=dataset_session['dataset_session']['raw_data_report']
                dataset=dataset_session['dataset_session']['raw_dataset']
            else:
                data_report=dataset_session['dataset_session']['processed_data_report']
                dataset=dataset_session['dataset_session']['processed_dataset']
            with st.container(border=True):
                    st.dataframe(dataset,use_container_width=True,)
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

        st.write('---')
        st.write('\n\n\n')
        st.markdown("<h1 style='text-align: center; font-size: 50px;'>Feature Overview</h1>", unsafe_allow_html=True)  
        for feature_name,feature_details in data_report['dataset_profile']['variables'].items():
            with hc.HyLoader("",hc.Loaders.pretty_loaders,index=[3]):
                self.show_feature(feature_name,feature_details)
                st.write('---')
    
    def show_feature(self,feature_name,feature_details):

        st.markdown(f"<h1 font-size: 30px;'>{feature_name}</h1>", unsafe_allow_html=True)
        if feature_details['type']=='Categorical':
            self.show_categorical(feature_details)
        elif feature_details['type']=='Numeric':
            self.show_numeric(feature_details)
        elif feature_details['type']=='Text':
            self.show_text(feature_details)

        self.visualize(feature_name,feature_details)

    def show_numeric(self,feature_details):
        columns=st.columns(4)
        with columns[0]:
            with st.expander("Basic Information"):
                st.write(f"**Data Type: {feature_details['type']}**")
                st.write(f"**Count: {feature_details['count']}**")
                if feature_details['ordering']:
                    st.write("**This Feature is Ordered**")
                else:
                    st.write('**This Feature is Not Ordered**')

        with columns[1]:
            with st.expander('Data Quality'):
                st.write(f"**Uniquness:**")
                distinct_cols=st.columns(2)
                with distinct_cols[0]:
                    st.write(f"**Number of Distinct Values: {feature_details['n_distinct']}**")

                with distinct_cols[1]:
                    st.write(f"**Percentage of Distinct Values: {feature_details['p_distinct']*100:.1f}%**")
                st.write("---")

                    
                st.write(f"\n**Missing Values:**")
                missing_cols=st.columns(2)
                with missing_cols[0]:
                    st.write(f"**Number of Missing Values: {feature_details['n_missing']}**")
                
                with missing_cols[1]:
                    st.write(f"**Percentage of Missing Values: {feature_details['p_missing']*100:.1f}%**")
                
                st.write("---")

                if feature_details['n_zeros']!=0:
                    st.write("\n**Zero Values:**")
                    zero_cols=st.columns(2)
                    with zero_cols[0]:
                        st.write(f"**Number of Zero Values: {feature_details['n_zeros']}**")
                    with zero_cols[1]:
                        st.write(f"**Percentage of Zero Values: {feature_details['p_zeros']*100:.1f}%**")
                    st.write("---")
                if (feature_details['n_negative'])!=0:
                    st.write("\n**Negative Values:**")
                    negative_cols=st.columns(2)
                    with negative_cols[0]:
                        st.write(f"**Number of Negative Values: {feature_details['n_negative']}**")
                    with negative_cols[1]:
                        st.write(f"**Percentage of Negative Values: {feature_details['p_negative']*100:.1f}%**")
                    st.write("---")

                if feature_details['n_infinite']!=0:
                    st.write("\n**Infinite Values:**")
                    infinite_cols=st.columns(2)
                    with infinite_cols[0]:
                        st.write(f"**Number of Infinite Values: {feature_details['n_infinite']}**")
                    with infinite_cols[1]:
                        st.write(f"**Percentage of Infinite Values: {feature_details['p_infinite']*100:.1f}%**")

        with columns[2]:
            with st.expander('Numerical Statistics'):
                st.write(f"**Mean: {feature_details['mean']:.1f}**")
                st.write(f"**Standard Deviation: {feature_details['std']:.1f}**")
                st.write(f"**Variance: {feature_details['variance']:.1f}**")
                st.write(f"**Minimum: {feature_details['min']:.1f}**")
                st.write(f"**Maximum: {feature_details['max']:.1f}**")
                st.write(f"**Sum: {feature_details['sum']:.1f}**")
                st.write(f"**Median: {feature_details['50%']:.1f}**")
                st.write(f"**Range: {feature_details['range']:.1f}**")
        
        with columns[3]:
            with st.expander("Advanced Statistics"):
                st.write(f"**Skewness: {feature_details['skewness']:.1f}**")
                st.write(f"**Kurtosis: {feature_details['kurtosis']:.1f}**")
                st.write(f"**Interquartile Range (IQR): {feature_details['iqr']:.1f}**")
                st.write(f"**Coefficient of Variation (CV): {feature_details['cv']:.1f}**")
                st.write(f"**Mean Absolute Deviation (MAD): {feature_details['mad']:.1f}**")
                with st.expander("Quantiles"):
                        st.write(f"**Q1:** {feature_details['25%']:.1f}")
                        st.write(f"**Q2:** {feature_details['50%']:.1f}")
                        st.write(f"**Q3:** {feature_details['75%']:.1f}")
                with st.expander("**Chi Squared**"):
                        st.write(f"**Statistic:** {feature_details['chi_squared']['statistic']}")
                        st.write(f"**P Value:** {feature_details['chi_squared']['pvalue']}")
                
    def show_categorical(self,feature_details):
        columns=st.columns(3)
        with columns[0]:
            with st.expander("Basic Information"):
                st.write(f"**Data Type: {feature_details['type']}**")
                st.write(f"**Count: {feature_details['count']}**")
        with columns[1]:
            with st.expander('Data Quality'):
                st.write(f"\n**Missing Values:**")
                missing_cols=st.columns(2)
                with missing_cols[0]:
                    st.write(f"**Number of Missing Values: {feature_details['n_missing']}**")
                
                with missing_cols[1]:
                    st.write(f"**Percentage of Missing Values: {feature_details['p_missing']*100:.1f}%**")
        with columns[2]:
            with st.expander('Categorical Statistics'):
                st.write(f"**Imbalance: {feature_details['imbalance']*100:.1f}%**")
                with st.expander("Distribution"):
                    for key,value in feature_details['word_counts'].items():
                        st.write(f'**"{key}" \: {value}**')
                with st.expander("**Chi Squared**"):
                        st.write(f"**Statistic:** {feature_details['chi_squared']['statistic']}")
                        st.write(f"**P Value:** {feature_details['chi_squared']['pvalue']}")

    def show_text(self,feature_details):
        columns=st.columns(4)
        with columns[0]:
            with st.expander("Basic Information"):
                st.write(f"**Data Type: {feature_details['type']}**")
                st.write(f"**Count: {feature_details['count']}**")
                if feature_details['ordering']:
                    st.write("**This Feature is Ordered**")
                else:
                    st.write('**This Feature is Not Ordered**')

        with columns[1]:
            with st.expander('Data Quality'):
                st.write(f"**Uniquness:**")
                distinct_cols=st.columns(2)
                with distinct_cols[0]:
                    st.write(f"**Number of Distinct Values: {feature_details['n_distinct']}**")

                with distinct_cols[1]:
                    st.write(f"**Percentage of Distinct Values: {feature_details['p_distinct']*100:.1f}%**")
                st.write("---")
                st.write(f"\n**Missing Values:**")
                missing_cols=st.columns(2)
                with missing_cols[0]:
                    st.write(f"**Number of Missing Values: {feature_details['n_missing']}**")
                
                with missing_cols[1]:
                    st.write(f"**Percentage of Missing Values: {feature_details['p_missing']*100:.1f}%**")
                
        with columns[2]:
            with st.expander('Textual Summary'):
                st.write(f"**Minimum Length: {feature_details['min_length']}**")
                st.write(f"**Maximum Length: {feature_details['max_length']}**")
                st.write(f"**Median Length: {feature_details['median_length']}%**")
                st.write(f"**Median Length: {feature_details['mean_length']}**")
                st.write(f"Number of Unique Characters Used: {feature_details['n_characters_distinct']}**")
        
        with columns[3]:
            with st.expander("Advanced Statistics"):
                with st.expander("First Values"):
                    for key,value in feature_details['first_rows'].items():
                        st.write(f'**"{value}"**')
                with st.expander("Most Common Characters"):
                    count=0
                    for key,value in feature_details['character_counts'].items():
                        st.write(f'**"{key}" \: {value}**')
                        count+=1
                        if count==4:
                            break
                with st.expander("Most Common Words"):
                    count=0
                    for key,value in feature_details['word_counts'].items():
                        st.write(f'**"{key}" \: {value}**')
                        count+=1
                        if count==4:
                            break

    def visualize(self,feature_name,feature_details):
        types=self.check_visualizations(feature_details)
        if len(types)!=0:
            with st.expander("Visualizations"):
                columns=st.columns(int(len(types)))
                for idx,viz_type in enumerate(types):
                    with columns[idx]:
                        with st.expander(self.viz_names[viz_type]):
                            
                            viz_options=self.viz_options[feature_details['type']].get(viz_type,[])
                            
                            if viz_options:
                                op=st.selectbox('Select Visualization Type',viz_options,key=f'{feature_name}_{viz_type}')
                                viz=self.viz_types[viz_type](project_id=dataset_session['project_id'],column_name=feature_name,plot_type=op)
                            else:
                                viz=self.viz_types[viz_type](project_id=dataset_session['project_id'],column_name=feature_name)
                            
                            if viz:
                                fig = pio.from_json(viz)
                                st.plotly_chart(fig, use_container_width=True)
                     
    def check_visualizations(self,feature_details):
        viz_list=[]
        if feature_details['type']=='Categorical':
            if feature_details['n_missing']>0:
                viz_list.append(visualizationRequests.plot_missing_column.__name__)
            viz_list.append(visualizationRequests.plot_distribution.__name__)
        elif feature_details['type']=='Numeric':
            if feature_details['n_missing']>0:
                viz_list.append(visualizationRequests.plot_missing_column.__name__)
            viz_list.append(visualizationRequests.plot_distribution.__name__)
        elif feature_details['type']=='Text':
            if feature_details['n_missing']>0:
                viz_list.append(visualizationRequests.plot_missing_column.__name__)
            viz_list.append(visualizationRequests.plot_top_n.__name__)
            viz_list.append(visualizationRequests.plot_word_cloud.__name__)
        return viz_list
        
        
        
        
