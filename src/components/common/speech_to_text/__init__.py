import os
import streamlit.components.v1 as components
import streamlit as st

# Declare the component
# Use absolute path resolution that works in both Windows and Docker
parent_dir = os.path.dirname(os.path.abspath(__file__))
index_path = os.path.join(parent_dir, "index.html")

# Debugging: check if file exists
if not os.path.exists(index_path):
    st.error(f"Critical Error: Component file not found at {index_path}")

_component_func = components.declare_component(
    "speech_to_text_component",
    path=parent_dir
)

def speech_to_text(key=None, default=None):
    """
    Componente de reconocimiento de voz usando Web Speech API.
    Devuelve un diccionario con el texto transcrito.
    Ejemplo: {'text': 'Hola mundo', 'isFinal': True}
    """
    # Forzamos height=50 para evitar "cuadrados grises" colapsados
    component_value = _component_func(key=key, default=default, height=50)
    return component_value

if __name__ == "__main__":
    st.header("Test Speech to Text")
    result = speech_to_text(key="test_mic")
    st.write("Resultado:", result)
