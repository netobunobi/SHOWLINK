<!-- ========================================== -->
<!-- ENCABEZADO Y DESCRIPCIÓN GENERAL           -->
<!-- ========================================== -->
# ⚛️ ShowLink

**ShowLink** es un software interactivo de escritorio desarrollado en **Python**, **PyQt6** y **OpenGL (`pyqtgraph`)** diseñado para analizar, clasificar y visualizar enlaces químicos y dopajes semiconductores en tiempo real.

El proyecto combina un backend físico-químico con una interfaz visual moderna que diagnostica el tipo de enlace, calcula configuraciones electrónicas y proyecta representaciones atómicas en 3D.

---

<!-- ========================================== -->
<!-- SECCIÓN: LO QUE YA ESTÁ HECHO Y FUNCIONA   -->
<!-- ========================================== -->
## 🚀 Estado Actual del Proyecto

Actualmente, el software cuenta con la arquitectura base de la interfaz gráfica, la lógica de cálculo químico y las pruebas de concepto del motor de renderizado tridimensional.

### 🧠 1. Backend y Lógica Química (Completado)
* **Procesamiento de entradas:** Validación y normalización de símbolos o nombres de elementos químicos.
* **Diagnóstico de enlace:** Clasificación automática del tipo de interacción entre dos elementos:
  * ⚪ Inerte / Sin enlace (Gases Nobles)
  * 🟡 Enlace Metálico (Conductores)
  * 🔴 Enlace Iónico (Aislantes en estado sólido)
  * 🔵 Enlace Covalente / Dopajes Semiconductores (Tipo N, Tipo P, Intrínseco)
* **Cálculo atómico:**
  * Configuración electrónica completa.
  * Determinación de electrones de valencia.
  * Conteo exacto de protones y neutrones.
  * Asignación de paleta de colores por elemento/familia.

### 🖥️ 2. Interfaz de Usuario (PyQt6 - Completado)
* **Diseño visual:** Estilo oscuro profesional (*Dark Theme*) estructurado en paneles divididos.
* **Selector interactivo:** Ventana modal con la Tabla Periódica completa optimizada para carga instantánea (0 ms).
* **Panel de diagnóstico:** Desglose detallado del comportamiento eléctrico del enlace y tarjetas de propiedades individuales para cada átomo.
* **Integración OpenGL:** Contenedor `GLViewWidget` incrustado directamente en la ventana principal.

### 🎨 3. Motor Gráfico 3D (Fase Inicial / Prototipo)
* Renderizado de mallas esféricas sólidas con cálculo de normales y sombreado (`GLMeshItem`).
* Trazado de órbitas circulares vectorizadas mediante funciones trigonométricas de NumPy y renderizado de líneas continuas (`GLLinePlotItem`).
* Control de cámara interactivo (rotación, traslación y zoom con ratón).

---

<!-- ========================================== -->
<!-- SECCIÓN: HOJA DE RUTA / LO QUE SE VIENE    -->
<!-- (Casillas de verificación: [ ] pendiente)  -->
<!-- ========================================== -->
## 🛠️ Hoja de Ruta (Roadmap / Próximas Implementaciones)

El desarrollo activo está centrado en la representación física tridimensional de los átomos y sus enlaces:

- [ ] **Distribución Atómica Realista:**
  - Núcleos generados mediante empaquetamiento esférico (Espiral de Fibonacci 3D) con esferas individuales diferenciadas para protones ($p^+$) y neutrones ($n^0$).
- [ ] **Electrones y Capas de Valencia:**
  - Posicionamiento de electrones activos sobre las órbitas.
  - Representación de huecos disponibles (electrones faltantes para el octeto/dueto).
- [ ] **Modos de Visualización Dinámicos:**
  - **Vista Separada:** Doble visor 3D interactivo independiente para inspeccionar ambos átomos por separado.
  - **Vista de Enlace:** Espacio unificado donde los átomos interactúan según el tipo de enlace (traslape de capas covalentes, transferencia iónica o nube metálica).
- [ ] **Controles de Perspectiva:**
  - Alternador de cámara 2D (plana) y 3D (perspectiva).
  - Simbología flotante en pantalla con guía de colores.

---

<!-- ========================================== -->
<!-- SECCIÓN: GUÍA DE INSTALACIÓN Y EJECUCIÓN   -->
<!-- ========================================== -->
## 📦 Requisitos e Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/ShowLink.git](https://github.com/tu-usuario/ShowLink.git)
   cd ShowLink
   ```

2. **Instalar dependencias necesarias:**
   ```bash
   pip install PyQt6 pyqtgraph PyOpenGL numpy
   ```

3. **Ejecutar la aplicación:**
   ```bash
   python main.py
   ```

---

<!-- ========================================== -->
<!-- ÁRBOL DE DIRECTORIOS DEL PROYECTO          -->
<!-- ========================================== -->
## 🏗️ Estructura del Proyecto

```text
ShowLink/
├── main.py              # Interfaz gráfica (PyQt6) y lógica de presentación
├── backend.py           # Cálculos químicos, configuraciones y reglas de enlace
├── SHOWLINK.ico         # Icono de la aplicación
└── README.md            # Documentación del proyecto
```
