"""
Referencia visual 3D — PyQt6 + pyqtgraph.opengl
-------------------------------------------------
Esto es un PROTOTIPO EXPLORATORIO para que veas si el enfoque te convence
visualmente. No está pensado para pegarse tal cual en tu proyecto: es más
bien un "boceto en código" de la idea de las 6 escenas (metálico, iónico,
covalente, intrínseco, extrínseco P, extrínseco N) con:
  - toggle 3D (arrastra para orbitar) / 2D (cámara fija cenital)
  - botón para animar "separados -> enlazados"
  - color por rol del electrón: propio / cedido / compartido
  - huecos representados como esferas wireframe (ver nota abajo sobre torus)

Requiere: PyQt6, pyqtgraph  (pip install PyQt6 pyqtgraph --break-system-packages)

Nota sobre pyqtgraph.opengl: no trae una primitiva de "dona" (torus) lista
para usar, así que representé el hueco como una esfera en modo wireframe
(solo aristas, sin caras) -- se ve "hueca" a simple vista y es mucho más
simple/estable que construir una malla toroidal a mano. Si de verdad
quieres el efecto donut, se puede generar una malla paramétrica de torus
con numpy y pasarla a GLMeshItem, pero para decidir si el enfoque general
te convence, esto ya comunica la idea.
"""
import sys
import math
import time
import numpy as np
import pyqtgraph.opengl as gl
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import QTimer


# ---------------------------------------------------------------- colores --
COL = {
    "metal":    (0.29, 0.50, 0.79, 1.0),
    "nonmetal": (0.25, 0.56, 0.49, 1.0),
    "dopant":   (0.54, 0.44, 0.84, 1.0),
    "own":      (0.95, 0.71, 0.20, 1.0),   # electrón propio
    "ceded":    (0.88, 0.33, 0.23, 1.0),   # electrón cedido / ajeno
    "shared":   (0.30, 0.69, 0.49, 1.0),   # electrón compartido
    "hole":     (0.61, 0.60, 0.57, 1.0),   # hueco
}


# ------------------------------------------------------------- geometría --
def tet(scale):
    """4 direcciones tetraédricas (coordinación real del Si en la red)."""
    dirs = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], dtype=float)
    dirs = dirs / np.linalg.norm(dirs[0])
    return dirs * scale


def ring_points(n, r):
    pts = []
    for i in range(n):
        a = i / n * 2 * math.pi
        pts.append(np.array([math.cos(a) * r, math.sin(a) * r, 0.0]))
    return pts


def mid(a, b, offset=(0, 0, 0)):
    return (np.array(a) + np.array(b)) / 2 + np.array(offset)


# --------------------------------------------------------- def. escenas ---
def build_metalico():
    nuc = [np.array([i * 1.7, j * 1.7, 0.0]) for i in (-1, 0, 1) for j in (-1, 0, 1)]
    atoms = []
    for p in nuc:
        start = p * 2.6 + np.array([0, 0, (np.random.rand() - 0.5) * 4])
        atoms.append({"start": start, "end": p, "color": COL["metal"], "radius": 0.32})

    electrons = []
    for k in range(14):
        base = nuc[k % len(nuc)]
        start = np.array([base[0], base[1], 0.0])
        end = base + (np.random.rand(3) - 0.5) * 0.6
        electrons.append({
            "start": start, "end": end,
            "color_start": COL["own"], "color_end": COL["shared"],
            "radius": 0.09, "mobile": True, "phase": np.random.rand() * 10,
        })
    return {"atoms": atoms, "electrons": electrons, "holes": [], "bonds": []}


def build_ionico():
    na, cl = np.array([-2.2, 0, 0]), np.array([2.2, 0, 0])
    atoms = [
        {"start": np.array([-4.5, 0.6, 0]), "end": na, "color": COL["metal"], "radius": 0.4},
        {"start": np.array([4.5, -0.6, 0]), "end": cl, "color": COL["nonmetal"], "radius": 0.42},
    ]
    electrons = [{
        "start": na + np.array([0.9, 0, 0]), "end": cl + np.array([1.0, 0, 0]),
        "color_start": COL["own"], "color_end": COL["ceded"],
        "radius": 0.1, "mobile": False, "phase": 0,
    }]
    for p in ring_points(7, 1.05):
        electrons.append({
            "start": cl + p, "end": cl + p,
            "color_start": COL["own"], "color_end": COL["own"],
            "radius": 0.09, "mobile": False, "phase": 0,
        })
    return {"atoms": atoms, "electrons": electrons, "holes": [], "bonds": [{"from": na, "to": cl}]}


