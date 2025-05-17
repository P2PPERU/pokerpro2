"""
Utilidades para procesamiento de imágenes
Mejora imágenes para OCR y proporciona comparación de imágenes
"""

import os
import sys
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
from typing import Optional, Tuple

# Añadir directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils.logger import log_message

def enhance_for_ocr(image: Image.Image) -> Image.Image:
    """
    Mejora una imagen para mejor reconocimiento OCR
    
    Args:
        image: Imagen PIL a mejorar
        
    Returns:
        Imagen mejorada
    """
    try:
        # Aumentar tamaño ligeramente si es pequeña
        width, height = image.size
        if width < 100 or height < 30:
            scale_factor = max(2, 100 / width, 30 / height)
            image = image.resize((int(width * scale_factor), int(height * scale_factor)), Image.LANCZOS)
            
        # Convertir a escala de grises
        if image.mode != 'L':
            image = image.convert('L')
        
        # Aumentar contraste
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Aumentar nitidez
        image = image.filter(ImageFilter.SHARPEN)
        image = image.filter(ImageFilter.SHARPEN)  # Aplicar dos veces
        
        # Umbralización adaptativa (para textos claros sobre fondos oscuros)
        width, height = image.size
        
        # Umbralización simple
        threshold = np.array(image).mean() * 0.7
        image = image.point(lambda p: p > threshold and 255)
        
        return image
    
    except Exception as e:
        log_message(f"Error al mejorar imagen para OCR: {e}", level='error')
        return image  # Devolver imagen original en caso de error

def enhance_for_asian_chars(image: Image.Image) -> Image.Image:
    """
    Mejora específica para reconocimiento de caracteres asiáticos
    
    Args:
        image: Imagen PIL a mejorar
        
    Returns:
        Imagen mejorada
    """
    try:
        # Aumentar tamaño
        width, height = image.size
        scale_factor = 2.0
        image = image.resize((int(width * scale_factor), int(height * scale_factor)), Image.LANCZOS)
        
        # Convertir a escala de grises
        if image.mode != 'L':
            image = image.convert('L')
        
        # Aumentar contraste más agresivamente
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(3.0)
        
        # Aumentar nitidez aún más
        for _ in range(3):
            image = image.filter(ImageFilter.SHARPEN)
        
        # Umbralización adaptativa más fuerte
        threshold = np.array(image).mean() * 0.6
        image = image.point(lambda p: p > threshold and 255)
        
        return image
    
    except Exception as e:
        log_message(f"Error al mejorar imagen para caracteres asiáticos: {e}", level='error')
        return image  # Devolver imagen original en caso de error

def generate_image_hash(image: Image.Image, hash_size: int = 16) -> str:
    """
    Genera un hash perceptual de una imagen para comparación
    
    Args:
        image: Imagen PIL a procesar
        hash_size: Tamaño del hash (lado del cuadrado)
        
    Returns:
        String de caracteres 0/1 representando el hash
    """
    try:
        # Reducir tamaño y convertir a escala de grises
        image = image.resize((hash_size, hash_size), Image.LANCZOS).convert('L')
        
        # Obtener datos de píxeles
        pixels = list(image.getdata())
        
        # Calcular promedio
        avg = sum(pixels) / len(pixels)
        
        # Generar hash binario (1 si está por encima del promedio, 0 si no)
        hash_value = ''.join('1' if pixel > avg else '0' for pixel in pixels)
        
        return hash_value
    
    except Exception as e:
        log_message(f"Error al generar hash de imagen: {e}", level='error')
        return "0" * (hash_size * hash_size)  # Devolver hash de ceros en caso de error

def compare_image_hashes(hash1: str, hash2: str) -> float:
    """
    Compara dos hashes de imagen y devuelve su similitud
    
    Args:
        hash1: Primer hash
        hash2: Segundo hash
        
    Returns:
        Similitud entre 0 (totalmente diferentes) y 1 (idénticos)
    """
    try:
        if len(hash1) != len(hash2):
            return 0.0
            
        # Calcular distancia de Hamming (número de bits diferentes)
        hamming_distance = sum(c1 != c2 for c1, c2 in zip(hash1, hash2))
        
        # Calcular similitud (0 a 1)
        max_distance = len(hash1)
        similarity = 1.0 - (hamming_distance / max_distance)
        
        return similarity
    
    except Exception as e:
        log_message(f"Error al comparar hashes de imagen: {e}", level='error')
        return 0.0

def create_test_image(text: str = "Test OCR 测试 テスト") -> Optional[Image.Image]:
    """
    Crea una imagen de prueba con texto para calibrar OCR
    
    Args:
        text: Texto para mostrar en la imagen
        
    Returns:
        Imagen PIL con el texto, o None si hay error
    """
    try:
        # Crear imagen negra
        img = Image.new('RGB', (200, 50), color=(0, 0, 0))
        d = ImageDraw.Draw(img)
        
        # Escribir texto en color blanco
        d.text((10, 10), text, fill=(255, 255, 255))
        
        log_message(f"Imagen de prueba OCR creada con texto: '{text}'")
        return img
    
    except Exception as e:
        log_message(f"Error al crear imagen de prueba: {e}", level='error')
        return None

# Función para pruebas
def test_image_processing():
    """Prueba las funciones de procesamiento de imágenes"""
    # Crear imagen de prueba
    test_img = create_test_image()
    if test_img:
        # Guardar original
        os.makedirs("capturas", exist_ok=True)
        test_img.save("capturas/test_original.png")
        
        # Mejorar para OCR y guardar
        enhanced = enhance_for_ocr(test_img)
        enhanced.save("capturas/test_enhanced.png")
        
        # Mejorar para caracteres asiáticos y guardar
        asian_enhanced = enhance_for_asian_chars(test_img)
        asian_enhanced.save("capturas/test_asian_enhanced.png")
        
        # Generar hashes
        hash1 = generate_image_hash(test_img)
        hash2 = generate_image_hash(enhanced)
        similarity = compare_image_hashes(hash1, hash2)
        
        log_message(f"Hash original: {hash1[:16]}...")
        log_message(f"Hash mejorado: {hash2[:16]}...")
        log_message(f"Similitud: {similarity:.2f}")

# Para pruebas directas
if __name__ == "__main__":
    test_image_processing()