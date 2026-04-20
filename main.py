from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Literal

app = FastAPI(title="Unit Converter API", version="1.0.0")

# ── Models ──────────────────────────────────────────────────────────────────

class ConvertRequest(BaseModel):
    value: float
    from_unit: str
    to_unit: str

class ConvertResponse(BaseModel):
    input_value: float
    input_unit: str
    output_value: float
    output_unit: str
    formula: str

# ── Conversion logic ─────────────────────────────────────────────────────────

LENGTH_TO_METERS = {
    "mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0,
    "in": 0.0254, "ft": 0.3048, "yd": 0.9144, "mi": 1609.344,
}

WEIGHT_TO_KG = {
    "mg": 0.000001, "g": 0.001, "kg": 1.0, "t": 1000.0,
    "oz": 0.0283495, "lb": 0.453592, "st": 6.35029,
}

def convert_length(value: float, from_unit: str, to_unit: str) -> tuple[float, str]:
    if from_unit not in LENGTH_TO_METERS or to_unit not in LENGTH_TO_METERS:
        raise HTTPException(400, f"Unknown length unit. Valid: {list(LENGTH_TO_METERS)}")
    meters = value * LENGTH_TO_METERS[from_unit]
    result = meters / LENGTH_TO_METERS[to_unit]
    formula = f"{value} {from_unit} × {LENGTH_TO_METERS[from_unit]} ÷ {LENGTH_TO_METERS[to_unit]}"
    return round(result, 6), formula

def convert_weight(value: float, from_unit: str, to_unit: str) -> tuple[float, str]:
    if from_unit not in WEIGHT_TO_KG or to_unit not in WEIGHT_TO_KG:
        raise HTTPException(400, f"Unknown weight unit. Valid: {list(WEIGHT_TO_KG)}")
    kg = value * WEIGHT_TO_KG[from_unit]
    result = kg / WEIGHT_TO_KG[to_unit]
    formula = f"{value} {from_unit} → kg × {WEIGHT_TO_KG[from_unit]} ÷ {WEIGHT_TO_KG[to_unit]}"
    return round(result, 6), formula

def convert_temperature(value: float, from_unit: str, to_unit: str) -> tuple[float, str]:
    units = {"C", "F", "K"}
    if from_unit not in units or to_unit not in units:
        raise HTTPException(400, "Unknown temp unit. Valid: C, F, K")
    # To Celsius first
    if from_unit == "C":   celsius = value
    elif from_unit == "F": celsius = (value - 32) * 5 / 9
    else:                  celsius = value - 273.15
    # From Celsius to target
    if to_unit == "C":   result, formula = celsius, f"({value}°{from_unit} - 32) × 5/9" if from_unit == "F" else f"{value} - 273.15"
    elif to_unit == "F": result, formula = celsius * 9 / 5 + 32, f"{value}°{from_unit} → °C → × 9/5 + 32"
    else:                result, formula = celsius + 273.15, f"{value}°{from_unit} → °C + 273.15"
    if from_unit == to_unit:
        result, formula = value, "same unit, no conversion"
    return round(result, 4), formula

# ── API Routes ───────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return FileResponse("static/index.html")

@app.get("/health")
def health():
    return {"status": "ok", "service": "unit-converter"}

@app.post("/convert/length", response_model=ConvertResponse)
def length(req: ConvertRequest):
    result, formula = convert_length(req.value, req.from_unit.lower(), req.to_unit.lower())
    return ConvertResponse(input_value=req.value, input_unit=req.from_unit,
                           output_value=result, output_unit=req.to_unit, formula=formula)

@app.post("/convert/weight", response_model=ConvertResponse)
def weight(req: ConvertRequest):
    result, formula = convert_weight(req.value, req.from_unit.lower(), req.to_unit.lower())
    return ConvertResponse(input_value=req.value, input_unit=req.from_unit,
                           output_value=result, output_unit=req.to_unit, formula=formula)

@app.post("/convert/temperature", response_model=ConvertResponse)
def temperature(req: ConvertRequest):
    result, formula = convert_temperature(req.value, req.from_unit.upper(), req.to_unit.upper())
    return ConvertResponse(input_value=req.value, input_unit=req.from_unit,
                           output_value=result, output_unit=req.to_unit, formula=formula)

@app.get("/units")
def list_units():
    return {
        "length": list(LENGTH_TO_METERS.keys()),
        "weight": list(WEIGHT_TO_KG.keys()),
        "temperature": ["C", "F", "K"],
    }

# Mount static files AFTER routes
app.mount("/static", StaticFiles(directory="static"), name="static")
