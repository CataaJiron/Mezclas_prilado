"""
Optimizador de Mezclas de Sales
================================
Balance de masa en dos etapas: Dilución → Tolva
Todos los cálculos son auditables y visibles en pantalla.
"""

import streamlit as st
import pandas as pd
import numpy as np
import random
import json

# ─── CONFIGURACIÓN DE PÁGINA ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Optimizador de Mezclas de Sales",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── ESTILOS PERSONALIZADOS ───────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fondo y colores generales */
    .stApp { background-color: #0B0E14; color: #E8EFF8; }
    [data-testid="stSidebar"] { background-color: #111620; border-right: 1px solid #1E2A3A; }
    [data-testid="stSidebar"] * { color: #E8EFF8 !important; }

    /* Métricas KPI */
    [data-testid="metric-container"] {
        background: #161C28;
        border: 1px solid #1E2A3A;
        border-radius: 8px;
        padding: 14px 16px;
    }
    [data-testid="metric-container"] label { color: #6B82A0 !important; font-size: 11px !important; }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #00B4D8 !important; font-family: 'Courier New', monospace; font-size: 22px !important;
    }

    /* Encabezados de sección */
    .section-header {
        background: #161C28;
        border: 1px solid #1E2A3A;
        border-left: 3px solid #00B4D8;
        border-radius: 6px;
        padding: 10px 16px;
        margin-bottom: 16px;
        font-weight: 600;
        font-size: 14px;
        color: #E8EFF8;
    }

    /* Semáforos */
    .sem-ok   { background:#22C55E22; border:1px solid #22C55E55; color:#22C55E;
                padding:3px 10px; border-radius:4px; font-size:11px; font-weight:700; }
    .sem-warn { background:#EAB30822; border:1px solid #EAB30855; color:#EAB308;
                padding:3px 10px; border-radius:4px; font-size:11px; font-weight:700; }
    .sem-fail { background:#EF444422; border:1px solid #EF444455; color:#EF4444;
                padding:3px 10px; border-radius:4px; font-size:11px; font-weight:700; }

    /* Tarjetas de resultado */
    .result-card {
        background: #161C28;
        border: 1px solid #1E2A3A;
        border-radius: 8px;
        padding: 16px;
        margin: 8px 0;
    }
    .formula-box {
        background: #0B0E14;
        border: 1px dashed #00B4D844;
        border-radius: 6px;
        padding: 10px 14px;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        color: #6B82A0;
        margin-top: 10px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { background: #111620; border-bottom: 1px solid #1E2A3A; gap: 4px; }
    .stTabs [data-baseweb="tab"] { background: transparent; color: #6B82A0; font-size: 12px; font-weight: 600; }
    .stTabs [aria-selected="true"] { background: #161C28 !important; color: #00B4D8 !important; border-bottom: 2px solid #00B4D8 !important; }

    /* Tablas */
    .dataframe { background: #161C28 !important; color: #E8EFF8 !important; border: 1px solid #1E2A3A !important; }
    .dataframe th { background: #111620 !important; color: #6B82A0 !important; font-size: 11px !important; }
    .dataframe td { font-family: 'Courier New', monospace !important; font-size: 12px !important; }

    /* Inputs */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background: #111620 !important; color: #E8EFF8 !important;
        border: 1px solid #1E2A3A !important; border-radius: 5px !important;
    }

    /* Botones */
    .stButton button {
        background: #111620; border: 1px solid #1E2A3A;
        color: #E8EFF8; border-radius: 5px; font-size: 12px;
        font-weight: 600; transition: all .15s;
    }
    .stButton button:hover { border-color: #00B4D8; color: #00B4D8; }

    /* Expander */
    .streamlit-expanderHeader {
        background: #161C28 !important; color: #6B82A0 !important;
        border: 1px solid #1E2A3A !important; border-radius: 6px !important;
        font-size: 12px !important;
    }
    div[data-testid="stExpander"] > div { background: #111620 !important; border: 1px solid #1E2A3A !important; }

    h1,h2,h3,h4 { color: #E8EFF8 !important; }
    .stMarkdown p { color: #6B82A0; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ─── Agregados QUÍMICOS ─────────────────────────────────────────────────────
COMPS = ["K2SO4", "B", "NaCl", "Mg", "Na", "SO4", "Na2SO4"]

# ─── DATOS POR DEFECTO ────────────────────────────────────────────────────────
DEFAULT_CRYSTALS = [
    {"nombre": "LDTP", "lote": 1001, "losa": "Losa 9B", "ton": 15.0, "K2SO4": 0.63,  "B": 0.01, "NaCl": 0.39,  "Mg": 0.09, "Na": 0.14, "SO4": 0.35, "Na2SO4": 0.05},
    {"nombre": "L",    "lote": 1002, "losa": "Losa 9A", "ton": 10.0, "K2SO4": 1.56,  "B": 0.03, "NaCl": 0.73,  "Mg": 0.10, "Na": 0.34, "SO4": 0.86, "Na2SO4": 0.00},
    {"nombre": "MFE",  "lote": 1003, "losa": "Losa 5",  "ton": 20.0, "K2SO4": 1.42,  "B": 0.03, "NaCl": 10.32, "Mg": 0.16, "Na": 2.25, "SO4": 0.79, "Na2SO4": 1.16},
    {"nombre": "SOP",  "lote": 1004, "losa": "Losa 3",  "ton": 5.0,  "K2SO4": 100.0, "B": 0.00, "NaCl": 0.00,  "Mg": 0.00, "Na": 0.00, "SO4": 55.0, "Na2SO4": 0.00},
    {"nombre": "MOP",  "lote": 1005, "losa": "Losa 1",  "ton": 5.0,  "K2SO4": 0.00,  "B": 0.00, "NaCl": 75.0,  "Mg": 0.00, "Na": 0.00, "SO4": 0.00, "Na2SO4": 0.00},
]

DEFAULT_PRODUCTS = {
    "QROP KPLUS": {
        "K2SO4":  {"min": 18.0,  "max": 22.0},
        "B":      {"min": None,  "max": 0.03},
        "NaCl":   {"min": None,  "max": None},
        "Mg":     {"min": None,  "max": 0.23},
        "Na":     {"min": None,  "max": 0.70},
        "SO4":    {"min": None,  "max": 1.50},
        "Na2SO4": {"min": None,  "max": None},
    },
}

# ─── INICIALIZAR SESSION STATE ────────────────────────────────────────────────
if "crystals" not in st.session_state:
    st.session_state.crystals = DEFAULT_CRYSTALS.copy()
if "products" not in st.session_state:
    st.session_state.products = {k: v.copy() for k, v in DEFAULT_PRODUCTS.items()}
if "active_product" not in st.session_state:
    st.session_state.active_product = list(st.session_state.products.keys())[0]
if "mix_dilucion" not in st.session_state:
    st.session_state.mix_dilucion = None  # {"total_masa": float, "law": dict, "streams": list}


def get_active_constraints():
    """Devuelve las restricciones del producto actualmente seleccionado."""
    products = st.session_state.products
    active = st.session_state.active_product
    if active not in products:
        active = list(products.keys())[0] if products else None
        st.session_state.active_product = active
    return products.get(active, {}) if active else {}



# ─── MOTOR MATEMÁTICO ─────────────────────────────────────────────────────────

def calc_blend(streams: list[dict]) -> dict:
    """
    Calcula la ley de mezcla ponderada por masa.
    streams: lista de {"nombre": str, "masa": float, "law": {comp: float}}
    Retorna: {"total_masa": float, "law": {comp: float}}

    Fórmula: Ley_mezcla = Σ(masa_i × ley_i) / Σ(masa_i)
    """
    total_masa = sum(s["masa"] for s in streams if s["masa"] > 0)
    if total_masa == 0:
        return {"total_masa": 0, "law": {c: 0.0 for c in COMPS}}

    law = {}
    for c in COMPS:
        law[c] = sum(s["masa"] * s["law"].get(c, 0) for s in streams) / total_masa

    return {"total_masa": total_masa, "law": law}


def check_constraints(law: dict, constraints: dict) -> list[dict]:
    """
    Evalúa cada Agregados contra sus restricciones.
    Retorna lista de {comp, val, min, max, ok, near_limit, status}
    """
    results = []
    for comp in COMPS:
        val = law.get(comp, 0)
        c = constraints.get(comp, {})
        cmin = c.get("min")
        cmax = c.get("max")

        ok_min = (cmin is None) or (val >= cmin)
        ok_max = (cmax is None) or (val <= cmax)
        ok = ok_min and ok_max

        near_limit = False
        if ok:
            if cmax is not None and val > cmax * 0.88:
                near_limit = True
            if cmin is not None and val < cmin * 1.08:
                near_limit = True

        if not ok:
            status = "FUERA"
        elif near_limit:
            status = "LÍMITE"
        else:
            status = "OK"

        results.append({
            "comp": comp, "val": val,
            "min": cmin, "max": cmax,
            "ok": ok, "near_limit": near_limit, "status": status
        })
    return results


def semaphore_html(status: str) -> str:
    cls = {"OK": "sem-ok", "LÍMITE": "sem-warn", "FUERA": "sem-fail"}.get(status, "sem-fail")
    icon = {"OK": "● OK", "LÍMITE": "● LÍMITE", "FUERA": "● FUERA"}.get(status, "●")
    return f'<span class="{cls}">{icon}</span>'


def optimize_blend(crystals: list, mix_dilucion: dict | None,
                   constraints: dict, total_target: float = 50.0,
                   use_mix: bool = True, n_iter: int = 3000) -> dict | None:
    """
    Optimizador: búsqueda aleatoria + refinamiento local (hill-climbing).

    Función objetivo:
      - Penaliza desviaciones fuera de rango × 1000
      - Penaliza desviación del punto medio × 0.5
      - Penaliza número de materiales activos × 0.1
    """
    sources = []
    for cr in crystals:
        law = {c: cr.get(c, 0) for c in COMPS}
        sources.append({"nombre": cr["nombre"], "law": law})

    if use_mix and mix_dilucion and mix_dilucion["total_masa"] > 0:
        sources.append({"nombre": "Mezcla Dilución", "law": mix_dilucion["law"]})

    n = len(sources)
    if n == 0:
        return None

    def score(weights):
        streams = [{"masa": w * total_target, "law": sources[i]["law"]}
                   for i, w in enumerate(weights)]
        blend = calc_blend(streams)
        law = blend["law"]
        s = 0.0
        for comp in COMPS:
            v = law.get(comp, 0)
            c = constraints.get(comp, {})
            cmin = c.get("min")
            cmax = c.get("max")
            if cmin is not None and v < cmin:
                s += ((cmin - v) / max(cmin, 1e-9)) ** 2 * 1000
            if cmax is not None and v > cmax:
                s += ((v - cmax) / max(cmax, 1e-9)) ** 2 * 1000
            if cmin is not None and cmax is not None:
                mid = (cmin + cmax) / 2
                s += ((v - mid) / max(mid, 1e-9)) ** 2 * 0.5
            elif cmax is not None:
                s += ((v - cmax * 0.8) / max(cmax * 0.8, 1e-9)) ** 2 * 0.5
        # penaliza materiales activos
        active = sum(1 for w in weights if w > 0.01)
        s += active * 0.1
        return s

    best_weights = None
    best_score = float("inf")

    # Búsqueda aleatoria
    for _ in range(n_iter):
        w = [random.random() for _ in range(n)]
        total = sum(w)
        w = [x / total for x in w]
        sc = score(w)
        if sc < best_score:
            best_score = sc
            best_weights = w[:]

    # Refinamiento local (hill-climbing)
    if best_weights:
        current = best_weights[:]
        for _ in range(500):
            i, j = random.sample(range(n), 2)
            delta = (random.random() - 0.5) * 0.1
            nb = current[:]
            nb[i] = max(0, nb[i] + delta)
            nb[j] = max(0, nb[j] - delta)
            total = sum(nb)
            if total <= 0:
                continue
            nb = [x / total for x in nb]
            sc = score(nb)
            if sc < best_score:
                best_score = sc
                best_weights = nb[:]
                current = nb[:]

    if not best_weights:
        return None

    streams = []
    for i, w in enumerate(best_weights):
        masa = w * total_target
        if masa > 0.05:
            streams.append({
                "nombre": sources[i]["nombre"],
                "masa": round(masa, 2),
                "pct": round(w * 100, 1),
                "law": sources[i]["law"],
            })

    blend = calc_blend(streams)
    return {
        "streams": streams,
        "total_masa": blend["total_masa"],
        "law": blend["law"],
        "score": best_score,
    }


# ─── SIDEBAR: NAVEGACIÓN ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### Optimizador de Mezclas")
    st.markdown("---")

    page = st.radio(
        "Módulo",
        options=["Dashboard", "Cristales", "Dilución", "Tolva", "Calidad", "Optimizador"],
        format_func=lambda x: {
            "Dashboard":   "Dashboard",
            "Cristales":   "Base de cristales",
            "Dilución":    "Mezcla de Dilución",
            "Tolva":       "Alimentación Tolva",
            "Calidad":     "Restricciones",
            "Optimizador": "Optimizador",
        }[x],
    )

    st.markdown("---")

    # Selector de producto activo
    products = st.session_state.products
    product_names = list(products.keys())
    if product_names:
        current = st.session_state.active_product
        idx = product_names.index(current) if current in product_names else 0
        sel_product = st.selectbox("Producto a fabricar", product_names, index=idx, key="sidebar_product_sel")
        st.session_state.active_product = sel_product

    st.markdown("---")

    # Estado rápido en sidebar
    mix = st.session_state.mix_dilucion
    if mix:
        st.success(f"✓ Dilución: {mix['total_masa']:.1f} Ton")
        st.caption(f"K₂SO₄: {mix['law']['K2SO4']:.4f}%  |  Na: {mix['law']['Na']:.4f}%")
    else:
        st.info("Sin Dilución calculada")

    st.markdown("---")
    #st.caption("Fórmula base:")
    #st.code("Ley = Σ(masa·ley) / Σmasa", language=None)


# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO: DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":
    st.markdown('<div class="section-header"> Dashboard — Estado del proceso</div>', unsafe_allow_html=True)

    mix = st.session_state.mix_dilucion
    law = mix["law"] if mix else None

    # KPIs
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Masa Dilución", f"{mix['total_masa']:.1f} Ton" if mix else "—")
    with col2:
        st.metric("K₂SO₄ final", f"{law['K2SO4']:.4f} %" if law else "—")
    with col3:
        st.metric("Na final", f"{law['Na']:.4f} %" if law else "—")
    with col4:
        st.metric("Mg final", f"{law['Mg']:.4f} %" if law else "—")
    with col5:
        if law:
            checks = check_constraints(law, get_active_constraints())
            fails = sum(1 for c in checks if not c["ok"])
            st.metric("Estado calidad", "✓ Aprobado" if fails == 0 else f"✗ {fails} falla(s)")
        else:
            st.metric("Estado calidad", "—")

    st.markdown("---")

    if law:
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown("#### Comparación objetivo vs real")
            active_constraints = get_active_constraints()
            checks = check_constraints(law, active_constraints)
            for ch in checks:
                constr = active_constraints.get(ch["comp"], {})
                if constr.get("min") is None and constr.get("max") is None:
                    continue
                col_a, col_b, col_c = st.columns([2, 2, 1])
                with col_a:
                    st.markdown(f"**{ch['comp']}**")
                with col_b:
                    cmin = constr.get("min", 0) or 0
                    cmax = constr.get("max") or (cmin * 2 if cmin else 1)
                    prog = min(1.0, max(0.0, ch["val"] / max(cmax, 1e-9)))
                    st.progress(prog)
                    st.caption(f"Valor: {ch['val']:.4f}  |  Obj: {cmin or '—'} – {cmax or '—'}")
                with col_c:
                    st.markdown(semaphore_html(ch["status"]), unsafe_allow_html=True)

        with col_right:
            st.markdown("#### Ley química del producto")
            df_law = pd.DataFrame([
                {"Agregados": c, "Ley (%)": f"{law.get(c, 0):.4f}"} for c in COMPS
            ])
            st.dataframe(df_law, hide_index=True, use_container_width=True)

        st.markdown('<div class="formula-box">Fórmula: Ley_mezcla = Σ(masa_i × ley_i) / Σ masa_i</div>',
                    unsafe_allow_html=True)
    else:
        st.info("Completa la Mezcla de Dilución para ver el dashboard. Navega a **Dilución** en el menú lateral.")


# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO 1: CRISTALES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Cristales":
    st.markdown('<div class="section-header">  Base de datos de cristales</div>', unsafe_allow_html=True)
    st.caption("Registra las leyes químicas (% en masa) de cada material disponible en cancha, junto con su lote, losa y stock.")

    # Mostrar tabla actual
    crystals = st.session_state.crystals
    if crystals:
        df = pd.DataFrame(crystals)
        df_display = df.copy()
        for c in COMPS:
            df_display[c] = df_display[c].apply(lambda x: f"{x:.3f}" if x > 0 else "—")
        if "ton" in df_display.columns:
            df_display["ton"] = df_display["ton"].apply(lambda x: f"{x:.1f}")
        # Reordenar columnas: nombre, lote, losa, ton, luego Agregados
        cols_order = ["nombre", "lote", "losa", "ton"] + COMPS
        cols_order = [c for c in cols_order if c in df_display.columns]
        df_display = df_display[cols_order]
        df_display = df_display.rename(columns={
            "nombre": "Cristal", "lote": "N° Lote", "losa": "Losa", "ton": "Ton",
        })
        st.dataframe(df_display, hide_index=True, use_container_width=True)
    else:
        st.warning("No hay cristales registrados. Agrega al menos uno.")

    st.markdown("---")

    # Formulario para nuevo cristal / edición
    with st.expander(" Agregar / editar cristal", expanded=False):
        mode = st.radio("Acción", ["Nuevo cristal", "Editar existente", "Eliminar"], horizontal=True)

        if mode == "Nuevo cristal":
            id_cols = st.columns(4)
            with id_cols[0]:
                nombre = st.text_input("Nombre del cristal", placeholder="Ej: MFE")
            with id_cols[1]:
                lote = st.number_input("N° Lote", min_value=0, step=1, value=0, key="new_lote")
            with id_cols[2]:
                losa = st.text_input("Losa", placeholder="Ej: Losa 9A", key="new_losa")
            with id_cols[3]:
                ton = st.number_input("Ton (stock disponible)", min_value=0.0, step=0.5, value=0.0, key="new_ton")

            cols = st.columns(4)
            vals = {}
            for i, comp in enumerate(COMPS):
                with cols[i % 4]:
                    vals[comp] = st.number_input(f"{comp} (%)", min_value=0.0, step=0.001,
                                                  format="%.3f", key=f"new_{comp}")
            if st.button("✓ Guardar cristal", type="primary"):
                if not nombre.strip():
                    st.error("Ingresa un nombre.")
                else:
                    entry = {"nombre": nombre.strip(), "lote": int(lote), "losa": losa.strip(), "ton": float(ton), **vals}
                    st.session_state.crystals.append(entry)
                    st.success(f"Cristal '{nombre}' guardado.")
                    st.rerun()

        elif mode == "Editar existente" and crystals:
            nombres = [c["nombre"] for c in crystals]
            sel = st.selectbox("Seleccionar cristal", nombres)
            idx = nombres.index(sel)
            cr = crystals[idx]

            id_cols = st.columns(4)
            with id_cols[0]:
                st.text_input("Nombre del cristal", value=sel, disabled=True, key="edit_nombre_display")
            with id_cols[1]:
                lote = st.number_input("N° Lote", min_value=0, step=1, value=int(cr.get("lote", 0)), key="edit_lote")
            with id_cols[2]:
                losa = st.text_input("Losa", value=cr.get("losa", ""), key="edit_losa")
            with id_cols[3]:
                ton = st.number_input("Ton (stock disponible)", min_value=0.0, step=0.5, value=float(cr.get("ton", 0)), key="edit_ton")

            cols = st.columns(4)
            vals = {}
            for i, comp in enumerate(COMPS):
                with cols[i % 4]:
                    vals[comp] = st.number_input(f"{comp} (%)", value=float(cr.get(comp, 0)),
                                                  min_value=0.0, step=0.001, format="%.3f",
                                                  key=f"edit_{comp}")
            if st.button("✓ Actualizar cristal", type="primary"):
                st.session_state.crystals[idx] = {
                    "nombre": sel, "lote": int(lote), "losa": losa.strip(), "ton": float(ton), **vals
                }
                st.success(f"Cristal '{sel}' actualizado.")
                st.rerun()

        elif mode == "Eliminar" and crystals:
            nombres = [c["nombre"] for c in crystals]
            sel = st.selectbox("Cristal a eliminar", nombres, key="del_sel")
            if st.button("🗑 Eliminar", type="secondary"):
                st.session_state.crystals = [c for c in crystals if c["nombre"] != sel]
                st.success(f"'{sel}' eliminado.")
                st.rerun()

    # (Sección de fórmulas auditables removida)



# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO 2: MEZCLA DE DILUCIÓN
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Dilución":
    st.markdown('<div class="section-header">⟳  Mezcla de Dilución — Etapa 1</div>', unsafe_allow_html=True)
    st.caption("1 baldada = 5 toneladas  |  Ley mezcla = Σ(masa × ley) / Σmasa")

    crystals = st.session_state.crystals
    if not crystals:
        st.warning("Primero registra cristales en el módulo **Cristales**.")
        st.stop()

    nombres_cristales = [c["nombre"] for c in crystals]
    crystal_map = {c["nombre"]: c for c in crystals}

    # Número de Agregados
    n_streams = st.number_input("Número de Agregados", min_value=1, max_value=8, value=4, step=1)

    st.markdown("---")

    # Inputs por Agregados
    stream_inputs = []
    cols_header = st.columns(n_streams + 1)
    with cols_header[0]:
        st.markdown("**Agregados**")

    for i in range(n_streams):
        with cols_header[i + 1]:
            st.markdown(f"**Agregado {i+1}**")

    # Fila: selección de cristal
    cols = st.columns(n_streams + 1)
    with cols[0]:
        st.markdown("<small style='color:#6B82A0'>Cristal</small>", unsafe_allow_html=True)
    selecciones = []
    for i in range(n_streams):
        with cols[i + 1]:
            sel = st.selectbox("", ["— Ninguno —"] + nombres_cristales,
                               key=f"dil_cristal_{i}", label_visibility="collapsed")
            selecciones.append(sel)

    # Fila: baldadas
    cols = st.columns(n_streams + 1)
    with cols[0]:
        st.markdown("<small style='color:#6B82A0'>Baldadas</small>", unsafe_allow_html=True)
    baldadas = []
    for i in range(n_streams):
        with cols[i + 1]:
            b = st.number_input("", min_value=0, step=1, value=0,
                                key=f"dil_bald_{i}", label_visibility="collapsed")
            baldadas.append(b)

    # Calcular masas y Agregados
    streams = []
    for i in range(n_streams):
        if selecciones[i] != "— Ninguno —" and baldadas[i] > 0:
            cr = crystal_map[selecciones[i]]
            masa = baldadas[i] * 5
            streams.append({
                "nombre": selecciones[i],
                "masa": masa,
                "law": {c: cr.get(c, 0) for c in COMPS},
            })

    # Tabla de leyes por Agregados
    st.markdown("---")
    st.markdown("#### Tabla de leyes por Agregados")

    tabla_data = []
    for comp in ["Masa (Ton)"] + COMPS:
        row = {"Agregados": comp}
        for i in range(n_streams):
            if selecciones[i] != "— Ninguno —" and baldadas[i] > 0:
                cr = crystal_map[selecciones[i]]
                if comp == "Masa (Ton)":
                    row[f"C{i+1} · {selecciones[i]}"] = f"{baldadas[i]*5:.1f}"
                else:
                    row[f"C{i+1} · {selecciones[i]}"] = f"{cr.get(comp,0):.4f}"
            else:
                row[f"C{i+1}"] = "—"
        # Columna resultado
        if streams and comp != "Masa (Ton)":
            blend = calc_blend(streams)
            row["⟶ Mezcla Dilución"] = f"{blend['law'].get(comp,0):.4f}"
        elif streams and comp == "Masa (Ton)":
            row["⟶ Mezcla Dilución"] = f"{sum(s['masa'] for s in streams):.1f}"
        else:
            row["⟶ Mezcla Dilución"] = "—"
        tabla_data.append(row)

    df_tabla = pd.DataFrame(tabla_data)
    st.dataframe(df_tabla, hide_index=True, use_container_width=True)

    # Resultado
    st.markdown("---")
    if streams:
        blend = calc_blend(streams)

        st.markdown("#### ✅ Mezcla Dilución Resultante")

        # KPIs
        kpi_cols = st.columns(4)
        with kpi_cols[0]:
            st.metric("Masa total", f"{blend['total_masa']:.1f} Ton")
        with kpi_cols[1]:
            st.metric("K₂SO₄", f"{blend['law']['K2SO4']:.4f} %")
        with kpi_cols[2]:
            st.metric("Na", f"{blend['law']['Na']:.4f} %")
        with kpi_cols[3]:
            st.metric("B", f"{blend['law']['B']:.4f} %")

        # Tabla completa de ley
        df_result = pd.DataFrame([
            {"Agregados": c, "Ley mezcla (%)": f"{blend['law'][c]:.4f}"} for c in COMPS
        ])
        col_res, col_form = st.columns([1, 1])
        with col_res:
            st.dataframe(df_result, hide_index=True, use_container_width=True)
        with col_form:
            formula_lines = "  +  ".join([
                f"({s['masa']:.0f} × {s['nombre']})" for s in streams
            ])
            st.markdown(f"""
<div class="formula-box">
<strong>Auditoría del cálculo</strong><br><br>
Masa total = {blend['total_masa']:.1f} Ton<br><br>
Ley_K2SO4 = ({formula_lines}) / {blend['total_masa']:.1f}<br><br>
<em>Aplicar misma fórmula a cada Agregados</em>
</div>
""", unsafe_allow_html=True)

        # Guardar en session_state
        st.session_state.mix_dilucion = {
            "total_masa": blend["total_masa"],
            "law": blend["law"],
            "streams": [{"nombre": s["nombre"], "masa": s["masa"]} for s in streams],
        }
        st.success("✓ Mezcla Dilución guardada. Disponible en módulo **Tolva** y **Optimizador**.")
    else:
        st.info("Selecciona al menos un cristal con baldadas > 0 para calcular.")
        st.session_state.mix_dilucion = None


# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO 3: ALIMENTACIÓN A TOLVA
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Tolva":
    st.markdown('<div class="section-header">▽  Alimentación a Tolva — Etapa 2</div>', unsafe_allow_html=True)
    st.caption("La Mezcla Dilución entra como una Agregados más. Ley final = Σ(masa × ley) / Σmasa")

    crystals = st.session_state.crystals
    mix = st.session_state.mix_dilucion
    constraints = get_active_constraints()
    st.info(f" Producto activo: **{st.session_state.active_product}** — cambia el producto desde el menú lateral.")

    # Agregados de Mezcla Dilución
    streams_tolva = []

    if mix:
        col_a, col_b = st.columns([3, 1])
        with col_a:
            usar_mix = st.checkbox(
                f"Incluir Mezcla Dilución ({mix['total_masa']:.1f} Ton)",
                value=True
            )
        with col_b:
            st.markdown('<span style="color:#00B4D8;font-size:11px;font-weight:700">← ETAPA 1</span>',
                        unsafe_allow_html=True)
        if usar_mix:
            streams_tolva.append({
                "nombre": "Mezcla Dilución",
                "masa": mix["total_masa"],
                "law": mix["law"],
            })
    else:
        st.warning("No hay Mezcla Dilución calculada. Ve al módulo **Dilución** para calcularla.")

    st.markdown("---")
    st.markdown("#### Agregados adicionales")

    nombres_cristales = [c["nombre"] for c in crystals]
    crystal_map = {c["nombre"]: c for c in crystals}

    n_extra = st.number_input("Número de Agregados adicionales", min_value=0, max_value=6, value=2, step=1)

    for i in range(int(n_extra)):
        col1, col2 = st.columns([2, 1])
        with col1:
            sel = st.selectbox(f"Material {i+1}", ["— Ninguno —"] + nombres_cristales, key=f"tolva_mat_{i}")
        with col2:
            masa = st.number_input(f"Masa (Ton)", min_value=0.0, step=1.0, value=0.0, key=f"tolva_masa_{i}")
        if sel != "— Ninguno —" and masa > 0:
            cr = crystal_map[sel]
            streams_tolva.append({
                "nombre": sel,
                "masa": masa,
                "law": {c: cr.get(c, 0) for c in COMPS},
            })

    # Cálculo
    st.markdown("---")
    if streams_tolva:
        blend_tolva = calc_blend(streams_tolva)
        checks = check_constraints(blend_tolva["law"], constraints)
        all_ok = all(c["ok"] for c in checks)
        fails = sum(1 for c in checks if not c["ok"])

        # KPIs
        st.markdown("#### Alimentación Final a Tolva")
        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.metric("Masa total", f"{blend_tolva['total_masa']:.1f} Ton")
        with k2:
            st.metric("K₂SO₄", f"{blend_tolva['law']['K2SO4']:.4f} %")
        with k3:
            st.metric("Na", f"{blend_tolva['law']['Na']:.4f} %")
        with k4:
            st.metric("Mg", f"{blend_tolva['law']['Mg']:.4f} %")
        with k5:
            if all_ok:
                st.metric("Calidad", "✓ Aprobado")
            else:
                st.metric("Calidad", f"✗ {fails} falla(s)")

        # Tabla de materiales
        st.markdown("#### Composición por material")
        rows = []
        for s in streams_tolva:
            row = {"Material": s["nombre"], "Masa (Ton)": f"{s['masa']:.1f}"}
            for c in COMPS:
                row[c] = f"{s['law'].get(c,0):.4f}"
            rows.append(row)
        # Fila total
        total_row = {"Material": "TOTAL", "Masa (Ton)": f"{blend_tolva['total_masa']:.1f}"}
        for c in COMPS:
            total_row[c] = f"{blend_tolva['law'].get(c,0):.4f}"
        rows.append(total_row)

        df_tolva = pd.DataFrame(rows)
        st.dataframe(df_tolva, hide_index=True, use_container_width=True)

        # Semáforos
        st.markdown("#### Verificación de calidad")
        cols_sem = st.columns(len(COMPS))
        for i, ch in enumerate(checks):
            with cols_sem[i]:
                constr = constraints.get(ch["comp"], {})
                rng = ""
                if constr.get("min") is not None:
                    rng += f"≥{constr['min']} "
                if constr.get("max") is not None:
                    rng += f"≤{constr['max']}"
                st.markdown(f"""
<div style="text-align:center;padding:10px 6px;background:#161C28;
border:1px solid #1E2A3A;border-radius:8px">
<div style="font-size:11px;color:#6B82A0;margin-bottom:4px">{ch['comp']}</div>
<div style="font-size:16px;font-weight:700;font-family:monospace;color:#E8EFF8">{ch['val']:.4f}%</div>
<div style="font-size:10px;color:#3A4F6A;margin-bottom:4px">{rng or 'Sin restricción'}</div>
{semaphore_html(ch['status'])}
</div>
""", unsafe_allow_html=True)

        # Conclusión
        st.markdown("---")
        if all_ok:
            st.success("✅ Mezcla APROBADA — Cumple todas las restricciones de calidad.")
        else:
            fallidas = [c["comp"] for c in checks if not c["ok"]]
            st.error(f"❌ Mezcla RECHAZADA — Agregados fuera de especificación: {', '.join(fallidas)}")

        st.markdown('<div class="formula-box">Ley_final = Σ(masa_i × ley_i) / Σ masa_i  '
                    '— aplicado a cada Agregados por separado</div>', unsafe_allow_html=True)
    else:
        st.info("Agrega al menos una Agregados para calcular la alimentación a tolva.")


# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO 4: RESTRICCIONES
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Calidad":
    st.markdown('<div class="section-header">◎  Restricciones de calidad por producto</div>', unsafe_allow_html=True)
    st.caption("Cada producto tiene su propio set de restricciones. Elige, crea, renombra o elimina un producto y define sus rangos objetivo. "
               "Semáforo: Verde=OK · Amarillo=cerca del límite · Rojo=fuera de spec.")

    products = st.session_state.products
    product_names = list(products.keys())

    # ─── Selector / gestor de productos ───────────────────────────────────────
    st.markdown("#### Producto")
    col_sel, col_new, col_edit = st.columns([2, 1, 1])
    with col_sel:
        if product_names:
            current = st.session_state.active_product
            idx = product_names.index(current) if current in product_names else 0
            active = st.selectbox("Si se hace este producto, estas son sus restricciones:",
                                  product_names, index=idx, key="calidad_product_sel")
            st.session_state.active_product = active
        else:
            st.warning("No hay productos creados todavía.")
            active = None
    with col_new:
        st.markdown("&nbsp;")
        with st.popover("➕ Nuevo producto"):
            new_name = st.text_input("Nombre del producto", placeholder="Ej: K2SO4 Premium", key="new_product_name")
            if st.button("Crear producto", type="primary", key="btn_create_product"):
                if not new_name.strip():
                    st.error("Ingresa un nombre.")
                elif new_name.strip() in products:
                    st.error("Ya existe un producto con ese nombre.")
                else:
                    st.session_state.products[new_name.strip()] = {
                        c: {"min": None, "max": None} for c in COMPS
                    }
                    st.session_state.active_product = new_name.strip()
                    st.success(f"Producto '{new_name}' creado.")
                    st.rerun()
    with col_edit:
        st.markdown("&nbsp;")
        if active:
            with st.popover("✏️ Renombrar"):
                rename_val = st.text_input("Nuevo nombre", value=active, key="rename_product_input")
                if st.button("Guardar nombre", type="primary", key="btn_rename_product"):
                    rename_val = rename_val.strip()
                    if not rename_val:
                        st.error("El nombre no puede estar vacío.")
                    elif rename_val != active and rename_val in products:
                        st.error("Ya existe un producto con ese nombre.")
                    else:
                        # Reconstruye el diccionario preservando el orden y los valores
                        new_products = {}
                        for pname, pvals in st.session_state.products.items():
                            key_name = rename_val if pname == active else pname
                            new_products[key_name] = pvals
                        st.session_state.products = new_products
                        st.session_state.active_product = rename_val
                        st.success(f"Producto renombrado a '{rename_val}'.")
                        st.rerun()

    if not active:
        st.stop()

    # Opción de eliminar producto (si hay más de uno)
    if len(product_names) > 1:
        with st.expander("🗑 Eliminar este producto"):
            st.warning(f"Vas a eliminar **{active}** y sus restricciones. Esta acción no se puede deshacer.")
            if st.button("Confirmar eliminación", type="secondary", key="btn_delete_product"):
                del st.session_state.products[active]
                st.session_state.active_product = list(st.session_state.products.keys())[0]
                st.rerun()

    st.markdown("---")

    # ─── Edición de restricciones del producto activo ─────────────────────────
    constraints = st.session_state.products[active]
    updated = {}

    st.markdown(f"#### Rangos objetivo — *{active}*")
    for comp in COMPS:
        c = constraints.get(comp, {})
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.markdown(f"**{comp}**")
        with col2:
            min_val = st.number_input(
                f"Mínimo", min_value=0.0, step=0.001, format="%.3f",
                value=float(c.get("min") or 0.0), key=f"cmin_{active}_{comp}",
                help="Dejar en 0 = sin mínimo"
            )
        with col3:
            max_val = st.number_input(
                f"Máximo", min_value=0.0, step=0.001, format="%.3f",
                value=float(c.get("max") or 0.0), key=f"cmax_{active}_{comp}",
                help="Dejar en 0 = sin máximo"
            )
        updated[comp] = {
            "min": min_val if min_val > 0 else None,
            "max": max_val if max_val > 0 else None,
        }

    if st.button("✓ Guardar restricciones de este producto", type="primary"):
        st.session_state.products[active] = updated
        st.success(f"Restricciones de '{active}' actualizadas.")
        st.rerun()

    st.markdown("---")
    st.markdown("#### Leyenda del semáforo")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="result-card" style="border-left:3px solid #22C55E">'
                    '<b style="color:#22C55E">● OK</b><br>'
                    '<small style="color:#6B82A0">Dentro del rango objetivo</small></div>',
                    unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="result-card" style="border-left:3px solid #EAB308">'
                    '<b style="color:#EAB308">● LÍMITE</b><br>'
                    '<small style="color:#6B82A0">Dentro del rango pero &gt;88% del límite</small></div>',
                    unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="result-card" style="border-left:3px solid #EF4444">'
                    '<b style="color:#EF4444">● FUERA</b><br>'
                    '<small style="color:#6B82A0">Fuera de especificación — requiere ajuste</small></div>',
                    unsafe_allow_html=True)

    # Tabla resumen actual
    st.markdown("---")
    st.markdown(f"#### Restricciones actuales — *{active}*")
    rows = []
    for comp, c in st.session_state.products[active].items():
        rows.append({
            "Agregados": comp,
            "Mínimo (%)": f"{c['min']:.3f}" if c.get("min") is not None else "Sin restricción",
            "Máximo (%)": f"{c['max']:.3f}" if c.get("max") is not None else "Sin restricción",
        })
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    # Tabla comparativa de todos los productos
    if len(product_names) > 1:
        st.markdown("---")
        st.markdown("#### Comparación entre productos")
        comp_rows = []
        for comp in COMPS:
            row = {"Agregados": comp}
            for pname in product_names:
                c = st.session_state.products[pname].get(comp, {})
                rng = []
                if c.get("min") is not None:
                    rng.append(f"≥{c['min']}")
                if c.get("max") is not None:
                    rng.append(f"≤{c['max']}")
                row[pname] = " ".join(rng) if rng else "—"
            comp_rows.append(row)
        st.dataframe(pd.DataFrame(comp_rows), hide_index=True, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MÓDULO 5: OPTIMIZADOR
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Optimizador":
    st.markdown('<div class="section-header">◆  Optimizador automático de mezcla</div>', unsafe_allow_html=True)
    st.caption("Busca automáticamente la combinación de materiales que minimiza la desviación química respecto a las restricciones.")

    crystals = st.session_state.crystals
    mix = st.session_state.mix_dilucion
    constraints = get_active_constraints()
    st.info(f"📦 Producto activo: **{st.session_state.active_product}** — cambia el producto desde el menú lateral.")

    if not crystals:
        st.warning("Primero registra cristales.")
        st.stop()

    # Parámetros
    col1, col2, col3 = st.columns(3)
    with col1:
        total_target = st.number_input("Masa total objetivo (Ton)", min_value=1.0, value=50.0, step=5.0)
    with col2:
        usar_mix = st.checkbox("Incluir Mezcla Dilución", value=bool(mix),
                               disabled=not bool(mix))
    with col3:
        n_iter = st.selectbox("Iteraciones", [1000, 3000, 5000, 10000], index=1)

    st.markdown("---")

    with st.expander("📐  Detalles del algoritmo"):
        st.markdown(f"""
**Búsqueda aleatoria + refinamiento local (Hill Climbing)**

1. **{n_iter} iteraciones aleatorias**: genera vectores de peso normalizados (suma = 1)
2. **500 pasos de refinamiento**: transfiere masa entre pares de fuentes para bajar el score
3. **Función objetivo**:
   - Penalización fuera de rango: `((v - límite) / límite)² × 1000`
   - Desviación del punto medio: `× 0.5`
   - Materiales activos (>1%): `× 0.1` (prefiere mezclas simples)
4. Materiales con peso < 0.1% son excluidos del resultado final
        """)

    if st.button("▶  Buscar mezcla óptima", type="primary"):
        with st.spinner("Optimizando... esto puede tomar unos segundos."):
            result = optimize_blend(
                crystals=crystals,
                mix_dilucion=mix if usar_mix else None,
                constraints=constraints,
                total_target=total_target,
                use_mix=usar_mix,
                n_iter=int(n_iter),
            )

        if result is None:
            st.error("No se pudo calcular una solución. Verifica que haya cristales con restricciones definidas.")
        else:
            checks = check_constraints(result["law"], constraints)
            all_ok = all(c["ok"] for c in checks)
            fails = [c["comp"] for c in checks if not c["ok"]]

            st.markdown("---")
            st.markdown("#### Mezcla óptima encontrada")

            # KPIs
            k1, k2, k3, k4 = st.columns(4)
            with k1:
                st.metric("Masa total", f"{result['total_masa']:.1f} Ton")
            with k2:
                st.metric("K₂SO₄", f"{result['law']['K2SO4']:.4f} %")
            with k3:
                st.metric("Materiales activos", str(len(result["streams"])))
            with k4:
                st.metric("Calidad", "✓ Cumple" if all_ok else f"✗ {len(fails)} falla(s)")

            # Tabla de composición
            st.markdown("#### Composición propuesta")
            rows = []
            for s in result["streams"]:
                row = {
                    "Material": s["nombre"],
                    "Masa (Ton)": f"{s['masa']:.2f}",
                    "% participación": f"{s['pct']:.1f}%",
                }
                for c in COMPS:
                    row[c] = f"{s['law'].get(c,0):.4f}"
                rows.append(row)
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

            # Semáforos
            st.markdown("#### Verificación vs restricciones")
            cols_sem = st.columns(len(COMPS))
            for i, ch in enumerate(checks):
                with cols_sem[i]:
                    constr = constraints.get(ch["comp"], {})
                    rng = ""
                    if constr.get("min"):
                        rng += f"≥{constr['min']} "
                    if constr.get("max"):
                        rng += f"≤{constr['max']}"
                    st.markdown(f"""
<div style="text-align:center;padding:10px 6px;background:#161C28;
border:1px solid #1E2A3A;border-radius:8px">
<div style="font-size:11px;color:#6B82A0">{ch['comp']}</div>
<div style="font-size:15px;font-weight:700;font-family:monospace;color:#E8EFF8">{ch['val']:.4f}%</div>
<div style="font-size:10px;color:#3A4F6A">{rng or '—'}</div>
{semaphore_html(ch['status'])}
</div>
""", unsafe_allow_html=True)

            st.markdown("---")
            if all_ok:
                st.success("✅ Mezcla APROBADA — Cumple todas las restricciones con la composición propuesta.")
            else:
                st.warning(
                    f"⚠️ No se encontró combinación perfecta. Agregados fuera de spec: {', '.join(fails)}. "
                    "Considera ampliar las restricciones o agregar más materiales."
                )

            st.markdown(f'<div class="formula-box">Score de optimización: {result["score"]:.6f} '
                        f'(menor = mejor) | Iteraciones: {n_iter} + 500 refinamiento</div>',
                        unsafe_allow_html=True)