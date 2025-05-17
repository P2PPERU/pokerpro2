"""
Definición de temas y paletas de colores para PokerBot TRACK
"""
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt

# Paleta oscura (predeterminada)
DARK = {
    # Colores base
    "bg_primary": "#121212",       # Fondo base
    "bg_secondary": "#1E1E1E",     # Fondo secundario
    "surface": "#262626",          # Superficie UI (tarjetas)
    "border": "#333333",           # Bordes y divisores
    
    # Acentos
    "primary": "#2D7FF9",          # Azul vibrante (color principal)
    "primary_hover": "#1E6FE6",    # Variante hover del color principal
    "primary_pressed": "#0F5FD3",  # Variante presionada del color principal
    
    "success": "#00C853",          # Verde brillante
    "success_hover": "#00B34A",    # Variante hover del verde
    "success_pressed": "#009E42",  # Variante presionada del verde
    
    "warning": "#FF9500",          # Naranja
    "warning_hover": "#F08200",    # Variante hover del naranja
    "warning_pressed": "#E17000",  # Variante presionada del naranja
    
    "danger": "#F03E3E",           # Rojo
    "danger_hover": "#E12D2D",     # Variante hover del rojo
    "danger_pressed": "#D21C1C",   # Variante presionada del rojo
    
    "info": "#50B5FF",             # Azul claro
    "info_hover": "#40A5F0",       # Variante hover del azul claro
    "info_pressed": "#3095E0",     # Variante presionada del azul claro
    
    # Tonos de gris
    "gray_100": "#F5F5F5",         # Gris muy claro
    "gray_200": "#E0E0E0",         # Gris claro
    "gray_300": "#CCCCCC",         # Gris medio-claro
    "gray_400": "#AAAAAA",         # Gris medio
    "gray_500": "#888888",         # Gris medio-oscuro
    "gray_600": "#666666",         # Gris oscuro
    "gray_700": "#444444",         # Gris muy oscuro
    "gray_800": "#333333",         # Casi negro
    
    # Textos
    "text_primary": "#FFFFFF",     # Texto principal
    "text_secondary": "#AAAAAA",   # Texto secundario
    "text_disabled": "#666666",    # Texto deshabilitado
    
    # Estados
    "disabled": "#555555",         # Fondo deshabilitado
    "highlight": "#3D5AFE",        # Resaltado de selección
    "overlay": "#000000CC"         # Overlay para modales (con transparencia)
}

# Paleta clara
LIGHT = {
    # Colores base
    "bg_primary": "#F8F9FA",       # Fondo base
    "bg_secondary": "#FFFFFF",     # Fondo secundario
    "surface": "#FFFFFF",          # Superficie UI (tarjetas)
    "border": "#E0E0E0",           # Bordes y divisores
    
    # Acentos (mismos que en oscuro para mantener identidad)
    "primary": "#2D7FF9",          # Azul vibrante (color principal)
    "primary_hover": "#1E6FE6",    # Variante hover del color principal
    "primary_pressed": "#0F5FD3",  # Variante presionada del color principal
    
    "success": "#00C853",          # Verde brillante
    "success_hover": "#00B34A",    # Variante hover del verde
    "success_pressed": "#009E42",  # Variante presionada del verde
    
    "warning": "#FF9500",          # Naranja
    "warning_hover": "#F08200",    # Variante hover del naranja
    "warning_pressed": "#E17000",  # Variante presionada del naranja
    
    "danger": "#F03E3E",           # Rojo
    "danger_hover": "#E12D2D",     # Variante hover del rojo
    "danger_pressed": "#D21C1C",   # Variante presionada del rojo
    
    "info": "#50B5FF",             # Azul claro
    "info_hover": "#40A5F0",       # Variante hover del azul claro
    "info_pressed": "#3095E0",     # Variante presionada del azul claro
    
    # Tonos de gris
    "gray_100": "#F5F5F5",         # Gris muy claro
    "gray_200": "#E0E0E0",         # Gris claro
    "gray_300": "#CCCCCC",         # Gris medio-claro
    "gray_400": "#AAAAAA",         # Gris medio
    "gray_500": "#888888",         # Gris medio-oscuro
    "gray_600": "#666666",         # Gris oscuro
    "gray_700": "#444444",         # Gris muy oscuro
    "gray_800": "#333333",         # Casi negro
    
    # Textos
    "text_primary": "#212121",     # Texto principal
    "text_secondary": "#666666",   # Texto secundario
    "text_disabled": "#AAAAAA",    # Texto deshabilitado
    
    # Estados
    "disabled": "#E0E0E0",         # Fondo deshabilitado
    "highlight": "#3D5AFE",        # Resaltado de selección
    "overlay": "#00000066"         # Overlay para modales (con transparencia)
}

