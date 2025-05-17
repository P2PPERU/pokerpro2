"""
Funciones para interactuar con ventanas del sistema operativo
Proporciona detección de mesas de poker y captura de pantalla
"""

import os
import sys
import re
from typing import List, Tuple, Optional
import win32gui
import win32ui
import win32con
import win32api
from ctypes import windll
from PIL import Image
import numpy as np

# Añadir directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils.logger import log_message

def is_poker_table(title: str) -> bool:
    """
    Determina si una ventana es una mesa de poker basándose en su título
    
    Args:
        title: Título de la ventana a comprobar
        
    Returns:
        True si parece una mesa de poker, False en caso contrario
    """
    # Lista de programas a excluir explícitamente
    exclude_programs = [
        'Google Chrome', 'Firefox', 'Edge', 
        'Visual Studio', 'Code', 'Notepad', 
        'Word', 'Excel', 'PowerPoint',
        'Explorer', 'File Explorer'
    ]
    
    # Excluir explícitamente las ventanas de estos programas
    for program in exclude_programs:
        if program in title:
            return False
    
    # Patrones comunes en títulos de mesas de poker
    patterns = [
        r'\b\d+\s*/\s*\d+\b',     # Formato "X / Y" (ciegos)
        r'\bNL\d+\b',              # NLXX (No Limit XX)
        r'\bPLO\d+\b',             # PLOXX (Pot Limit Omaha XX)
        r'\bPK[0-9]+\b',           # Número de mesa PKxxxx
        r'\bTable\s+\d+\b',        # Table XX
        r'\bPoker.*Table\b',       # "Poker" y "Table" en el título
        r'\bHold\'?em\b',          # Hold'em o Holdem
        r'\bOmaha\b',              # Omaha
        r'\bbb\b',                 # bb (big blinds)
        r'\d+\.\d+/\d+\.\d+',      # Formato de ciegos con decimales
        r'[xX]-Poker\(',           # Formato X-Poker común en algunas salas
    ]
    
    # Nombres de programas de poker conocidos (necesita al menos uno de estos)
    poker_clients = [
        'PokerStars', 'GGPoker', 'PokerKing', 'Winamax', 'Pokerstars', 'PPPoker',
        'PartyPoker', '888Poker', 'XPoker', 'WPN', 'TigerGaming', 
        'America\'s Cardroom', '6max'
    ]
    
    # Sistema de puntuación para determinar si es una mesa
    score = 0
    
    # Verificar patrones (cada coincidencia suma 2 puntos)
    for pattern in patterns:
        if re.search(pattern, title, re.IGNORECASE):
            score += 2
    
    # Verificar clientes de poker (cada coincidencia suma 1 punto)
    for client in poker_clients:
        if client.lower() in title.lower():
            score += 1
    
    # Para ser considerada mesa, debe tener un puntaje mínimo de 2
    return score >= 2

def find_poker_tables() -> List[Tuple[int, str]]:
    """
    Busca todas las ventanas de mesas de poker abiertas
    
    Returns:
        Lista de tuplas (hwnd, title) con los handles y títulos de las mesas
    """
    tables = []
    
    def enum_windows_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and is_poker_table(title):
                tables.append((hwnd, title))
    
    # Enumerar todas las ventanas
    try:
        win32gui.EnumWindows(enum_windows_callback, None)
        log_message(f"Se encontraron {len(tables)} mesas de poker")
    except Exception as e:
        log_message(f"Error al enumerar ventanas: {e}", level='error')
    
    # Ordenar por título para consistencia
    tables.sort(key=lambda x: x[1])
    
    return tables

def get_window_under_cursor() -> Tuple[Optional[int], Optional[str]]:
    """
    Obtiene la ventana que está bajo el cursor actual
    
    Returns:
        Tupla (hwnd, title) con el handle y título de la ventana, o (None, None) si no se encuentra
    """
    try:
        # Obtener posición del cursor
        cursor_pos = win32gui.GetCursorPos()
        
        # Obtener ventana en esa posición
        hwnd = win32gui.WindowFromPoint(cursor_pos)
        
        if hwnd:
            title = win32gui.GetWindowText(hwnd)
            
            # Verificar si es una mesa de poker
            if title and is_poker_table(title):
                log_message(f"Ventana bajo cursor: {title}")
                return hwnd, title
            
            # Verificar ventana padre
            parent_hwnd = win32gui.GetParent(hwnd)
            if parent_hwnd:
                parent_title = win32gui.GetWindowText(parent_hwnd)
                if parent_title and is_poker_table(parent_title):
                    log_message(f"Ventana padre bajo cursor: {parent_title}")
                    return parent_hwnd, parent_title
        
        log_message("No se encontró mesa de poker bajo el cursor")
        return None, None
    
    except Exception as e:
        log_message(f"Error al obtener ventana bajo cursor: {e}", level='error')
        return None, None