def build_covalente():
    a, b = np.array([-2.4, 0, 0]), np.array([2.4, 0, 0])
    a2, b2 = np.array([-1.35, 0, 0]), np.array([1.35, 0, 0])
    atoms = [
        {"start": a, "end": a2, "color": COL["nonmetal"], "radius": 0.34},
        {"start": b, "end": b2, "color": COL["nonmetal"], "radius": 0.4},
    ]
    electrons = [
        {"start": a + np.array([0.8, 0, 0]), "end": np.array([-0.16, 0.14, 0]),
         "color_start": COL["own"], "color_end": COL["shared"], "radius": 0.09, "mobile": False, "phase": 0},
        {"start": b + np.array([-0.8, 0, 0]), "end": np.array([0.16, -0.14, 0]),
         "color_start": COL["own"], "color_end": COL["shared"], "radius": 0.09, "mobile": False, "phase": 0},
    ]
    for p in ring_points(6, 1.0):
        electrons.append({
            "start": b + p, "end": b2 + p,
            "color_start": COL["own"], "color_end": COL["own"],
            "radius": 0.09, "mobile": False, "phase": 0,
        })
    return {"atoms": atoms, "electrons": electrons, "holes": [], "bonds": []}


def lattice_base(center_color, neighbor_color_fn):
    """Átomo central + 4 vecinos tetraédricos (fragmento simplificado de red)."""
    dirs_far, dirs_near = tet(4.2), tet(1.9)
    atoms = [{"start": np.zeros(3), "end": np.zeros(3), "color": center_color, "radius": 0.36}]
    for i in range(4):
        atoms.append({"start": dirs_far[i], "end": dirs_near[i],
                       "color": neighbor_color_fn(i), "radius": 0.34})
    return atoms, dirs_near, dirs_far


def build_intrinseco():
    atoms, dirs_near, dirs_far = lattice_base(COL["nonmetal"], lambda i: COL["nonmetal"])
    origin = np.zeros(3)
    electrons = []
    for i in range(4):
        far, near = dirs_far[i], dirs_near[i]
        for sign in (1, -1):
            electrons.append({
                "start": mid(origin, far, (0, 0.15 * sign, 0)),
                "end": mid(origin, near, (0, 0.12 * sign, 0)),
                "color_start": COL["own"], "color_end": COL["shared"],
                "radius": 0.08, "mobile": False, "phase": 0,
            })
    return {"atoms": atoms, "electrons": electrons, "holes": [], "bonds": []}


def build_extrinseco_p():
    atoms, dirs_near, dirs_far = lattice_base(
        COL["nonmetal"], lambda i: COL["dopant"] if i == 0 else COL["nonmetal"])
    origin = np.zeros(3)
    electrons = []
    for i in range(1, 4):
        far, near = dirs_far[i], dirs_near[i]
        for sign in (1, -1):
            electrons.append({
                "start": mid(origin, far, (0, 0.15 * sign, 0)),
                "end": mid(origin, near, (0, 0.12 * sign, 0)),
                "color_start": COL["own"], "color_end": COL["shared"],
                "radius": 0.08, "mobile": False, "phase": 0,
            })
    dop_far, dop_near = dirs_far[0], dirs_near[0]
    for p in ring_points(3, 1.0):
        electrons.append({
            "start": dop_far + p, "end": dop_far + p,
            "color_start": COL["own"], "color_end": COL["own"],
            "radius": 0.08, "mobile": False, "phase": 0,
        })
    holes = [{"pos": mid(origin, dop_near, (0, 0, 0)), "radius": 0.16}]
    return {"atoms": atoms, "electrons": electrons, "holes": holes, "bonds": []}


def build_extrinseco_n():
    atoms, dirs_near, dirs_far = lattice_base(
        COL["nonmetal"], lambda i: COL["dopant"] if i == 0 else COL["nonmetal"])
    origin = np.zeros(3)
    electrons = []
    for i in range(4):
        far, near = dirs_far[i], dirs_near[i]
        for sign in (1, -1):
            electrons.append({
                "start": mid(origin, far, (0, 0.15 * sign, 0)),
                "end": mid(origin, near, (0, 0.12 * sign, 0)),
                "color_start": COL["own"], "color_end": COL["shared"],
                "radius": 0.08, "mobile": False, "phase": 0,
            })
    dop_far, dop_near = dirs_far[0], dirs_near[0]
    # el 5to electrón del dopante (grupo 15): no forma parte de un enlace,
    # queda "libre" -- portador de carga negativa del semiconductor tipo N
    electrons.append({
        "start": dop_far + np.array([0.6, 0.6, 0]),
        "end": dop_near + np.array([0.9, 0.9, 0]),
        "color_start": COL["own"], "color_end": COL["own"],
        "radius": 0.1, "mobile": True, "phase": np.random.rand() * 10,
    })
    return {"atoms": atoms, "electrons": electrons, "holes": [], "bonds": []}


