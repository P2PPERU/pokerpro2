"""
Ventana de login para PokerBot TRACK
Proporciona autenticación con pokerprotrack.com
"""

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QFrame, QApplication, QGraphicsDropShadowEffect
)
import os
import sys

# Añadir directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils.logger import log_message
from src.utils.session import session_manager
from src.ui.widgets.modern_button import ModernButton
from src.ui.widgets.card_widget import CardWidget
from src.ui.widgets.status_indicator import StatusIndicator
from src.ui.widgets.toast_notification import ToastManager
from src.ui.styles.theme import get_color

class LoginWindow(QDialog):
    loginSuccessful = Signal(dict)  # Señal para emitir datos de usuario tras login exitoso
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Login - PokerPro TRACK")
        self.setFixedSize(420, 520)
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        
        # Toast manager para notificaciones
        self.toast_manager = ToastManager(self)
        
        # Layout principal con margen para sombra
        main_frame = QFrame(self)
        main_frame.setGeometry(10, 10, 400, 500)
        main_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {get_color('surface')};
                border-radius: 10px;
                border: 1px solid {get_color('border')};
            }}
        """)
        
        # Agregar sombra al frame principal
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        main_frame.setGraphicsEffect(shadow)
        
        # Layout dentro del frame
        layout = QVBoxLayout(main_frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Logo
        logo_layout = QHBoxLayout()
        logo = QLabel()
        # Intentar cargar el logo desde el archivo
        try:
            pixmap = QPixmap("assets/logo.png")
            logo.setPixmap(pixmap.scaled(200, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except:
            # Fallback si no hay logo
            logo.setText("PokerPro TRACK")
            logo.setStyleSheet(f"font-size: 28pt; font-weight: bold; color: {get_color('primary')};")
        
        logo_layout.addStretch()
        logo_layout.addWidget(logo)
        logo_layout.addStretch()
        layout.addLayout(logo_layout)
        
        # Título
        title = QLabel("Iniciar Sesión")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            font-size: 22px; 
            font-weight: bold; 
            margin-bottom: 10px; 
            color: {get_color('text_primary')};
        """)
        layout.addWidget(title)
        
        # Tarjeta para formulario
        login_card = CardWidget(parent=main_frame)
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # Usuario
        user_layout = QHBoxLayout()
        
        # Icono de usuario
        user_icon = QLabel()
        user_icon.setFixedSize(24, 24)
        try:
            user_icon_pixmap = QPixmap("assets/icons/user.svg")
            user_icon.setPixmap(user_icon_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except:
            # Fallback si no hay icono
            user_icon.setText("👤")
        
        user_layout.addWidget(user_icon)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Tu nombre de usuario")
        self.user_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {get_color('bg_secondary')};
                color: {get_color('text_primary')};
                border: 1px solid {get_color('border')};
                border-radius: 5px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {get_color('primary')};
            }}
        """)
        
        user_layout.addWidget(self.user_input)
        form_layout.addLayout(user_layout)
        
        # Contraseña
        pass_layout = QHBoxLayout()
        
        # Icono de contraseña
        pass_icon = QLabel()
        pass_icon.setFixedSize(24, 24)
        try:
            pass_icon_pixmap = QPixmap("assets/icons/lock.svg")
            pass_icon.setPixmap(pass_icon_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except:
            # Fallback si no hay icono
            pass_icon.setText("🔒")
        
        pass_layout.addWidget(pass_icon)
        
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Tu contraseña")
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {get_color('bg_secondary')};
                color: {get_color('text_primary')};
                border: 1px solid {get_color('border')};
                border-radius: 5px;
                padding: 8px 12px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {get_color('primary')};
            }}
        """)
        
        pass_layout.addWidget(self.pass_input)
        form_layout.addLayout(pass_layout)
        
        # Recordar credenciales
        remember_layout = QHBoxLayout()
        
        # Checkbox moderno con indicador de status
        remember_indicator = StatusIndicator(status="inactive", text="Recordar mis credenciales")
        self.remember_cb = remember_indicator
        
        # Conectar el indicador para alternar su estado
        def toggle_remember():
            if remember_indicator._status == "active":
                remember_indicator.set_status("inactive")
            else:
                remember_indicator.set_status("active")
        
        remember_indicator.mousePressEvent = lambda e: toggle_remember()
        remember_indicator.setCursor(Qt.PointingHandCursor)
        
        remember_layout.addWidget(remember_indicator)
        remember_layout.addStretch()
        form_layout.addLayout(remember_layout)
        
        # Añadir el layout del formulario al CardWidget
        login_card.content_layout.addLayout(form_layout)
        layout.addWidget(login_card)
        
        # Botones
        button_layout = QHBoxLayout()
        
        # Botón de acceso invitado
        self.guest_button = ModernButton("Modo Invitado", variant="info")
        self.guest_button.clicked.connect(self.login_as_guest)
        button_layout.addWidget(self.guest_button)
        
        # Botón de login
        self.login_button = ModernButton("Iniciar Sesión", variant="primary")
        self.login_button.clicked.connect(self.login)
        button_layout.addWidget(self.login_button)
        
        layout.addLayout(button_layout)
        
        # Enlace para crear cuenta
        register_layout = QHBoxLayout()
        register_label = QLabel("¿No tienes cuenta? ")
        register_label.setStyleSheet(f"color: {get_color('text_secondary')};")
        
        register_link = QLabel("<a href='https://pokerprotrack.com/register'>Regístrate aquí</a>")
        register_link.setTextFormat(Qt.RichText)
        register_link.setTextInteractionFlags(Qt.TextBrowserInteraction)
        register_link.setOpenExternalLinks(True)
        register_link.setStyleSheet(f"color: {get_color('primary')};")
        
        register_layout.addStretch()
        register_layout.addWidget(register_label)
        register_layout.addWidget(register_link)
        register_layout.addStretch()
        
        layout.addLayout(register_layout)
        
        # Status
        self.status_layout = QHBoxLayout()
        self.status_indicator = StatusIndicator(status="inactive", text="Listo para iniciar sesión")
        self.status_layout.addWidget(self.status_indicator)
        layout.addLayout(self.status_layout)
        
        layout.addStretch()
        
        # Footer
        footer = QLabel("© 2025 PokerPro TRACK - Todos los derechos reservados")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: {get_color('text_secondary')}; font-size: 10px;")
        layout.addWidget(footer)
        
        # Preparar para animaciones
        self.setFocus()
    
    def login(self):
        """Realiza la autenticación contra pokerprotrack.com"""
        
        username = self.user_input.text().strip()
        password = self.pass_input.text().strip()
        
        if not username or not password:
            self.toast_manager.warning(
                "Campos vacíos", 
                "Por favor introduce usuario y contraseña"
            )
            return
        
        self.status_indicator.set_status("warning", "Conectando...")
        self.status_indicator.start_animation()
        self.login_button.setEnabled(False)
        
        # Autenticar usando el gestor de sesiones
        success, user_data = session_manager.login(username, password)
        
        if success:
            # Actualizar status
            self.status_indicator.set_status("active", "Autenticación exitosa")
            
            # Guardar credenciales si "Recordar" está activo
            if self.remember_cb._status == "active":
                session_manager.save_credentials(username, True)
            
            # Mostrar toast de éxito
            self.toast_manager.success(
                "Bienvenido", 
                f"¡Hola {username}! Iniciando aplicación..."
            )
            
            # Emitir señal de login exitoso tras un breve retraso
            QTimer.singleShot(1200, lambda: self.loginSuccessful.emit(user_data))
            QTimer.singleShot(1500, self.accept)  # Cerrar diálogo con un breve retraso
        else:
            # Mostrar error
            error_msg = user_data.get("error", "Error de autenticación")
            self.status_indicator.set_status("inactive", error_msg)
            self.status_indicator.stop_animation()
            self.login_button.setEnabled(True)
            
            # Mostrar toast de error
            self.toast_manager.error("Error de autenticación", error_msg)
            
    def login_as_guest(self):
        """Permite el acceso en modo limitado sin autenticación"""
        
        # Actualizar status
        self.status_indicator.set_status("warning", "Iniciando modo invitado...")
        self.status_indicator.start_animation()
        
        # Usar gestor de sesiones para login como invitado
        success, guest_data = session_manager.login_as_guest()
        
        if success:
            # Actualizar status
            self.status_indicator.set_status("active", "Modo invitado activado")
            
            # Mostrar toast
            self.toast_manager.info(
                "Modo Invitado", 
                "Acceso limitado activado. Iniciando aplicación..."
            )
            
            # Emitir señal con datos de invitado tras un breve retraso
            QTimer.singleShot(1200, lambda: self.loginSuccessful.emit(guest_data))
            QTimer.singleShot(1500, self.accept)
        else:
            self.status_indicator.set_status("inactive", "Error al iniciar modo invitado")
            self.status_indicator.stop_animation()
            
            # Mostrar toast de error
            self.toast_manager.error(
                "Error", 
                "No se pudo iniciar el modo invitado"
            )