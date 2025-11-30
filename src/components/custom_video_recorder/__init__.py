import os
import streamlit.components.v1 as components

# Create a _RELEASE constant. We'll set this to True for now since we are serving static HTML.
_RELEASE = True

if not _RELEASE:
    # Development mode: use a dev server (not applicable here as we use static html)
    _component_func = components.declare_component(
        "video_recorder",
        url="http://localhost:3001",
    )
else:
    # Production mode: load from local build directory
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    _component_func = components.declare_component(
        "video_recorder",
        path=parent_dir
    )

def video_recorder(key=None):
    """
    Create a new instance of "video_recorder".
    
    Returns:
        str: Base64 encoded video data (or None).
    """
    component_value = _component_func(key=key, default=None)
    return component_value
