"""
Generador de hojas de estilo QSS para PokerBot TRACK
Crea estilos dinámicos basados en el tema actual
"""

import os
from src.ui.styles.theme import get_theme, get_color
from src.ui.styles.constants import *

def generate_global_stylesheet():
    """
    Genera la hoja de estilo global para toda la aplicación
    basada en el tema actual
    
    Returns:
        str: Hoja de estilo QSS completa
    """
    theme = get_theme()
    
    # Estilos globales
    stylesheet = f"""
    /* Estilos globales */
    QWidget {{
        background-color: {theme["bg_primary"]};
        color: {theme["text_primary"]};
        font-family: 'Segoe UI', 'Roboto', sans-serif;
        font-size: {FONT_SIZE_MEDIUM}px;
    }}
    
    /* QMainWindow y QDialog */
    QMainWindow, QDialog {{
        background-color: {theme["bg_primary"]};
    }}
    
    /* QLabel */
    QLabel {{
        color: {theme["text_primary"]};
        padding: {PADDING_TINY}px;
    }}
    
    QLabel[heading="true"] {{
        font-size: {FONT_SIZE_LARGE}px;
        font-weight: {FONT_WEIGHT_BOLD};
        color: {theme["primary"]};
    }}
    
    QLabel[subheading="true"] {{
        font-size: {FONT_SIZE_MEDIUM}px;
        color: {theme["text_secondary"]};
    }}
    
    /* QPushButton */
    QPushButton {{
        background-color: {theme["surface"]};
        color: {theme["text_primary"]};
        border: 1px solid {theme["border"]};
        border-radius: {BORDER_RADIUS_SMALL}px;
        padding: {PADDING_SMALL}px {PADDING_MEDIUM}px;
        min-height: {WIDGET_HEIGHT_MEDIUM}px;
        outline: none;
    }}
    
    QPushButton:hover {{
        background-color: {theme["primary_hover"]};
        color: white;
    }}
    
    QPushButton:pressed {{
        background-color: {theme["primary_pressed"]};
    }}
    
    QPushButton:disabled {{
        background-color: {theme["disabled"]};
        color: {theme["text_disabled"]};
    }}
    
    QPushButton[primary="true"] {{
        background-color: {theme["primary"]};
        color: white;
        border: none;
    }}
    
    QPushButton[success="true"] {{
        background-color: {theme["success"]};
        color: white;
        border: none;
    }}
    
    QPushButton[warning="true"] {{
        background-color: {theme["warning"]};
        color: white;
        border: none;
    }}
    
    QPushButton[danger="true"] {{
        background-color: {theme["danger"]};
        color: white;
        border: none;
    }}
    
    QPushButton[info="true"] {{
        background-color: {theme["info"]};
        color: white;
        border: none;
    }}
    
    QPushButton[flat="true"] {{
        background-color: transparent;
        border: none;
    }}
    
    /* QLineEdit */
    QLineEdit {{
        background-color: {theme["bg_secondary"]};
        color: {theme["text_primary"]};
        border: 1px solid {theme["border"]};
        border-radius: {BORDER_RADIUS_SMALL}px;
        padding: {PADDING_SMALL}px;
        min-height: {WIDGET_HEIGHT_MEDIUM}px;
        selection-background-color: {theme["primary"]};
    }}
    
    QLineEdit:focus {{
        border: 1px solid {theme["primary"]};
    }}
    
    QLineEdit:disabled {{
        background-color: {theme["disabled"]};
        color: {theme["text_disabled"]};
    }}
    
    /* QComboBox */
    QComboBox {{
        background-color: {theme["bg_secondary"]};
        color: {theme["text_primary"]};
        border: 1px solid {theme["border"]};
        border-radius: {BORDER_RADIUS_SMALL}px;
        padding: {PADDING_SMALL}px;
        min-height: {WIDGET_HEIGHT_MEDIUM}px;
        padding-right: 20px;  /* Espacio para la flecha */
    }}
    
    QComboBox::drop-down {{
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left: 1px solid {theme["border"]};
    }}
    
    QComboBox::down-arrow {{
        image: url({get_dropdown_arrow_path()});
        width: 12px;
        height: 12px;
    }}
    
    QComboBox QAbstractItemView {{
        background-color: {theme["bg_secondary"]};
        color: {theme["text_primary"]};
        border: 1px solid {theme["border"]};
        selection-background-color: {theme["primary"]};
        selection-color: white;
    }}
    
    /* QCheckBox */
    QCheckBox {{
        spacing: 8px;
    }}
    
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border: 1px solid {theme["border"]};
        border-radius: {BORDER_RADIUS_SMALL / 2}px;
        background-color: {theme["bg_secondary"]};
    }}
    
    QCheckBox::indicator:checked {{
        background-color: {theme["primary"]};
        border: 1px solid {theme["primary"]};
        image: url({get_checkbox_path()});
    }}
    
    QCheckBox::indicator:unchecked:hover {{
        border: 1px solid {theme["primary"]};
    }}
    
    /* QGroupBox */
    QGroupBox {{
        background-color: {theme["surface"]};
        border: 1px solid {theme["border"]};
        border-radius: {BORDER_RADIUS_MEDIUM}px;
        margin-top: 1em;
        padding-top: 1.5em;
    }}
    
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        background-color: {theme["primary"]};
        color: white;
        padding: 5px 10px;
        border-radius: {BORDER_RADIUS_SMALL}px;
    }}
    
    /* QTabWidget */
    QTabWidget::pane {{
        border: 1px solid {theme["border"]};
        border-radius: {BORDER_RADIUS_SMALL}px;
        top: -1px;
    }}
    
    QTabBar::tab {{
        background-color: {theme["bg_secondary"]};
        color: {theme["text_primary"]};
        border: 1px solid {theme["border"]};
        border-bottom: none;
        border-top-left-radius: {BORDER_RADIUS_SMALL}px;
        border-top-right-radius: {BORDER_RADIUS_SMALL}px;
        min-width: 80px;
        padding: {PADDING_SMALL}px {PADDING_MEDIUM}px;
    }}
    
    QTabBar::tab:selected {{
        background-color: {theme["primary"]};
        color: white;
    }}
    
    QTabBar::tab:!selected:hover {{
        background-color: {theme["primary_hover"]};
        color: white;
    }}
    
    /* QTableWidget */
    QTableWidget {{
        background-color: {theme["bg_secondary"]};
        color: {theme["text_primary"]};
        gridline-color: {theme["border"]};
        border: none;
        border-radius: {BORDER_RADIUS_SMALL}px;
    }}
    
    QTableWidget::item {{
        padding: {PADDING_SMALL}px;
        border: none;
    }}
    
    QTableWidget::item:selected {{
        background-color: {theme["primary"]};
        color: white;
    }}
    
    QHeaderView::section {{
        background-color: {theme["surface"]};
        color: {theme["text_primary"]};
        padding: {PADDING_SMALL}px;
        border: none;
        border-right: 1px solid {theme["border"]};
        border-bottom: 1px solid {theme["border"]};
    }}
    
    QHeaderView::section:checked {{
        background-color: {theme["primary"]};
        color: white;
    }}
    
    /* QScrollBar */
    QScrollBar:vertical {{
        background: {theme["bg_secondary"]};
        width: 12px;
        margin: 0px;
    }}
    
    QScrollBar::handle:vertical {{
        background: {theme["gray_600"]};
        min-height: 20px;
        border-radius: 5px;
        margin: 2px;
    }}
    
    QScrollBar::handle:vertical:hover {{
        background: {theme["gray_500"]};
    }}
    
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        background: none;
        height: 0px;
    }}
    
    QScrollBar:horizontal {{
        background: {theme["bg_secondary"]};
        height: 12px;
        margin: 0px;
    }}
    
    QScrollBar::handle:horizontal {{
        background: {theme["gray_600"]};
        min-width: 20px;
        border-radius: 5px;
        margin: 2px;
    }}
    
    QScrollBar::handle:horizontal:hover {{
        background: {theme["gray_500"]};
    }}
    
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        background: none;
        width: 0px;
    }}
    
    /* QProgressBar */
    QProgressBar {{
        border: 1px solid {theme["border"]};
        border-radius: {BORDER_RADIUS_MEDIUM}px;
        background-color: {theme["bg_secondary"]};
        text-align: center;
        color: {theme["text_primary"]};
    }}
    
    QProgressBar::chunk {{
        background-color: {theme["primary"]};
        border-radius: {BORDER_RADIUS_MEDIUM}px;
    }}
    
    /* QMenu */
    QMenu {{
        background-color: {theme["bg_secondary"]};
        color: {theme["text_primary"]};
        border: 1px solid {theme["border"]};
        border-radius: {BORDER_RADIUS_SMALL}px;
    }}
    
    QMenu::item {{
        padding: {PADDING_SMALL}px {PADDING_MEDIUM}px;
    }}
    
    QMenu::item:selected {{
        background-color: {theme["primary"]};
        color: white;
    }}
    
    QMenu::separator {{
        height: 1px;
        background-color: {theme["border"]};
        margin: 4px 0px;
    }}
    
    /* QStatusBar */
    QStatusBar {{
        background-color: {theme["bg_secondary"]};
        color: {theme["text_primary"]};
        border-top: 1px solid {theme["border"]};
    }}
    
    /* QToolBar */
    QToolBar {{
        background-color: {theme["bg_secondary"]};
        border-bottom: 1px solid {theme["border"]};
        spacing: 4px;
    }}
    
    QToolBar::separator {{
        width: 1px;
        background-color: {theme["border"]};
        margin: 0px 8px;
    }}
    
    /* QToolTip */
    QToolTip {{
        background-color: {theme["bg_secondary"]};
        color: {theme["text_primary"]};
        border: 1px solid {theme["border"]};
        border-radius: {BORDER_RADIUS_SMALL}px;
        padding: {PADDING_SMALL}px;
    }}
    
    /* QFrame */
    QFrame[frameShape="4"] {{  /* HLine */
        background-color: {theme["border"]};
        max-height: 1px;
    }}
    
    QFrame[frameShape="5"] {{  /* VLine */
        background-color: {theme["border"]};
        max-width: 1px;
    }}
    """
    
    return stylesheet

