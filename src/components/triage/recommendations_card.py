import streamlit as st
from utils.icons import render_icon

def render_recommendations_card(recommendations: list):
    """
    Renders a card with self-care recommendations.
    """
    if not recommendations:
        return

    with st.container(border=True):
        col_icon, col_title = st.columns([1, 15])
        with col_icon:
            st.markdown("🩹") # Placeholder icon if render_icon not available or simple emoji preferred
        with col_title:
            st.markdown("### Recomendaciones al Paciente")
        
        st.info("💡 **Por favor, transmita estas indicaciones al paciente mientras espera:**")
        
        for rec in recommendations:
            st.markdown(f"- {rec}")
            
        # Placeholder for future print functionality
        # st.button("🖨️ Imprimir Hoja de Recomendaciones", key="print_rec_btn", disabled=True)

        st.markdown('<div class="debug-footer">src/components/triage/recommendations_card.py</div>', unsafe_allow_html=True)
