"""
Indicador visual para mostrar estados con animaciones
"""

from PySide6.QtWidgets import QWidget, QFrame, QHBoxLayout, QLabel
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Property, QTimer, Qt
from PySide6.QtGui import QColor, QPainter, QPen

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.ui.styles.theme import get_theme, get_color
from src.ui.styles.constants import *
from src.ui.styles.stylesheet import generate_component_stylesheet

class StatusIndicator(QWidget):
    """
    Indicador visual de estado con animación de pulso
    
    Muestra el estado mediante un círculo de color con animación
    opcional y una etiqueta descriptiva.
    """
    
    def __init__(self, status="inactive", text=None, parent=None, animate=False):
        """
        Inicializa un indicador de estado
        
        Args:
            status: Estado inicial ('active', 'inactive', 'warning', 'info')
            text: Texto descriptivo opcional
            parent: Widget padre
            animate: Si se debe animar el indicador (pulso)
        """
        super().__init__(parent)
        
        # Propiedades
        self._status = status
        self._text = text
        self._animate = animate
        self._pulse_scale = 1.0
        
        # Configuración del widget
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumWidth(16)  # Ancho mínimo del indicador
        
        # Layout principal
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Contenedor del indicador (para centrado y tamaño)
        self.indicator_container = QFrame()
        self.indicator_container.setObjectName("status-container")
        self.indicator_container.setMinimumSize(16, 16)
        self.indicator_container.setMaximumSize(16, 16)
        
        # Añadir contenedor al layout
        self.main_layout.addWidget(self.indicator_container)
        
        # Label de texto si se especificó
        if text:
            self.text_label = QLabel(text)
            self.text_label.setObjectName("status-label")
            self.main_layout.addWidget(self.text_label)
            self.main_layout.addStretch(1)  # Espacio flexible al final
        
        # Aplicar estilo
        self.setProperty("status", status)
        self.setStyleSheet(generate_component_stylesheet("StatusIndicator"))
        
        # Configurar animaciones
        self._setup_animations()
        
        # Iniciar animación si está habilitada
        if animate:
            self.start_animation()
    
    def _setup_animations(self):
        """Configura las animaciones del indicador"""
        # Animación de pulso
        self._pulse_animation = QPropertyAnimation(self, b"pulseScale")
        self._pulse_animation.setDuration(1500)  # 1.5 segundos por ciclo
        self._pulse_animation.setStartValue(1.0)
        self._pulse_animation.setEndValue(1.2)
        self._pulse_animation.setLoopCount(-1)  # Infinito
        self._pulse_animation.setEasingCurve(QEasingCurve.InOutQuad)
    
    # Propiedades animadas
    def _get_pulse_scale(self):
        return self._pulse_scale
    
    def _set_pulse_scale(self, scale):
        self._pulse_scale = scale
        self.update()  # Forzar repintado
    
    pulseScale = Property(float, _get_pulse_scale, _set_pulse_scale)
    
    def paintEvent(self, event):
        """Sobreescribe el evento de pintado para dibujar el indicador"""
        super().paintEvent(event)
        
        # Obtener colores según el estado
        colors = {
            "active": get_color("success"),
            "inactive": get_color("danger"),
            "warning": get_color("warning"),
            "info": get_color("info")
        }
        
        color = QColor(colors.get(self._status, get_color("danger")))
        
        # Crear pintor
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calcular posición del centro del indicador
        indicator_rect = self.indicator_container.geometry()
        center_x = indicator_rect.x() + indicator_rect.width() / 2
        center_y = indicator_rect.y() + indicator_rect.height() / 2
        
        # Calcular radio base
        base_radius = min(indicator_rect.width(), indicator_rect.height()) / 2
        
        # Si está animando, dibujar halo exterior
        if self._animate and self._pulse_scale > 1.0:
            # Dibujar halo con opacidad decreciente
            glow_color = QColor(color)
            glow_color.setAlphaF(0.2 * (2.0 - self._pulse_scale))  # Reducir opacidad mientras crece
            
            painter.setPen(Qt.NoPen)
            painter.setBrush(glow_color)
            
            # Dibujar círculo exterior
            outer_radius = base_radius * self._pulse_scale
            painter.drawEllipse(center_x - outer_radius, center_y - outer_radius, 
                               outer_radius * 2, outer_radius * 2)
        
        # Dibujar círculo principal
        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        painter.drawEllipse(center_x - base_radius, center_y - base_radius, 
                           base_radius * 2, base_radius * 2)
    
    def start_animation(self):
        """Inicia la animación de pulso"""
        self._animate = True
        self._pulse_animation.start()
    
    def stop_animation(self):
        """Detiene la animación de pulso"""
        self._pulse_animation.stop()
        self._pulse_scale = 1.0
        self._animate = False
        self.update()
    
    def set_status(self, status, text=None):
        """
        Cambia el estado del indicador
        
        Args:
            status: Nuevo estado ('active', 'inactive', 'warning', 'info')
            text: Nuevo texto opcional
        """
        self._status = status
        self.setProperty("status", status)
        
        # Actualizar texto si se especificó
        if text is not None:
            self._text = text
            if hasattr(self, 'text_label'):
                self.text_label.setText(text)
            else:
                # Crear label si no existe
                self.text_label = QLabel(text)
                self.text_label.setObjectName("status-label")
                self.main_layout.addWidget(self.text_label)
                self.main_layout.addStretch(1)
        
        # Forzar actualización de estilo
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()