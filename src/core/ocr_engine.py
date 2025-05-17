"""
Motor OCR para reconocimiento de texto en imágenes de mesas de poker
Utiliza PaddleOCR con fallback a Tesseract
"""

import os
import sys
import time
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
from PySide6.QtCore import QObject, Signal, Slot, QDateTime, QThread
from PIL import Image

# Añadir directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils.logger import log_message
from src.utils.image_utils import enhance_for_ocr, enhance_for_asian_chars, create_test_image

# Importar OCR (manejo condicional)
try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    log_message("PaddleOCR no disponible. Funcionalidad limitada.", level='warning')

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    log_message("Tesseract no disponible. Funcionalidad limitada.", level='warning')

class OCRWorker(QThread):
    """Thread worker para procesamiento OCR en segundo plano"""
    resultReady = Signal(str, float)  # texto, confianza
    failed = Signal(str)  # mensaje de error
    
    def __init__(self, image_data, lang='ch', parent=None):
        super().__init__(parent)
        self.image_data = image_data
        self.lang = lang
    
    def run(self):
        """Ejecuta el procesamiento OCR en segundo plano"""
        try:
            # Convertir a imagen PIL si es necesario
            if isinstance(self.image_data, np.ndarray):
                image = Image.fromarray(self.image_data)
            elif isinstance(self.image_data, Image.Image):
                image = self.image_data
            else:
                self.failed.emit("Formato de imagen no soportado")
                return
            
            # Guardar para debug
            timestamp = QDateTime.currentDateTime().toString("HHmmss")
            debug_path = f"capturas/capture_{timestamp}.png"
            image.save(debug_path)
            
            # Mejorar imagen para OCR
            enhanced = enhance_for_ocr(image)
            enhanced.save(f"capturas/enhanced_{timestamp}.png")
            
            # Intentar con PaddleOCR primero
            if PADDLE_AVAILABLE:
                # Convertir a numpy array para Paddle
                img_array = np.array(enhanced)
                
                # Instanciar OCR con el idioma correcto
                ocr = PaddleOCR(
                    use_angle_cls=True,
                    lang=self.lang,
                    det_db_thresh=0.3,
                    show_log=False,
                    rec_batch_num=1,
                    use_gpu=False
                )
                
                # Ejecutar OCR
                results = ocr.ocr(img_array, cls=True)
                
                if results and results[0]:
                    best_text = ""
                    best_confidence = 0.0
                    
                    for result in results:
                        for line in result:
                            text = line[1][0].strip()
                            confidence = line[1][1]
                            
                            if text and confidence > best_confidence:
                                best_text = text
                                best_confidence = confidence
                    
                    if best_text:
                        log_message(f"PaddleOCR detectó: '{best_text}' (confianza: {best_confidence:.2f})")
                        self.resultReady.emit(best_text, best_confidence)
                        return
            
            # Si PaddleOCR falló o no está disponible, intentar con Tesseract
            if TESSERACT_AVAILABLE:
                # Mejorar específicamente para caracteres asiáticos
                asian_enhanced = enhance_for_asian_chars(image)
                asian_enhanced.save(f"capturas/asian_enhanced_{timestamp}.png")
                
                # Configuración para Tesseract
                custom_config = r'--oem 3 --psm 7 -l chi_sim+jpn+kor+eng'
                
                # Intentar primero con la mejora asiática
                text = pytesseract.image_to_string(asian_enhanced, config=custom_config).strip()
                
                if not text:
                    # Si falla, intentar con la mejora normal
                    text = pytesseract.image_to_string(enhanced, config=custom_config).strip()
                
                if text:
                    log_message(f"Tesseract detectó: '{text}'")
                    self.resultReady.emit(text, 0.7)  # Confianza arbitraria
                    return
            
            # Si llegamos aquí, no se pudo detectar texto
            self.failed.emit("No se pudo detectar texto en la imagen")
            
        except Exception as e:
            log_message(f"Error en procesamiento OCR: {e}", level='error')
            self.failed.emit(f"Error en OCR: {str(e)}")

class OCREngine(QObject):
    """Motor OCR con soporte asíncrono y múltiples motores de reconocimiento"""
    
    # Señales
    ocrCompleted = Signal(str, float)  # texto, confianza
    ocrFailed = Signal(str)            # mensaje de error
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.worker = None
        self.ocr_initialized = False
        self.test_ocr()
    
    def test_ocr(self):
        """Prueba si el OCR está disponible y funcionando"""
        engines_available = []
        
        if PADDLE_AVAILABLE:
            engines_available.append("PaddleOCR")
        
        if TESSERACT_AVAILABLE:
            engines_available.append("Tesseract")
        
        if engines_available:
            log_message(f"Motores OCR disponibles: {', '.join(engines_available)}")
            self.ocr_initialized = True
            
            # Crear y procesar imagen de prueba para pre-inicializar
            test_img = create_test_image()
            if test_img:
                test_img.save("capturas/test_ocr.png")
        else:
            log_message("No hay motores OCR disponibles. La detección de texto no funcionará.", level='warning')
            self.ocr_initialized = False
    
    @Slot(object)
    def process_image(self, image_data, lang=None):
        """
        Procesa una imagen para reconocer texto de forma asíncrona
        
        Args:
            image_data: Imagen a procesar (PIL.Image, numpy.ndarray, o ruta)
            lang: Idioma para OCR (ch, en, etc.)
        """
        if not self.ocr_initialized:
            self.ocrFailed.emit("OCR no inicializado")
            return
        
        # Usar idioma configurado o por defecto
        ocr_lang = lang or self.config.get("idioma_ocr", "ch")
        
        # Limpiar worker anterior si existe
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        
        # Crear nuevo worker
        self.worker = OCRWorker(image_data, ocr_lang)
        
        # Conectar señales
        self.worker.resultReady.connect(self.handle_ocr_result)
        self.worker.failed.connect(self.handle_ocr_error)
        
        # Iniciar procesamiento
        self.worker.start()
        
        log_message(f"Iniciado procesamiento OCR (idioma: {ocr_lang})")
    
    @Slot(str, float)
    def handle_ocr_result(self, text, confidence):
        """Maneja el resultado del OCR asíncrono"""
        # Truncar texto si es muy largo
        if len(text) > 30:
            text = text[:30]
        
        # Emitir señal de resultado
        self.ocrCompleted.emit(text, confidence)
    
    @Slot(str)
    def handle_ocr_error(self, error_message):
        """Maneja los errores del OCR asíncrono"""
        self.ocrFailed.emit(error_message)

# Función para pruebas
def test_ocr_engine():
    """Prueba el motor OCR"""
    from PySide6.QtCore import QCoreApplication
    import sys
    
    app = QCoreApplication(sys.argv)
    
    # Crear motor OCR
    engine = OCREngine()
    
    # Manejar resultados y errores
    def on_ocr_completed(text, confidence):
        log_message(f"OCR completado: '{text}' (confianza: {confidence:.2f})")
        app.quit()
    
    def on_ocr_failed(error):
        log_message(f"OCR falló: {error}", level='error')
        app.quit()
    
    # Conectar señales
    engine.ocrCompleted.connect(on_ocr_completed)
    engine.ocrFailed.connect(on_ocr_failed)
    
    # Crear y procesar imagen de prueba
    test_img = create_test_image("Test OCR 123 ABC")
    if test_img:
        engine.process_image(test_img)
    else:
        log_message("No se pudo crear imagen de prueba", level='error')
        app.quit()
    
    # Ejecutar hasta que se complete el OCR
    sys.exit(app.exec())

# Para pruebas directas
if __name__ == "__main__":
    test_ocr_engine()