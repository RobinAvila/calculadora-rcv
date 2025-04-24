import streamlit as st

st.set_page_config(page_title="Calculadora RCV", layout="centered")
st.title("Evaluador de Riesgo Cardiovascular")

# --- Layout vertical completo ---
st.subheader("1. Criterios de RCV ALTO (cualquiera clasifica automáticamente)")
ecv = st.checkbox("ECV aterosclerótica")
dm = st.checkbox("Diabetes Mellitus")
erc = st.checkbox("ERC etapa 3b–5 o albuminuria ≥30 mg/g")
hta = st.checkbox("HTA refractaria")
dislip = st.checkbox("Dislipidemia severa (LDL ≥190 mg/dL)")

# --- Datos clínicos base ---
st.subheader("2. Datos clínicos para estimar RCV")
sexo = st.radio("Sexo:", ["Hombre", "Mujer"], index=None)
edad = st.number_input("Edad (años):", min_value=1, max_value=120, value=None, placeholder="Ingresa edad")
fuma = st.checkbox("Fumador/a")
pas = st.number_input("Presión arterial sistólica (mmHg):", min_value=60, max_value=260, value=None, placeholder="Ej: 130")
pad = st.number_input("Presión arterial diastólica (mmHg):", min_value=40, max_value=160, value=None, placeholder="Ej: 85")
col = st.number_input("Colesterol total (mg/dL):", min_value=80, max_value=400, value=None, placeholder="Ej: 200")
hdl = st.number_input("Colesterol HDL (mg/dL):", min_value=10, max_value=100, value=None, placeholder="Ej: 50")

# --- Modificadores adicionales ---
st.subheader("3. Factores que aumentan la categoría de riesgo")
familiar = st.checkbox("ECV prematura en familiar de 1º grado")
st.markdown("**Síndrome metabólico – selecciona ≥3 criterios:**")
c3, c4 = st.columns(2)
with c3:
    cc = st.checkbox("CC elevada: ≥90cm (H) o ≥80cm (M)")
    pa_elevada = st.checkbox("PA ≥130/85 o en tratamiento")
    tg = st.checkbox("TG ≥150 o en tratamiento")
with c4:
    hdl_bajo = st.checkbox("HDL bajo: <40 (H) / <50 (M)")
    glicemia = st.checkbox("Glicemia ≥100 o en tratamiento")

# --- Clasificadores ---
def clasificar_edad(e):
    if e < 35: return "35-44"
    elif e <= 44: return "35-44"
    elif e <= 54: return "45-54"
    elif e <= 64: return "55-64"
    else: return "65-74"

def clasificar_pa(sist, diast):
    if sist >= 160 or diast >= 100: return "≥160/≥100"
    elif sist >= 140 or diast >= 90: return "140-159/90-99"
    elif sist >= 130 or diast >= 85: return "130-139/85-89"
    elif sist >= 120 or diast >= 80: return "120-129/80-84"
    else: return "<120/80"

def clasificar_col(c):
    if c < 160: return "<160"
    elif c < 180: return "160-179"
    elif c < 220: return "180-219"
    elif c < 280: return "220-279"
    else: return "≥280"

# --- Tablas ---

from tablas_riesgo_code import tablas_riesgo

# --- Botón de cálculo ---
if st.button("Calcular riesgo"):
    causas_alto = []
    if ecv: causas_alto.append("ECV aterosclerótica")
    if dm: causas_alto.append("Diabetes Mellitus")
    if erc: causas_alto.append("ERC etapa 3b–5")
    if hta: causas_alto.append("HTA refractaria")
    if dislip: causas_alto.append("Dislipidemia severa")

    if causas_alto:
        st.markdown(f"### 🔴 RCV ALTO por {' y '.join(causas_alto)}")
    else:
        grupo = (sexo, fuma, clasificar_edad(edad))
        pa_cat = clasificar_pa(pas, pad)
        col_cat = clasificar_col(col)

        try:
            riesgo = tablas_riesgo[grupo][pa_cat][col_cat]
        except:
            st.warning("No se encontró combinación en la tabla.")
            st.stop()

        # Corrección por cHDL
        if hdl < 35:
            riesgo *= 1.5
            cor_hdl = "corregido al alza por cHDL <35"
        elif hdl >= 60:
            riesgo *= 0.5
            cor_hdl = "corregido a la baja por cHDL ≥60"
        else:
            cor_hdl = "no corregido por cHDL"

        # Categoría base
        if riesgo >= 10:
            categoria = "ALTO"
            color = "🔴"
        elif riesgo >= 5:
            categoria = "MODERADO"
            color = "🟠"
        else:
            categoria = "BAJO"
            color = "🟢"

        # Evaluación de SM
        componentes = sum([cc, pa_elevada, tg, hdl_bajo, glicemia])
        sm_presente = componentes >= 3

        # Ajuste por SM o antecedentes
        factores_extra = []
        if sm_presente:
            factores_extra.append("síndrome metabólico")
        if familiar:
            factores_extra.append("ECV familiar prematura")

        if categoria != "ALTO" and factores_extra:
            if categoria == "BAJO":
                categoria = "MODERADO"
                color = "🟠"
            elif categoria == "MODERADO":
                categoria = "ALTO"
                color = "🔴"

        # Resultado final
        resumen = f"RCV según tablas adaptadas: Base {riesgo:.1f}% {cor_hdl}"
        if factores_extra:
            resumen += " + " + " y ".join(factores_extra)
        else:
            resumen += " sin factores adicionales que modifiquen la categoría"

        resumen += f" → RCV final estimado: {color} {categoria}"
        st.markdown(f"### {resumen}")