SCENES = {
    "metalico": build_metalico, "ionico": build_ionico, "covalente": build_covalente,
    "intrinseco": build_intrinseco, "extrinsecoP": build_extrinseco_p, "extrinsecoN": build_extrinseco_n,
}
LABELS = {
    "metalico": "Metálico", "ionico": "Iónico", "covalente": "Covalente",
    "intrinseco": "Intrínseco", "extrinsecoP": "Extr. tipo P", "extrinsecoN": "Extr. tipo N",
}


# ---------------------------------------------------------- vista lockeable --
class LockableGLView(gl.GLViewWidget):
    """GLViewWidget normal, pero se puede "congelar" (modo 2D fijo)
    ignorando arrastre/zoom del mouse."""
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.locked = False

    def mousePressEvent(self, ev):
        if self.locked:
            return
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        if self.locked:
            return
        super().mouseMoveEvent(ev)

    def wheelEvent(self, ev):
        if self.locked:
            return
        super().wheelEvent(ev)


# --------------------------------------------------------------- widget ---
class BondScene3D(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador de enlaces — referencia 3D")
        self.resize(950, 680)

        self.mode3d = True
        self.playing = False
        self.t = 0.0
        self.start_time = 0.0
        self.current = None
        self.atoms_scatter = None
        self.elec_scatter = None
        self.hole_items = []
        self.bond_item = None

        self._build_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(30)

        self.load_scene("metalico")

    # ---------------- UI ----------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        legend = QHBoxLayout()
        for color, label in [(COL["own"], "propio"), (COL["ceded"], "cedido/ajeno"),
                              (COL["shared"], "compartido"), (COL["hole"], "hueco (wireframe)")]:
            sw = QFrame()
            sw.setFixedSize(12, 12)
            rgb = tuple(int(c * 255) for c in color[:3])
            sw.setStyleSheet(f"background-color: rgb{rgb}; border-radius: 6px;")
            legend.addWidget(sw)
            legend.addWidget(QLabel(label))
        legend.addStretch()
        layout.addLayout(legend)

        btnrow = QHBoxLayout()
        self.scene_buttons = {}
        for key, label in LABELS.items():
            b = QPushButton(label)
            b.clicked.connect(lambda checked=False, k=key: self.load_scene(k))
            btnrow.addWidget(b)
            self.scene_buttons[key] = b
        layout.addLayout(btnrow)

        self.view = LockableGLView()
        self.view.setCameraPosition(distance=12, elevation=20, azimuth=45)
        grid = gl.GLGridItem()
        grid.translate(0, 0, -3)
        grid.setColor((1, 1, 1, 0.08))
        self.view.addItem(grid)  # queda como items[0], nunca se borra
        layout.addWidget(self.view)

        ctrlrow = QHBoxLayout()
        self.btn_play = QPushButton("Formar enlace ▶")
        self.btn_play.clicked.connect(self.toggle_play)
        ctrlrow.addWidget(self.btn_play)

        self.btn_mode = QPushButton("3D (arrastra)")
        self.btn_mode.clicked.connect(self.toggle_mode)
        ctrlrow.addWidget(self.btn_mode)
        layout.addLayout(ctrlrow)

    # ---------------- controles ----------------
    def toggle_mode(self):
        self.mode3d = not self.mode3d
        self.view.locked = not self.mode3d
        if not self.mode3d:
            self.view.setCameraPosition(elevation=90, azimuth=-90)
            self.btn_mode.setText("2D (fijo)")
        else:
            self.view.setCameraPosition(elevation=20, azimuth=45)
            self.btn_mode.setText("3D (arrastra)")

    def toggle_play(self):
        if self.playing:
            return
        if self.t >= 1.0:
            # invertir para poder regresar a "separados"
            for a in self.current["atoms"]:
                a["start"], a["end"] = a["end"], a["start"]
            for e in self.current["electrons"]:
                e["start"], e["end"] = e["end"], e["start"]
                e["color_start"], e["color_end"] = e["color_end"], e["color_start"]
        self.playing = True
        self.start_time = time.time()
        self.t = 0.0

    # ---------------- carga de escena ----------------
    def load_scene(self, key):
        self.current = SCENES[key]()
        self.t = 0.0
        self.playing = False
        self.btn_play.setText("Formar enlace ▶")
        for k, b in self.scene_buttons.items():
            b.setStyleSheet("font-weight: bold;" if k == key else "")

        # limpiar todo menos el grid (items[0])
        for item in list(self.view.items[1:]):
            self.view.removeItem(item)
        self.hole_items = []
        self.bond_item = None

        pos_a = np.array([a["start"] for a in self.current["atoms"]])
        col_a = np.array([a["color"] for a in self.current["atoms"]])
        size_a = np.array([a["radius"] * 2 for a in self.current["atoms"]])
        self.atoms_scatter = gl.GLScatterPlotItem(pos=pos_a, size=size_a, color=col_a, pxMode=False)
        self.view.addItem(self.atoms_scatter)

        pos_e = np.array([e["start"] for e in self.current["electrons"]])
        col_e = np.array([e["color_start"] for e in self.current["electrons"]])
        size_e = np.array([e["radius"] * 2 for e in self.current["electrons"]])
        self.elec_scatter = gl.GLScatterPlotItem(pos=pos_e, size=size_e, color=col_e, pxMode=False)
        self.view.addItem(self.elec_scatter)

        for h in self.current["holes"]:
            md = gl.MeshData.sphere(rows=8, cols=8)
            mesh = gl.GLMeshItem(meshdata=md, smooth=False, drawFaces=False,
                                  drawEdges=True, edgeColor=(*COL["hole"][:3], 0.0))
            mesh.scale(h["radius"], h["radius"], h["radius"])
            mesh.translate(*h["pos"])
            mesh.setGLOptions("translucent")
            self.view.addItem(mesh)
            self.hole_items.append({"mesh": mesh, "def": h})

        if self.current["bonds"]:
            b = self.current["bonds"][0]
            pts = self._dashed_points(b["from"], b["to"], 6)
            self.bond_item = gl.GLLinePlotItem(pos=pts, color=(1, 1, 1, 0.0),
                                                width=1.5, mode="lines", antialias=True)
            self.view.addItem(self.bond_item)

        self._apply_frame(0.0)

    def _dashed_points(self, p1, p2, n_dashes):
        p1, p2 = np.array(p1), np.array(p2)
        pts = []
        for i in range(n_dashes):
            t0 = i / n_dashes
            t1 = t0 + 0.5 / n_dashes
            pts.append(p1 + (p2 - p1) * t0)
            pts.append(p1 + (p2 - p1) * t1)
        return np.array(pts)

    def _ease(self, x):
        return 1 - (1 - x) ** 3

    # ---------------- animación ----------------
    def _apply_frame(self, tt):
        e = self._ease(tt)
        now = time.time()

        pos_a = np.array([a["start"] + (a["end"] - a["start"]) * e for a in self.current["atoms"]])
        self.atoms_scatter.setData(pos=pos_a)

        pos_e, col_e = [], []
        for el in self.current["electrons"]:
            p = el["start"] + (el["end"] - el["start"]) * e
            if el["mobile"]:
                wob = now * 1.4 + el["phase"]
                p = p + np.array([math.sin(wob) * 0.22, math.cos(wob * 1.3) * 0.22, 0.0])
            pos_e.append(p)
            c0, c1 = np.array(el["color_start"]), np.array(el["color_end"])
            col_e.append(c0 + (c1 - c0) * e)
        self.elec_scatter.setData(pos=np.array(pos_e), color=np.array(col_e))

        for h in self.hole_items:
            op = max(0.0, (tt - 0.6) / 0.4) * 0.6
            h["mesh"].opts["edgeColor"] = (*COL["hole"][:3], op)
            h["mesh"].update()

        if self.bond_item is not None:
            op = max(0.0, (tt - 0.6) / 0.4)
            self.bond_item.setData(color=(1, 1, 1, op))

    def _tick(self):
        if self.current is None:
            return
        if self.playing:
            elapsed = time.time() - self.start_time
            self.t = min(1.0, elapsed / 0.9)
            self._apply_frame(self.t)
            if self.t >= 1.0:
                self.playing = False
                self.btn_play.setText("Separar átomos ◀")
        else:
            if any(el["mobile"] for el in self.current["electrons"]):
                self._apply_frame(self.t)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = BondScene3D()
    win.show()
    sys.exit(app.exec())