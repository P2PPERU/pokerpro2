"""
Ventana principal de PokerBot TRACK
Gestiona todas las pestañas y funcionalidades de la aplicación
"""

import os
import sys
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QWidget, QMessageBox, 
    QHBoxLayout, QLabel, QFrame, QSizePolicy, QStackedWidget
)
from PySide6.QtCore import Slot, Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap

# Añadir directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils.logger import log_message
from src.ui.tabs.main_tab import MainTab
from src.config.settings import load_config, save_config
from src.ui.widgets.icon_button import IconButton
from src.ui.widgets.toast_notification import ToastManager
from src.ui.styles.theme import get_color

class SidebarButton(QFrame):
    """Botón personalizado para la barra lateral"""
    
    clicked = Signal()
    
    def __init__(self, icon_path, text, parent=None):
        super().__init__(parent)
        
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("selected", False)
        
        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # Icono
        icon_label = QLabel()
        icon_label.setFixedSize(24, 24)
        
        try:
            pixmap = QPixmap(icon_path)
            icon_label.setPixmap(pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except Exception as e:
            # Fallback si no hay icono
            icon_label.setText("•")
            log_message(f"Error al cargar icono {icon_path}: {e}", level='debug')
        
        layout.addWidget(icon_label)
        
        # Texto
        text_label = QLabel(text)
        text_label.setStyleSheet(f"color: {get_color('text_primary')}; font-size: 14px;")
        layout.addWidget(text_label)
        
        # Estilo base
        self.update_style()
    
    def set_selected(self, selected):
        """Establece si el botón está seleccionado"""
        self.setProperty("selected", selected)
        self.update_style()
    
    def update_style(self):
        """Actualiza el estilo según el estado"""
        selected = self.property("selected")
        
        if selected:
            self.setStyleSheet(f"""
                SidebarButton {{
                    background-color: {get_color('primary')};
                    border-radius: 6px;
                }}
                QLabel {{
                    color: white;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                SidebarButton {{
                    background-color: transparent;
                    border-radius: 6px;
                }}
                SidebarButton:hover {{
                    background-color: rgba(45, 127, 249, 0.1);
                }}
            """)
    
    def mousePressEvent(self, event):
        """Maneja el evento de clic"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class MainWindow(QMainWindow):
    """Ventana principal de la aplicación PokerBot TRACK"""
    
    def __init__(self, user_data):
        super().__init__()
        
        self.user_data = user_data
        self.config = load_config()
        
        # Configuración básica de la ventana
        self.setWindowTitle(f"PokerBot TRACK - {user_data.get('username', 'Usuario')}")
        self.resize(1100, 700)
        self.setMinimumSize(900, 600)
        
        # Gestor de notificaciones
        self.toast_manager = ToastManager(self)
        
        # Intentar cargar el icono
        try:
            self.setWindowIcon(QIcon("assets/icon.ico"))
        except Exception as e:
            log_message(f"No se pudo cargar el icono: {e}", level='debug')
        
        # Widget central que contendrá todo
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        self.main_layout = QHBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Crear sidebar
        self.create_sidebar()
        
        # Contenedor principal para contenido
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # Barra superior con título y controles
        self.create_topbar()
        
        # Stack para las diferentes vistas
        self.stack = QStackedWidget()
        self.content_layout.addWidget(self.stack)
        
        # Inicializar pestañas como páginas del stack
        self.init_tabs()
        
        # Añadir barra de estado mejorada
        self.create_statusbar()
        
        # Añadir contenedor principal al layout
        self.main_layout.addWidget(self.content_container)
        
        log_message(f"Ventana principal inicializada para usuario: {user_data.get('username', 'Desconocido')}")
        
        # Mostrar mensaje de bienvenida
        self.toast_manager.success(
            "Sesión iniciada", 
            f"Bienvenido a PokerBot TRACK, {user_data.get('username', 'Usuario')}"
        )
    
    def create_sidebar(self):
        """Crea la barra lateral con navegación"""
        # Frame para la barra lateral
        sidebar_frame = QFrame()
        sidebar_frame.setFixedWidth(220)
        sidebar_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {get_color('bg_secondary')};
                border-right: 1px solid {get_color('border')};
            }}
        """)
        
        # Layout de la barra lateral
        sidebar_layout = QVBoxLayout(sidebar_frame)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(10)
        
        # Logo en la parte superior
        logo_layout = QHBoxLayout()
        logo = QLabel()
        
        try:
            pixmap = QPixmap("assets/logo.png")
            logo.setPixmap(pixmap.scaled(160, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except:
            # Fallback si no hay logo
            logo.setText("PokerBot TRACK")
            logo.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {get_color('primary')};")
        
        logo_layout.addWidget(logo)
        logo_layout.addStretch()
        sidebar_layout.addLayout(logo_layout)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"background-color: {get_color('border')};")
        sidebar_layout.addWidget(separator)
        
        # Botones de navegación
        self.nav_buttons = []
        
        # Función para crear botones
        def create_nav_button(icon_path, text, index):
            button = SidebarButton(icon_path, text)
            button.clicked.connect(lambda: self.change_tab(index))
            sidebar_layout.addWidget(button)
            self.nav_buttons.append(button)
            return button
        
        # Botones para las diferentes secciones
        create_nav_button("assets/icons/home.svg", "Principal", 0)
        create_nav_button("assets/icons/history.svg", "Historial", 1)
        create_nav_button("assets/icons/settings.svg", "Configuración", 2)
        create_nav_button("assets/icons/log.svg", "Logs", 3)
        
        # Seleccionar el primer botón por defecto
        if self.nav_buttons:
            self.nav_buttons[0].set_selected(True)
        
        # Espacio flexible
        sidebar_layout.addStretch(1)
        
        # Información de usuario
        user_frame = QFrame()
        user_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {get_color('surface')};
                border: 1px solid {get_color('border')};
                border-radius: 8px;
            }}
        """)
        
        user_layout = QVBoxLayout(user_frame)
        user_layout.setContentsMargins(10, 10, 10, 10)
        
        # Avatar y nombre de usuario
        user_info_layout = QHBoxLayout()
        
        # Avatar
        avatar_label = QLabel()
        avatar_label.setFixedSize(32, 32)
        
        try:
            # Tratar de cargar avatar (en implementación real, sería del usuario)
            avatar_pixmap = QPixmap("assets/icons/user.svg")
            avatar_label.setPixmap(avatar_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except:
            # Fallback
            avatar_label.setText("👤")
            avatar_label.setAlignment(Qt.AlignCenter)
            avatar_label.setStyleSheet(f"""
                background-color: {get_color('primary')};
                color: white;
                border-radius: 16px;
            """)
        
        user_info_layout.addWidget(avatar_label)
        
        # Nombre de usuario
        username_label = QLabel(self.user_data.get('username', 'Usuario'))
        username_label.setStyleSheet(f"color: {get_color('text_primary')}; font-weight: bold;")
        user_info_layout.addWidget(username_label)
        user_info_layout.addStretch()
        
        user_layout.addLayout(user_info_layout)
        
        # Tipo de cuenta
        account_type = "Invitado" if self.user_data.get('guest_mode', False) else "Usuario"
        account_label = QLabel(f"Tipo: {account_type}")
        account_label.setStyleSheet(f"color: {get_color('text_secondary')}; font-size: 12px;")
        user_layout.addWidget(account_label)
        
        sidebar_layout.addWidget(user_frame)
        
        # Añadir sidebar al layout principal
        self.main_layout.addWidget(sidebar_frame)
    
    def create_topbar(self):
        """Crea la barra superior con título y controles"""
        topbar = QFrame()
        topbar.setFixedHeight(60)
        topbar.setStyleSheet(f"""
            QFrame {{
                background-color: {get_color('surface')};
                border-bottom: 1px solid {get_color('border')};
            }}
        """)
        
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(20, 0, 20, 0)
        
        # Título de sección
        self.section_title = QLabel("Principal")
        self.section_title.setStyleSheet(f"""
            color: {get_color('text_primary')};
            font-size: 18px;
            font-weight: bold;
        """)
        topbar_layout.addWidget(self.section_title)
        
        # Espacio flexible
        topbar_layout.addStretch(1)
        
        # Botones de acción
        refresh_button = IconButton(
            icon_path="assets/icons/refresh.svg",
            tooltip="Refrescar",
            variant="info"
        )
        topbar_layout.addWidget(refresh_button)
        
        settings_button = IconButton(
            icon_path="assets/icons/settings.svg",
            tooltip="Configuración rápida",
            variant="primary"
        )
        topbar_layout.addWidget(settings_button)
        
        # Añadir al layout principal
        self.content_layout.addWidget(topbar)
    
    def create_statusbar(self):
        """Crea una barra de estado mejorada"""
        statusbar = QFrame()
        statusbar.setFixedHeight(30)
        statusbar.setStyleSheet(f"""
            QFrame {{
                background-color: {get_color('bg_secondary')};
                border-top: 1px solid {get_color('border')};
            }}
        """)
        
        statusbar_layout = QHBoxLayout(statusbar)
        statusbar_layout.setContentsMargins(10, 0, 10, 0)
        
        # Indicador de estado
        self.status_indicator = QLabel("Listo")
        self.status_indicator.setStyleSheet(f"color: {get_color('text_secondary')};")
        statusbar_layout.addWidget(self.status_indicator)
        
        # Espacio flexible
        statusbar_layout.addStretch(1)
        
        # Versión
        version_label = QLabel("PokerBot TRACK v1.0")
        version_label.setStyleSheet(f"color: {get_color('text_secondary')};")
        statusbar_layout.addWidget(version_label)
        
        # Añadir al layout principal
        self.content_layout.addWidget(statusbar)
    
    def init_tabs(self):
        """Inicializa todas las pestañas como páginas del stack"""
        # Pestaña Principal
        self.main_tab = MainTab(self)
        self.stack.addWidget(self.main_tab)
        
        # Página de Historial (placeholder por ahora)
        self.history_placeholder = QWidget()
        history_layout = QVBoxLayout(self.history_placeholder)
        history_layout.addWidget(QLabel("Historial (próximamente)"))
        self.stack.addWidget(self.history_placeholder)
        
        # Página de Configuración (placeholder por ahora)
        self.config_placeholder = QWidget()
        config_layout = QVBoxLayout(self.config_placeholder)
        config_layout.addWidget(QLabel("Configuración (próximamente)"))
        self.stack.addWidget(self.config_placeholder)
        
        # Página de Logs (placeholder por ahora)
        self.logs_placeholder = QWidget()
        logs_layout = QVBoxLayout(self.logs_placeholder)
        logs_layout.addWidget(QLabel("Logs (próximamente)"))
        self.stack.addWidget(self.logs_placeholder)
        
        # Mostrar la primera página por defecto
        self.stack.setCurrentIndex(0)
    
    def change_tab(self, index):
        """Cambia la pestaña activa"""
        # Actualizar botones de navegación
        for i, button in enumerate(self.nav_buttons):
            button.set_selected(i == index)
        
        # Cambiar página del stack
        self.stack.setCurrentIndex(index)
        
        # Actualizar título de sección
        titles = ["Principal", "Historial", "Configuración", "Logs"]
        if 0 <= index < len(titles):
            self.section_title.setText(titles[index])
        
        # Activar la pestaña
        current_tab = self.stack.currentWidget()
        if hasattr(current_tab, "on_tab_activated"):
            current_tab.on_tab_activated()
        
        log_message(f"Cambiado a sección: {titles[index] if 0 <= index < len(titles) else 'Desconocida'}")
    
    def set_status(self, message):
        """Actualiza el mensaje de la barra de estado"""
        self.status_indicator.setText(message)
    
    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana principal"""
        # Preguntar si realmente quiere salir
        reply = QMessageBox.question(
            self, 'Confirmar salida', 
            '¿Estás seguro de que quieres salir?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Guardar configuración antes de cerrar
            save_config(self.config)
            event.accept()
        else:
            event.ignore()