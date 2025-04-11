from io import StringIO
import streamlit as st
from Requests import insightRequests
import streamlit_nested_layout # Leave it here, dont remove it.
from streamlit_extras.stylable_container import stylable_container
from Style import buttons
import fireducks.pandas as pd


class Insights:

    def __init__(self):
        
        self.insight_session=st.session_state['user_data']['projects']['current_project']
        self.max_columns = 4
        if 'insight_session' not in  self.insight_session:
            self.insight_session['insight_session'] = {}
        
        if 'generated_insights' not in self.insight_session['insight_session']:
            self.insight_session['insight_session']['generated_insights'] = insightRequests.fetch_insights(self.insight_session['project_id'])
        
        if self.insight_session['insight_session']['generated_insights'] is None:
            st.info("Insights are being generated. Thank you for your patience")
        else:
            self.run()
    
    def run(self):
        insights=self.insight_session['insight_session']['generated_insights']
        for basic_insight in insights['insight_cards']:
            id = basic_insight['id']
            with st.expander(basic_insight['question']):
                st.markdown("<h1 style='text-align: center; font-size: 30px;'>Basic Overview</h1>", unsafe_allow_html=True)
                st.markdown("<h1 style=' font-size: 20px;'>Description</h1>", unsafe_allow_html=True)
                st.markdown(insights['insights_explanation'][id], unsafe_allow_html=True)
                cols_mr = st.columns([10.9, 0.2, 10.9])
                with cols_mr[0]:
                    st.write("\n")
                    st.write("\n")
                    st.write("\n")
                    cols = st.columns(2)
                    with cols[0]:
                        st.markdown("<h1 style=' font-size: 20px;'>Type of Insight:</h1>", unsafe_allow_html=True)
                    with cols[1]:
                        st.markdown(f"<h1 style='text-align: right;font-size: 20px;'>{basic_insight['insight_type']}</h1>", unsafe_allow_html=True)
                    
                    st.markdown("<h1 style=' font-size: 20px;'>How is this important?</h1>", unsafe_allow_html=True)
                    st.markdown(basic_insight['reason'], unsafe_allow_html=True)
                with cols_mr[1]:
                    st.html(
                                '''
                                    <div class="divider-vertical-line"></div>
                                    <style>
                                        .divider-vertical-line {
                                            border-left: 2px solid rgba(255,255,255, 0.5);
                                            height: 320px;
                                            margin: auto;
                                        }
                                    </style>
                                '''
                            )
                with cols_mr[2]:
                    st.markdown("<h1 style=' font-size: 20px;'>Insight Table</h1>", unsafe_allow_html=True)
                    df=basic_insight['resulted_df']
                    try:
                        df=pd.read_json(StringIO(df))
                        st.dataframe(df,use_container_width=True, hide_index=True,height=200)
                    except:
                        pass


                st.write("---")
                st.markdown("<h1 style='text-align: center; font-size: 30px;'>Advanced Insights</h1>", unsafe_allow_html=True)
                max_columns = min(self.max_columns,len(insights['advanced_insight_cards'][id]))
                for idx,advanced_insight in enumerate(insights['advanced_insight_cards'][id]):
                    if idx % max_columns == 0:
                        columns = st.columns(max_columns)
                  
                    with columns[idx % max_columns]:  # Add project to the appropriate column
                        st.markdown(buttons.project_button.format(first=idx,second=idx) ,unsafe_allow_html=True)
                        st.markdown(f'<span id="button-after-{idx}"></span>', unsafe_allow_html=True)
                        placeholder = st.empty()
                        placeholder.button(f"{advanced_insight[1]['question']}",on_click=self.more_info,args=[advanced_insight],key=advanced_insight[1]['id'])
    
    @st.dialog("Advanced Insights", width='large')
    def more_info(self,advanced_insight):
        st.markdown(advanced_insight[1]['question'])
        st.write('---')
        st.write("The Answer Should be Here but there is no explanation for advanced insight...")
        st.markdown("<h1 style=' font-size: 20px;'>How is this important?</h1>", unsafe_allow_html=True)
        st.markdown(advanced_insight[1]['reason'], unsafe_allow_html=True)
        cols_mr = st.columns(2)
        with cols_mr[0]:
            st.markdown("<h1 style=' font-size: 20px;'>Insight Table</h1>", unsafe_allow_html=True)
            df=pd.read_json(StringIO(advanced_insight[1]['resulted_df']))
            st.dataframe(df,use_container_width=True, hide_index=True,height=200)
        with cols_mr[1]:
            st.write("\n")
            st.write("\n")
            st.write("\n")
            st.write("\n")
            with st.expander("Filters used"):
                for filter in advanced_insight[0]['filters']:
                    st.write(f"{filter[0]} is equal to {filter[1]}")
            with st.expander("Columns Behind the Insight"):
                for idx,column in enumerate(advanced_insight[1]['used_columns']):
                    st.write(f"{idx+1}. {column}")
            






        
