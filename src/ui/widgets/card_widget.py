"""
Widget tipo tarjeta con sombras y esquinas redondeadas para UI moderna
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QGraphicsDropShadowEffect, QLabel, QWidget
from PySide6.QtCore import Qt, QPropertyAnimation, Property, QPoint, QEasingCurve
from PySide6.QtGui import QColor

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.ui.styles.theme import get_theme, get_color
from src.ui.styles.constants import *
from src.ui.styles.stylesheet import generate_component_stylesheet

class CardWidget(QFrame):
    """
    Widget tipo tarjeta con sombras y bordes redondeados
    
    Una tarjeta es un contenedor visual que agrupa elementos relacionados
    y proporciona una jerarquía visual clara.
    """
    
    def __init__(self, title=None, parent=None, show_shadow=True, elevation=2):
        """
        Inicializa un widget tipo tarjeta
        
        Args:
            title: Título opcional de la tarjeta
            parent: Widget padre
            show_shadow: Si se debe mostrar sombra
            elevation: Nivel de elevación (1=bajo, 2=medio, 3=alto)
        """
        super().__init__(parent)
        
        # Propiedades
        self._title = title
        self._show_shadow = show_shadow
        self._elevation = elevation
        self._hover_enabled = True
        self._current_elevation = float(elevation)
        
        # Configurar objeto
        self.setObjectName("card")
        self.setContentsMargins(0, 0, 0, 0)
        
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Titulo (si se especificó)
        if title:
            self.title_label = QLabel(title)
            self.title_label.setObjectName("card-title")
            self.main_layout.addWidget(self.title_label)
        
        # Contenedor de contenido
        self.content_widget = QWidget()
        self.content_widget.setObjectName("card-content")
        
        # Layout para el contenido
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(PADDING_MEDIUM, PADDING_MEDIUM, PADDING_MEDIUM, PADDING_MEDIUM)
        self.content_layout.setSpacing(PADDING_SMALL)
        
        # Añadir contenedor al layout principal
        self.main_layout.addWidget(self.content_widget)
        
        # Aplicar sombra
        self.update_shadow()
        
        # Aplicar hoja de estilos
        self.setStyleSheet(generate_component_stylesheet("CardWidget"))
        
        # Configurar animaciones
        self._setup_animations()
        
        # Seguir eventos del ratón para animaciones
        self.setMouseTracking(True)
    
    def update_shadow(self):
        """Actualiza la sombra según la configuración"""
        if self._show_shadow:
            shadow = QGraphicsDropShadowEffect(self)
            
            # Ajustar según elevación
            if self._elevation == 1:
                shadow.setBlurRadius(10)
                shadow.setOffset(0, 3)
                shadow.setColor(QColor(0, 0, 0, 60))
            elif self._elevation == 2:
                shadow.setBlurRadius(15)
                shadow.setOffset(0, 4)
                shadow.setColor(QColor(0, 0, 0, 80))
            else:  # 3 o mayor
                shadow.setBlurRadius(25)
                shadow.setOffset(0, 6)
                shadow.setColor(QColor(0, 0, 0, 100))
            
            self.setGraphicsEffect(shadow)
        else:
            self.setGraphicsEffect(None)
    
    def _setup_animations(self):
        """Configura animaciones para hover y clic"""
        # Animación para hover
        self._shadow_animation = QPropertyAnimation(self, b"elevation")
        self._shadow_animation.setDuration(ANIMATION_DURATION_FAST)
        self._shadow_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Propiedad de elevación
        self._current_elevation = float(self._elevation)
    
    # Propiedades animadas
    def _get_elevation(self):
        return self._current_elevation
    
    def _set_elevation(self, value):
        self._current_elevation = value
        # Actualizar elevación visualmente - simulamos con margen
        self.setContentsMargins(0, 0, 0, int(value))
        # También podríamos actualizar la sombra, pero es más costoso
    
    elevation = Property(float, _get_elevation, _set_elevation)
    
    def enterEvent(self, event):
        """Maneja el evento de entrada del ratón"""
        if self._hover_enabled:
            # Animar elevación en hover
            self._shadow_animation.stop()
            self._shadow_animation.setStartValue(self._current_elevation)
            self._shadow_animation.setEndValue(self._elevation + 1.0)
            self._shadow_animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Maneja el evento de salida del ratón"""
        if self._hover_enabled:
            # Volver a elevación normal
            self._shadow_animation.stop()
            self._shadow_animation.setStartValue(self._current_elevation)
            self._shadow_animation.setEndValue(float(self._elevation))
            self._shadow_animation.start()
        super().leaveEvent(event)
    
    def set_title(self, title):
        """Cambia el título de la tarjeta"""
        if hasattr(self, 'title_label'):
            self.title_label.setText(title)
        else:
            # Crear nuevo label de título
            self.title_label = QLabel(title)
            self.title_label.setObjectName("card-title")
            self.main_layout.insertWidget(0, self.title_label)
        self._title = title
    
    def set_hover_enabled(self, enabled):
        """Habilita o deshabilita el efecto hover"""
        self._hover_enabled = enabled
    
    def set_elevation(self, elevation):
        """Cambia la elevación de la tarjeta"""
        self._elevation = elevation
        self._current_elevation = float(elevation)
        self.update_shadow()
    
    def set_shadow_visible(self, visible):
        """Muestra u oculta la sombra"""
        self._show_shadow = visible
        self.update_shadow()