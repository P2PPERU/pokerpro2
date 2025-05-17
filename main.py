"""
PokerBot TRACK - Herramienta de análisis para jugadores de poker
Punto de entrada principal de la aplicación
"""

import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFontDatabase, QFont

from src.utils.logger import setup_logger, log_message
from src.config.settings import load_config, save_config
from src.ui.login_window import LoginWindow
from src.ui.styles.theme import apply_theme

def load_fonts():
    """Carga las fuentes personalizadas de la aplicación"""
    fonts_dir = os.path.join("assets", "fonts")
    roboto_dir = os.path.join(fonts_dir, "Roboto")
    
    # Verificar si existe el directorio
    if os.path.exists(roboto_dir):
        # Cargar todas las fuentes Roboto
        font_files = [
            "Roboto-Regular.ttf",
            "Roboto-Bold.ttf",
            "Roboto-Light.ttf",
            "Roboto-Medium.ttf",
            "Roboto-Italic.ttf",
            "Roboto-BoldItalic.ttf"
        ]
        
        for font_file in font_files:
            font_path = os.path.join(roboto_dir, font_file)
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id < 0:
                    log_message(f"Error al cargar fuente: {font_file}", level='warning')
                else:
                    log_message(f"Fuente cargada: {font_file}")
        
        # Establecer Roboto como fuente predeterminada de la aplicación
        app_font = QFont("Roboto")
        app_font.setStyleHint(QFont.SansSerif)
        QApplication.setFont(app_font)
    else:
        log_message("Directorio de fuentes no encontrado, usando fuente del sistema", level='warning')

def verify_resources():
    """Verifica que existan los recursos necesarios"""
    # Verificar carpetas base
    os.makedirs("assets/icons", exist_ok=True)
    os.makedirs("assets/fonts", exist_ok=True)

    log_message("Verificando recursos...", level="info")

    # Lista de íconos requeridos
    required_icons = [
        "dropdown_arrow.svg",
        "check.svg",
        "user.svg",
        "lock.svg",
        "home.svg",
        "history.svg",
        "settings.svg",
        "log.svg",
        "refresh.svg",
        "analyze.svg"
    ]

    for icon in required_icons:
        path = os.path.join("assets", "icons", icon)
        if not os.path.exists(path):
            log_message(f"⚠️  FALTA recurso: {icon} en assets/icons/", level="warning")


def main():
    """Función principal que inicia la aplicación"""
    try:
        # Crear carpetas necesarias
        os.makedirs("logs", exist_ok=True)
        os.makedirs("capturas", exist_ok=True)
        os.makedirs("config", exist_ok=True)
        
        # Configurar logger
        logger = setup_logger()
        log_message("Iniciando PokerBot TRACK...")
        
        # Cargar configuración
        config = load_config()
        log_message("Sistema de configuración funcional")
        
        # Verificar y crear recursos si no existen
        verify_resources()
        
        # Inicializar aplicación Qt
        app = QApplication(sys.argv)
        
        # Cargar fuentes personalizadas
        load_fonts()
        
        # Aplicar tema según configuración
        theme_name = config["tema"]
        apply_theme(app, theme_name)
        log_message(f"Tema aplicado: {theme_name}")
        
        # Mostrar ventana de login
        login_window = LoginWindow()
        
        # Manejar login exitoso
        def on_login_successful(user_data):
            log_message(f"Login exitoso para usuario: {user_data.get('username', 'Desconocido')}")
            
            # Importar aquí para evitar dependencias circulares
            from src.ui.main_window import MainWindow
            
            # Crear y mostrar ventana principal
            main_window = MainWindow(user_data)
            main_window.show()
            
            # Cerrar ventana de login
            login_window.close()
        
        # Conectar señal de login exitoso
        login_window.loginSuccessful.connect(on_login_successful)
        
        # Mostrar ventana de login
        login_window.show()
        
        # Iniciar loop de eventos
        sys.exit(app.exec())
        
    except Exception as e:
        log_message(f"Error crítico en la aplicación: {e}", level='critical')
        import traceback
        log_message(traceback.format_exc(), level='critical')
        sys.exit(1)

if __name__ == "__main__":
    main()