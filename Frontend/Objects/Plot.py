import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from .Dashboard import Dashboard
from streamlit_elements import mui, plotly
import plotly.express as px

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
        self.name=kwargs['name'] if 'name' in kwargs else 'PLOT'
        self.icons={
               'Line':"mui.icon.Radar()",
               'Scatter':"mui.icon.ScatterPlotRounded()",
                'Pie':"mui.icon.PieChartRounded()",
                'Bubble':"mui.icon.BubbleChartRounded()",
                'Swarm':"mui.icon.DeblurRounded()",
                'Grouped Bar':"mui.icon.BarChartRounded()",
                'Pair':"mui.icon.TroubleshootRounded()",
                'Radar':"mui.icon.RadarRounded()",
                'Treemap':"mui.icon.AccountTreeRounded()",
                'Heatmap':"mui.icon.LocalFireDepartmentRounded()",
                'Faceted Bar':"mui.icon.StackedBarChartRounded()",
                'Histogram':"mui.icon.InsertChartRounded()",
                'Area':"mui.icon.QueryStatsRounded()",
                'Box':"mui.icon.DashboardRounded()",
                'Violin':"mui.icon.DiamondRounded()",

        }

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
                                        if self.name is not 'PLOT':
                                            exec(self.icons[self.name])
                                        else:
                                            mui.icon.TimelineRounded()
                                        mui.Typography(self.name)
                                    self.create_plot()


                
