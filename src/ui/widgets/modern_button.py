"""
Botón moderno con efectos visuales y estados mejorados
"""

from PySide6.QtWidgets import QPushButton, QGraphicsOpacityEffect
from PySide6.QtCore import QPropertyAnimation, Property, QEasingCurve, Signal, Qt
from PySide6.QtGui import QIcon, QColor, QPainter, QFont

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.ui.styles.theme import get_theme, get_color
from src.ui.styles.constants import *
from src.ui.styles.stylesheet import generate_component_stylesheet

class ModernButton(QPushButton):
    """
    Botón moderno con efectos visuales mejorados
    
    Proporciona diferentes variantes de estilo, soporte para iconos,
    y animaciones suaves para interacciones.
    """
    
    clicked_with_animation = Signal()  # Señal personalizada después de la animación
    
    def __init__(self, text="", parent=None, variant="primary", icon=None):
        """
        Inicializa un botón moderno
        
        Args:
            text: Texto del botón
            parent: Widget padre
            variant: Variante de estilo ('primary', 'success', 'warning', 'danger', 'info', 'flat')
            icon: Icono opcional (ruta o QIcon)
        """
        super().__init__(text, parent)
        
        # Propiedades
        self._variant = variant
        self._ripple_opacity = 0.0
        self._ripple_pos = None
        self._has_ripple = False
        self._is_flat = variant == "flat"
        
        # Configuración inicial
        self.setObjectName("modern-button")
        self.setCursor(Qt.PointingHandCursor)
        
        # Propiedades para variante
        if variant in ["primary", "success", "warning", "danger", "info", "flat"]:
            self.setProperty(variant, "true")
        
        # Aplicar icono si se proporcionó
        if icon:
            if isinstance(icon, str):
                self.setIcon(QIcon(icon))
            else:
                self.setIcon(icon)
        
        # Aplicar hoja de estilos
        self.setStyleSheet(generate_component_stylesheet("ModernButton"))
        
        # Configurar animaciones
        self._setup_animations()
        
        # Conectar señal original a nuestra personalizada
        super().clicked.connect(self._on_click_with_animation)
    
    def _setup_animations(self):
        """Configura las animaciones del botón"""
        # Animación para opacidad (efecto hover)
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)
        
        self._opacity_animation = QPropertyAnimation(self._opacity_effect, b"opacity")
        self._opacity_animation.setDuration(ANIMATION_DURATION_FAST)
        self._opacity_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Animación para efecto ripple (clic)
        self._ripple_animation = QPropertyAnimation(self, b"rippleOpacity")
        self._ripple_animation.setDuration(ANIMATION_DURATION_NORMAL)
        self._ripple_animation.setStartValue(0.5)
        self._ripple_animation.setEndValue(0.0)
        self._ripple_animation.setEasingCurve(QEasingCurve.OutCubic)
    
    # Propiedades animadas para el efecto ripple
    def _get_ripple_opacity(self):
        return self._ripple_opacity
    
    def _set_ripple_opacity(self, opacity):
        self._ripple_opacity = opacity
        self.update()  # Forzar repintado
    
    rippleOpacity = Property(float, _get_ripple_opacity, _set_ripple_opacity)
    
    def paintEvent(self, event):
        """Sobreescribe el evento de pintado para añadir efectos visuales"""
        super().paintEvent(event)
        
        # Dibujar efecto ripple si está activo
        if self._has_ripple and self._ripple_pos:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Calcular tamaño del círculo (máxima dimensión diagonal)
            max_radius = 1.5 * max(self.width(), self.height())
            current_radius = max_radius * (1.0 - self._ripple_opacity)
            
            # Definir color del efecto ripple (blanco o negro según variante)
            if self._is_flat:
                painter.setBrush(QColor(get_color("primary")))
                painter.setOpacity(self._ripple_opacity * 0.3)
            else:
                painter.setBrush(QColor(255, 255, 255))
                painter.setOpacity(self._ripple_opacity * 0.4)
            
            # Dibujar círculo
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self._ripple_pos, current_radius, current_radius)
    
    def mousePressEvent(self, event):
        """Captura el evento de presionar el botón para iniciar animación"""
        if event.button() == Qt.LeftButton:
            # Guardar posición para el efecto ripple
            self._ripple_pos = event.position()
            self._has_ripple = True
            
            # Animar opacidad (reducir un poco)
            self._opacity_animation.stop()
            self._opacity_animation.setStartValue(self._opacity_effect.opacity())
            self._opacity_animation.setEndValue(0.85)
            self._opacity_animation.start()
            
            # Actualizar
            self.update()
        
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Captura el evento de soltar el botón para finalizar animación"""
        if event.button() == Qt.LeftButton:
            # Animar opacidad (volver a normal)
            self._opacity_animation.stop()
            self._opacity_animation.setStartValue(self._opacity_effect.opacity())
            self._opacity_animation.setEndValue(1.0)
            self._opacity_animation.start()
            
            # Iniciar animación de ripple
            self._ripple_animation.stop()
            self._ripple_animation.start()
        
        super().mouseReleaseEvent(event)
    
    def enterEvent(self, event):
        """Maneja el evento de entrada del ratón"""
        # Animar opacidad (aumentar un poco)
        self._opacity_animation.stop()
        self._opacity_animation.setStartValue(self._opacity_effect.opacity())
        self._opacity_animation.setEndValue(0.92)
        self._opacity_animation.start()
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Maneja el evento de salida del ratón"""
        # Animar opacidad (volver a normal)
        self._opacity_animation.stop()
        self._opacity_animation.setStartValue(self._opacity_effect.opacity())
        self._opacity_animation.setEndValue(1.0)
        self._opacity_animation.start()
        
        super().leaveEvent(event)
    
    def _on_click_with_animation(self):
        """Manejador de clic que espera a que termine la animación"""
        # Emitir señal personalizada después de la animación
        self._ripple_animation.finished.connect(self._emit_clicked_signal)
    
    def _emit_clicked_signal(self):
        """Emite la señal personalizada y desconecta el slot"""
        # Desconectar para evitar múltiples emisiones
        self._ripple_animation.finished.disconnect(self._emit_clicked_signal)
        # Emitir señal
        self.clicked_with_animation.emit()
    
    def set_variant(self, variant):
        """Cambia la variante de estilo del botón"""
        # Limpiar propiedades anteriores
        if self._variant in ["primary", "success", "warning", "danger", "info", "flat"]:
            self.setProperty(self._variant, None)
        
        # Establecer nueva variante
        self._variant = variant
        self._is_flat = variant == "flat"
        
        # Aplicar propiedad
        if variant in ["primary", "success", "warning", "danger", "info", "flat"]:
            self.setProperty(variant, "true")
        
        # Forzar actualización de estilo
        self.setStyleSheet(generate_component_stylesheet("ModernButton"))
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()