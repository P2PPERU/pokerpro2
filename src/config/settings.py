"""
Módulo para gestionar la configuración de PokerBot TRACK
Proporciona funciones para cargar y guardar configuración
"""

import json
import os
from pathlib import Path
from typing import Dict, Any
import sys
from dotenv import load_dotenv

# Añadir directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils.logger import log_message

# Cargar las variables de entorno
load_dotenv()

# Rutas de configuración
CONFIG_PATH = Path("config/config.json")
CREDENTIALS_PATH = Path("config/credentials.json")
HISTORY_PATH = Path("config/historial.json")

# Configuración por defecto
DEFAULT_CONFIG = {
    "api_url": "https://pokerprotrack.com/api",
    "token": "",  # será reemplazado desde .env si está disponible
    "openai_api_key": "",  # será reemplazado desde .env si está disponible
    "ocr_coords": {"x": 95, "y": 110, "w": 95, "h": 22},
    "sala_default": "XPK",
    "hotkey": "alt+q",
    "modo_automatico": False,
    "auto_check_interval": 30,
    "mostrar_stats": True,
    "mostrar_analisis": True,
    "tema": "dark",
    "idioma_ocr": "multilingual",
    "mostrar_dialogo_copia": False,
    
    # Nuevas configuraciones para tema y UI
    "ui_animations": True,
    "ui_sidebar_visible": True,
    "ui_compact_mode": False,
    "ui_font_size": "medium",  # small, medium, large
    "ui_card_elevation": 2,    # 1=bajo, 2=medio, 3=alto
    
    # Configuraciones de estadísticas
    "stats_seleccionadas": {
        "vpip": True, "pfr": True, "three_bet": True, "fold_to_3bet_pct": True,
        "wtsd": True, "wsd": True, "cbet_flop": True, "cbet_turn": True,
        "fold_to_flop_cbet_pct": False, "fold_to_turn_cbet_pct": False,
        "limp_pct": False, "limp_raise_pct": False, "four_bet_preflop_pct": False,
        "fold_to_4bet_pct": False, "probe_bet_turn_pct": False, "bet_river_pct": False,
        "fold_to_river_bet_pct": False, "overbet_turn_pct": False, "overbet_river_pct": False,
        "wsdwbr_pct": False, "wwsf": False, "total_manos": False, "bb_100": False, "win_usd": False
    },
    "stats_order": [
        "vpip", "pfr", "three_bet", "fold_to_3bet_pct", "wtsd", "wsd", "cbet_flop", "cbet_turn",
        "fold_to_flop_cbet_pct", "fold_to_turn_cbet_pct", "four_bet_preflop_pct", "fold_to_4bet_pct",
        "limp_pct", "limp_raise_pct", "probe_bet_turn_pct", "bet_river_pct",
        "fold_to_river_bet_pct", "overbet_turn_pct", "overbet_river_pct", "wsdwbr_pct",
        "wwsf", "total_manos", "bb_100", "win_usd"
    ],
    "stats_format": {
        "vpip": "VPIP:{value}", "pfr": "PFR:{value}", "three_bet": "3B:{value}",
        "fold_to_3bet_pct": "F3B:{value}", "wtsd": "WTSD:{value}", "wsd": "WSD:{value}",
        "cbet_flop": "CF:{value}", "cbet_turn": "CT:{value}", "fold_to_flop_cbet_pct": "FFC:{value}",
        "fold_to_turn_cbet_pct": "FTC:{value}", "limp_pct": "LIMP:{value}", "limp_raise_pct": "LR:{value}",
        "four_bet_preflop_pct": "4B:{value}", "fold_to_4bet_pct": "F4B:{value}", "probe_bet_turn_pct": "PBT:{value}",
        "bet_river_pct": "BR:{value}", "fold_to_river_bet_pct": "FRB:{value}", "overbet_turn_pct": "OBT:{value}",
        "overbet_river_pct": "OBR:{value}", "wsdwbr_pct": "WBR:{value}", "wwsf": "WWSF:{value}",
        "total_manos": "Manos:{value}", "bb_100": "BB/100:{value}", "win_usd": "USD:{value}"
    }
}

def load_config() -> Dict[str, Any]:
    """Carga la configuración desde el archivo config.json y el entorno"""
    try:
        config = DEFAULT_CONFIG.copy()

        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config_loaded = json.load(f)
                
                # Actualizar la configuración con los valores cargados
                for key, value in config_loaded.items():
                    if key in config:
                        if isinstance(config[key], dict) and isinstance(value, dict):
                            config[key].update(value)
                        else:
                            config[key] = value
                    else:
                        config[key] = value

        # Validaciones de estadísticas
        _validate_stats_config(config)

        # Cargar valores sensibles desde .env
        config["token"] = os.getenv("TOKEN", config.get("token", ""))
        config["openai_api_key"] = os.getenv("OPENAI_API_KEY", config.get("openai_api_key", ""))

        log_message("Configuración cargada correctamente")
        return config

    except Exception as e:
        log_message(f"Error al cargar configuración: {e}", level='error')
        return DEFAULT_CONFIG.copy()

