import sys
import os
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import requests
import json
from dataModels.visualization import ChatViz
import fireducks.pandas as pd
import streamlit as st
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
url='http://Backend:8005'


def make_serializable(obj):
    """
    Convert an object to a serializable format.
    """
    if isinstance(obj, dict):
        return {k: make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_serializable(i) for i in obj]
    elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
    elif isinstance(obj, (np.float64, np.float32, np.float16)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.Interval):
        return {'left': obj.left, 'right': obj.right, 'closed': obj.closed}
    
    elif isinstance(obj, (np.float64, float)) and (np.isnan(obj) or np.isinf(obj)):
        return None
    else:
        return obj

def fetch_visualizations(project_id: str):
    response = requests.get(url+f'/project/{project_id}/visualization/get_Auto_Gen')
    if response.status_code != 200:
        return []
    return json.loads(response.json())['visualizations']

def create_visualizations(project_id: str, features: list=None):
    response = requests.post(url+f'/project/{project_id}/visualization/update_Auto_Gen',json={'features':features} if features else {})
    if response.status_code != 200:
        return []
    return json.loads(response.json())['visualizations']

def fetch_chat_visualizations(project_id:str):
    response = requests.get(url+f'/project/{project_id}/visualization/get_Chat_Viz')
    return json.loads(response.json())['visualizations']


def save_chat_visualizations(project_id:str,new_viz:ChatViz):    
    response = requests.post(url+f'/project/{project_id}/visualization/Chat_viz',json=new_viz.model_dump())
    return response.status_code==200


@st.cache_data
def plot_column_types(project_id:str):
    response = requests.get(url+f'/project/{project_id}/visualization/plot_column_type')
    if response.status_code==200:
        return response.json()
    else:
        return None

@st.cache_data
def plot_missing_column(project_id:str,column_name:str,plot_type:str='Pie Chart',**kwargs):
    response = requests.get(url+f'/project/{project_id}/visualization/plot_missing_column',json={'column_name':column_name,'plot_type':plot_type})
    if response.status_code==200:
        return response.json()
    else:
        return None
@st.cache_data
def plot_distribution(project_id:str,column_name:str,plot_type:str='histogram',**kwargs):
    response = requests.get(url+f'/project/{project_id}/visualization/plot_distribution',json={'column_name':column_name,'plot_type':plot_type})
    if response.status_code==200:
        return response.json()
    else:
        return None

@st.cache_data
def plot_top_n(project_id:str,column_name:str,plot_type:str='Word Frequency',**kwargs):
    response = requests.get(url+f'/project/{project_id}/visualization/top-n',json={'column_name':column_name,'plot_type':plot_type})
    if response.status_code==200:
        return response.json()
    else:
        return None

@st.cache_data
def plot_word_cloud(project_id:str,column_name:str,**kwargs):
    response = requests.get(url+f'/project/{project_id}/visualization/wordcloud',json={'column_name':column_name})
    if response.status_code==200:
        return response.json()
    else:
        return None
@st.cache_data
def plot_split_distribution(project_id: str, train_size: int, test_size: int, val_size: int = 0, total_rows: int = None):
    print(train_size,test_size,val_size,total_rows)
    # Create payload with required parameters
    payload = {
        'train_size': int(train_size),
        'test_size': int(test_size)
    }
    
    # Add optional parameters if they exist
    if val_size:
        payload['val_size'] = int(val_size)
    
    if total_rows:
        payload['total_rows'] = int(total_rows)
        
    # Send the request with the prepared payload
    response = requests.get(url+f'/project/{project_id}/visualization/split_distribution', json=payload)
    if response.status_code==200:
        return response.json()
    else:
        return None

@st.cache_data
def render_gauge(value, title, color, size=200):
    gauge_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    body {{
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      background-color: transparent;
      font-family: Arial, sans-serif;
      overflow: hidden; /* Prevent scrollbars */
    }}

    .gauge-container {{
      position: relative;
      width: {size}px;
      height: {size}px;
      margin: 0; /* Reduced margin */
    }}

    .value-display {{
      position: absolute;
      top: {30 if title=='Accuracy' else 30}%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: {24 if title != 'Accuracy' else 60}px;
      font-weight: bold;
      color: white;
    }}

    .gauge-title {{
      text-align: center;
      font-size: {50 if title == 'Accuracy' else 25}px;
      font-weight: bold;
      color: white;
      margin-bottom: 5px; /* Add small margin below the title */
    }}
    
    .content-wrapper {{
      display: flex;
      flex-direction: column;
      align-items: center;
    }}
  </style>