def capture_window_area(hwnd: int, rect: Tuple[int, int, int, int] = None) -> Optional[Image.Image]:
    """
    Captura una región de una ventana como imagen PIL
    
    Args:
        hwnd: Handle de la ventana a capturar
        rect: Tupla (x, y, width, height) con la región a capturar, o None para toda la ventana
    
    Returns:
        Imagen PIL de la región capturada, o None si hay error
    """
    try:
        # Si no se especifica rect, capturar toda la ventana
        if rect is None:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width, height = right - left, bottom - top
            x, y = 0, 0
        else:
            x, y, width, height = rect
        
        # Obtener DC y crear DC compatible
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        
        # Crear bitmap compatible y seleccionarlo en el DC
        save_bitmap = win32ui.CreateBitmap()
        save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
        save_dc.SelectObject(save_bitmap)
        
        # Copiar bits de la ventana al bitmap
        result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), 3)
        
        # Alternativa si PrintWindow no funciona 
        if not result:
            save_dc.BitBlt((0, 0), (width, height), mfc_dc, (x, y), win32con.SRCCOPY)
        
        # Convertir a imagen PIL
        bmpinfo = save_bitmap.GetInfo()
        bmpstr = save_bitmap.GetBitmapBits(True)
        img = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1
        )
        
        # Liberar recursos
        win32gui.DeleteObject(save_bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)
        
        return img
    
    except Exception as e:
        log_message(f"Error al capturar ventana: {e}", level='error')
        return None

def get_window_position(hwnd: int) -> Tuple[int, int, int, int]:
    """
    Obtiene la posición y tamaño de una ventana
    
    Args:
        hwnd: Handle de la ventana
    
    Returns:
        Tupla (left, top, width, height)
    """
    try:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top
        return left, top, width, height
    except Exception as e:
        log_message(f"Error al obtener posición de ventana: {e}", level='error')
        return 0, 0, 0, 0

def focus_window(hwnd: int) -> bool:
    """
    Pone el foco en una ventana
    
    Args:
        hwnd: Handle de la ventana
    
    Returns:
        True si se pudo dar foco, False en caso contrario
    """
    try:
        # Comprobar si la ventana existe
        if not win32gui.IsWindow(hwnd):
            log_message(f"La ventana {hwnd} no existe", level='warning')
            return False
        
        # Comprobar si está minimizada y restaurarla
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        
        # Traer la ventana al frente
        win32gui.SetForegroundWindow(hwnd)
        
        # Verificar que realmente se activó
        active_hwnd = win32gui.GetForegroundWindow()
        result = (active_hwnd == hwnd)
        
        if result:
            log_message(f"Ventana {hwnd} activada correctamente")
        else:
            log_message(f"No se pudo activar la ventana {hwnd}", level='warning')
        
        return result
        
    except Exception as e:
        log_message(f"Error al dar foco a ventana: {e}", level='error')
        return False

def click_on_window_point(hwnd: int, x: int, y: int) -> bool:
    """
    Realiza un clic en una posición relativa de una ventana
    
    Args:
        hwnd: Handle de la ventana
        x: Coordenada X relativa a la ventana
        y: Coordenada Y relativa a la ventana
    
    Returns:
        True si se realizó el clic, False en caso contrario
    """
    try:
        # Calcular coordenadas absolutas
        left, top, _, _ = win32gui.GetWindowRect(hwnd)
        abs_x, abs_y = left + x, top + y
        
        # Enviar mensaje de clic sin mover el cursor físico
        win32api.SendMessage(
            hwnd, 
            win32con.WM_LBUTTONDOWN, 
            win32con.MK_LBUTTON, 
            win32api.MAKELONG(x, y)
        )
        
        win32api.SendMessage(
            hwnd, 
            win32con.WM_LBUTTONUP, 
            0, 
            win32api.MAKELONG(x, y)
        )
        
        log_message(f"Clic realizado en la posición ({x}, {y}) de la ventana {hwnd}")
        return True
        
    except Exception as e:
        log_message(f"Error al hacer clic en ventana: {e}", level='error')
        return False

# Función para pruebas
def test_find_tables():
    """Prueba la detección de mesas de poker"""
    tables = find_poker_tables()
    for hwnd, title in tables:
        log_message(f"Mesa encontrada: {title} (HWND: {hwnd})")
        
        # Capturar imagen de la ventana
        img = capture_window_area(hwnd)
        if img:
            # Guardar imagen para verificación
            os.makedirs("capturas", exist_ok=True)
            img.save(f"capturas/ventana_{hwnd}.png")
            log_message(f"Imagen guardada en capturas/ventana_{hwnd}.png")

# Para pruebas directas
if __name__ == "__main__":
    test_find_tables()