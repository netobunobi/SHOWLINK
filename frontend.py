import sys
import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QColor
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)

import pyqtgraph.opengl as gl
from backend import *

class DialogoTablaPeriodica(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Seleccionar Elemento Químico")
        self.elemento_seleccionado = None
        self.setStyleSheet("background-color: #0f172a;")

        layoutPrincipal = QVBoxLayout(self)

        titulo = QLabel("SELECCIONA UN ELEMENTO")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("color: #fbbf24; font-size: 13pt; font-weight: bold; padding: 6px;")
        layoutPrincipal.addWidget(titulo)

        grid = QGridLayout()
        grid.setSpacing(4)
        layoutPrincipal.addLayout(grid)

        for z, simbolo, color, fila, columna in DATOS_TABLA:
            btn = QPushButton(f"{z}\n{simbolo}")
            btn.setFixedSize(48, 48)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #1e293b;
                    color: {color};
                    border: 1.5px solid {color};
                    border-radius: 4px;
                    font-size: 9pt;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    color: #0f172a;
                }}
            """)
            btn.clicked.connect(lambda _, s=simbolo: self.seleccionar(s))
            grid.addWidget(btn, fila, columna)

    def seleccionar(self, simbolo):
        self.elemento_seleccionado = simbolo
        self.accept()

class VentanaPrincipal(QMainWindow):
    def __init__(self):

        
        #creamos el molde de las esferas pa no peliar despues con recursos
        self.molde = gl.MeshData.sphere(rows=10, cols=10, radius=1.5)

        self.molde_electron = gl.MeshData.sphere(rows=10, cols=10, radius=0.25)


        super().__init__()
        self.setWindowTitle("ShowLink")
        self.resize(1100, 750)

        # ----------------- CONTENEDOR PRINCIPAL -----------------
        contenedorMain = QWidget()
        self.setCentralWidget(contenedorMain)
        contenedorMain.setStyleSheet("""
            background-color: #0F172A;
            font-family: 'Segoe UI', Arial, sans-serif;
        """)

        layoutPadreHorizontal = QHBoxLayout(contenedorMain)
        layoutPadreHorizontal.setContentsMargins(12, 12, 12, 12)
        layoutPadreHorizontal.setSpacing(12)

        # ----------------- PANEL IZQUIERDO (VISOR 3D) -----------------
        self.panelIzquierdo = QWidget()
        self.panelIzquierdo.setStyleSheet("""
            background-color: #1E293B;
            border: 2px solid #38bdf8;
            border-radius: 8px;
        """)

        layoutPanelIzquierdo = QVBoxLayout(self.panelIzquierdo)
        layoutPanelIzquierdo.setContentsMargins(0,0,0,0)
        layoutPanelIzquierdo.setSpacing(0)


        #----------------- pestañas, visor 3d -----------------
        
        self.pestañasVisor = QTabWidget()
        layoutPanelIzquierdo.addWidget(self.pestañasVisor)

        self.pestañasVisor.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #38bdf8;
                border-radius: 8px;
                background-color: #000000;
                top: -1px; /* Hace que encaje perfecto con la barra */
            }
            QTabBar::tab {
                background-color: #1e293b;
                color: #94a3b8;
                border: 1.5px solid #334155;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 10px 24px;
                font-size: 11pt;
                font-weight: bold;
                min-width: 140px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: #0f172a;
                color: #38bdf8;
                border: 2px solid #38bdf8;
                border-bottom: 2px solid #000000; /* Se funde con el fondo del visor */
            }
            QTabBar::tab:hover:!selected {
                background-color: #334155;
                color: #f8fafc;
            }
        """)



        # ----------------------PESTAÑA DE ENLACE---------------

        self.Visor3dEnlace = gl.GLViewWidget()

        self.pestañasVisor.addTab(self.Visor3dEnlace, "🔗 ENLACE INTERACTIVO")


        # ----------------------PESTAÑA ATOMOS SEPARADOS---------------
        # ---------------------- PESTAÑA ÁTOMOS SEPARADOS ----------------------
        self.panelPadreVisor = QWidget()
        layoutPanelVisorPrincipal = QVBoxLayout(self.panelPadreVisor)
        layoutPanelVisorPrincipal.setContentsMargins(12, 12, 12, 12)
        layoutPanelVisorPrincipal.setSpacing(8)

        # 1. Barra de Simbología / Leyenda (Flotante arriba de los visores)
        barraLeyenda = QWidget()
        barraLeyenda.setStyleSheet("""
            background-color: rgba(15, 23, 42, 0.85);
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 4px;
        """)
        layoutLeyenda = QHBoxLayout(barraLeyenda)
        layoutLeyenda.setContentsMargins(10, 4, 10, 4)
        layoutLeyenda.setSpacing(20)

        lblElec = QLabel("🟡 Electrón de Valencia")
        lblElec.setStyleSheet("color: #fef08a; font-weight: bold; font-size: 9.5pt; border: none; background: transparent;")

        lblHueco = QLabel("🔴 Hueco / Vacancia")
        lblHueco.setStyleSheet("color: #f87171; font-weight: bold; font-size: 9.5pt; border: none; background: transparent;")

        layoutLeyenda.addStretch()
        layoutLeyenda.addWidget(lblElec)
        layoutLeyenda.addWidget(lblHueco)
        layoutLeyenda.addStretch()

        # 2. Contenedor de los dos visores 3D
        contenedorVisores = QWidget()
        contenedorVisores.setStyleSheet("border: none; background: transparent;")
        layoutVisores = QHBoxLayout(contenedorVisores)
        layoutVisores.setContentsMargins(0, 0, 0, 0)
        layoutVisores.setSpacing(8)

        self.Visor3dA1 = gl.GLViewWidget()
        self.Visor3dA2 = gl.GLViewWidget()

        layoutVisores.addWidget(self.Visor3dA1)
        layoutVisores.addWidget(self.Visor3dA2)

        # 3. Ensamblar todo en la pestaña
        layoutPanelVisorPrincipal.addWidget(barraLeyenda)
        layoutPanelVisorPrincipal.addWidget(contenedorVisores, 1)

        self.pestañasVisor.addTab(self.panelPadreVisor, "⚛️ ÁTOMOS SEPARADOS")



        # ----------------- PANEL DERECHO -----------------
        self.panelDerecho = QWidget()
        self.panelDerecho.setStyleSheet("""
            background-color: #111827;
            border: 2px solid #fbbf24;
            border-radius: 8px;
        """)

        layoutPanelDerecho = QVBoxLayout(self.panelDerecho)
        layoutPanelDerecho.setContentsMargins(16, 16, 16, 16)
        layoutPanelDerecho.setSpacing(12)

        layoutPadreHorizontal.addWidget(self.panelIzquierdo, 7)
        layoutPadreHorizontal.addWidget(self.panelDerecho, 3)

        # ==================== CONTROLES DE ENTRADA ====================
        self.tituloPanel = QLabel("CONTROL DE ENLACE: SHOWLINK")
        self.tituloPanel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tituloPanel.setStyleSheet("color: #fbbf24; font-size: 14pt; font-weight: bold; border: none;")
        layoutPanelDerecho.addWidget(self.tituloPanel)

        # Entradas
        filaElem1 = QHBoxLayout()
        self.inputElem1 = QLineEdit()
        self.inputElem1.setPlaceholderText("Elemento 1 (Base)")
        self.inputElem1.setStyleSheet("""
            background-color: #1e293b;
            color: #f8fafc;
            border: 1px solid #38bdf8;
            border-radius: 5px;
            padding: 8px;
            font-size: 11pt;
        """)
        self.btnTabla1 = QPushButton("⚛")
        self.btnTabla1.setFixedWidth(44)
        self.btnTabla1.setStyleSheet("""
            background-color: #1e293b;
            color: #38bdf8;
            border: 1px solid #38bdf8;
            border-radius: 5px;
            font-weight: bold;
            font-size: 12pt;
            padding: 6px;
        """)
        filaElem1.addWidget(self.inputElem1)
        filaElem1.addWidget(self.btnTabla1)
        layoutPanelDerecho.addLayout(filaElem1)

        self.btnTabla1.clicked.connect(lambda: self.abrirSelector(self.inputElem1))

        filaElem2 = QHBoxLayout()
        self.inputElem2 = QLineEdit()
        self.inputElem2.setPlaceholderText("Elemento 2 (Dopante/Secundario)")
        self.inputElem2.setStyleSheet("""
            background-color: #1e293b;
            color: #f8fafc;
            border: 1px solid #38bdf8;
            border-radius: 5px;
            padding: 8px;
            font-size: 11pt;
        """)
        self.btnTabla2 = QPushButton("⚛")
        self.btnTabla2.setFixedWidth(44)
        self.btnTabla2.setStyleSheet("""
            background-color: #1e293b;
            color: #38bdf8;
            border: 1px solid #38bdf8;
            border-radius: 5px;
            font-weight: bold;
            font-size: 12pt;
            padding: 6px;
        """)
        filaElem2.addWidget(self.inputElem2)
        filaElem2.addWidget(self.btnTabla2)
        layoutPanelDerecho.addLayout(filaElem2)

        self.btnTabla2.clicked.connect(lambda: self.abrirSelector(self.inputElem2))

        # Botón
        self.btnProcesar = QPushButton("PROCESAR ENLACE")
        self.btnProcesar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btnProcesar.setStyleSheet("""
            QPushButton {
                background-color: #fbbf24;
                color: #0f172a;
                font-weight: bold;
                font-size: 12pt;
                padding: 10px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #f59e0b;
            }
        """)
        layoutPanelDerecho.addWidget(self.btnProcesar)
        self.btnProcesar.clicked.connect(self.actualizarDatos)

        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.HLine)
        separador.setStyleSheet("border: 1px solid #38bdf8; max-height: 1px; margin: 4px 0;")
        layoutPanelDerecho.addWidget(separador)

        # ==================== TARJETA RESULTADOS ====================
        tarjetaResultados = QWidget()
        tarjetaResultados.setStyleSheet("""
            background-color: #0b132b;
            border: 1px solid #1e3a8a;
            border-radius: 6px;
        """)
        layoutResultados = QVBoxLayout(tarjetaResultados)
        layoutResultados.setContentsMargins(12, 12, 12, 12)
        layoutResultados.setSpacing(10)

        # --- TARJETA 1: DIAGNÓSTICO DEL ENLACE Y COMPORTAMIENTO (Morado) ---
        self.cajaMorada = QWidget()
        self.cajaMorada.setStyleSheet("""
            background-color: #1e113a;
            border: 2px solid #a855f7;
            border-radius: 8px;
        """)
        layoutMorado = QVBoxLayout(self.cajaMorada)
        layoutMorado.setContentsMargins(14, 12, 14, 12)
        layoutMorado.setSpacing(6)

        self.lblTipoEnlace = QLabel("TIPO DE ENLACE: --")
        self.lblTipoEnlace.setWordWrap(True)
        self.lblTipoEnlace.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.lblTipoEnlace.setStyleSheet("color: #f3e8ff; font-weight: 800; font-size: 13.5pt; border: none;")

        self.lblTituloComportamiento = QLabel("COMPORTAMIENTO: --")
        self.lblTituloComportamiento.setWordWrap(True)
        self.lblTituloComportamiento.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.lblTituloComportamiento.setStyleSheet("color: #e9d5ff; font-weight: 700; font-size: 11.5pt; border: none;")

        self.lblDescComportamiento = QLabel("")
        self.lblDescComportamiento.setWordWrap(True)
        self.lblDescComportamiento.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.lblDescComportamiento.setStyleSheet("color: #cbd5e1; font-size: 10pt; line-height: 140%; border: none;")

        layoutMorado.addWidget(self.lblTipoEnlace)
        layoutMorado.addWidget(self.lblTituloComportamiento)
        layoutMorado.addWidget(self.lblDescComportamiento)
        layoutResultados.addWidget(self.cajaMorada)

        # --- TARJETA 2: ELEMENTO BASE ---
        self.cajaElem1 = QWidget()
        self.cajaElem1.setStyleSheet("""
            background-color: #1e293b;
            border: 2px solid #475569;
            border-radius: 6px;
        """)
        layoutCaja1 = QVBoxLayout(self.cajaElem1)
        layoutCaja1.setContentsMargins(12, 10, 12, 10)
        layoutCaja1.setSpacing(4)

        self.lblTituloElem1 = QLabel("BASE: --")
        self.lblTituloElem1.setWordWrap(True)
        self.lblTituloElem1.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.lblTituloElem1.setStyleSheet("color: #34d399; font-size: 12pt; font-weight: bold; border: none;")

        self.lblConfigElem1 = QLabel("Config: --")
        self.lblConfigElem1.setWordWrap(True)
        self.lblConfigElem1.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.lblConfigElem1.setStyleSheet("color: #a7f3d0; font-size: 10.5pt; font-weight: 500; border: none;")

        self.lblDatosElem1 = QLabel("Valencia: -- | Protones: -- | Neutrones: --")
        self.lblDatosElem1.setWordWrap(True)
        self.lblDatosElem1.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.lblDatosElem1.setStyleSheet("color: #6ee7b7; font-size: 10pt; border: none;")

        layoutCaja1.addWidget(self.lblTituloElem1)
        layoutCaja1.addWidget(self.lblConfigElem1)
        layoutCaja1.addWidget(self.lblDatosElem1)
        layoutResultados.addWidget(self.cajaElem1)

        # --- TARJETA 3: ELEMENTO SECUNDARIO / DOPANTE ---
        self.cajaElem2 = QWidget()
        self.cajaElem2.setStyleSheet("""
            background-color: #1e293b;
            border: 2px solid #475569;
            border-radius: 6px;
        """)
        layoutCaja2 = QVBoxLayout(self.cajaElem2)
        layoutCaja2.setContentsMargins(12, 10, 12, 10)
        layoutCaja2.setSpacing(4)

        self.lblTituloElem2 = QLabel("SECUNDARIO / DOPANTE: --")
        self.lblTituloElem2.setWordWrap(True)
        self.lblTituloElem2.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.lblTituloElem2.setStyleSheet("color: #38bdf8; font-size: 12pt; font-weight: bold; border: none;")

        self.lblConfigElem2 = QLabel("Config: --")
        self.lblConfigElem2.setWordWrap(True)
        self.lblConfigElem2.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.lblConfigElem2.setStyleSheet("color: #bae6fd; font-size: 10.5pt; font-weight: 500; border: none;")

        self.lblDatosElem2 = QLabel("Valencia: -- | Protones: -- | Neutrones: --")
        self.lblDatosElem2.setWordWrap(True)
        self.lblDatosElem2.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.lblDatosElem2.setStyleSheet("color: #7dd3fc; font-size: 10pt; border: none;")

        layoutCaja2.addWidget(self.lblTituloElem2)
        layoutCaja2.addWidget(self.lblConfigElem2)
        layoutCaja2.addWidget(self.lblDatosElem2)
        layoutResultados.addWidget(self.cajaElem2)

        layoutPanelDerecho.addWidget(tarjetaResultados, 1)

    # ==================== LÓGICA DE ACTUALIZACIÓN ====================
    def actualizarDatos(self):
        entryElement1 = self.inputElem1.text().strip()
        entryElement2 = self.inputElem2.text().strip()

        element1, errorE1 = cleaninput(entryElement1)
        element2, errorE2 = cleaninput(entryElement2)

        if errorE1 is not None:
            self.mostrarAlerta("Error", f"ELEMENTO 1: {errorE1}")
            return
        elif errorE2 is not None:
            self.mostrarAlerta("Error", f"ELEMENTO 2: {errorE2}") 
            return

        # Diagnóstico y Asignación de Textos/Colores
        tipoEnlace, msgEnlace = getTypeLink(element1, element2)
        
        # Si tipoEnlace == 1 representa "Sin enlace / Gas Noble"
        if tipoEnlace == 1 or element1.group_id == 18 or element2.group_id == 18:
            colorEnlace = "#94a3b8"          # Gris / Neutro
            colorComportamiento = "#cbd5e1"
            tipoMaterial = "Inerte / No Conductor (Gas Noble)"
            msgtipoMaterial = (
                "Los gases nobles tienen su capa de valencia completa. No forman enlaces "
                "químicos estables ni redes conductoras bajo condiciones estándar."
            )
        elif tipoEnlace == 1:
            colorEnlace = "#fbbf24"          # Ámbar neón para Metálico
            colorComportamiento = "#fef08a"
            tipoMaterial = "Conductor Eléctrico (Metálico)"
            msgtipoMaterial = (
                "Red de cationes inmersos en un 'mar de electrones' deslocalizados. "
                "Los electrones se mueven con total libertad ante un campo eléctrico, "
                "presentando una conductividad extremadamente alta."
            )
        elif tipoEnlace == 2:
            colorEnlace = "#f87171"          # Coral/Rojo para Iónico
            colorComportamiento = "#fca5a5"
            tipoMaterial = "Aislante Eléctrico (Iónico / Sólido)"
            msgtipoMaterial = (
                "Red cristalina rígida formada por atracción electrostática entre iones. "
                "Los electrones están fuertemente retenidos y los iones fijos; no conduce en estado sólido."
            )
        else:
            colorEnlace = "#38bdf8"          # Cian neón para Covalente / Semiconductor
            colorComportamiento = "#a5f3fc"
            tipoMaterial, msgtipoMaterial = getMaterialType(element1, element2)

        # Inyección de textos y colores en el bloque superior
        self.lblTipoEnlace.setText(f"TIPO DE ENLACE: {msgEnlace.upper()}")
        self.lblTipoEnlace.setStyleSheet(f"color: {colorEnlace}; font-weight: 800; font-size: 13.5pt; border: none;")

        self.lblTituloComportamiento.setText(f"COMPORTAMIENTO: {tipoMaterial}")
        self.lblTituloComportamiento.setStyleSheet(f"color: {colorComportamiento}; font-weight: 700; font-size: 11.5pt; border: none;")

        self.lblDescComportamiento.setText(msgtipoMaterial)

        # Tarjeta Elemento 1 (Base)
        nombre1 = getName(element1).capitalize()
        self.lblTituloElem1.setText(f"BASE: {nombre1}")
        self.lblConfigElem1.setText(f"Config: {getElectronicConfiguration(element1)}")
        self.lblDatosElem1.setText(
            f"Valencia: {getValence(element1)} e⁻   |   Protones: {getProtons(element1)}   |   Neutrones: {getNeutrons(element1)}"
        )

        # Tarjeta Elemento 2 (Secundario/Dopante)
        nombre2 = getName(element2).capitalize()
        self.lblTituloElem2.setText(f"SECUNDARIO / DOPANTE: {nombre2}")
        self.lblConfigElem2.setText(f"Config: {getElectronicConfiguration(element2)}")
        self.lblDatosElem2.setText(
            f"Valencia: {getValence(element2)} e⁻   |   Protones: {getProtons(element2)}   |   Neutrones: {getNeutrons(element2)}"
        )

        color1 = getColor(element1)
        color2 = getColor(element2) 

        # Actualizar colores de la Tarjeta 1
        self.cajaElem1.setStyleSheet(f"""
            background-color: #0f172a;
            border: 2px solid {color1};
            border-radius: 6px;
        """)
        self.lblTituloElem1.setStyleSheet(f"color: {color1}; font-size: 12pt; font-weight: bold; border: none;")
        self.lblConfigElem1.setStyleSheet(f"color: {color1}; font-size: 10.5pt; font-weight: 500; border: none;")
        self.lblDatosElem1.setStyleSheet(f"color: {color1}; font-size: 10pt; border: none;")

        # Actualizar colores de la Tarjeta 2
        self.cajaElem2.setStyleSheet(f"""
            background-color: #0f172a;
            border: 2px solid {color2};
            border-radius: 6px;
        """)
        self.lblTituloElem2.setStyleSheet(f"color: {color2}; font-size: 12pt; font-weight: bold; border: none;")
        self.lblConfigElem2.setStyleSheet(f"color: {color2}; font-size: 10.5pt; font-weight: 500; border: none;")
        self.lblDatosElem2.setStyleSheet(f"color: {color2}; font-size: 10pt; border: none;")

        self.dibujarAtomosSeparados(element1, element2)
        self.dibujarEnlaceAtomos(element1, element2)


    def mostrarAlerta(self, titulo, mensaje):
        msg = QMessageBox(self)
        msg.setWindowTitle(titulo)
        msg.setText(mensaje)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowIcon(QIcon("SHOWLINK.ico"))
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #0f172a;
            }
            QLabel {
                color: #f8fafc;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #fbbf24;
                color: #0f172a;
                font-weight: bold;
                font-size: 10.5pt;
                padding: 6px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #f59e0b;
            }
        """)
        msg.exec()

    def abrirSelector(self, input_destino):
        dialogo = DialogoTablaPeriodica(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            simbolo = dialogo.elemento_seleccionado
            if simbolo:
                input_destino.setText(simbolo)


    def dibujarUnAtomo(self, visor, atomo, offset_x=0.0):
        radio_orbita = 3
        angulos_orbita = np.linspace(0, 2 * np.pi, 80)
        puntos_orbita = np.column_stack((
            offset_x + radio_orbita * np.cos(angulos_orbita),
            radio_orbita * np.sin(angulos_orbita),
            np.zeros(80)
        ))

        # Órbita
        linea_orbita = gl.GLLinePlotItem(
            pos=puntos_orbita,
            color=(1, 1, 1, 1),
            width=1.5,
            mode='line_strip',
            glOptions='opaque'
        )
        visor.addItem(linea_orbita)

        # Núcleo
        color = QColor(getColor(atomo))
        colorOpengl = (color.redF(), color.greenF(), color.blueF(), 1.0)
        esferaAtomo = gl.GLMeshItem(
            meshdata=self.molde,
            color=colorOpengl,
            shader='shaded',
            glOptions='opaque'
        )
        esferaAtomo.translate(offset_x, 0.0, 0.0)
        visor.addItem(esferaAtomo)

        # Electrones y Huecos
        capacidad = 2 if atomo.symbol in ['H', 'He'] else 8
        posiciones = np.linspace(0, 2 * np.pi, capacidad, endpoint=False)
        valencia = getValence(atomo)

        for i, theta in enumerate(posiciones):
            ex = offset_x + radio_orbita * np.cos(theta)
            ey = radio_orbita * np.sin(theta)
            ez = 0.0

            if i < valencia:
                e_mesh = gl.GLMeshItem(
                    meshdata=self.molde_electron,
                    color=(1.0, 0.9, 0.1, 1.0),
                    shader='shaded',
                    glOptions='opaque'
                )
            else:
                e_mesh = gl.GLMeshItem(
                    meshdata=self.molde_electron,
                    color=(0.95, 0.2, 0.2, 0.55),
                    shader='shaded',
                    glOptions='translucent'
                )

            e_mesh.translate(ex, ey, ez)
            visor.addItem(e_mesh)

    def dibujarAtomosSeparados(self, atomo1, atomo2):
        self.Visor3dA1.clear()
        self.Visor3dA2.clear()

        self.dibujarUnAtomo(self.Visor3dA1, atomo1, offset_x=0.0)
        self.dibujarUnAtomo(self.Visor3dA2, atomo2, offset_x=0.0)


    def dibujarEnlaceAtomos(self, elemento1, elemento2):
        self.Visor3dEnlace.clear()
        tipoEnlace, msg = getTypeLink(elemento1, elemento2)

        # CASO 1: Gas noble / Sin enlace
        if tipoEnlace == 1:
            self.dibujarUnAtomo(self.Visor3dEnlace, elemento1, offset_x=-3.5)
            self.dibujarUnAtomo(self.Visor3dEnlace, elemento2, offset_x=3.5)
            
        # CASO 2: Enlace Metálico
        elif tipoEnlace == 2:
            self.mostrarAlerta("En desarrollo", "El enlace metálico aún no está implementado.")
            
        # CASO 3: Enlace Iónico
        elif tipoEnlace == 3:
            self.mostrarAlerta("En desarrollo", "El enlace iónico aún no está implementado.")
            
        # CASO 4: Enlace Covalente
        elif tipoEnlace == 4:
            self.mostrarAlerta("En desarrollo", "El enlace covalente aún no está implementado.")


if __name__ == "__main__":

    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    app.setWindowIcon(QIcon("SHOWLINK.ico"))
    ventana.show()
    ventana.showMaximized()
    sys.exit(app.exec())