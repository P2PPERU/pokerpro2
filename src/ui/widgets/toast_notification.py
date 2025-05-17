"""
Sistema de notificaciones temporales no intrusivas (Toast)
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Property, QPoint
from PySide6.QtGui import QFont, QIcon, QColor

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.ui.styles.theme import get_theme, get_color
from src.ui.styles.constants import *
from src.ui.styles.stylesheet import generate_component_stylesheet

class ToastNotification(QFrame):
    """
    Notificación temporal flotante tipo Toast
    
    Muestra una notificación emergente que desaparece automáticamente
    después de un tiempo determinado.
    """
    
    def __init__(self, parent=None, title="", message="", notification_type="info", 
                 duration=TOAST_DURATION, closable=True):
        """
        Inicializa una notificación toast
        
        Args:
            parent: Widget padre (normalmente la ventana principal)
            title: Título de la notificación
            message: Mensaje de la notificación
            notification_type: Tipo de notificación ('info', 'success', 'warning', 'error')
            duration: Duración en milisegundos (0 para no desaparecer automáticamente)
            closable: Si se puede cerrar manualmente
        """
        super().__init__(parent)
        
        # Propiedades
        self._title = title
        self._message = message
        self._type = notification_type
        self._duration = duration
        self._closable = closable
        self._offset_y = 0
        
        # Configuración del widget
        self.setObjectName("toast")
        self.setProperty("type", notification_type)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # Layout
        self.setup_ui()
        
        # Aplicar estilos
        self.setStyleSheet(generate_component_stylesheet("ToastNotification"))
        
        # Configurar temporizador para cierre automático
        if duration > 0:
            QTimer.singleShot(duration, self.close_with_animation)
        
        # Configurar animaciones
        self._setup_animations()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(PADDING_MEDIUM, PADDING_MEDIUM, PADDING_MEDIUM, PADDING_MEDIUM)
        main_layout.setSpacing(PADDING_SMALL)
        
        # Contenedor para título y botón de cierre
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(PADDING_SMALL)
        
        # Título
        if self._title:
            title_label = QLabel(self._title)
            title_label.setObjectName("toast-title")
            header_layout.addWidget(title_label)
        
        # Espacio flexible
        header_layout.addStretch(1)
        
        # Botón de cierre
        if self._closable:
            close_button = QPushButton("×")
            close_button.setFlat(True)
            close_button.setCursor(Qt.PointingHandCursor)
            close_button.clicked.connect(self.close_with_animation)
            header_layout.addWidget(close_button)
        
        # Añadir header al layout principal
        main_layout.addLayout(header_layout)
        
        # Mensaje
        if self._message:
            message_label = QLabel(self._message)
            message_label.setObjectName("toast-message")
            message_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            message_label.setWordWrap(True)
            main_layout.addWidget(message_label)
    
    def _setup_animations(self):
        """Configura las animaciones de entrada y salida"""
        # Animación de entrada (opacidad y desplazamiento)
        self._show_animation = QPropertyAnimation(self, b"pos")
        self._show_animation.setDuration(ANIMATION_DURATION_NORMAL)
        self._show_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Animación de salida
        self._hide_animation = QPropertyAnimation(self, b"pos")
        self._hide_animation.setDuration(ANIMATION_DURATION_NORMAL)
        self._hide_animation.setEasingCurve(QEasingCurve.InCubic)
        self._hide_animation.finished.connect(self.hide)
    
    def showEvent(self, event):
        """Sobreescribe el evento de mostrar para animar la entrada"""
        super().showEvent(event)
        
        # Posicionar en la esquina superior derecha
        if self.parent():
            parent_rect = self.parent().rect()
            start_x = parent_rect.width() - self.width() - PADDING_MEDIUM
            start_y = -self.height()  # Empieza fuera de la pantalla
            
            end_x = parent_rect.width() - self.width() - PADDING_MEDIUM
            end_y = PADDING_MEDIUM + self._offset_y
            
            self.move(start_x, start_y)
            
            # Animar entrada
            self._show_animation.setStartValue(QPoint(start_x, start_y))
            self._show_animation.setEndValue(QPoint(end_x, end_y))
            self._show_animation.start()
    
    def close_with_animation(self):
        """Cierra la notificación con animación"""
        if self.parent():
            parent_rect = self.parent().rect()
            
            start_x = self.x()
            start_y = self.y()
            
            end_x = parent_rect.width()  # Desaparece por la derecha
            end_y = start_y
            
            # Animar salida
            self._hide_animation.setStartValue(QPoint(start_x, start_y))
            self._hide_animation.setEndValue(QPoint(end_x, end_y))
            self._hide_animation.start()
    
    def set_offset_y(self, offset):
        """Establece el desplazamiento vertical para apilar notificaciones"""
        self._offset_y = offset
    
    def set_type(self, notification_type):
        """Cambia el tipo de notificación"""
        self._type = notification_type
        self.setProperty("type", notification_type)
        
        # Forzar actualización de estilo
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
    
    def set_title(self, title):
        """Cambia el título de la notificación"""
        self._title = title
        # Recrear UI
        self.setup_ui()
    
    def set_message(self, message):
        """Cambia el mensaje de la notificación"""
        self._message = message
        # Recrear UI
        self.setup_ui()

class ToastManager:
    """
    Gestor de notificaciones toast
    
    Maneja la creación y posicionamiento de múltiples notificaciones
    para evitar superposiciones.
    """
    
    def __init__(self, parent=None):
        """
        Inicializa el gestor de notificaciones
        
        Args:
            parent: Widget padre (normalmente la ventana principal)
        """
        self.parent = parent
        self.active_toasts = []
        self.default_duration = TOAST_DURATION
    
    def show(self, title="", message="", notification_type="info", duration=None):
        """
        Muestra una nueva notificación
        
        Args:
            title: Título de la notificación
            message: Mensaje de la notificación
            notification_type: Tipo de notificación ('info', 'success', 'warning', 'error')
            duration: Duración en milisegundos (None para usar default)
            
        Returns:
            ToastNotification: La notificación creada
        """
        if duration is None:
            duration = self.default_duration
        
        # Limpiar notificaciones cerradas
        self.active_toasts = [toast for toast in self.active_toasts if toast.isVisible()]
        
        # Calcular offset para no superponer notificaciones
        offset_y = 0
        for toast in self.active_toasts:
            offset_y += toast.height() + PADDING_SMALL
        
        # Crear nueva notificación
        toast = ToastNotification(
            parent=self.parent,
            title=title,
            message=message,
            notification_type=notification_type,
            duration=duration
        )
        
        # Establecer offset
        toast.set_offset_y(offset_y)
        
        # Mostrar
        toast.show()
        
        # Añadir a la lista
        self.active_toasts.append(toast)
        
        return toast
    
    def info(self, title="", message="", duration=None):
        """Muestra una notificación de tipo info"""
        return self.show(title, message, "info", duration)
    
    def success(self, title="", message="", duration=None):
        """Muestra una notificación de tipo success"""
        return self.show(title, message, "success", duration)
    
    def warning(self, title="", message="", duration=None):
        """Muestra una notificación de tipo warning"""
        return self.show(title, message, "warning", duration)
    
    def error(self, title="", message="", duration=None):
        """Muestra una notificación de tipo error"""
        return self.show(title, message, "error", duration)
    
    def close_all(self):
        """Cierra todas las notificaciones activas"""
        for toast in self.active_toasts:
            if toast.isVisible():
                toast.close_with_animation()