def get_resource_path(folder, filename):
    """
    Obtiene la ruta a un recurso de la aplicación
    
    Args:
        folder: Carpeta del recurso
        filename: Nombre del archivo
        
    Returns:
        str: Ruta completa al recurso
    """
    # En el futuro se podría implementar un sistema más complejo de recursos
    # Por ahora, usamos rutas relativas
    base_path = os.path.join("assets", folder)
    return os.path.join(base_path, filename)

def get_dropdown_arrow_path():
    """Ruta al ícono de flecha para QComboBox"""
    path = get_resource_path("icons", "dropdown_arrow.svg")
    if os.path.exists(path):
        return path
    else:
        print("[WARNING] Icono 'dropdown_arrow.svg' no encontrado.")
        return ""  # Evita que se rompa el QSS


def get_checkbox_path():
    """Obtiene la ruta al icono de checkmark para QCheckBox"""
    # Por ahora devolvemos un valor ficticio
    # En la implementación real deberás tener estos iconos
    return get_resource_path("icons", "check.svg")

def generate_component_stylesheet(component_name):
    """
    Genera una hoja de estilo para un componente específico
    
    Args:
        component_name: Nombre del componente (ej. 'CardWidget')
        
    Returns:
        str: Hoja de estilo QSS para el componente
    """
    theme = get_theme()
    
    if component_name == "CardWidget":
        return f"""
        #card {{
            background-color: {theme["surface"]};
            border: 1px solid {theme["border"]};
            border-radius: {BORDER_RADIUS_MEDIUM}px;
        }}
        
        #card-title {{
            color: {theme["primary"]};
            font-size: {FONT_SIZE_LARGE}px;
            font-weight: {FONT_WEIGHT_BOLD};
            padding: {PADDING_SMALL}px {PADDING_MEDIUM}px;
            border-bottom: 1px solid {theme["border"]};
        }}
        
        #card-content {{
            padding: {PADDING_MEDIUM}px;
        }}
        """
    
    elif component_name == "ModernButton":
        return f"""
        #modern-button {{
            background-color: {theme["primary"]};
            color: white;
            border: none;
            border-radius: {BORDER_RADIUS_SMALL}px;
            padding: {PADDING_SMALL}px {PADDING_MEDIUM}px;
            min-height: {WIDGET_HEIGHT_MEDIUM}px;
            font-weight: {FONT_WEIGHT_MEDIUM};
        }}
        
        #modern-button:hover {{
            background-color: {theme["primary_hover"]};
        }}
        
        #modern-button:pressed {{
            background-color: {theme["primary_pressed"]};
        }}
        
        #modern-button:disabled {{
            background-color: {theme["disabled"]};
            color: {theme["text_disabled"]};
        }}
        
        #modern-button[success="true"] {{
            background-color: {theme["success"]};
        }}
        
        #modern-button[success="true"]:hover {{
            background-color: {theme["success_hover"]};
        }}
        
        #modern-button[success="true"]:pressed {{
            background-color: {theme["success_pressed"]};
        }}
        
        #modern-button[warning="true"] {{
            background-color: {theme["warning"]};
        }}
        
        #modern-button[warning="true"]:hover {{
            background-color: {theme["warning_hover"]};
        }}
        
        #modern-button[warning="true"]:pressed {{
            background-color: {theme["warning_pressed"]};
        }}
        
        #modern-button[danger="true"] {{
            background-color: {theme["danger"]};
        }}
        
        #modern-button[danger="true"]:hover {{
            background-color: {theme["danger_hover"]};
        }}
        
        #modern-button[danger="true"]:pressed {{
            background-color: {theme["danger_pressed"]};
        }}
        
        #modern-button[info="true"] {{
            background-color: {theme["info"]};
        }}
        
        #modern-button[info="true"]:hover {{
            background-color: {theme["info_hover"]};
        }}
        
        #modern-button[info="true"]:pressed {{
            background-color: {theme["info_pressed"]};
        }}
        
        #modern-button[flat="true"] {{
            background-color: transparent;
            color: {theme["primary"]};
        }}
        
        #modern-button[flat="true"]:hover {{
            background-color: rgba(45, 127, 249, 0.1);
            color: {theme["primary_hover"]};
        }}
        """
    
    elif component_name == "StatusIndicator":
        return f"""
        #status-indicator {{
            border: none;
            border-radius: {BORDER_RADIUS_CIRCLE}px;
            min-width: 12px;
            min-height: 12px;
            max-width: 12px;
            max-height: 12px;
        }}
        
        #status-indicator[status="active"] {{
            background-color: {theme["success"]};
        }}
        
        #status-indicator[status="inactive"] {{
            background-color: {theme["danger"]};
        }}
        
        #status-indicator[status="warning"] {{
            background-color: {theme["warning"]};
        }}
        
        #status-indicator[status="info"] {{
            background-color: {theme["info"]};
        }}
        
        #status-container {{
            border: none;
            background-color: transparent;
        }}
        
        #status-label {{
            color: {theme["text_primary"]};
            margin-left: 4px;
        }}
        """
    
    elif component_name == "ToastNotification":
        return f"""
        #toast {{
            background-color: {theme["surface"]};
            color: {theme["text_primary"]};
            border: 1px solid {theme["border"]};
            border-radius: {BORDER_RADIUS_MEDIUM}px;
            padding: {PADDING_MEDIUM}px;
        }}
        
        #toast[type="success"] {{
            background-color: {theme["success"]};
            color: white;
            border: none;
        }}
        
        #toast[type="warning"] {{
            background-color: {theme["warning"]};
            color: white;
            border: none;
        }}
        
        #toast[type="error"] {{
            background-color: {theme["danger"]};
            color: white;
            border: none;
        }}
        
        #toast[type="info"] {{
            background-color: {theme["info"]};
            color: white;
            border: none;
        }}
        
        #toast-title {{
            font-weight: {FONT_WEIGHT_BOLD};
            font-size: {FONT_SIZE_MEDIUM}px;
        }}
        
        #toast-message {{
            font-size: {FONT_SIZE_SMALL}px;
        }}
        """
    
    # Por defecto, devolver una cadena vacía
    return ""