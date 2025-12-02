import streamlit as st
import plotly.graph_objects as go

def render_body_map(key="body_map"):
    """
    Renders an interactive schematic body map using Plotly.
    Returns the name of the selected body part, or None if nothing is selected.
    """
    
    # Define body parts coordinates (Schematic Frontal View)
    body_parts = [
        {"name": "Cabeza", "x": 0, "y": 10, "color": "#FFB6C1"},
        {"name": "Cuello", "x": 0, "y": 8.5, "color": "#FFDAB9"},
        {"name": "Hombro Izq.", "x": -2.5, "y": 8, "color": "#ADD8E6"},
        {"name": "Hombro Der.", "x": 2.5, "y": 8, "color": "#ADD8E6"},
        {"name": "Pecho", "x": 0, "y": 7, "color": "#90EE90"},
        {"name": "Abdomen", "x": 0, "y": 5, "color": "#98FB98"},
        {"name": "Brazo Izq.", "x": -3.5, "y": 6, "color": "#87CEEB"},
        {"name": "Brazo Der.", "x": 3.5, "y": 6, "color": "#87CEEB"},
        {"name": "Mano Izq.", "x": -4.5, "y": 4, "color": "#B0E0E6"},
        {"name": "Mano Der.", "x": 4.5, "y": 4, "color": "#B0E0E6"},
        {"name": "Cadera", "x": 0, "y": 3, "color": "#F0E68C"},
        {"name": "Pierna Izq.", "x": -1.5, "y": 0, "color": "#D8BFD8"},
        {"name": "Pierna Der.", "x": 1.5, "y": 0, "color": "#D8BFD8"},
        {"name": "Pie Izq.", "x": -1.5, "y": -3, "color": "#E6E6FA"},
        {"name": "Pie Der.", "x": 1.5, "y": -3, "color": "#E6E6FA"},
    ]

    names = [p["name"] for p in body_parts]
    x_coords = [p["x"] for p in body_parts]
    y_coords = [p["y"] for p in body_parts]
    colors = [p["color"] for p in body_parts]

    # Create Scatter plot
    fig = go.Figure(data=[go.Scatter(
        x=x_coords,
        y=y_coords,
        mode='markers+text',
        text=names,
        textposition="top center",
        marker=dict(
            size=25,
            color=colors,
            line=dict(width=2, color='DarkSlateGrey')
        ),
        hoverinfo='text',
        hovertext=names
    )])

    # Configure Layout (Hide axes, make it look like a diagram)
    fig.update_layout(
        title=dict(text="Selecciona la zona de dolor", x=0.5, xanchor='center'),
        showlegend=False,
        xaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            range=[-6, 6],
            fixedrange=True
        ),
        yaxis=dict(
            showgrid=False, 
            zeroline=False, 
            showticklabels=False,
            range=[-4, 11],
            fixedrange=True
        ),
        height=450,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        dragmode=False # Disable zooming/panning
    )

    # Render with selection event
    # on_select="rerun" will trigger a rerun when a point is clicked
    event = st.plotly_chart(
        fig, 
        key=key, 
        on_select="rerun", 
        selection_mode="points",
        use_container_width=True
    )

    selected_part = None
    if event and event.selection and event.selection["points"]:
        # Get the index of the selected point
        point_index = event.selection["points"][0]["point_index"]
        selected_part = names[point_index]

    return selected_part
