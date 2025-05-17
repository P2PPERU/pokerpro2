"""
Pestaña principal de PokerBot TRACK
Contiene los controles para búsqueda, análisis y modo automático
"""

import os
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QComboBox, QTableWidget, QTableWidgetItem, QCheckBox, 
    QFrame, QHeaderView, QSizePolicy, QMessageBox, QSpacerItem
)
from PySide6.QtCore import Qt, Signal, Slot, QTimer, QSize
from PySide6.QtGui import QIntValidator, QIcon, QPixmap

# Añadir directorio raíz al path para importaciones
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))
from src.utils.logger import log_message
from src.config.settings import load_config, save_config
from src.utils.windows import find_poker_tables, get_window_under_cursor
from src.ui.widgets.card_widget import CardWidget
from src.ui.widgets.modern_button import ModernButton
from src.ui.widgets.status_indicator import StatusIndicator
from src.ui.widgets.toast_notification import ToastManager
from src.ui.styles.theme import get_color

class MainTab(QWidget):
    """Pestaña principal de la aplicación"""
    
    # Señales
    analyzeRequested = Signal(str, str, bool)  # nick, sala, is_manual
    autoModeToggled = Signal(bool)            # estado del modo automático
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Cargar configuración
        self.config = load_config()
        
        # Estado del modo automático
        self.auto_mode_active = False
        
        # Gestor de notificaciones
        self.toast_manager = ToastManager(self)
        
        # Crear UI
        self.setup_ui()
        
        # Actualizar estado inicial
        self.update_auto_mode_ui()
        
        log_message("Pestaña principal inicializada")
    
    def setup_ui(self):
        """Configura la interfaz de usuario de la pestaña principal"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Sección de búsqueda manual
        self.setup_search_section(main_layout)
        
        # Sección de mesas detectadas
        self.setup_tables_section(main_layout)
        
        # Sección de opciones
        self.setup_options_section(main_layout)
        
        # Sección de modo automático
        self.setup_auto_mode_section(main_layout)
        
        # Espacio flexible al final
        main_layout.addStretch(1)
    
    def setup_search_section(self, parent_layout):
        """Configura la sección de búsqueda manual"""
        # Tarjeta de búsqueda
        search_card = CardWidget(title="Búsqueda Manual", parent=self)
        
        # Layout interno para el contenido
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)
        
        # Icono de búsqueda
        search_icon = QLabel()
        search_icon.setFixedSize(24, 24)
        try:
            icon_pixmap = QPixmap("assets/icons/search.svg")
            search_icon.setPixmap(icon_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except:
            # Fallback
            search_icon.setText("🔍")
        
        search_layout.addWidget(search_icon)
        
        # Input de nick
        self.nick_input = QLineEdit()
        self.nick_input.setPlaceholderText("Introduce el nick a buscar")
        self.nick_input.returnPressed.connect(self.on_search_clicked)
        search_layout.addWidget(self.nick_input)
        
        # Selector de sala
        search_layout.addWidget(QLabel("Sala:"))
        self.room_combo = QComboBox()
        self.room_combo.addItems(["XPK", "PS", "GG", "WPN", "888"])
        self.room_combo.setCurrentText(self.config["sala_default"])
        search_layout.addWidget(self.room_combo)
        
        # Botón de búsqueda
        self.search_button = ModernButton("Buscar", variant="primary")
        self.search_button.clicked.connect(self.on_search_clicked)
        search_layout.addWidget(self.search_button)
        
        # Añadir layout al contenido de la tarjeta
        search_card.content_layout.addLayout(search_layout)
        
        # Añadir tarjeta al layout principal
        parent_layout.addWidget(search_card)
    
    def setup_tables_section(self, parent_layout):
        """Configura la sección de mesas detectadas"""
        # Tarjeta de mesas
        tables_card = CardWidget(title="Mesas Detectadas", parent=self)
        
        # Tabla de mesas
        self.tables_table = QTableWidget(0, 2)
        self.tables_table.setHorizontalHeaderLabels(["ID", "Título"])
        self.tables_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tables_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tables_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tables_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.tables_table.setSelectionMode(QTableWidget.SingleSelection)
        self.tables_table.setAlternatingRowColors(True)
        self.tables_table.setStyleSheet(f"""
            QTableView {{
                border: 1px solid {get_color('border')};
                border-radius: 4px;
            }}
            QHeaderView::section {{
                background-color: {get_color('surface')};
                padding: 6px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid {get_color('border')};
            }}
        """)
        
        # Añadir tabla al contenido de la tarjeta
        tables_card.content_layout.addWidget(self.tables_table)
        
        # Botones de acción para mesas
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        
        # Botón para refrescar mesas
        self.refresh_button = ModernButton("Refrescar Mesas", variant="info")
        self.refresh_button.setIcon(QIcon("assets/icons/refresh.svg"))
        self.refresh_button.clicked.connect(self.refresh_tables)
        buttons_layout.addWidget(self.refresh_button)
        
        # Botón para analizar mesa seleccionada
        self.analyze_button = ModernButton("Analizar Mesa Seleccionada", variant="success")
        self.analyze_button.setIcon(QIcon("assets/icons/analyze.svg"))
        self.analyze_button.clicked.connect(self.analyze_selected_table)
        buttons_layout.addWidget(self.analyze_button)
        
        # Botón para limpiar caché
        self.clear_cache_button = ModernButton("Limpiar Caché", variant="warning")
        self.clear_cache_button.clicked.connect(self.clear_cache)
        buttons_layout.addWidget(self.clear_cache_button)
        
        # Añadir botones al contenido de la tarjeta
        tables_card.content_layout.addLayout(buttons_layout)
        
        # Añadir tarjeta al layout principal
        parent_layout.addWidget(tables_card)
    
    def setup_options_section(self, parent_layout):
        """Configura la sección de opciones de visualización"""
        # Tarjeta de opciones
        options_card = CardWidget(title="Opciones de Visualización", parent=self)
        
        # Layout para opciones
        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(20)
        
        # Label de opciones
        options_layout.addWidget(QLabel("Incluir en la salida:"))
        
        # Checkbox de estadísticas con StatusIndicator
        self.stats_indicator = StatusIndicator(
            status="active" if self.config["mostrar_stats"] else "inactive",
            text="Estadísticas"
        )
        
        # Conectar el indicador
        def toggle_stats():
            if self.stats_indicator._status == "active":
                self.stats_indicator.set_status("inactive")
                self.toggle_show_stats(False)
            else:
                self.stats_indicator.set_status("active")
                self.toggle_show_stats(True)
        
        self.stats_indicator.mousePressEvent = lambda e: toggle_stats()
        self.stats_indicator.setCursor(Qt.PointingHandCursor)
        
        options_layout.addWidget(self.stats_indicator)
        
        # Checkbox de análisis con StatusIndicator
        self.analysis_indicator = StatusIndicator(
            status="active" if self.config["mostrar_analisis"] else "inactive",
            text="Análisis"
        )
        
        # Conectar el indicador
        def toggle_analysis():
            if self.analysis_indicator._status == "active":
                self.analysis_indicator.set_status("inactive")
                self.toggle_show_analysis(False)
            else:
                self.analysis_indicator.set_status("active")
                self.toggle_show_analysis(True)
        
        self.analysis_indicator.mousePressEvent = lambda e: toggle_analysis()
        self.analysis_indicator.setCursor(Qt.PointingHandCursor)
        
        options_layout.addWidget(self.analysis_indicator)
        
        # Checkbox de diálogo con StatusIndicator
        self.dialog_indicator = StatusIndicator(
            status="active" if self.config.get("mostrar_dialogo_copia", False) else "inactive",
            text="Mostrar diálogo de copia"
        )
        
        # Conectar el indicador
        def toggle_dialog():
            if self.dialog_indicator._status == "active":
                self.dialog_indicator.set_status("inactive")
                self.toggle_show_dialog(False)
            else:
                self.dialog_indicator.set_status("active")
                self.toggle_show_dialog(True)
        
        self.dialog_indicator.mousePressEvent = lambda e: toggle_dialog()
        self.dialog_indicator.setCursor(Qt.PointingHandCursor)
        
        options_layout.addWidget(self.dialog_indicator)
        
        # Espacio flexible
        options_layout.addStretch(1)
        
        # Botón para seleccionar estadísticas
        self.stats_button = ModernButton("Seleccionar Estadísticas", variant="secondary")
        self.stats_button.clicked.connect(self.open_stats_selector)
        options_layout.addWidget(self.stats_button)
        
        # Añadir layout al contenido de la tarjeta
        options_card.content_layout.addLayout(options_layout)
        
        # Añadir tarjeta al layout principal
        parent_layout.addWidget(options_card)
    
    def setup_auto_mode_section(self, parent_layout):
        """Configura la sección de modo automático"""
        # Tarjeta de modo automático
        auto_card = CardWidget(title="Modo Automático", parent=self)
        
        # Layout para modo automático
        auto_layout = QHBoxLayout()
        auto_layout.setContentsMargins(0, 0, 0, 0)
        
        # Indicador de estado animado
        self.auto_status = StatusIndicator(
            status="inactive",
            text="Estado: Inactivo",
            animate=False
        )
        auto_layout.addWidget(self.auto_status)
        
        # Intervalo de actualización
        auto_layout.addSpacing(20)
        auto_layout.addWidget(QLabel("Intervalo (seg):"))
        
        # Input para intervalo
        self.interval_input = QLineEdit()
        self.interval_input.setMaximumWidth(60)
        self.interval_input.setText(str(self.config["auto_check_interval"]))
        self.interval_input.setValidator(QIntValidator(5, 300))  # Mínimo 5s, máximo 5min
        self.interval_input.textChanged.connect(self.update_interval)
        auto_layout.addWidget(self.interval_input)
        
        # Espacio flexible
        auto_layout.addStretch(1)
        
        # Botón de modo automático
        self.auto_button = ModernButton("Iniciar Modo Automático", variant="success")
        self.auto_button.clicked.connect(self.toggle_auto_mode)
        auto_layout.addWidget(self.auto_button)
        
        # Añadir layout al contenido de la tarjeta
        auto_card.content_layout.addLayout(auto_layout)
        
        # Añadir tarjeta al layout principal
        parent_layout.addWidget(auto_card)
    
    def on_search_clicked(self):
        """Maneja el clic en el botón de búsqueda"""
        nick = self.nick_input.text().strip()
        if not nick:
            self.toast_manager.warning(
                "Campo vacío", 
                "Por favor introduce un nick para buscar"
            )
            return
        
        sala = self.room_combo.currentText()
        log_message(f"Búsqueda manual: {nick} en sala {sala}")
        
        # Guardar sala por defecto en config
        self.config["sala_default"] = sala
        save_config(self.config)
        
        # Notificar al usuario
        self.parent.set_status(f"Buscando {nick} en {sala}...")
        
        # En esta etapa simplemente mostramos un mensaje con el toast, 
        # en la siguiente etapa enviaremos la señal analyzeRequested
        self.toast_manager.info(
            "Búsqueda iniciada", 
            f"Buscando '{nick}' en '{sala}'"
        )
        
        # Simular proceso
        QTimer.singleShot(1500, lambda: self.parent.set_status("Listo"))
    
    def refresh_tables(self):
        """Refresca la lista de mesas detectadas"""
        log_message("Refrescando lista de mesas")
        
        # Mostrar indicador de carga
        self.parent.set_status("Buscando mesas de poker...")
        
        # Limpiar tabla primero
        self.tables_table.setRowCount(0)
        
        # Detectar mesas reales
        tables = find_poker_tables()
        
        # Añadir filas a la tabla con animación simple
        for i, (hwnd, title) in enumerate(tables):
            # Pequeña pausa para efecto visual
            QTimer.singleShot(i * 100, lambda h=hwnd, t=title: self.add_table_row(h, t))
        
        # Mostrar mensaje sin mesas
        if not tables:
            self.toast_manager.warning(
                "Sin mesas", 
                "No se encontraron mesas de poker abiertas"
            )
        
        # Actualizar mensaje de estado
        QTimer.singleShot(len(tables) * 100 + 200, 
                        lambda: self.parent.set_status(f"Se encontraron {len(tables)} mesas"))
    
    def add_table_row(self, hwnd, title):
        """Añade una fila a la tabla de mesas (con efecto visual)"""
        row = self.tables_table.rowCount()
        self.tables_table.insertRow(row)
        self.tables_table.setItem(row, 0, QTableWidgetItem(str(hwnd)))
        self.tables_table.setItem(row, 1, QTableWidgetItem(title))
    
    def analyze_selected_table(self):
        """Analiza la mesa seleccionada"""
        selected_rows = self.tables_table.selectedItems()
        if not selected_rows:
            self.toast_manager.warning(
                "Sin selección", 
                "Por favor selecciona una mesa para analizar"
            )
            return
        
        # Obtener datos de la mesa seleccionada
        row = selected_rows[0].row()
        hwnd = self.tables_table.item(row, 0).text()
        title = self.tables_table.item(row, 1).text()
        
        log_message(f"Análisis solicitado para mesa: {title} (HWND: {hwnd})")
        
        # Notificar al usuario
        self.parent.set_status(f"Analizando mesa: {title}...")
        
        self.toast_manager.info(
            "Análisis iniciado", 
            f"Analizando mesa: '{title}'"
        )
        
        # Simular proceso
        QTimer.singleShot(2000, lambda: self.parent.set_status("Listo"))
    
    def clear_cache(self):
        """Limpia la caché de nicks"""
        log_message("Solicitud para limpiar caché de nicks")
        
        # Notificar al usuario
        self.toast_manager.success(
            "Caché limpiada", 
            "Se ha limpiado la caché de nicks correctamente"
        )
    
    def toggle_auto_mode(self):
        """Activa/desactiva el modo automático"""
        self.auto_mode_active = not self.auto_mode_active
        
        # Actualizar interfaz
        self.update_auto_mode_ui()
        
        # Emitir señal (se usará en la siguiente etapa)
        self.autoModeToggled.emit(self.auto_mode_active)
        
        # Notificar estado
        if self.auto_mode_active:
            log_message("Modo automático activado")
            self.parent.set_status("Modo automático activado")
            self.auto_status.start_animation()
            
            self.toast_manager.success(
                "Modo automático", 
                "Modo automático activado. Analizando mesas periódicamente."
            )
        else:
            log_message("Modo automático desactivado")
            self.parent.set_status("Modo automático desactivado")
            self.auto_status.stop_animation()
            
            self.toast_manager.info(
                "Modo automático", 
                "Modo automático desactivado"
            )
    
    def update_auto_mode_ui(self):
        """Actualiza la interfaz según el estado del modo automático"""
        if self.auto_mode_active:
            self.auto_status.set_status("active", "Estado: Activo")
            self.auto_button.set_variant("danger")
            self.auto_button.setText("Detener Modo Automático")
            self.auto_button.setIcon(QIcon("assets/icons/stop.svg"))
        else:
            self.auto_status.set_status("inactive", "Estado: Inactivo")
            self.auto_button.set_variant("success")
            self.auto_button.setText("Iniciar Modo Automático")
            self.auto_button.setIcon(QIcon("assets/icons/play.svg"))
    
    def update_interval(self, text):
        """Actualiza el intervalo del modo automático"""
        if not text:
            return
            
        try:
            interval = int(text)
            if 5 <= interval <= 300:
                self.config["auto_check_interval"] = interval
                save_config(self.config)
                log_message(f"Intervalo de modo automático actualizado a {interval} segundos")
        except ValueError:
            pass
    
    def toggle_show_stats(self, checked):
        """Actualiza la configuración para mostrar estadísticas"""
        self.config["mostrar_stats"] = checked
        save_config(self.config)
        log_message(f"Mostrar estadísticas: {checked}")
    
    def toggle_show_analysis(self, checked):
        """Actualiza la configuración para mostrar análisis"""
        self.config["mostrar_analisis"] = checked
        save_config(self.config)
        log_message(f"Mostrar análisis: {checked}")
    
    def toggle_show_dialog(self, checked):
        """Actualiza la configuración para mostrar diálogo de copia"""
        self.config["mostrar_dialogo_copia"] = checked
        save_config(self.config)
        log_message(f"Mostrar diálogo de copia: {checked}")
    
    def open_stats_selector(self):
        """Abre el selector de estadísticas"""
        # Notificar al usuario
        self.toast_manager.info(
            "Selector de estadísticas", 
            "El selector de estadísticas se implementará en la siguiente etapa"
        )
    
    def on_tab_activated(self):
        """Se llama cuando esta pestaña se activa"""
        # Refrescar mesas automáticamente al activar la pestaña
        self.refresh_tables()