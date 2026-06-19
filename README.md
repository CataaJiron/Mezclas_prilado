# ⚗️ Optimizador de Mezclas de Sales

Aplicación web para balance de masa en dos etapas: **Mezcla Dilución → Alimentación Tolva**.

## Módulos

| Módulo | Descripción |
|--------|-------------|
| Dashboard | KPIs en tiempo real, comparación objetivo vs real |
| Cristales | Base de datos de materiales y leyes químicas |
| Dilución | Etapa 1: mezcla ponderada por baldadas (1 baldada = 5 Ton) |
| Tolva | Etapa 2: alimentación final combinando dilución + cristales |
| Calidad | Restricciones con semáforo verde/amarillo/rojo |
| Optimizador | Búsqueda automática de mezcla óptima |

## Fórmula base

```
Ley_mezcla = Σ(masa_i × ley_i) / Σ masa_i
```

---

## 🚀 Cómo ejecutar localmente

### 1. Instalar Python
Descarga Python 3.11+ desde https://python.org

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar

```bash
streamlit run app.py
```

Se abre automáticamente en http://localhost:8501

---

## ☁️ Publicar en Streamlit Cloud (gratis)

### Paso 1 — Subir a GitHub

1. Crea una cuenta en https://github.com
2. Crea un repositorio nuevo (botón verde "New repository")
   - Nombre: `optimizador-mezclas` (o el que prefieras)
   - Visibilidad: **Public** (necesario para el plan gratuito)
3. En tu computador, abre la terminal y ejecuta:

```bash
# Navega a la carpeta donde están los archivos
cd ruta/a/tu/carpeta

# Inicializa git
git init
git add app.py requirements.txt README.md
git commit -m "Optimizador de mezclas de sales - versión inicial"

# Conecta con GitHub (reemplaza TU_USUARIO y TU_REPOSITORIO)
git remote add origin https://github.com/TU_USUARIO/optimizador-mezclas.git
git branch -M main
git push -u origin main
```

### Paso 2 — Publicar en Streamlit Cloud

1. Ve a https://share.streamlit.io
2. Inicia sesión con tu cuenta de GitHub
3. Haz clic en **"New app"**
4. Selecciona:
   - **Repository**: TU_USUARIO/optimizador-mezclas
   - **Branch**: main
   - **Main file path**: app.py
5. Haz clic en **"Deploy!"**

En 2-3 minutos tu app estará en:
```
https://TU_USUARIO-optimizador-mezclas-app-XXXX.streamlit.app
```

### Paso 3 — Actualizar la app

Cada vez que modifiques el código:

```bash
git add .
git commit -m "descripción del cambio"
git push
```

Streamlit Cloud se actualiza automáticamente.

---

## 📁 Estructura de archivos

```
optimizador-mezclas/
├── app.py              ← Aplicación principal (este archivo)
├── requirements.txt    ← Dependencias Python
└── README.md           ← Este archivo
```

## Componentes químicos

- K2SO4, B, NaCl, Mg, Na, SO4, Na2SO4

## Cristales disponibles por defecto

| Cristal | K2SO4 | B | NaCl | Mg | Na | SO4 | Na2SO4 |
|---------|-------|---|------|----|----|-----|--------|
| LDTP    | 0.630 | 0.010 | 0.390 | 0.090 | 0.140 | 0.350 | 0.050 |
| L       | 1.560 | 0.030 | 0.730 | 0.100 | 0.340 | 0.860 | 0.000 |
| MFE     | 1.420 | 0.030 | 10.320 | 0.160 | 2.250 | 0.790 | 1.160 |
| SOP     | 100.000 | 0.000 | 0.000 | 0.000 | 0.000 | 55.000 | 0.000 |
| MOP     | 0.000 | 0.000 | 75.000 | 0.000 | 0.000 | 0.000 | 0.000 |
