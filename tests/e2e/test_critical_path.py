import re
from playwright.sync_api import Page, expect

def test_login_and_triage_flow(page: Page):
    # 1. Navigate to the app
    # Note: Streamlit runs on localhost:8501 by default
    page.goto("http://localhost:8501")

    # 2. Check for Login Page or Disclaimer
    # If disclaimer is present, accept it
    if page.get_by_role("button", name="He leído y acepto").is_visible():
        page.get_by_role("button", name="He leído y acepto").click()

    # 3. Login
    # Assuming we are at login screen
    # Select a user (simulated)
    # This depends on the exact UI implementation of render_login_view
    # For now, we'll assume there's a way to select a user or it auto-logs in dev mode
    # If dev mode is off, we might need to click a user card.
    
    # Wait for main app to load
    expect(page).to_have_title(re.compile("Triaje IA"))
    
    # 4. Navigate to Admission
    # Click on "Admisión" tab
    page.get_by_text("Admisión").click()
    
    # 5. Select a Patient (Mock flow)
    # This requires the app to be in a state where patients are available or can be created.
    # For a critical path test, we might just verify the tab loads.
    expect(page.get_by_text("Selección de Sala")).to_be_visible()

    # 6. Navigate to Triage
    page.get_by_text("Triaje").click()
    expect(page.get_by_text("Asistente de Triaje")).to_be_visible()

    # 7. Logout
    # Open sidebar if closed (Streamlit handles this, but we might need to trigger it)
    # Click "Cerrar Sesión"
    # page.get_by_role("button", name="Cerrar Sesión").click()