</head>
<body>
  <div class="content-wrapper">
    <div class="gauge-title">{title}</div>
    <div class="gauge-container">
      <canvas id="dialChart" width="{size-20}" height="{size-20}"></canvas>
      <div class="value-display">{value}%</div>
    </div>
  </div>

  <script>
    const canvas = document.getElementById('dialChart');
    const ctx = canvas.getContext('2d');
    const valueDisplay = document.querySelector('.value-display');

    let currentValue = 0;
    const targetValue = {value};
    const animationDuration = 2000;
    const startTime = performance.now();

function drawDial() {{
      const width = canvas.width;
      const height = canvas.height;
      const radius = Math.min(width, height) / 2 - 20; /* Increased padding */
      const centerX = width / 2;
      const centerY = height / 2;

      // Clear the canvas with a transparent background
      ctx.clearRect(0, 0, width, height);
      ctx.fillStyle = "transparent";
      ctx.fillRect(0, 0, width, height);

      // Draw the background arc (unfilled portion) FIRST
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0.75 * Math.PI, 2.25 * Math.PI); // Full arc
      ctx.strokeStyle = '#801818'; // Red for the unfilled portion
      ctx.lineWidth = 20;
      ctx.lineCap = 'round';
      ctx.stroke();

      // Draw the value arc (filled portion) SECOND
      const endAngle = 0.75 * Math.PI + (1.5 * Math.PI * currentValue) / 100;
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0.75 * Math.PI, endAngle);
      ctx.strokeStyle = '{color}'; // Color for the filled portion
      ctx.lineWidth = 20;
      ctx.lineCap = 'round';
      ctx.shadowBlur = 15;
      ctx.shadowColor = 'rgba(255, 255, 255, 0.8)';
      ctx.stroke();

      // Draw the needle
      const needleLength = radius * 0.8;
      const needleAngle = 0.75 * Math.PI + (1.5 * Math.PI * currentValue) / 100;
      ctx.beginPath();
      ctx.moveTo(centerX, centerY);
      ctx.lineTo(
        centerX + needleLength * Math.cos(needleAngle),
        centerY + needleLength * Math.sin(needleAngle)
      );
      ctx.strokeStyle = 'white';
      ctx.lineWidth = 4;
      ctx.shadowBlur = 8;
      ctx.shadowColor = 'rgba(255, 255, 255, 0.8)';
      ctx.stroke();

      // Draw the center circle
      ctx.beginPath();
      ctx.arc(centerX, centerY, 5, 0, 2 * Math.PI);
      ctx.fillStyle = 'white';
      ctx.shadowBlur = 8;
      ctx.shadowColor = 'rgba(255, 255, 255, 0.8)';
      ctx.fill();
    }}

    function animateValue(timestamp) {{
      const elapsedTime = timestamp - startTime;
      const progress = Math.min(elapsedTime / animationDuration, 1);
      currentValue = progress * targetValue;

      // Update the display
      valueDisplay.textContent = `${{Math.round(currentValue)}}%`;

      // Draw the dial
      drawDial();

      if (progress < 1) {{
        requestAnimationFrame(animateValue);
      }}
    }}

    // Start the animation
    requestAnimationFrame(animateValue);
  </script>
