import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .Dashboard import Dashboard
from streamlit_elements import mui, plotly
import plotly.express as px
import numpy as np

def dynamic_color_map(df, column_name):
    unique_values = df[column_name].unique()
    colors = px.colors.qualitative.Set1  # You can choose any color palette
    color_map = {value: colors[i % len(colors)] for i, value in enumerate(unique_values)}
    return color_map



def hex_to_rgb(hex_color):
        # Remove the hash (#) at the start if it's there
        hex_color = hex_color.lstrip('#')   

        # Convert the hex values to integers
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        # Return as an RGB string
        return f"rgb({rgb[0]+10}, {rgb[1]+10}, {rgb[2]+10})"

class Plots(Dashboard.Item):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.type=kwargs['type']
        self.fig_dict=kwargs['fig']

    def create_plot(self):
        fig_dict=self.fig_dict
        try:
            self.fig = plotly.Plot(data=fig_dict['data'], layout=fig_dict['layout'],config={
                                        'displayModeBar': True,
                                        'scrollZoom': True,
                                        'displaylogo': True,
                                            'editable': True,
                                            'showLink': False,
                                            'modeBarButtonsToRemove': ['zoom', 'resetScale'],
                                            'responsive': True,
                                        },)
        except Exception as e:
               print(fig_dict)
                            

    def __call__(self):
      with mui.Paper(key=self._key,
                      sx={  "display": "grid",
                            "gridTemplateColumns": "1fr",  # One column
                            "gridTemplateRows": "auto 1fr",  # First row auto-sized, second row takes remaining space
                            "gap": "10px",
                            'alignItems': 'stretch',
                            "borderRadius": 3,
                            "overflow": "hidden",
                            'width':'100%',
                        }, 
                        elevation=1):
                                    with self.title_bar():
                                        mui.icon.Radar()
                                        mui.Typography('PLOT')
                                    self.create_plot()
            # with html.Div():
            #     html.div(
            #         html.details(
            #             html.summary("Options"),
            #             html.select(
            #                 html.option("Option 1", value="1"),
            #                 html.option("Option 2", value="2"),
            #                 html.option("Option 3", value="3"),
            #                 style={"width": "50%"}
            #             ),
            #             open=True,
            #             style={"marginTop": "10px"}
            #         ),
            #         style={"padding": "10px"}
            #     )
                


                
