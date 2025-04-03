import streamlit as st
from Requests import insightRequests
import streamlit_nested_layout # Leave it here, dont remove it.
from streamlit_extras.stylable_container import stylable_container
from Style import buttons
import fireducks.pandas as pd


class Insights:

    def __init__(self):
        
        self.insight_session=st.session_state['user_data']['projects']['current_project']
        self.max_columns = 3
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
                st.markdown("<h1 style=' font-size: 20px;'>How is this important?</h1>", unsafe_allow_html=True)
                st.markdown(basic_insight['reason'], unsafe_allow_html=True)

                st.markdown("<h1 style=' font-size: 20px;'>Table</h1>", unsafe_allow_html=True)
                df=basic_insight['resulted_df']
                try:
                    df=pd.read_json(df)
                    st.write(df)
                except:
                    pass


                st.write("---")
                st.markdown("<h1 style='text-align: center; font-size: 30px;'>Advanced Insights</h1>", unsafe_allow_html=True)
                for idx,advanced_insight in enumerate(insights['advanced_insight_cards'][id]):
                    if idx % self.max_columns == 0:
                        columns = st.columns(self.max_columns)
                
                    with columns[idx % self.max_columns]:  # Add project to the appropriate column
                        st.markdown(buttons.project_button.format(first=idx,second=idx) ,unsafe_allow_html=True)
                        st.markdown(f'<span id="button-after-{idx}"></span>', unsafe_allow_html=True)
                        placeholder = st.empty()
                        placeholder.button(f"{advanced_insight[1]['question']}",on_click=self.more_info,args=[advanced_insight],key=advanced_insight[1]['id'])
    
    @st.dialog("Advanced Insights", width='large')
    def more_info(self,advanced_insight):
        st.header(advanced_insight[1]['insight_type'])
        st.markdown(advanced_insight[1]['question'])

        
