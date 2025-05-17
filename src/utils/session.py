"""
Módulo para gestionar sesiones de usuario en PokerBot TRACK
"""

import os
import time
import json
import sys

# Añadir directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils.logger import log_message

class SessionManager:
    """Gestiona la sesión del usuario y su estado de autenticación"""
    
    def __init__(self):
        self.user_data = None
        self.authenticated = False
        self.guest_mode = False
        self.token = None
        self.token_expiry = 0
        self.username = None
    
    def load_session(self):
        """Intenta cargar datos de sesión desde configuración guardada"""
        try:
            credentials_path = os.path.join("config", "credentials.json")
            if os.path.exists(credentials_path):
                with open(credentials_path, "r", encoding="utf-8") as f:
                    credentials = json.load(f)
                if "username" in credentials:
                    self.username = credentials["username"]
                    return True
            return False
        except Exception as e:
            log_message(f"Error al cargar sesión: {e}", level='error')
            return False
    
    def login(self, username, password):
        """
        Realiza el login con las credenciales proporcionadas
        Esta es una versión simulada - en producción se conectaría con el servidor
        """
        try:
            # Simulación de autenticación exitosa
            log_message(f"Autenticación simulada para: {username}")
            
            self.username = username
            self.token = "sample_token_123456"
            self.authenticated = True
            self.guest_mode = False
            self.token_expiry = time.time() + 3600  # 1 hora
            
            self.user_data = {
                "username": username,
                "token": self.token,
                "guest_mode": self.guest_mode
            }
            
            return True, self.user_data
            
        except Exception as e:
            log_message(f"Error de autenticación: {e}", level='error')
            return False, {"error": str(e)}
    
    def login_as_guest(self):
        """Inicia sesión en modo invitado con funcionalidad limitada"""
        self.username = "Invitado"
        self.token = None
        self.authenticated = True
        self.guest_mode = True
        
        self.user_data = {
            "username": self.username,
            "token": "",
            "guest_mode": True
        }
        
        log_message("Iniciada sesión en modo invitado")
        return True, self.user_data
    
    def is_authenticated(self):
        """Verifica si el usuario está autenticado"""
        return self.authenticated
    
    def is_guest(self):
        """Verifica si el usuario está en modo invitado"""
        return self.guest_mode
    
    def logout(self):
        """Cierra la sesión actual"""
        self.user_data = None
        self.authenticated = False
        self.guest_mode = False
        self.token = None
        self.token_expiry = 0
        self.username = None
        
        log_message("Sesión cerrada")
        return True
    
    def save_credentials(self, username, remember=False):
        """Guarda las credenciales si el usuario marcó 'Recordar'"""
        if remember:
            try:
                credentials_path = os.path.join("config", "credentials.json")
                with open(credentials_path, "w", encoding="utf-8") as f:
                    json.dump({"username": username}, f)
                log_message("Credenciales guardadas")
            except Exception as e:
                log_message(f"Error al guardar credenciales: {e}", level='error')

# Instancia global del gestor de sesiones
session_manager = SessionManager()