</body>
</html>
    """
    return gauge_html

@st.cache_data
def plot_confusion_matrix(cm):
    """
    Create a confusion matrix visualization using Plotly.
    
    Args:
        project_id (str): The project ID
        true_labels (list): List of actual/true labels
        predicted_labels (list): List of predicted labels
        class_names (list, optional): List of class names. If None, unique values from labels will be used.
    
    Returns:
        plotly.graph_objects.Figure: Plotly figure object containing the confusion matrix
    """
    # Determine size of the matrix
    n_classes = len(cm)
    
    # Create class labels (0, 1, 2, etc.)
    labels = [str(i) for i in range(n_classes)]
    
    # Create the heatmap figure
    fig = ff.create_annotated_heatmap(
        z=cm,
        x=labels,
        y=labels,
        annotation_text=cm,
        colorscale='Blues',
        showscale=False
    )
    
    # Update layout for better readability
    fig.update_layout(
        title='Confusion Matrix',
        xaxis=dict(title='Predicted labels', side='bottom'),
        yaxis=dict(title='True labels', autorange='reversed'),
        width=700,
        height=700,
        margin=dict(t=50, l=100)
    )
    
    # Adjust annotations
    for i in range(len(fig.layout.annotations)):
        fig.layout.annotations[i].font.size = 30
    
    return fig

@st.cache_data
def plot_feature_importance(feature_importance_json):
    """
    Plots feature importance using Plotly.
    
    Parameters:
    - feature_importance_json (str or dict): JSON string or dictionary of feature importance values.
    
    Returns:
    - A Plotly figure object.
    """
    # Convert JSON string to dictionary if needed
    if isinstance(feature_importance_json, str):
        feature_importance = json.loads(feature_importance_json)
    else:
        feature_importance = feature_importance_json

    # Convert to DataFrame and sort
    importance_df = pd.DataFrame(list(feature_importance.items()), columns=["Feature", "Importance"])
    importance_df = importance_df.sort_values(by="Importance", ascending=True)

    # Plot using Plotly
    fig = px.bar(
        importance_df,
        x="Importance",
        y="Feature",
        orientation="h",
        title="Feature Importance (Higher values are more important)",
        labels={"Importance": "Feature Importance", "Feature": "Features"},
    )

    fig.show()
    return fig

@st.cache_data
def plot_precision_recall_curve(precision_recall):
    """
    Create an enhanced precision-recall curve visualization using Plotly.
    
    Args:
        precision_recall (tuple): Tuple containing (precision, recall) arrays
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object containing the precision-recall curve
    """
    precision, recall = precision_recall[0], precision_recall[1]
    
    # Convert to numpy arrays if they aren't already
    precision = np.array(precision)
    recall = np.array(recall)
    
    # Filter out potential anomalies where recall=0 but precision=0
    # Typically at recall=0, precision should be 1 (or undefined)
    valid_indices = []
    has_zero_recall = False
    
    for i in range(len(recall)):
        # Skip points where recall is 0 and precision is 0
        if recall[i] == 0 and precision[i] == 0:
            continue
        
        # Keep track if we have a valid zero recall point
        if recall[i] == 0:
            has_zero_recall = True
            
        valid_indices.append(i)
    
    # If we don't have a valid point at recall=0, add one with precision=1
    if not has_zero_recall and len(valid_indices) > 0:
        # Prepend a point at recall=0, precision=1
        recall = np.insert(recall, 0, 0)
        precision = np.insert(precision, 0, 1)
    elif len(valid_indices) > 0:
        # Use only valid indices - convert to numpy array for proper indexing
        valid_indices = np.array(valid_indices)
        recall = recall[valid_indices]
        precision = precision[valid_indices]
    
    # Calculate average precision (area under PR curve)
    avg_precision = 0
    for i in range(len(recall)-1):
        avg_precision += precision[i] * (recall[i+1] - recall[i])
    
    # Create figure
    fig = go.Figure()
    
    # Add the precision-recall curve with improved styling
    fig.add_trace(go.Scatter(
        x=recall, 
        y=precision, 
        mode='lines', 
        name='Precision-Recall',
        line=dict(color='royalblue', width=3),
        fill='tozeroy',
        fillcolor='rgba(65, 105, 225, 0.2)'
    ))
    
    # Calculate positive ratio (prevalence) for the baseline
    # For a random classifier, the expected precision equals the positive class prevalence
    positive_ratio = precision[-1] if len(precision) > 0 else 0.5  # Use last precision value as approximation
    
    # Add a reference line for random classifier
    fig.add_trace(go.Scatter(
        x=[0, 1], 
        y=[positive_ratio, positive_ratio], 
        mode='lines', 
        name='Random Classifier',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    # Update layout with better styling and information
    fig.update_layout(
        title=f'Precision-Recall Curve (AP = {avg_precision:.3f})',
        xaxis=dict(title='Recall', range=[0, 1]),
        yaxis=dict(title='Precision', range=[0, 1.05]),
        legend=dict(x=0.01, y=0.01),
        width=700,
        height=500,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # Add grid
    fig.update_xaxes(showgrid=True, gridwidth=1)
    fig.update_yaxes(showgrid=True, gridwidth=1)
    
    return fig

@st.cache_data
def plot_roc_curve(roc_data):
    """
    Create a ROC curve visualization using Plotly.
    
    Args:
        roc_data (tuple): Tuple containing (fpr, tpr, thresholds) arrays
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object containing the ROC curve
    """
    fpr, tpr = roc_data[0], roc_data[1]
    
    # Create the ROC curve figure
    fig = go.Figure()
    
    # Add the ROC curve
    fig.add_trace(go.Scatter(
        x=fpr, 
        y=tpr, 
        mode='lines', 
        name='ROC Curve',
        line=dict(color='royalblue', width=2)
    ))
    
    # Add the diagonal reference line (random classifier)
    fig.add_trace(go.Scatter(
        x=[0, 1], 
        y=[0, 1], 
        mode='lines', 
        name='Random Classifier',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    # Calculate the AUC
    auc = np.trapz(tpr, fpr)
    
    # Update layout
    fig.update_layout(
        title=f'ROC Curve (AUC = {auc:.3f})',
        xaxis=dict(title='False Positive Rate'),
        yaxis=dict(title='True Positive Rate'),
        template='plotly_dark',
        legend=dict(x=0.01, y=0.99, bordercolor='black', borderwidth=1),
        width=700,
        height=500
    )
    
    return fig