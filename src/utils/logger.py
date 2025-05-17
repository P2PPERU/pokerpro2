"""
Sistema de logging para PokerBot TRACK
Proporciona funciones para registrar mensajes en diferentes niveles de importancia
"""

import logging
import os
from datetime import datetime
from typing import Optional

# Variable global para mantener la instancia del logger
_logger: Optional[logging.Logger] = None

def setup_logger(log_level=logging.INFO) -> logging.Logger:
    """Configura e inicializa el sistema de logging"""
    global _logger
    
    if _logger:
        return _logger
    
    # Crear logger
    _logger = logging.getLogger("PokerBot")
    _logger.setLevel(log_level)
    
    # Crear formato
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s', 
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Crear manejador para la consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    _logger.addHandler(console_handler)
    
    # Crear manejador para archivo
    os.makedirs("logs", exist_ok=True)
    log_file = f"logs/pokerbot_{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)
    
    return _logger

def get_logger() -> logging.Logger:
    """Obtiene el logger inicializado"""
    global _logger
    if not _logger:
        _logger = setup_logger()
    return _logger

def log_message(message: str, level: str = 'info') -> str:
    """Registra un mensaje en el log con el nivel especificado"""
    logger = get_logger()
    
    level_methods = {
        'debug': logger.debug,
        'info': logger.info,
        'warning': logger.warning,
        'error': logger.error,
        'critical': logger.critical
    }
    
    # Llamar al método de logging correspondiente
    log_func = level_methods.get(level.lower(), logger.info)
    log_func(message)
    
    return message

def get_logs(max_lines: int = 100) -> list[str]:
    """Obtiene las últimas líneas de log del día actual"""
    try:
        log_file = f"logs/pokerbot_{datetime.now().strftime('%Y-%m-%d')}.log"
        if not os.path.exists(log_file):
            return ["No hay registros disponibles para hoy"]
        
        with open(log_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            return lines[-max_lines:] if len(lines) > max_lines else lines
    except Exception as e:
        return [f"Error al leer logs: {str(e)}"]