import sys
import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import pyqtgraph.opengl as gl

from backend import (
    cleaninput, getTypeLink, getMaterialType, isMetal,
    getProtons, getNeutrons, getValence, getColor, getName
)

COLOR_E_LIBRE = (0.1, 0.95, 0.4, 1.0)        # Verde neón (electrones normales)
COLOR_E_COMPARTIDO = (0.2, 0.6, 1.0, 1.0)    # Azul celeste (covalente)
COLOR_E_TRANSFERIDO = (0.9, 0.6, 0.1, 1.0)   # Naranja (iónico transferido)
COLOR_E_DOPANTE = (0.95, 0.85, 0.1, 1.0)     # Amarillo brillante (electrón libre tipo N)
COLOR_HUECO = (0.9, 0.3, 0.3, 0.7)          # Aro rojo (hueco libre)

MOLDE_NUCLEO = gl.MeshData.sphere(rows=10, cols=10, radius=0.22)
MOLDE_ELECTRON = gl.MeshData.sphere(rows=10, cols=10, radius=0.16)

def hex_a_rgba(hex_color):
    c = QColor(hex_color)
    return (c.redF(), c.greenF(), c.blueF(), 1.0)


class VisorSandbox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #0b1120;")

        self.es_3d = True
        self.enlazado = True
        self.modo_malla = False  # Alternar entre Par Molecular y Red Cristalina

        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        layout_principal.setSpacing(0)

        # ---------------------------------------------------------
        # BARRA DE CONTROL SUPERIOR
        # ---------------------------------------------------------
        contenedor_barra = QWidget()
        contenedor_barra.setFixedHeight(54)
        contenedor_barra.setStyleSheet("background-color: #0f172a; border-bottom: 1px solid #1e293b;")

        barra = QHBoxLayout(contenedor_barra)
        barra.setContentsMargins(12, 0, 12, 0)
        barra.setSpacing(8)

        self.in_elem1 = QLineEdit("Si")
        self.in_elem1.setFixedWidth(55)
        self.in_elem1.setFixedHeight(28)
        self.in_elem1.setStyleSheet("padding: 2px 6px; font-size: 13px; background-color: #1e293b; color: white; border: 1px solid #334155; border-radius: 4px;")
        self.in_elem1.returnPressed.connect(self.actualizar_escena)

        self.in_elem2 = QLineEdit("B")
        self.in_elem2.setFixedWidth(55)
        self.in_elem2.setFixedHeight(28)
        self.in_elem2.setStyleSheet("padding: 2px 6px; font-size: 13px; background-color: #1e293b; color: white; border: 1px solid #334155; border-radius: 4px;")
        self.in_elem2.returnPressed.connect(self.actualizar_escena)

        self.btn_cargar = QPushButton("Cargar")
        self.btn_cargar.setFixedHeight(28)
        self.btn_cargar.setStyleSheet("font-size: 12px; font-weight: bold; background-color: #2563eb; color: white; border: none; border-radius: 4px; padding: 0 8px;")
        self.btn_cargar.clicked.connect(self.actualizar_escena)

        self.btn_toggle_modo = QPushButton("Modo: Par Molecular")
        self.btn_toggle_modo.setFixedHeight(28)
        self.btn_toggle_modo.setStyleSheet("font-size: 12px; font-weight: bold; background-color: #0284c7; color: white; border: none; border-radius: 4px; padding: 0 10px;")
        self.btn_toggle_modo.clicked.connect(self.alternar_modo_malla)

        self.btn_toggle_enlace = QPushButton("Estado: Enlazados")
        self.btn_toggle_enlace.setFixedHeight(28)
        self.btn_toggle_enlace.setStyleSheet("font-size: 12px; font-weight: bold; background-color: #059669; color: white; border: none; border-radius: 4px; padding: 0 10px;")
        self.btn_toggle_enlace.clicked.connect(self.alternar_enlace)

        self.btn_toggle_vista = QPushButton("Vista: 3D")
        self.btn_toggle_vista.setFixedHeight(28)
        self.btn_toggle_vista.setStyleSheet("font-size: 12px; font-weight: bold; background-color: #475569; color: white; border: none; border-radius: 4px; padding: 0 10px;")
        self.btn_toggle_vista.clicked.connect(self.alternar_vista)

        lbl_leyenda = QLabel("""
            <span style='color:#38bdf8; font-size:14px;'>●</span> <span style='color:#cbd5e1; font-size:11px;'>Compartido</span> &nbsp;
            <span style='color:#f59e0b; font-size:14px;'>●</span> <span style='color:#cbd5e1; font-size:11px;'>Transferido/Dopante</span> &nbsp;
            <span style='color:#4ade80; font-size:14px;'>●</span> <span style='color:#cbd5e1; font-size:11px;'>Libre</span> &nbsp;
            <span style='color:#f87171; font-size:14px;'>○</span> <span style='color:#cbd5e1; font-size:11px;'>Hueco</span>
        """)
        lbl_leyenda.setStyleSheet("border: none; margin-left: 6px;")

        self.lbl_info = QLabel("")
        self.lbl_info.setStyleSheet("color: #94a3b8; font-size: 12px; margin-left: 8px; border: none;")

        barra.addWidget(QLabel("<span style='color:white; font-weight:bold;'>Base:</span>"))
        barra.addWidget(self.in_elem1)
        barra.addWidget(QLabel("<span style='color:white; font-weight:bold;'>Dopante:</span>"))
        barra.addWidget(self.in_elem2)
        barra.addWidget(self.btn_cargar)
        barra.addWidget(self.btn_toggle_modo)
        barra.addWidget(self.btn_toggle_enlace)
        barra.addWidget(self.btn_toggle_vista)
        barra.addWidget(lbl_leyenda)
        barra.addWidget(self.lbl_info)
        barra.addStretch()

        # ---------------------------------------------------------
        # VIEWPORT 3D
        # ---------------------------------------------------------
        self.view = gl.GLViewWidget()
        self.view.setBackgroundColor('#0b1120')

        self.mouse_orig = self.view.mouseMoveEvent
        self.wheel_orig = self.view.wheelEvent

        layout_principal.addWidget(contenedor_barra, stretch=0)
        layout_principal.addWidget(self.view, stretch=1)

        self.items_en_escena = []
        self.aplicar_modo_camara()
        self.actualizar_escena()

    def alternar_modo_malla(self):
        self.modo_malla = not self.modo_malla
        self.btn_toggle_modo.setText("Modo: Malla Cristalina" if self.modo_malla else "Modo: Par Molecular")
        self.btn_toggle_modo.setStyleSheet(
            "font-size: 12px; font-weight: bold; background-color: #9333ea; color: white; border: none; border-radius: 4px; padding: 0 10px;"
            if self.modo_malla else
            "font-size: 12px; font-weight: bold; background-color: #0284c7; color: white; border: none; border-radius: 4px; padding: 0 10px;"
        )
        self.btn_toggle_enlace.setEnabled(not self.modo_malla)
        self.actualizar_escena()

    def alternar_vista(self):
        self.es_3d = not self.es_3d
        self.btn_toggle_vista.setText("Vista: 3D" if self.es_3d else "Vista: 2D")
        self.btn_toggle_vista.setStyleSheet(
            "font-size: 12px; font-weight: bold; background-color: #475569; color: white; border: none; border-radius: 4px; padding: 0 10px;"
            if self.es_3d else
            "font-size: 12px; font-weight: bold; background-color: #7c3aed; color: white; border: none; border-radius: 4px; padding: 0 10px;"
        )
        self.aplicar_modo_camara()

    def alternar_enlace(self):
        self.enlazado = not self.enlazado
        self.btn_toggle_enlace.setText("Estado: Enlazados" if self.enlazado else "Estado: Separados")
        self.btn_toggle_enlace.setStyleSheet(
            "font-size: 12px; font-weight: bold; background-color: #059669; color: white; border: none; border-radius: 4px; padding: 0 10px;"
            if self.enlazado else
            "font-size: 12px; font-weight: bold; background-color: #d97706; color: white; border: none; border-radius: 4px; padding: 0 10px;"
        )
        self.actualizar_escena()

    def aplicar_modo_camara(self):
        distancia = 20 if self.modo_malla else 15
        if self.es_3d:
            self.view.opts['center'] = pg.Vector(0, 0, 0)
            self.view.setCameraPosition(distance=distancia, elevation=35, azimuth=15)
            self.view.mouseMoveEvent = lambda ev: None if (ev.buttons() & (Qt.MouseButton.MiddleButton | Qt.MouseButton.RightButton)) else self.mouse_orig(ev)
            self.view.wheelEvent = self.wheel_orig
        else:
            self.view.opts['center'] = pg.Vector(0, 0, 0)
            self.view.setCameraPosition(distance=distancia, elevation=90, azimuth=-90)
            self.view.mouseMoveEvent = lambda ev: None
            self.view.wheelEvent = lambda ev: None

    def limpiar(self):
        for item in self.items_en_escena:
            self.view.removeItem(item)
        self.items_en_escena.clear()

    def actualizar_escena(self):
        e1, err1 = cleaninput(self.in_elem1.text())
        e2, err2 = cleaninput(self.in_elem2.text())

        if err1 or err2 or not e1 or not e2:
            self.lbl_info.setText(f"<span style='color:#ef4444;'>Error: {err1 or err2}</span>")
            return

        self.limpiar()

        if self.modo_malla:
            self.dibujar_red_semiconductora(e1, e2)
        else:
            self.dibujar_par_molecular(e1, e2)

    # =============================================================
    # MODO 1: RED SEMICONDUCTORA / MALLA CRISTALINA
    # =============================================================
    def dibujar_red_semiconductora(self, e_base, e_dopante):
        titulo_mat, _ = getMaterialType(e_base, e_dopante)
        v_base = getValence(e_base)
        v_dop = getValence(e_dopante)

        self.lbl_info.setText(f"<b style='color:#c084fc;'>Malla:</b> {titulo_mat} (Base: {e_base.symbol}, Dopante centro: {e_dopante.symbol})")

        espaciado = 4.5
        radio_orbita = 1.6

        # Generar cuadrícula 3x3 de átomos
        for i in range(3):
            for j in range(3):
                x = (i - 1) * espaciado
                y = (j - 1) * espaciado
                es_centro = (i == 1 and j == 1)

                elem_actual = e_dopante if es_centro else e_base
                self.dibujar_nucleo(elem_actual, x, y)
                self.dibujar_anillo(x, y, radio_orbita)

                if not es_centro:
                    # Átomo base con 4 electrones en cruz conectados a sus vecinos
                    posiciones = [(0, radio_orbita), (radio_orbita, 0), (0, -radio_orbita), (-radio_orbita, 0)]
                    for dx, dy in posiciones:
                        e = gl.GLMeshItem(meshdata=MOLDE_ELECTRON, color=COLOR_E_COMPARTIDO, shader='shaded')
                        e.translate(x + dx, y + dy, 0.0)
                        self.view.addItem(e)
                        self.items_en_escena.append(e)
                else:
                    # Átomo Dopante Central
                    # 4 posiciones cardinales
                    posiciones = [(0, radio_orbita), (radio_orbita, 0), (0, -radio_orbita), (-radio_orbita, 0)]
                    electrones_en_cruz = min(v_dop, 4)
                    
                    for k in range(4):
                        dx, dy = posiciones[k]
                        if k < electrones_en_cruz:
                            e = gl.GLMeshItem(meshdata=MOLDE_ELECTRON, color=COLOR_E_COMPARTIDO, shader='shaded')
                            e.translate(x + dx, y + dy, 0.0)
                            self.view.addItem(e)
                            self.items_en_escena.append(e)
                        else:
                            # Falta un electrón en la red -> HUECO LIBRE (Tipo P)
                            self.dibujar_hueco_aro(x + dx, y + dy)

                    # Si tiene un 5to electrón (Grupo 15) -> ELECTRÓN LIBRE (Tipo N)
                    if v_dop > 4:
                        e_extra = gl.GLMeshItem(meshdata=MOLDE_ELECTRON, color=COLOR_E_DOPANTE, shader='shaded')
                        # Posicionado en diagonal libre fuera de enlace
                        e_extra.translate(x + radio_orbita * 0.7, y + radio_orbita * 0.7, 0.0)
                        self.view.addItem(e_extra)
                        self.items_en_escena.append(e_extra)

        # Líneas de enlace de la red
        for i in range(3):
            # Líneas horizontales
            y = (i - 1) * espaciado
            pts_h = np.array([[-espaciado, y, 0.0], [espaciado, y, 0.0]])
            linea_h = gl.GLLinePlotItem(pos=pts_h, color=(1.0, 1.0, 1.0, 0.15), width=1.0, mode='lines')
            self.view.addItem(linea_h)
            self.items_en_escena.append(linea_h)

            # Líneas verticales
            x = (i - 1) * espaciado
            pts_v = np.array([[x, -espaciado, 0.0], [x, espaciado, 0.0]])
            linea_v = gl.GLLinePlotItem(pos=pts_v, color=(1.0, 1.0, 1.0, 0.15), width=1.0, mode='lines')
            self.view.addItem(linea_v)
            self.items_en_escena.append(linea_v)

    # =============================================================
    # MODO 2: PAR MOLECULAR (1 a 1)
    # =============================================================
    def dibujar_par_molecular(self, e1, e2):
        tipo_enlace, mensaje_enlace = getTypeLink(e1, e2)
        v1 = getValence(e1)
        v2 = getValence(e2)
        max_e1 = 2 if e1.symbol in ['H', 'He'] else 8
        max_e2 = 2 if e2.symbol in ['H', 'He'] else 8
        radio = 2.5

        if tipo_enlace == 1 or not self.enlazado:
            if tipo_enlace == 1:
                self.lbl_info.setText(f"<b style='color:#f87171;'>Sin Enlace:</b> {mensaje_enlace}")
            else:
                self.lbl_info.setText(f"<b style='color:#fbbf24;'>Estado Inicial</b> | Átomos Libres")

            distancia_centro = 3.6
            self.dibujar_nucleo(e1, -distancia_centro, 0)
            self.dibujar_nucleo(e2, distancia_centro, 0)
            self.dibujar_anillo(-distancia_centro, 0, radio)
            self.dibujar_anillo(distancia_centro, 0, radio)

            self.dibujar_orbita_aislada(-distancia_centro, radio, v1, max_e1)
            self.dibujar_orbita_aislada(distancia_centro, radio, v2, max_e2)
            return

        # Enlace Iónico
        if tipo_enlace == 3:
            distancia_centro = radio
            if isMetal(e1):
                metal, no_metal = e1, e2
                x_metal, x_nometal = -distancia_centro, distancia_centro
                v_metal, v_nometal = v1, v2
                max_nm = max_e2
            else:
                metal, no_metal = e2, e1
                x_metal, x_nometal = distancia_centro, -distancia_centro
                v_metal, v_nometal = v2, v1
                max_nm = max_e1

            transferidos = min(v_metal, max_nm - v_nometal)
            huecos_nm_restantes = max(0, max_nm - (v_nometal + transferidos))

            self.lbl_info.setText(
                f"<b style='color:#f59e0b;'>Enlace Iónico:</b> "
                f"<span style='color:#38bdf8;'>[{metal.symbol}]⁺{transferidos}</span> ⇄ "
                f"<span style='color:#f87171;'>[{no_metal.symbol}]⁻{transferidos}</span>"
            )

            self.dibujar_nucleo(e1, -distancia_centro, 0)
            self.dibujar_nucleo(e2, distancia_centro, 0)
            self.dibujar_anillo(-distancia_centro, 0, radio)
            self.dibujar_anillo(distancia_centro, 0, radio)

            for y_offset in [-0.5, 0.0, 0.5]:
                puntos_fuerza = np.array([[-0.5, y_offset, 0.0], [0.5, y_offset, 0.0]])
                linea = gl.GLLinePlotItem(pos=puntos_fuerza, color=(0.96, 0.62, 0.04, 0.8), width=3.0, mode='lines')
                self.view.addItem(linea)
                self.items_en_escena.append(linea)

            self.dibujar_orbita_aislada(x_metal, radio, 0, v_metal)
            self.dibujar_orbita_ionica(x_nometal, radio, v_nometal, transferidos, huecos_nm_restantes, max_nm)
            return

        # Enlace Covalente
        distancia_centro = 1.9
        faltan1 = max(0, max_e1 - v1)
        faltan2 = max(0, max_e2 - v2)
        pares_compartidos = min(faltan1, faltan2, v1, v2)
        e_compartidos = pares_compartidos * 2 if pares_compartidos > 0 else 0

        libres1 = max(0, v1 - pares_compartidos)
        libres2 = max(0, v2 - pares_compartidos)
        huecos1 = max(0, max_e1 - (v1 + pares_compartidos))
        huecos2 = max(0, max_e2 - (v2 + pares_compartidos))

        self.lbl_info.setText(f"<b style='color:#38bdf8;'>Enlace {mensaje_enlace}</b>")

        self.dibujar_nucleo(e1, -distancia_centro, 0)
        self.dibujar_nucleo(e2, distancia_centro, 0)
        self.dibujar_anillo(-distancia_centro, 0, radio)
        self.dibujar_anillo(distancia_centro, 0, radio)

        if e_compartidos > 0:
            ys = np.linspace(-0.7, 0.7, e_compartidos)
            for y in ys:
                e = gl.GLMeshItem(meshdata=MOLDE_ELECTRON, color=COLOR_E_COMPARTIDO, shader='shaded')
                e.translate(0.0, y, 0.0)
                self.view.addItem(e)
                self.items_en_escena.append(e)

        self.dibujar_arco_exterior(-distancia_centro, radio, libres1, huecos1, lado="izq")
        self.dibujar_arco_exterior(distancia_centro, radio, libres2, huecos2, lado="der")

    # =============================================================
    # MÉTODOS DE DIBUJO BASE
    # =============================================================
    def dibujar_hueco_aro(self, x, y):
        angulos = np.linspace(0, 2 * np.pi, 24)
        radio_aro = 0.16
        puntos = np.array([[x + radio_aro * np.cos(a), y + radio_aro * np.sin(a), 0.0] for a in angulos])
        aro = gl.GLLinePlotItem(pos=puntos, color=COLOR_HUECO, width=2.0, mode='line_strip')
        self.view.addItem(aro)
        self.items_en_escena.append(aro)

    def dibujar_orbita_aislada(self, centro_x, radio, cant_e, total_posiciones):
        angulos = np.linspace(0, 2 * np.pi, total_posiciones, endpoint=False)
        for i, a in enumerate(angulos):
            x = centro_x + radio * np.cos(a)
            y = radio * np.sin(a)
            if i < cant_e:
                p = gl.GLMeshItem(meshdata=MOLDE_ELECTRON, color=COLOR_E_LIBRE, shader='shaded')
                p.translate(x, y, 0.0)
                self.view.addItem(p)
                self.items_en_escena.append(p)
            else:
                self.dibujar_hueco_aro(x, y)

    def dibujar_orbita_ionica(self, centro_x, radio, cant_original, cant_transferida, cant_huecos, total_max):
        angulos = np.linspace(0, 2 * np.pi, total_max, endpoint=False)
        for i, a in enumerate(angulos):
            x = centro_x + radio * np.cos(a)
            y = radio * np.sin(a)
            if i < cant_original:
                p = gl.GLMeshItem(meshdata=MOLDE_ELECTRON, color=COLOR_E_LIBRE, shader='shaded')
            elif i < (cant_original + cant_transferida):
                p = gl.GLMeshItem(meshdata=MOLDE_ELECTRON, color=COLOR_E_TRANSFERIDO, shader='shaded')
            else:
                self.dibujar_hueco_aro(x, y)
                continue
            p.translate(x, y, 0.0)
            self.view.addItem(p)
            self.items_en_escena.append(p)

    def dibujar_arco_exterior(self, centro_x, radio, cant_libres, cant_huecos, lado="izq"):
        total = cant_libres + cant_huecos
        if total <= 0:
            return

        if lado == "izq":
            angulos = np.linspace(np.pi / 2 + 0.35, 3 * np.pi / 2 - 0.35, total)
        else:
            angulos = np.linspace(-np.pi / 2 + 0.35, np.pi / 2 - 0.35, total)

        for i, a in enumerate(angulos):
            x = centro_x + radio * np.cos(a)
            y = radio * np.sin(a)
            if i < cant_libres:
                p = gl.GLMeshItem(meshdata=MOLDE_ELECTRON, color=COLOR_E_LIBRE, shader='shaded')
                p.translate(x, y, 0.0)
                self.view.addItem(p)
                self.items_en_escena.append(p)
            else:
                self.dibujar_hueco_aro(x, y)

    def dibujar_nucleo(self, elem, centro_x, centro_y=0.0):
        protones = getProtons(elem)
        neutrones = int(getNeutrons(elem)) if getNeutrons(elem) is not None else protones
        color = hex_a_rgba(getColor(elem))
        np.random.seed(protones)

        for _ in range(protones):
            p = gl.GLMeshItem(meshdata=MOLDE_NUCLEO, color=color, shader='shaded')
            off = np.random.uniform(-0.35, 0.35, 3)
            p.translate(centro_x + off[0], centro_y + off[1], off[2])
            self.view.addItem(p)
            self.items_en_escena.append(p)

        for _ in range(neutrones):
            n = gl.GLMeshItem(meshdata=MOLDE_NUCLEO, color=(0.7, 0.7, 0.7, 1.0), shader='shaded')
            off = np.random.uniform(-0.35, 0.35, 3)
            n.translate(centro_x + off[0], centro_y + off[1], off[2])
            self.view.addItem(n)
            self.items_en_escena.append(n)

    def dibujar_anillo(self, centro_x, centro_y, radio):
        angulos = np.linspace(0, 2 * np.pi, 60)
        puntos = np.array([[centro_x + radio * np.cos(a), centro_y + radio * np.sin(a), 0.0] for a in angulos])
        anillo = gl.GLLinePlotItem(pos=puntos, color=(1.0, 1.0, 1.0, 0.25), width=1.5, mode='line_strip')
        self.view.addItem(anillo)
        self.items_en_escena.append(anillo)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VisorSandbox()
    ventana.setWindowTitle("SHOWLINK - Visor Interactivo y Redes")
    ventana.resize(1100, 680)
    ventana.show()
    sys.exit(app.exec())