import re
import os
from datetime import datetime, timezone

import streamlit as st

try:
    from supabase import create_client, Client
except Exception:
    create_client = None
    Client = None


st.set_page_config(
    page_title="Raio-X Comercial",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {max-width: 720px; padding-top: 1.5rem; padding-bottom: 3rem;}
    .hero {text-align:center; padding: .5rem 0 1rem;}
    .hero h1 {font-size: 2.1rem; margin-bottom:.2rem; letter-spacing:-.5px;}
    .hero p {font-size:1rem; opacity:.75; margin:0;}
    .step-label {font-size:.85rem; font-weight:600; opacity:.6; text-transform:uppercase; letter-spacing:.5px; margin-bottom:.4rem;}
    .card {padding:1.3rem 1.4rem; border:1px solid rgba(128,128,128,.18); border-radius:18px; margin:1rem 0; background:rgba(255,255,255,.03);}
    .highlight {padding:1.1rem 1.3rem; border-radius:16px; background:rgba(255,102,0,.12); border:1px solid rgba(255,102,0,.3); margin:1rem 0;}
    .success {padding:1.1rem 1.3rem; border-radius:16px; background:rgba(0,160,80,.1); border:1px solid rgba(0,160,80,.25); margin:1rem 0;}
    .insight {padding:1rem 1.2rem; border-radius:14px; background:rgba(100,140,255,.08); border:1px solid rgba(100,140,255,.2); margin:.8rem 0;}
    .muted {opacity:.7;}
    .small {font-size:.88rem; opacity:.7;}
    .stButton > button {border-radius:12px; font-weight:600; padding:.6rem 1.2rem;}
    div[data-testid="stMetric"] {background:rgba(255,255,255,.04); padding:.8rem; border-radius:14px; border:1px solid rgba(128,128,128,.12);}
    .progress-bar {height:6px; background:rgba(128,128,128,.15); border-radius:99px; margin:1rem 0 1.5rem; overflow:hidden;}
    .progress-fill {height:100%; background:linear-gradient(90deg,#ff6600,#ff9933); border-radius:99px; transition:width .3s;}
</style>
""", unsafe_allow_html=True)


def brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(v):
    return f"{v * 100:.1f}%".replace(".", ",")


def clean_phone(phone):
    return re.sub(r"\D", "", phone or "")


def validate_phone(phone):
    p = clean_phone(phone)
    return 10 <= len(p) <= 13


def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key or create_client is None:
        return None
    return create_client(url, key)


def save_lead(data):
    sb = get_supabase()
    if sb is None:
        return False, "Supabase não configurado. Diagnóstico liberado mesmo assim."
    try:
        sb.table("raio_x_leads").insert(data).execute()
        return True, "Lead salvo."
    except Exception as exc:
        return False, f"Não deu pra salvar agora: {exc}"


def calculate(data):
    contacts = data["contacts"]
    conversations = data["conversations"]
    quotes = data["quotes"]
    sales = data["sales"]
    gain = data["gain"]
    target = data["target"]

    r1 = conversations / contacts if contacts else 0
    r2 = quotes / conversations if conversations else 0
    r3 = sales / quotes if quotes else 0
    rates = {
        "Contato → conversa": r1,
        "Conversa → cotação": r2,
        "Cotação → venda": r3,
    }
    bottleneck = min(rates, key=rates.get)

    current_revenue = sales * gain
    target_revenue = target * gain

    candidates = []
    if contacts > 0 and r2 > 0 and r3 > 0:
        needed_r1 = target / (contacts * r2 * r3)
        candidates.append(("Contato → conversa", needed_r1))
    if conversations > 0 and r1 > 0 and r3 > 0:
        needed_r2 = target / (contacts * r1 * r3)
        candidates.append(("Conversa → cotação", needed_r2))
    if quotes > 0 and r1 > 0 and r2 > 0:
        needed_r3 = target / (contacts * r1 * r2)
        candidates.append(("Cotação → venda", needed_r3))

    current_rates = {
        "Contato → conversa": r1,
        "Conversa → cotação": r2,
        "Cotação → venda": r3,
    }

    bottleneck_need = next((x[1] for x in
... 