def _validate_stats_config(config: Dict[str, Any]) -> None:
    """Valida y corrige la configuración de estadísticas"""
    # Asegurar que todas las estadísticas del orden estén en la selección
    for stat in config["stats_order"]:
        if stat not in config["stats_seleccionadas"]:
            config["stats_seleccionadas"][stat] = False
    
    # Asegurar que todas las estadísticas seleccionadas estén en el orden
    for stat in config["stats_seleccionadas"]:
        if stat not in config["stats_order"]:
            config["stats_order"].append(stat)
    
    # Asegurar que todas las estadísticas tengan un formato
    for stat in config["stats_seleccionadas"]:
        if stat not in config["stats_format"]:
            config["stats_format"][stat] = f"{stat.upper()}:{{value}}"
    
    # Asegurar ajustes UI
    if "ui_animations" not in config:
        config["ui_animations"] = DEFAULT_CONFIG["ui_animations"]
    if "ui_sidebar_visible" not in config:
        config["ui_sidebar_visible"] = DEFAULT_CONFIG["ui_sidebar_visible"]
    if "ui_compact_mode" not in config:
        config["ui_compact_mode"] = DEFAULT_CONFIG["ui_compact_mode"]
    if "ui_font_size" not in config:
        config["ui_font_size"] = DEFAULT_CONFIG["ui_font_size"]
    if "ui_card_elevation" not in config:
        config["ui_card_elevation"] = DEFAULT_CONFIG["ui_card_elevation"]

def save_config(config: Dict[str, Any]) -> bool:
    """Guarda la configuración en el archivo config.json"""
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        
        # Crear una copia para no modificar el original
        config_copy = config.copy()
        
        # Remover datos sensibles que deberían estar solo en .env
        if "token" in config_copy:
            config_copy["token"] = ""
        if "openai_api_key" in config_copy:
            config_copy["openai_api_key"] = ""
        
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config_copy, f, indent=4, ensure_ascii=False)
        
        log_message("Configuración guardada correctamente")
        return True
    except Exception as e:
        log_message(f"Error al guardar configuración: {e}", level='error')
        return False

def reset_config() -> bool:
    """Restablece la configuración a los valores por defecto"""
    try:
        save_config(DEFAULT_CONFIG.copy())
        log_message("Configuración restablecida a valores por defecto")
        return True
    except Exception as e:
        log_message(f"Error al restablecer configuración: {e}", level='error')
        return False

def get_stat_display_name(stat_key: str) -> str:
    """Obtiene el nombre para mostrar de una estadística"""
    stat_display_names = {
        "vpip": "VPIP", "pfr": "PFR", "three_bet": "3-Bet", "fold_to_3bet_pct": "Fold to 3-Bet",
        "wtsd": "WTSD", "wsd": "WSD", "cbet_flop": "C-Bet Flop", "cbet_turn": "C-Bet Turn",
        "fold_to_flop_cbet_pct": "Fold to Flop C-Bet", "fold_to_turn_cbet_pct": "Fold to Turn C-Bet",
        "limp_pct": "Limp %", "limp_raise_pct": "Limp-Raise %", "four_bet_preflop_pct": "4-Bet Preflop",
        "fold_to_4bet_pct": "Fold to 4-Bet", "probe_bet_turn_pct": "Probe Bet Turn", "bet_river_pct": "Bet River",
        "fold_to_river_bet_pct": "Fold to River Bet", "overbet_turn_pct": "Overbet Turn",
        "overbet_river_pct": "Overbet River", "wsdwbr_pct": "WSD with Bet River", "wwsf": "WWSF",
        "total_manos": "Total Manos", "bb_100": "BB/100", "win_usd": "Ganancias USD"
    }
    return stat_display_names.get(stat_key, stat_key.upper())

def get_ui_font_size_px(config: Dict[str, Any]) -> int:
    """Obtiene el tamaño de fuente en píxeles según la configuración"""
    font_sizes = {
        "small": 12,
        "medium": 14,
        "large": 16
    }
    return font_sizes.get(config.get("ui_font_size", "medium"), 14)

def get_ui_spacing(config: Dict[str, Any]) -> int:
    """Obtiene el espaciado en píxeles según el modo compacto"""
    if config.get("ui_compact_mode", False):
        return 10  # Espaciado reducido para modo compacto
    else:
        return 20  # Espaciado normal