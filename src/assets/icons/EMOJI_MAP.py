# Mapeo de Emojis a Iconos SVG
# Este archivo documenta el reemplazo de emojis por iconos SVG Material Design

EMOJI_TO_ICON_MAP = {
    # Iconos de estado
    "🟢": ("circle", "#4CAF50"),  # Verde - activo
    "🔴": ("circle", "#F44336"),  # Rojo - inactivo
    "⚫": ("circle", "#757575"),  # Gris - deprecated
    
    # Iconos de acción
    "🗑️": "delete",
    "✏️": "edit",
    "📁": "folder",
    "✅": "check_circle",
    "❌": "cancel",
    "⚠️": "warning",
    
    # Iconos de tipo de sala/función
    "📋": "clipboard",
    "🏥": "medical",
    "⏳": "schedule",
    "🚪": "target",  # o "door" si se crea
    "🔧": "build",
    
    # Iconos de comunicación
    "📧": "email",
    "📞": "phone",
    "📍": "location",
    "🎤": "mic",
    "🗣️": "record_voice",
    
    # Iconos de usuario/persona
    "🤖": "robot",
    "👤": "person",
    
    # Iconos de análisis/datos
    "📊": "bar_chart",
    "🔍": "search",
    "🕵️": "search",
    
    # Iconos de tiempo/calendario
    "🕒": "schedule",
    "📅": "event",
    
    # Iconos de documento/nota
    "📝": "note",
    "💾": "save",
    
    # Iconos de prueba/ciencia
    "🧪": "science",
    
    # Iconos de lanzamiento/activación
    "🚀": "rocket",
    
    # Iconos de feedback
    "👍": "thumb_up",
    "👎": "thumb_down",
    
    # Iconos de herramientas
    "🛠️": "build",
}

# Uso:
# render_icon("circle", size=16, color="#4CAF50")  # Para 🟢
# render_icon("delete", size=20)  # Para 🗑️