# Tema actual
current_theme = DARK

def get_theme():
    """Obtiene el tema actual"""
    return current_theme

def set_theme(theme_name):
    """Establece el tema actual"""
    global current_theme
    
    if theme_name.lower() == "dark":
        current_theme = DARK
    elif theme_name.lower() == "light":
        current_theme = LIGHT
    else:
        raise ValueError(f"Tema no válido: {theme_name}")

def apply_theme(app, theme_name="dark"):
    """
    Aplica el tema especificado a toda la aplicación
    
    Args:
        app: La instancia de QApplication
        theme_name: Nombre del tema a aplicar ("dark" o "light")
    """
    set_theme(theme_name)
    theme = get_theme()
    
    # Crear paleta según el tema
    palette = QPalette()
    
    if theme_name.lower() == "dark":
        # Configurar paleta oscura
        palette.setColor(QPalette.Window, QColor(theme["bg_primary"]))
        palette.setColor(QPalette.WindowText, QColor(theme["text_primary"]))
        palette.setColor(QPalette.Base, QColor(theme["bg_secondary"]))
        palette.setColor(QPalette.AlternateBase, QColor(theme["surface"]))
        palette.setColor(QPalette.ToolTipBase, QColor(theme["bg_secondary"]))
        palette.setColor(QPalette.ToolTipText, QColor(theme["text_primary"]))
        palette.setColor(QPalette.Text, QColor(theme["text_primary"]))
        palette.setColor(QPalette.Button, QColor(theme["surface"]))
        palette.setColor(QPalette.ButtonText, QColor(theme["text_primary"]))
        palette.setColor(QPalette.BrightText, QColor("#FFFFFF"))
        palette.setColor(QPalette.Link, QColor(theme["primary"]))
        palette.setColor(QPalette.Highlight, QColor(theme["primary"]))
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(theme["text_disabled"]))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(theme["text_disabled"]))
    else:
        # Configurar paleta clara
        palette.setColor(QPalette.Window, QColor(theme["bg_primary"]))
        palette.setColor(QPalette.WindowText, QColor(theme["text_primary"]))
        palette.setColor(QPalette.Base, QColor(theme["bg_secondary"]))
        palette.setColor(QPalette.AlternateBase, QColor(theme["surface"]))
        palette.setColor(QPalette.ToolTipBase, QColor(theme["bg_secondary"]))
        palette.setColor(QPalette.ToolTipText, QColor(theme["text_primary"]))
        palette.setColor(QPalette.Text, QColor(theme["text_primary"]))
        palette.setColor(QPalette.Button, QColor(theme["surface"]))
        palette.setColor(QPalette.ButtonText, QColor(theme["text_primary"]))
        palette.setColor(QPalette.BrightText, QColor("#000000"))
        palette.setColor(QPalette.Link, QColor(theme["primary"]))
        palette.setColor(QPalette.Highlight, QColor(theme["primary"]))
        palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(theme["text_disabled"]))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(theme["text_disabled"]))
    
    # Aplicar paleta
    app.setPalette(palette)
    
    # También actualizamos el stylesheet global de la aplicación
    from src.ui.styles.stylesheet import generate_global_stylesheet
    app.setStyleSheet(generate_global_stylesheet())

def get_color(name):
    """
    Obtiene un color del tema actual por su nombre
    
    Args:
        name: Nombre del color a obtener
        
    Returns:
        Color como cadena hexadecimal
    """
    return current_theme.get(name, "#000000")  # Negro por defecto