"""
Botón con iconos SVG estilizados
"""

from PySide6.QtWidgets import QPushButton, QGraphicsColorizeEffect
from PySide6.QtCore import QSize, Qt, QPropertyAnimation, Property, QEasingCurve
from PySide6.QtGui import QIcon, QColor

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.ui.styles.theme import get_theme, get_color
from src.ui.styles.constants import *

class IconButton(QPushButton):
    """
    Botón con icono SVG estilizado
    
    Proporciona cambios de color dinámicos y animaciones para iconos SVG,
    ideal para botones de acción compactos.
    """
    
    def __init__(self, icon_path=None, tooltip="", parent=None, size=ICON_SIZE_MEDIUM,
                 color_normal=None, color_hover=None, color_pressed=None, variant="primary"):
        """
        Inicializa un botón con icono
        
        Args:
            icon_path: Ruta al icono SVG
            tooltip: Texto descriptivo al poner el cursor encima
            parent: Widget padre
            size: Tamaño del botón (ICON_SIZE_SMALL, ICON_SIZE_MEDIUM, ICON_SIZE_LARGE)
            color_normal: Color normal del icono (None para usar el tema)
            color_hover: Color hover del icono (None para usar el tema)
            color_pressed: Color de presionado del icono (None para usar el tema)
            variant: Variante de color ('primary', 'success', 'warning', 'danger', 'info')
        """
        super().__init__(parent)
        
        # Propiedades
        self._icon_path = icon_path
        self._size = size
        self._variant = variant
        
        # Obtener colores del tema si no se especificaron
        theme = get_theme()
        self._color_normal = color_normal or get_color(variant)
        self._color_hover = color_hover or get_color(f"{variant}_hover")
        self._color_pressed = color_pressed or get_color(f"{variant}_pressed")
        
        # Configuración del botón
        self.setToolTip(tooltip)
        self.setCursor(Qt.PointingHandCursor)
        self.setFlat(True)
        
        # Establecer tamaño fijo
        self.setFixedSize(size, size)
        self.setIconSize(QSize(size - 4, size - 4))  # Icono un poco más pequeño que el botón
        
        # Cargar icono si se proporcionó
        if icon_path:
            self.setIcon(QIcon(icon_path))
        
        # Efecto de colorización para el icono
        self._color_effect = QGraphicsColorizeEffect(self)
        self._color_effect.setColor(QColor(self._color_normal))
        self.setGraphicsEffect(self._color_effect)
        
        # Sin borde y transparente
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                padding: 0px;
            }}
            
            QPushButton:hover {{
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: {BORDER_RADIUS_SMALL}px;
            }}
            
            QPushButton:pressed {{
                background-color: rgba(0, 0, 0, 0.2);
            }}
        """)
        
        # Configurar animaciones
        self._setup_animations()
    
    def _setup_animations(self):
        """Configura animaciones de color"""
        # Valor actual de color
        self._current_color = self._color_normal
        
        # Animación de color
        self._color_animation = QPropertyAnimation(self, b"iconColor")
        self._color_animation.setDuration(ANIMATION_DURATION_FAST)
        self._color_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    # Propiedades para animar color del icono
    def _get_icon_color(self):
        return self._current_color
    
    def _set_icon_color(self, color_str):
        self._current_color = color_str
        self._color_effect.setColor(QColor(color_str))
    
    iconColor = Property(str, _get_icon_color, _set_icon_color)
    
    def enterEvent(self, event):
        """Maneja el evento de entrada del ratón"""
        # Animar cambio de color a hover
        self._color_animation.stop()
        self._color_animation.setStartValue(self._current_color)
        self._color_animation.setEndValue(self._color_hover)
        self._color_animation.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Maneja el evento de salida del ratón"""
        # Animar cambio de color a normal
        self._color_animation.stop()
        self._color_animation.setStartValue(self._current_color)
        self._color_animation.setEndValue(self._color_normal)
        self._color_animation.start()
        
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Maneja el evento de presionar el botón"""
        if event.button() == Qt.LeftButton:
            # Cambiar a color presionado inmediatamente
            self._color_animation.stop()
            self._color_animation.setStartValue(self._current_color)
            self._color_animation.setEndValue(self._color_pressed)
            self._color_animation.start()
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Maneja el evento de soltar el botón"""
        if event.button() == Qt.LeftButton:
            # Volver a color hover si está dentro, o normal si está fuera
            color_end = self._color_hover if self.rect().contains(event.position().toPoint()) else self._color_normal
            
            self._color_animation.stop()
            self._color_animation.setStartValue(self._current_color)
            self._color_animation.setEndValue(color_end)
            self._color_animation.start()
        
        super().mouseReleaseEvent(event)
    
    def set_icon(self, icon_path):
        """Cambia el icono del botón"""
        self._icon_path = icon_path
        self.setIcon(QIcon(icon_path))
    
    def set_colors(self, normal=None, hover=None, pressed=None):
        """Cambia los colores del icono"""
        if normal:
            self._color_normal = normal
        if hover:
            self._color_hover = hover
        if pressed:
            self._color_pressed = pressed
        
        # Actualizar color actual
        self._current_color = self._color_normal
        self._color_effect.setColor(QColor(self._color_normal))
    
    def set_variant(self, variant):
        """Cambia la variante de color del botón"""
        self._variant = variant
        
        # Actualizar colores
        self._color_normal = get_color(variant)
        self._color_hover = get_color(f"{variant}_hover")
        self._color_pressed = get_color(f"{variant}_pressed")
        
        # Actualizar color actual
        self._current_color = self._color_normal
        self._color_effect.setColor(QColor(self._color_normal))