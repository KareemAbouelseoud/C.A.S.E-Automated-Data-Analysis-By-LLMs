"""
maintools.py

This module defines various tools for data visualization using Plotly Express.
The tools are designed to generate different types of plots based on the provided data.
Tool node has also been defined to invoke the tools based on the caller.

Dependencies:
- plotly.express
- pandas
- numpy
- langchain_core.tools
- langchain_core.messages
- dotenv

Usage:
1. Ensure that the required dependencies are installed.
2. Set up the necessary environment variables in a .env file.
3. Use the provided tools to generate visualizations based on the dataset.

Functions:
- load_dotenv: Loads environment variables from a .env file.
- create_line_plot: Generates a line plot using Plotly Express and returns the figure as a dictionary.

Variables:
- logger: A logger instance for logging messages.
"""
import plotly.express as px
from typing import Dict, Optional,List
import pandas as pd
from typing import Literal
import pandas as pd
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','Agents')))
import loggerModule

logger=loggerModule.setup_logging()

@tool
async def create_line_plot(x: str, y: str,title: str , color: str = None,x_label: str=None,y_label: str=None, df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Generates a line plot using Plotly Express and returns the figure as a dictionary.

    Args:
    x (str): Column for the x-axis.
    y (str): Column for the y-axis.
    color (str, optional): Column to color the lines.
    labels: A dictionary where keys and values are strings. Example: {"key1": "value1", "key2": "value2"}
    title (str): Title of the plot.

    Returns:
    - dict: The generated line plot as a dictionary.
    """
    try:
        
        # Check if provided column names exist in the dataset
        for col in [x, y, color]:
            if col and col not in df.columns:
                raise ValueError(f"The specified '{col}' column is not found in the dataset.")
        
        # Check if the specified columns are the same
        if x == y or x == color or y == color:
            raise ValueError("The specified x, y, or color column is the same as the other column.")
        
        # Drop rows with missing values in the relevant columns
        relevant_columns = [col for col in [x, y, color] if col is not None]
        df = df.dropna(subset=relevant_columns)

        fig = px.line(
            data_frame=df,
            x=x,
            y=y,
            color=color,
            symbol=color,
            labels={'x':x_label,'y':y_label},
            color_discrete_sequence=px.colors.qualitative.Set1,
            title=title,
            template="plotly_dark",
        )
        return fig.to_dict()
    except Exception as e:
        print(f"Error creating line plot: {e}")

@tool
async def create_scatter_plot(x: str, y: str,title: str, color: Optional[str] = None,x_label: str=None,y_label: str=None, marginal_x: Optional[str] = None, marginal_y: Optional[str] = None, trendline: Optional[str] = None, trendline_scope: Optional[str] = None, df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Generates a scatter plot using Plotly Express and returns the figure as a dictionary.

    Parameters:
    - x (str): The column name for the x-axis.
    - y (str): The column name for the y-axis.
    - color (str, optional): Column name to differentiate points by color (e.g., groups or categories).
    - labels (dict, optional): Dictionary of axis label mappings for x and y.
    - marginal_x (str, optional): Type of marginal plot for x (e.g., 'box', 'violin').
    - marginal_y (str, optional): Type of marginal plot for y (e.g., 'box', 'violin').
    - trendline (str, optional): Type of trendline to draw (e.g., 'ols', 'lowess').
    - trendline_scope (str, optional): Whether trendlines are fit per trace or across traces (default: 'trace').
    - title (str): The title of the plot.

    Returns:
    - dict: The generated scatter plot as a dictionary.
    """
    try:
        # Check if provided column names exist in the dataset
        for col in [x, y, color]:
            if col and col not in df.columns:
                raise ValueError(f"The specified '{col}' column is not found in the dataset.")
                
        # Check if the specified columns are the same
        if x == y or x == color or y == color:
            raise ValueError("The specified x, y, or color column is the same as the other column.")
        
        # Drop rows with missing values in the relevant columns 
        relevant_columns = [col for col in [x, y, color] if col is not None]
        df = df.dropna(subset=relevant_columns)

        fig = px.scatter(
            data_frame=df,
            x=x,
            y=y,
            color=color,
            symbol=color,
            labels={'x':x_label,'y':y_label},
            color_discrete_sequence=px.colors.qualitative.Set1,
            marginal_x=marginal_x,
            marginal_y=marginal_y,
            trendline=trendline,
            trendline_scope=trendline_scope,
            title=title,
            template='plotly_dark',
        )
        return fig.to_dict()
    except Exception as e:
        print(f"Error creating scatter plot: {e}")

@tool
async def create_bubble_plot(x: str, y: str, title: str, color: Optional[str] = None, size: Optional[str] = None, x_label: str=None,y_label: str=None, df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Generates a bubble plot using Plotly Express and returns the figure as a dictionary.

    Parameters:
    - x (str): The column name for the x-axis.
    - y (str): The column name for the y-axis.
    - color (str, optional): Column name to differentiate points by color (e.g., groups or categories).
    - size (str, optional): Column name representing the size of the bubbles.
    - labels (dict, optional): Dictionary of axis label mappings for x and y.
    - title (str,): The title of the plot.

    Returns:
    - dict: The generated bubble plot as a dictionary.
    """
    try:
        # Check if provided column names exist in the dataset
        for col in [x, y, color, size]:
            if col and col not in df.columns:
                raise ValueError(f"The specified '{col}' column is not found in the dataset.")
            
        # Check if the specified columns are the same
        if x == y or x == color or y == color:
            raise ValueError("The specified x, y, or color column is the same as the other column.")
        
        # Drop rows with missing values in the relevant columns
        relevant_columns = [col for col in [x, y, color, size] if col is not None]
        df = df.dropna(subset=relevant_columns)

        fig = px.scatter(
            data_frame=df,
            x=x,
            y=y,
            color=color,
            symbol=color,
            size=size,
            labels={'x':x_label,'y':y_label},
            color_discrete_sequence=px.colors.qualitative.Set1,
            title=title,
            template="plotly_dark",
        )
        return fig.to_dict()
    except Exception as e:
        print(f"Error creating bubble plot: {e}")

@tool
async def create_swarm_plot(x: str, y: str,title: str , color: Optional[str] = None,  x_label: str=None,y_label: str=None, stripmode: Optional[str] = "group", df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Creates a swarm plot (approximated using scatter plot) using Plotly Express and returns the figure as a dictionary.

    Parameters:
        x (str): Column name for the x-axis.
        y (str): Column name for the y-axis.
        color (str, optional): Column name to group points by color.
        labels (dict, optional): Dictionary of axis or legend labels.
        stripmode (str, optional): Mode for strip plot, e.g., "group".
        title (str): Title of the plot.

    Returns:
        dict: The generated swarm plot as a dictionary.
    """
    try:
        # Check if provided column names exist in the dataset
        for col in [x, y, color]:
            if col and col not in df.columns:
                raise ValueError(f"The specified '{col}' column is not found in the dataset.")
        
        # Check if the specified columns are the same
        if x == y or x == color or y == color:
            raise ValueError("The specified x, y, or color column is the same as the other column.")
        
        # Drop rows with missing values in the relevant columns
        relevant_columns = [col for col in [x, y, color] if col is not None]
        df = df.dropna(subset=relevant_columns)

        fig = px.strip(
            data_frame=df,
            x=x, 
            y=y, 
            color=color,
            # symbol=color, 
            labels={'x':x_label,'y':y_label},
            color_discrete_sequence=px.colors.qualitative.Set1, 
            orientation="v", 
            stripmode=stripmode, 
            title=title, 
            template="plotly_dark", 
        )
        return fig.to_dict()
    except Exception as e:
        print(f"Error creating swarm plot: {e}")

@tool
async def grouped_bar_plot(x: str, y: str,title:str, color: Optional[str] = None, df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Creates a grouped bar plot using Plotly Express and returns the plot as a dictionary.

    Parameters:
        x (str): Column name for the x-axis.
        y (str): Column name for the y-axis.
        color (str, optional): Column name to group bars by color.
        title (str): Title of the plot.

    Returns:
        dict: The generated grouped bar plot as a dictionary.
    """
    try:

        # Check if provided column names exist in the dataset
        for col in [x, y, color]:
            if col and col not in df.columns:
                raise ValueError(f"The specified '{col}' column is not found in the dataset.")

        # check if the specified columns are the same
        if x == y or x == color or y == color:
            raise ValueError("The specified x, y, or color column is the same as the other column.")
        
        # drop rows with missing values in the relevant columns
        relevant_columns = [col for col in [x, y, color] if col is not None]
        df = df.dropna(subset=relevant_columns)

        fig = px.bar(
            df, 
            x=x, 
            y=y, 
            color=color, 
            title=title, 
            barmode="group"
            )
        return fig.to_dict()
    except Exception as e:
        print(f"Error creating grouped bar plot: {e}")

@tool
async def create_pairplot(color: Optional[str] = None, dimensions: List[str] = None, diagonal_visible: Optional[bool] = True, title: Optional[str] = 'Pair Plot', df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Create a pairplot using Plotly and returns the plot as a dictionary.

    Parameters:
    color (str): Column name to be used for color encoding.
    dimensions (list): List of column names to be used as dimensions for the pairplot.
    diagonal_visible (bool): Whether to show the diagonal plots.

    Returns:
    dict: The generated pairplot as a dictionary.
    """
    try:
        # Check if DataFrame has more than one column
        if df.shape[1] < 2:
            raise ValueError("DataFrame must have at least two columns for a pairplot.")
        
        # Create the pairplot using Plotly
        if dimensions is not None:
            fig = px.scatter_matrix(df, color=color,symbol=color, dimensions=dimensions,title=title)
        else:
            fig = px.scatter_matrix(df, color=color,symbol=color,title=title)

        fig.update_traces(diagonal_visible=diagonal_visible)
        logger.info(f"Pair Plot Created Successfully")
        fig.update_layout(
                template="plotly_dark",)
        return fig.to_dict()
        
    except ValueError as e:
        logger.error(f"ValueError: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

@tool
async def create_radar_chart(category_column: str,title: str, value_columns: List[str] = None, color_column: Optional[str] = None, df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Generates a radar chart using Plotly Express and returns the plot as a dictionary.

    Args:
        category_column (str): The column name that defines the categories (radial axis).
        value_columns (list, optional): List of column names to plot as radar lines.
                                         If None, all numerical columns except the category column will be used.
        title (str): The title of the radar chart.
        color_column (str, optional): Column name for grouping different lines (optional).
                                       If None, no grouping is applied.

    Returns:
        dict: The generated radar chart as a dictionary.
    """
    # Example dataset

    try:
        if category_column not in df.columns:
            raise ValueError(f"Category column '{category_column}' is not in the DataFrame.")

        
        # Default value columns to all numeric columns except the category column
        if value_columns is None:
            value_columns = df.select_dtypes(include=['number']).columns.difference([category_column]).tolist()
        
        if not value_columns:
            raise ValueError("No numerical columns found for plotting.")
        
        # Check if the color column exists
        if color_column and color_column not in df.columns:
            raise ValueError(f"Color column '{color_column}' is not in the DataFrame.")
        
        # Melt the data for radar chart format
        melted_data = df.melt(
            id_vars=[category_column] + ([color_column] if color_column else []),
            value_vars=value_columns,
            var_name="Metric",
            value_name="Value"
        )
        
        # Create the radar chart
        fig = px.line_polar(
            melted_data,
            r="Value",
            theta="Metric",
            color=color_column,
            line_close=True,
            title=title,
        )
        fig.update_traces(fill="toself")
        logger.info(f"Radar Plot Created Successfully")

        fig.update_layout(
                template="plotly_dark",)
        return fig.to_dict()  

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

@tool
async def create_treemap(path_columns: List[str],title: str, value_column: Optional[str] = None, color_column: Optional[str] = None, color_scale: Optional[str] = "Viridis", df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Generates a treemap using Plotly Express and returns the plot as a dictionary.

    Args:
        path_columns (list): A list of columns defining the hierarchy for the treemap.
        value_column (str, optional): The column to determine the size of the segments. If None, all segments will be of equal size.
        color_column (str, optional): The column to determine the color of the segments. If None, no color mapping is applied.
        title (str): Title of the treemap. Default is "Treemap".
        color_scale (str, optional): Color scale to use for the treemap. Default is "Viridis".

    Returns:
        dict: The generated treemap as a dictionary.
    """
    try:  

        valid_path_columns = [col for col in path_columns if col in df.columns]
        if len(valid_path_columns) < len(path_columns):
            missing_cols = set(path_columns) - set(valid_path_columns)
            print(f"Warning: The following columns are missing and will be removed: {missing_cols}")

        # Ensure there is at least one valid path column
        if not valid_path_columns:
            print("Warning: No valid columns for the treemap hierarchy. Returning None.")
            return None
        
        # Check value and color columns
        if value_column and value_column not in df.columns:
            print(f"Warning: Value column '{value_column}' is not in the DataFrame. Ignoring it.")
            value_column = None
        
        if color_column and color_column not in df.columns:
            print(f"Warning: Color column '{color_column}' is not in the DataFrame. Ignoring it.")
            color_column = None
        
        # Handle missing values in relevant columns
        all_columns = valid_path_columns + [value_column, color_column]
        for col in filter(None, all_columns):  # Skip None columns
            if col in df.columns:
                df[col] = df[col].fillna(None)
        

        df["all"] = "all" # in order to have a single root node

        # Create the treemap
        fig = px.treemap(
            df,
            path=valid_path_columns,
            values=value_column,
            color=color_column,
            title=title,
            color_continuous_scale=color_scale
        )
        fig.update_traces(root_color="lightgrey")
        fig.update_traces(marker=dict(cornerradius=5))

        logger.info(f"Tree Map Plot Created Successfully")

        fig.update_layout(
                template="plotly_dark",)
        return fig.to_dict()

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

@tool
async def create_correlation_heatmap(columns: List[str] = None,title: Optional[str] = "Correlation Heatmap", color_scale: Optional[str] = "Viridis", show_values: Optional[bool] = True, df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Generates a heatmap of correlations between numerical columns in the dataset and returns it as a dictionary.

    Args:
        columns (list, optional): List of specific columns to include in the correlation. Default is None (use all numerical columns).
        color_scale (str, optional): Color scale to use for the heatmap. Default is "Viridis".
        title (str, optional): Title of the heatmap. Default is "Correlation Heatmap".
        show_values (bool, optional): Whether to overlay correlation values on the heatmap. Default is True.

    Returns:
        dict: The generated correlation heatmap in dictionary format.
    """
    try:
        numerical_data = df.select_dtypes(include=["number"])

        if columns:
            numerical_data = numerical_data[columns]

        correlation_matrix = numerical_data.corr()
        correlation_matrix = correlation_matrix.applymap(lambda x: None if pd.isna(x) else x)

        fig = px.imshow(
            correlation_matrix,
            labels=dict(x="Features", y="Features", color="Correlation"),
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            color_continuous_scale=color_scale,
            title=title
        )

        if show_values:
            fig.update_traces(text=correlation_matrix.values, texttemplate="%{text:.2f}", textfont_size=12)

        fig.update_layout(template="plotly_dark")
        return fig.to_dict()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

@tool
async def create_faceted_bar_chart(x: str, y: str,title: str, color: Optional[str] = None, barmode: Optional[str] = "group", facet_row: Optional[str] = None, facet_col: Optional[str] = None, df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Generates a faceted bar chart using Plotly Express and returns it as a dictionary.

    Args:
        x (str): Column name for the x-axis.
        y (str): Column name for the y-axis.
        color (str, optional): Column name for bar colors. Default is None.
        barmode (str, optional): Bar mode. Options: 'group', 'overlay', 'relative'. Default is 'group'.
        facet_row (str, optional): Column name for facet rows. Default is None.
        facet_col (str, optional): Column name for facet columns. Default is None.
        title (str): Title of the chart.

    Returns:
        dict: The generated faceted bar chart in dictionary format.
    """
    try:
        relevant_columns = [col for col in [x, y, color, facet_row, facet_col] if col]
        df = df.dropna(subset=relevant_columns)

        fig = px.bar(
            df,
            x=x,
            y=y,
            color=color,
            barmode=barmode,
            facet_row=facet_row,
            facet_col=facet_col,
            title=title
        )

        fig.update_layout(
            title=dict(x=0.5),
            coloraxis_colorbar=dict(title=color),
            font=dict(size=12),
            template="plotly_dark"
        )
        return fig.to_dict()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

@tool
async def create_histogram(x: str, color: Optional[str] = None, x_label: Optional[str] = None, y_label: Optional[str] = None, df:Optional[pd.DataFrame] = None) -> Dict:
    """
    Creates a histogram using Plotly Express and returns it as a dictionary.

    Args:
        x (str): The column name for the x-axis.
        color (str, optional): The column name to be used for color encoding. Default is None.
        x_label (str, optional): Label for the x-axis. Default is None.
        y_label (str, optional): Label for the y-axis. Default is None.

    Returns:
        dict: The generated histogram in dictionary format.
    """
    try:
        if x not in df.columns:
            raise ValueError(f"Column '{x}' not found in the dataset.")

        fig = px.histogram(df, x=x, color=color)
        return fig.to_dict()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

@tool
async def create_pie_chart(values: str, names: str,title: str, color: Optional[str] = None, df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Creates a pie chart using Plotly Express and returns it as a dictionary.

    Args:
        values (str): The column name for the values.
        names (str): The column name for the names (labels).
        color (str, optional): The column name to be used for color encoding. Default is None.
        title (str): The title of the pie chart. Default is None.

    Returns:
        dict: The generated pie chart in dictionary format.
    """
    try:

        if values not in df.columns or names not in df.columns:
            raise ValueError("Specified columns not found in the dataset.")

        fig = px.pie(df, values=values, names=names, color=color, title=title)
        return fig.to_dict()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

@tool
async def create_area_chart(x: str, y: str, title: str,color: Optional[str] = None,  x_label: Optional[str] = None, y_label: Optional[str] = None, df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Creates an area chart using Plotly Express and returns it as a dictionary.

    Args:
        x (str): The column name for the x-axis.
        y (str): The column name for the y-axis.
        color (Optional[str], optional): The column name to be used for color encoding. Default is None.
        x_label (Optional[str], optional): Label for the x-axis. Default is None.
        y_label (Optional[str], optional): Label for the y-axis. Default is None.
        title (str): Title of the area chart. Default is None.

    Returns:
        dict: The generated area chart in dictionary format.
    """
    try:

        if x not in df.columns or y not in df.columns:
            raise ValueError("Specified columns not found in the dataset.")

        fig = px.area(df, x=x, y=y, color=color, title=title, labels={'x': x_label, 'y': y_label})
        return fig.to_dict()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

@tool
async def create_boxplot(x: Optional[str] = None, y: Optional[str] = None, color: Optional[str] = None, x_label: Optional[str] = None, y_label: Optional[str] = None, df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Creates a box plot using Plotly Express and returns it as a dictionary.

    Args:
        x (Optional[str], optional): The column name for the x-axis. Default is None.
        y (Optional[str], optional): The column name for the y-axis. Default is None.
        color (Optional[str], optional): The column name to be used for color encoding. Default is None.
        x_label (Optional[str], optional): Label for the x-axis. Default is None.
        y_label (Optional[str], optional): Label for the y-axis. Default is None.

    Returns:
        dict: The generated box plot in dictionary format.
    """
    try:

        if y not in df.columns or (x and x not in df.columns) or (color and color not in df.columns):
            raise ValueError("Specified columns not found in the dataset.")

        fig = px.box(df, x=x, y=y, color=color)

        if x_label:
            fig.update_xaxes(title_text=x_label)
        if y_label:
            fig.update_yaxes(title_text=y_label)
        return fig.to_dict()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None

@tool
async def create_violin_plot(x: Optional[str] = None, y: Optional[str] = None, color: Optional[str] = None, points: Optional[str] = None, hover_data: List[str] = None, x_label: Optional[str] = None, y_label: Optional[str] = None, df: Optional[pd.DataFrame] = None) -> Dict:
    """
    Creates a violin plot using Plotly Express and returns it as a dictionary.

    Args:
        x (Optional[str]): The column name for the x-axis.
        y (Optional[str]): The column name for the y-axis.
        color (Optional[str], optional): The column name to be used for color encoding. Default is None.
        points (Optional[str], optional): Whether to show data points. Options are 'all', 'outliers', 'suspectedoutliers', or 'false'. Default is 'all'.
        hover_data (Optional[list], optional): Additional data to display when hovering over points. Default is None.
        x_label (Optional[str], optional): Label for the x-axis. Default is None.
        y_label (Optional[str], optional): Label for the y-axis. Default is None.

    Returns:
        dict: The generated violin plot in dictionary format.
    """
    try:
        
        if y not in df.columns or (x and x not in df.columns) or (color and color not in df.columns):
            raise ValueError("Specified columns not found in the dataset.")

        fig = px.violin(df, x=x, y=y, color=color, points=points, hover_data=hover_data)

        if x_label:
            fig.update_xaxes(title_text=x_label)
        if y_label:
            fig.update_yaxes(title_text=y_label)
        return fig.to_dict()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return None


tools = [create_line_plot,
        create_scatter_plot,
        create_bubble_plot,
        create_swarm_plot,
        grouped_bar_plot,
        create_pairplot,
        create_radar_chart,
        create_treemap,
        create_correlation_heatmap,
        create_faceted_bar_chart,
        create_histogram,
        create_pie_chart,
        create_area_chart,
        create_boxplot,
        create_violin_plot]

async def tool_node(state)->Literal["caller", "__end__"]:
    tools_by_name = {tool.name: tool for tool in tools}
    
    messages = state["messages"]
    # get the last message of this state
    last_message = messages[-1]
    output_messages = []
    df = state['dataframe']
    for tool_call in last_message.tool_calls:
        try:
            # Invoke the tool based on the tool call
            tool_call["args"]["df"] = df
            tool_result = await tools_by_name[tool_call["name"]].ainvoke(tool_call["args"])
            return {"next": "__end__",'visualization':tool_result}
        except Exception as e:
            # Return the error if the tool call fails
            output_messages.append(
                ToolMessage(
                    content="an error occurred while running the tool",
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"],
                    additional_kwargs={"error": e},
                )
            )
            return {'next':'caller','messages':output_messages}

