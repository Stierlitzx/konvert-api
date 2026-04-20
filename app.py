import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="KONVERT — Unit Converter",
    page_icon="⚡",
    layout="centered",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&display=swap');
  html, body, [class*="css"] { font-family: 'DM Mono', monospace; }
  .result-box {
    background: #0a0a0a; border: 1px solid #e8ff47;
    padding: 20px 24px; border-radius: 2px; margin-top: 16px;
  }
  .result-big { font-size: 2.5rem; color: #47ffa3; font-weight: 500; }
  .result-formula { font-size: 0.75rem; color: #555; margin-top: 6px; }
</style>
""", unsafe_allow_html=True)

# ── Conversion data ──────────────────────────────────────────────────────────

LENGTH_TO_METERS = {
    "mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0,
    "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344,
}

WEIGHT_TO_KG = {
    "mg": 0.000001, "g": 0.001, "kg": 1.0, "t": 1000.0,
    "oz": 0.0283495, "lb": 0.453592, "st": 6.35029,
}

def convert_length(value, f, t):
    meters = value * LENGTH_TO_METERS[f]
    result = meters / LENGTH_TO_METERS[t]
    formula = f"{value} {f} × {LENGTH_TO_METERS[f]} ÷ {LENGTH_TO_METERS[t]} = {round(result, 6)} {t}"
    return round(result, 6), formula

def convert_weight(value, f, t):
    kg = value * WEIGHT_TO_KG[f]
    result = kg / WEIGHT_TO_KG[t]
    formula = f"{value} {f} × {WEIGHT_TO_KG[f]} ÷ {WEIGHT_TO_KG[t]} = {round(result, 6)} {t}"
    return round(result, 6), formula

def convert_temperature(value, f, t):
    if f == "C":   c = value
    elif f == "F": c = (value - 32) * 5 / 9
    else:          c = value - 273.15

    if t == "C":   result = c
    elif t == "F": result = c * 9 / 5 + 32
    else:          result = c + 273.15

    formula = f"{value}°{f} → {round(result, 4)}°{t}"
    return round(result, 4), formula

# ── UI ───────────────────────────────────────────────────────────────────────

st.title("⚡ KONVERT")
st.caption("Simple unit conversion — Length · Weight · Temperature")
st.divider()

category = st.segmented_control(
    "Category",
    options=["Length", "Weight", "Temperature"],
    default="Length",
)

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    value = st.number_input("Value", value=1.0, format="%.4f")

if category == "Length":
    units = list(LENGTH_TO_METERS.keys())
elif category == "Weight":
    units = list(WEIGHT_TO_KG.keys())
else:
    units = ["C", "F", "K"]

with col2:
    from_unit = st.selectbox("From", units, index=0)
with col3:
    to_unit = st.selectbox("To", units, index=1 if len(units) > 1 else 0)

if st.button("CONVERT ⚡", use_container_width=True, type="primary"):
    try:
        if category == "Length":
            result, formula = convert_length(value, from_unit, to_unit)
        elif category == "Weight":
            result, formula = convert_weight(value, from_unit, to_unit)
        else:
            result, formula = convert_temperature(value, from_unit, to_unit)

        st.markdown(f"""
        <div class="result-box">
            <div class="result-big">{result} {to_unit}</div>
            <div class="result-formula">Formula: {formula}</div>
        </div>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Conversion error: {e}")

st.divider()
st.caption("Built with FastAPI + Streamlit · Deployed on Railway + Streamlit Cloud")
