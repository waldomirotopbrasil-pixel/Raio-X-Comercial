import re
import os
import smtplib
import secrets as py_secrets
import hashlib
import hmac
from email.message import EmailMessage
from datetime import datetime, timezone, timedelta

import streamlit as st

try:
    from supabase import create_client
except Exception:
    create_client = None

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Raio-X Comercial | David Fernandes",
    page_icon="logo.png",
    layout="centered",
    initial_sidebar_state="collapsed",
)

ORANGE = "#FF6600"
DARK = "#080808"
TEXT = "#F5F5F5"

st.markdown(
    f"""
<style>
:root {{
    --bg: #080808;
    --surface: #111111;
    --surface-2: #171717;
    --surface-3: #1D1D1D;
    --border: #292929;
    --text: #F5F5F5;
    --text-secondary: #BDBDBD;
    --text-muted: #969696;
    --text-faint: #6F6F6F;
    --progress-bg: #242424;
    --orange: #FF6600;
    --orange-light: #FF9A5A;
    --danger-bg: rgba(255,102,0,.08);
    --danger-border: rgba(255,102,0,.38);
    --shadow: rgba(0,0,0,.22);
    --shadow-strong: rgba(0,0,0,.35);
}}

@media (prefers-color-scheme: light) {{
    :root {{
        --bg: #F5F5F5;
        --surface: #FFFFFF;
        --surface-2: #FFFFFF;
        --surface-3: #F0F0F0;
        --border: #D9D9D9;
        --text: #171717;
        --text-secondary: #555555;
        --text-muted: #707070;
        --text-faint: #888888;
        --progress-bg: #DCDCDC;
        --orange: #F05A00;
        --orange-light: #C94C00;
        --danger-bg: rgba(240,90,0,.07);
        --danger-border: rgba(240,90,0,.32);
        --shadow: rgba(0,0,0,.08);
        --shadow-strong: rgba(0,0,0,.14);
    }}
}}

#MainMenu, footer, header {{ visibility: hidden; }}

.stApp {{
    background: var(--bg) !important;
    color: var(--text) !important;
}}

.block-container {{
    max-width: 760px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
}}

html, body, [class*="st-"], .stApp {{
    font-family: "Montserrat", Arial, sans-serif !important;
}}

div[data-testid="stNumberInput"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stSelectbox"] label {{
    color: var(--text-secondary) !important;
    font-weight: 650 !important;
}}

input, textarea, select, button,
[data-testid="stNumberInput"] input {{
    font-family: "Montserrat", Arial, sans-serif !important;
    font-weight: 600 !important;
}}

div[data-baseweb="input"],
div[data-baseweb="select"],
div[data-baseweb="textarea"] {{
    background: var(--surface) !important;
    border-color: var(--border) !important;
}}

div[data-baseweb="input"] input,
div[data-baseweb="select"] input,
div[data-baseweb="textarea"] textarea {{
    color: var(--text) !important;
    background: var(--surface) !important;
    caret-color: var(--orange) !important;
}}

div[data-baseweb="input"] input::placeholder,
div[data-baseweb="textarea"] textarea::placeholder {{
    color: var(--text-muted) !important;
    opacity: 1 !important;
}}

div[data-baseweb="select"] > div {{
    background: var(--surface) !important;
    border-color: var(--border) !important;
}}

div[data-baseweb="select"] span {{
    color: var(--text) !important;
}}

[data-baseweb="popover"] {{
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
}}

[role="option"] {{
    background: var(--surface) !important;
    color: var(--text) !important;
}}

[role="option"]:hover {{
    background: var(--surface-3) !important;
}}

[data-testid="stMetricValue"] {{
    font-family: "Montserrat", Arial, sans-serif !important;
    font-weight: 700 !important;
    color: var(--text) !important;
}}

[data-testid="stMetricLabel"] {{
    color: var(--text-muted) !important;
}}

.brand {{
    text-align: center;
    margin-bottom: 1.35rem;
}}

.brand img {{
    width: 180px;
    height: 180px;
    object-fit: contain;
    margin: 0 auto;
    display: block;
    filter: drop-shadow(0 0 28px rgba(255,102,0,.25));
}}

.eyebrow {{
    color: var(--orange);
    font-size: .76rem;
    font-weight: 850;
    letter-spacing: .16em;
    text-transform: uppercase;
    margin-top: .55rem;
}}

.hero-title {{
    font-size: clamp(2rem, 7vw, 3.15rem);
    line-height: 1.03;
    font-weight: 900;
    margin: .35rem 0 .6rem;
    color: var(--text);
}}

.hero-sub {{
    color: var(--text-secondary);
    font-size: 1.03rem;
    line-height: 1.55;
    max-width: 620px;
    margin: 0 auto;
}}

.question-card {{
    background: linear-gradient(145deg, var(--surface-2), var(--surface));
    border: 1px solid var(--border);
    border-radius: 24px;
    padding: 1.35rem 1.25rem;
    margin-top: 1.15rem;
    box-shadow: 0 15px 45px var(--shadow);
}}

.step {{
    color: var(--orange);
    font-size: .77rem;
    font-weight: 850;
    letter-spacing: .08em;
    text-transform: uppercase;
}}

.question {{
    font-size: 1.5rem;
    line-height: 1.2;
    font-weight: 850;
    color: var(--text);
    margin: .35rem 0 .4rem;
}}

.helper {{
    color: var(--text-muted);
    font-size: .92rem;
    line-height: 1.45;
    margin-bottom: .8rem;
}}

.progress-wrap {{
    background: var(--progress-bg);
    height: 6px;
    border-radius: 99px;
    overflow: hidden;
    margin: .8rem 0 1.1rem;
}}

.progress-bar {{
    height: 100%;
    background: var(--orange);
    border-radius: 99px;
}}

.mini-note {{
    color: var(--text-faint);
    font-size: .82rem;
    text-align: center;
    margin-top: .55rem;
}}

.result-card {{
    background: linear-gradient(145deg, var(--surface-2), var(--surface));
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 1.25rem;
    margin: .9rem 0;
}}

.result-label {{
    color: var(--text-muted);
    font-size: .78rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    font-weight: 800;
}}

.result-value {{
    color: var(--text);
    font-size: 2rem;
    font-weight: 900;
    margin-top: .15rem;
}}

.orange {{ color: var(--orange); }}

.danger-card {{
    background: var(--danger-bg);
    border: 1px solid var(--danger-border);
    border-radius: 20px;
    padding: 1.15rem;
    margin: 1rem 0;
}}

.tip-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1rem 1.05rem;
    margin: .65rem 0;
}}

.tip-title {{
    color: var(--text);
    font-weight: 800;
    margin-bottom: .25rem;
}}

.tip-text {{
    color: var(--text-secondary);
    line-height: 1.48;
    font-size: .92rem;
}}

.potential {{
    border: 1px solid rgba(255,102,0,.45);
    background: linear-gradient(145deg, rgba(255,102,0,.13), rgba(255,102,0,.04));
    border-radius: 22px;
    padding: 1.25rem;
    text-align: center;
    margin: 1rem 0;
}}

.potential-number {{
    color: var(--orange);
    font-size: 2.35rem;
    line-height: 1;
    font-weight: 950;
    margin: .35rem 0;
}}

.celebration {{
    border: 1px solid rgba(255,102,0,.55);
    background:
        radial-gradient(circle at 50% 0%, rgba(255,102,0,.20), transparent 48%),
        linear-gradient(145deg, var(--surface-2), var(--surface));
    border-radius: 26px;
    padding: 1.7rem 1.25rem;
    text-align: center;
    margin: 1rem 0 1.25rem;
    box-shadow: 0 0 45px rgba(255,102,0,.10);
}}

.celebration-icon {{
    font-size: 3.3rem;
    line-height: 1;
    margin-bottom: .45rem;
}}

.celebration-title {{
    color: var(--text);
    font-size: 2rem;
    font-weight: 950;
    line-height: 1.05;
}}

.celebration-sub {{
    color: var(--text-secondary);
    font-size: .98rem;
    line-height: 1.5;
    margin-top: .6rem;
}}

.source-badge {{
    display: inline-block;
    border: 1px solid rgba(255,102,0,.35);
    background: rgba(255,102,0,.08);
    color: var(--orange-light);
    border-radius: 999px;
    padding: .35rem .7rem;
    font-size: .78rem;
    font-weight: 800;
    margin-top: .45rem;
}}

div.stButton > button {{
    border-radius: 14px !important;
    min-height: 48px !important;
    font-weight: 850 !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
    color: var(--text) !important;
    transition: transform .15s ease, border-color .15s ease, background .15s ease;
}}

div.stButton > button:hover {{
    border-color: var(--orange) !important;
    color: var(--text) !important;
}}

div.stButton > button[kind="primary"] {{
    background: var(--orange) !important;
    border-color: var(--orange) !important;
    color: #FFFFFF !important;
}}

div.stButton > button[kind="primary"]:hover {{
    background: var(--orange) !important;
    border-color: var(--orange) !important;
    color: #FFFFFF !important;
    filter: brightness(1.05);
}}

.section-title {{
    font-size: 1.15rem;
    font-weight: 850;
    margin: 1.3rem 0 .7rem;
    color: var(--text);
}}

.privacy {{
    text-align: center;
    color: var(--text-faint);
    font-size: .76rem;
    margin-top: .7rem;
}}

.profile-card {{
    background:
        radial-gradient(circle at 50% 0%, rgba(255,102,0,.16), transparent 54%),
        linear-gradient(145deg, var(--surface-2), var(--surface));
    border: 1px solid rgba(255,102,0,.52);
    border-radius: 26px;
    padding: 1.5rem 1.25rem;
    text-align: center;
    margin: 0 0 1.2rem;
    box-shadow: 0 0 42px rgba(255,102,0,.09);
}}

.profile-kicker {{
    color: var(--orange-light);
    font-size: .74rem;
    font-weight: 900;
    letter-spacing: .16em;
    text-transform: uppercase;
}}

.profile-name {{
    color: var(--text);
    font-size: clamp(1.55rem, 5vw, 2.2rem);
    line-height: 1.08;
    font-weight: 900;
    margin: .35rem 0 .45rem;
}}

.final-banner {{
    width: 100%;
    margin: 28px 0 24px 0;
    overflow: hidden;
    border-radius: 14px;
    border: 1px solid var(--border);
    line-height: 0;
}}

.final-banner img {{
    width: 100%;
    aspect-ratio: 4 / 1;
    object-fit: cover;
    display: block;
}}

.profile-desc {{
    color: var(--text-secondary);
    font-size: .9rem;
    line-height: 1.5;
    max-width: 580px;
    margin: 0 auto;
}}

.admin-float {{
    position: fixed;
    left: 18px;
    bottom: 16px;
    z-index: 9999;
    width: 34px;
    height: 34px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--border);
    background: var(--surface);
    border-radius: 50%;
    box-shadow: 0 5px 20px var(--shadow-strong);
    backdrop-filter: blur(8px);
}}

.admin-float a {{
    color: var(--text-muted);
    text-decoration: none;
    font-size: 13px;
}}

.admin-float a:hover {{ color: var(--orange); }}

.admin-shell {{ max-width: 1200px; margin: 0 auto; }}

.cta-team {{
    display: block;
    width: 100%;
    text-align: center;
    background: var(--orange);
    color: #FFFFFF !important;
    font-weight: 900;
    font-size: 1.05rem;
    padding: 1rem 1.25rem;
    border-radius: 14px;
    text-decoration: none !important;
    margin: 0.5rem 0 1.5rem;
    box-shadow: 0 8px 28px rgba(255,102,0,.28);
    transition: filter .15s ease, transform .15s ease;
}}

.cta-team:hover {{
    filter: brightness(1.06);
    transform: translateY(-1px);
    color: #FFFFFF !important;
}}

.earn-card {{
    background: linear-gradient(145deg, var(--surface-2), var(--surface));
    border: 1px solid rgba(255,102,0,.45);
    border-radius: 22px;
    padding: 1.35rem 1.2rem;
    text-align: center;
    margin: 0.6rem 0;
}}

.earn-label {{
    color: var(--text-muted);
    font-size: .78rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    font-weight: 800;
}}

.earn-value {{
    color: var(--orange);
    font-size: clamp(1.8rem, 6vw, 2.5rem);
    font-weight: 950;
    line-height: 1.1;
    margin: .4rem 0 .15rem;
}}

.earn-sub {{
    color: var(--text-secondary);
    font-size: .88rem;
    line-height: 1.4;
}}

@media (prefers-color-scheme: light) {{
    .stApp {{ background: var(--bg) !important; }}
    .stMarkdown, .stCaption, .stText {{ color: var(--text); }}
    [data-testid="stCaptionContainer"] {{ color: var(--text-muted) !important; }}
    hr {{ border-color: var(--border) !important; }}
    [data-testid="stMetric"] {{ color: var(--text) !important; }}
    [data-testid="stMetricValue"] {{ color: var(--text) !important; }}
    [data-testid="stMetricLabel"] {{ color: var(--text-muted) !important; }}
    input, textarea {{
        color: var(--text) !important;
        -webkit-text-fill-color: var(--text) !important;
    }}
    [data-baseweb="select"] {{ color: var(--text) !important; }}
    [data-baseweb="popover"] {{ background: var(--surface) !important; }}
    [data-testid="stDataFrame"] {{
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
    }}
}}

@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800;900&display=swap");
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# HELPERS
# ============================================================

def brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def pct(v):
    return f"{v * 100:.1f}%".replace(".", ",")

def clean_phone(phone):
    return re.sub(r"\D", "", phone or "")

def validate_phone(phone):
    p = clean_phone(phone)
    return 10 <= len(p) <= 13

def get_secret(name, default=None):
    try:
        value = st.secrets.get(name, None)
        if value is not None:
            return value
    except Exception:
        pass
    return os.getenv(name, default)

def get_smtp_config():
    try:
        cfg = st.secrets.get("smtp", {})
        if cfg:
            return {
                "host": cfg.get("host", "smtp.gmail.com"),
                "port": int(cfg.get("port", 465)),
                "username": cfg.get("username", ""),
                "password": str(cfg.get("password", "")).replace(" ", ""),
                "from_email": cfg.get("from_email", cfg.get("username", "")),
                "from_name": cfg.get("from_name", "Raio-X do Consultor"),
            }
    except Exception:
        pass
    return {
        "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "465")),
        "username": os.getenv("SMTP_USERNAME", ""),
        "password": os.getenv("SMTP_PASSWORD", "").replace(" ", ""),
        "from_email": os.getenv("SMTP_FROM_EMAIL", os.getenv("SMTP_USERNAME", "")),
        "from_name": os.getenv("SMTP_FROM_NAME", "Raio-X do Consultor"),
    }

def get_admin_emails():
    raw = get_secret("ADMIN_EMAILS", None)
    if raw is None:
        raw = get_smtp_config().get("username", "")
    if isinstance(raw, str):
        raw = [x.strip() for x in raw.split(",") if x.strip()]
    return {str(x).strip().lower() for x in (raw or []) if str(x).strip()}

def send_admin_otp(email, code):
    smtp = get_smtp_config()
    if not smtp["username"] or not smtp["password"] or not smtp["from_email"]:
        return False, "Configuração SMTP incompleta."

    msg = EmailMessage()
    msg["Subject"] = "Seu código de acesso — Raio-X do Consultor"
    msg["From"] = f'{smtp["from_name"]} <{smtp["from_email"]}>'
    msg["To"] = email
    msg.set_content(
        f"Seu código de acesso à Área Administrativa do Raio-X do Consultor é: {code}\n\n"
        "Este código expira em 10 minutos. Se você não solicitou o acesso, ignore este e-mail."
    )

    attempts = []
    ports = [smtp["port"]]
    if smtp["port"] == 465:
        ports.append(587)
    elif smtp["port"] == 587:
        ports.append(465)

    for port in ports:
        try:
            if port == 465:
                with smtplib.SMTP_SSL(smtp["host"], port, timeout=20) as server:
                    server.login(smtp["username"], smtp["password"])
                    server.send_message(msg)
            else:
                with smtplib.SMTP(smtp["host"], port, timeout=20) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(smtp["username"], smtp["password"])
                    server.send_message(msg)
            return True, "Código enviado."
        except Exception as exc:
            attempts.append(f"porta {port}: {type(exc).__name__}")

    return False, "Não foi possível enviar o código. Verifique o SMTP/Gmail. " + " | ".join(attempts)

def request_admin_otp(email):
    allowed = get_admin_emails()
    email = email.strip().lower()
    if email not in allowed:
        return False, "Se o e-mail estiver autorizado, o código será enviado."

    code = f"{py_secrets.randbelow(1_000_000):06d}"
    otp_secret = str(get_secret("OTP_SECRET", ""))
    if not otp_secret:
        return False, "OTP_SECRET não configurado."

    digest = hmac.new(
        otp_secret.encode("utf-8"),
        f"{email}:{code}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    st.session_state.admin_otp_hash = digest
    st.session_state.admin_otp_expires = datetime.now(timezone.utc) + timedelta(minutes=10)
    st.session_state.admin_otp_email = email
    st.session_state.admin_otp_attempts = 0

    ok, msg = send_admin_otp(email, code)
    st.session_state.admin_otp_send_ok = ok
    st.session_state.admin_otp_send_message = msg
    if not ok:
        return False, msg
    return True, msg

def verify_admin_otp(code):
    expected = st.session_state.get("admin_otp_hash")
    expires = st.session_state.get("admin_otp_expires")
    email = st.session_state.get("admin_otp_email", "")
    if not expected or not expires or not email:
        return False
    if datetime.now(timezone.utc) > expires:
        return False
    st.session_state.admin_otp_attempts = st.session_state.get("admin_otp_attempts", 0) + 1
    if st.session_state.admin_otp_attempts > 5:
        return False
    otp_secret = str(get_secret("OTP_SECRET", ""))
    if not otp_secret:
        return False
    digest = hmac.new(
        otp_secret.encode("utf-8"),
        f"{email}:{str(code).strip()}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(digest, expected)

def classify_profile(data, result):
    sales = data["sales"]
    quote_sale = result["rates"]["Cotação → venda"]
    contact_sale = result["contact_to_sale"]

    score = 0
    score += 3 if sales >= 20 else 2 if sales >= 10 else 1 if sales >= 5 else 0
    score += 3 if quote_sale >= .25 else 2 if quote_sale >= .20 else 1 if quote_sale >= .15 else 0
    score += 3 if contact_sale >= .10 else 2 if contact_sale >= .075 else 1 if contact_sale >= .05 else 0

    if score >= 7:
        return {"name": "Consultor Avançado", "level": 4, "description": "Você combina volume de vendas com boa eficiência comercial. Seu próximo salto tende a vir de escala, previsibilidade e refinamento do processo."}
    if score >= 5:
        return {"name": "Consultor Consistente", "level": 3, "description": "Seu processo já apresenta sinais de consistência. Existe uma base comercial sobre a qual dá para construir mais previsibilidade."}
    if score >= 3:
        return {"name": "Consultor em Desenvolvimento", "level": 2, "description": "Você já tem operação comercial acontecendo. O próximo passo é transformar esforço em um processo mais previsível."}
    return {"name": "Consultor em Formação", "level": 1, "description": "Você está construindo sua operação comercial. Mais volume, rotina e acompanhamento das conversões podem acelerar sua evolução."}

def admin_rows():
    sb = get_supabase()
    if sb is None:
        return None, "Supabase não configurado."
    try:
        response = sb.table("raio_x_leads").select("*").order("created_at", desc=True).execute()
        return response.data or [], None
    except Exception as exc:
        return None, f"Não foi possível carregar os leads agora: {exc}"

def render_admin():
    st.markdown('<div class="admin-shell">', unsafe_allow_html=True)
    st.markdown("## 🔐 Área Administrativa")
    st.caption("Acesso restrito por código enviado ao e-mail autorizado.")

    if not st.session_state.get("admin_authenticated"):
        if not st.session_state.get("admin_otp_hash"):
            email = st.text_input("E-mail cadastrado", placeholder="seu@email.com")
            if st.button("Enviar código", type="primary", use_container_width=True):
                if not email.strip() or "@" not in email:
                    st.error("Informe um e-mail válido.")
                else:
                    ok, msg = request_admin_otp(email)
                    if ok:
                        st.success("Código enviado. Confira seu e-mail.")
                        st.rerun()
                    else:
                        st.info(msg)
                        if st.session_state.get("admin_otp_hash"):
                            st.rerun()
        else:
            if st.session_state.get("admin_otp_send_ok", False):
                st.success(f"Código enviado para {st.session_state.get('admin_otp_email', '')}.")
            else:
                st.warning(st.session_state.get("admin_otp_send_message", "O código foi gerado, mas o envio por e-mail falhou."))
                st.caption("O campo abaixo continua disponível para que você possa reenviar o código.")
            st.caption("O código expira em 10 minutos e pode ser tentado até 5 vezes.")
            code = st.text_input("Digite o código de 6 dígitos", max_chars=6, placeholder="000000", key="admin_code")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Entrar", type="primary", use_container_width=True):
                    if verify_admin_otp(code):
                        st.session_state.admin_authenticated = True
                        st.session_state.pop("admin_otp_hash", None)
                        st.session_state.pop("admin_otp_expires", None)
                        st.session_state.pop("admin_otp_attempts", None)
                        st.session_state.pop("admin_otp_send_ok", None)
                        st.session_state.pop("admin_otp_send_message", None)
                        st.rerun()
                    else:
                        st.error("Código inválido ou expirado.")
            with c2:
                if st.button("Reenviar código", use_container_width=True):
                    email = st.session_state.get("admin_otp_email", "")
                    ok, msg = request_admin_otp(email)
                    st.info(msg if not ok else "Novo código enviado.")
                    st.rerun()
    else:
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown("### Leads captados")
        with c2:
            if st.button("Sair", use_container_width=True):
                st.session_state.admin_authenticated = False
                st.rerun()

        rows, error = admin_rows()
        if error:
            st.error(error)
        else:
            st.caption(f"{len(rows)} diagnóstico(s) registrado(s)")
            import pandas as pd
            df = pd.DataFrame(rows)
            wanted = [
                "created_at", "name", "whatsapp", "city", "experience", "works_protection",
                "biggest_pain", "profile_name", "contacts_month", "conversations_month",
                "quotes_month", "sales_month", "gain_per_sale", "discount_label",
                "lead_source", "rate_quote_sale", "rate_contact_sale", "contacts_per_sale",
                "bottleneck", "target_sales",
            ]
            cols = [c for c in wanted if c in df.columns]
            if cols:
                st.dataframe(df[cols], use_container_width=True, hide_index=True)
            else:
                st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)

def get_supabase():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key or create_client is None:
        return None
    return create_client(url, key)

def save_lead(data):
    sb = get_supabase()
    if sb is None:
        return False, "Supabase não configurado."
    try:
        sb.table("raio_x_leads").insert(data).execute()
        return True, "Lead salvo."
    except Exception as exc:
        return False, f"Não foi possível salvar agora: {exc}"

def source_factor(source):
    factors = {
        "Ações de Rua": 1.15,
        "Parceiros": 1.30,
        "Indicações de Associados": 1.20,
        "Tráfego Pago": 1.30,
        "Outros": 1.00,
    }
    return factors.get(source, 1.00)

def source_message(source, factor):
    if factor > 1:
        return (
            f"Para esta simulação, a ferramenta considera uma conversão "
            f"cotação → venda {pct(factor - 1)} maior do que a sua atual "
            f"quando a oportunidade vem de {source.lower()}."
        )
    return (
        "Para esta simulação, mantivemos sua conversão atual de cotação → venda "
        "como referência."
    )

def discount_label(value):
    labels = {
        0.0: "Quase nunca (0%)",
        0.10: "Às vezes (até 10%)",
        0.30: "Com frequência (até 30%)",
        0.50: "Frequentemente (30% a 50%)",
        0.70: "Muito frequentemente (50% a 70%)",
        1.00: "Frequentemente preciso zerar a adesão",
    }
    return labels.get(float(value), "")

def discount_insights(discount):
    if discount > 0.30:
        return {
            "title": "Seu desconto pode estar comendo sua comissão.",
            "text": (
                "Quando o desconto vira uma ferramenta recorrente para fechar, "
                "o consultor pode acabar reduzindo a própria margem antes de descobrir "
                "qual é a objeção real do cliente. O objetivo não é nunca conceder desconto, "
                "mas fazer o cliente perceber valor antes de mexer no preço."
            ),
            "actions": [
                ("Use SPIN Selling", "Antes de negociar preço, aprofunde a situação, o problema, as consequências e o que o cliente precisa resolver. A conversa deixa de ser só 'quanto custa?'."),
                ("Defenda o valor antes do preço", "Explique cobertura, assistência, experiência de atendimento e o que o cliente realmente recebe. Compare valor entregue, não apenas mensalidade."),
                ("Troque texto por conversa", "Quando a negociação trava no WhatsApp, tente ligação ou atendimento presencial. Comunicação síncrona permite entender objeções e responder na hora."),
                ("Tenha uma regra de desconto", "Defina previamente até onde você pode negociar e em quais situações. Isso evita conceder desconto por impulso só para não perder a venda."),
            ],
        }
    return None

def volume_bonus(sales):
    if sales >= 20:
        return 1200.0
    if sales >= 15:
        return 900.0
    if sales >= 10:
        return 600.0
    return 0.0

def simulate_team_earnings(monthly_sales, months=12):
    commission_per_sale = 450.0
    residual_per_client = 50.0
    portfolio_bonus_per_client = 10.0
    portfolio_threshold = 100

    sales = max(0, int(monthly_sales))
    monthly_incomes = []
    clients = 0

    for m in range(1, months + 1):
        clients += sales
        commission = sales * commission_per_sale
        residual = clients * residual_per_client
        portfolio_extra = clients * portfolio_bonus_per_client if clients >= portfolio_threshold else 0.0
        bonus = volume_bonus(sales)
        total = commission + residual + portfolio_extra + bonus
        monthly_incomes.append(total)

    avg_3 = sum(monthly_incomes[:3]) / 3 if months >= 3 else (sum(monthly_incomes) / len(monthly_incomes) if monthly_incomes else 0)
    month_12 = monthly_incomes[11] if len(monthly_incomes) >= 12 else (monthly_incomes[-1] if monthly_incomes else 0)

    return {
        "monthly": monthly_incomes,
        "avg_3_months": avg_3,
        "month_12": month_12,
        "clients_at_12": clients,
    }

def calculate(data):
    contacts = data["contacts"]
    conversations = data["conversations"]
    quotes = data["quotes"]
    sales = data["sales"]
    gain = data["gain"]
    target = data["target"]
    source = data.get("lead_source")
    discount = float(data.get("discount", 0) or 0)

    r1 = conversations / contacts if contacts else 0
    r2 = quotes / conversations if conversations else 0
    r3 = sales / quotes if quotes else 0

    contact_to_sale = sales / contacts if contacts else 0
    contacts_per_sale = contacts / sales if sales else None
    conversations_per_sale = conversations / sales if sales else None

    rates = {
        "Contato → conversa": r1,
        "Conversa → cotação": r2,
        "Cotação → venda": r3,
        "Contato → venda": contact_to_sale,
    }

    funnel_stages = ("Contato → conversa", "Conversa → cotação", "Cotação → venda")
    stage_rates = {s: rates[s] for s in funnel_stages}

    low_volume = contacts < 60 or quotes < 50

    factor = source_factor(source) if source else 1.0
    source_quote_sale_rate = min(1.0, r3 * factor)

    current_revenue = sales * gain
    target_revenue = target * gain
    extra_sales = max(0, target - sales)
    extra_revenue = max(0, target_revenue - current_revenue)

    current_rates = rates.copy()
    candidates = []

    if contacts and r2 > 0 and r3 > 0:
        candidates.append(("Contato → conversa", target / (contacts * r2 * r3)))
    if contacts and r1 > 0 and r3 > 0:
        candidates.append(("Conversa → cotação", target / (contacts * r1 * r3)))
    if contacts and r1 > 0 and r2 > 0:
        candidates.append(("Cotação → venda", target / (contacts * r1 * r2)))

    viable = [(stage, req) for stage, req in candidates if req <= 1]

    if low_volume:
        focus_stage = "Volume de oportunidades"
        needed_rate = None
        current_rate = None
        achievable = False
    elif "Cotação → venda" in dict(viable) and r3 == min(stage_rates.values()):
        focus_stage = "Cotação → venda"
        needed_rate = dict(viable)["Cotação → venda"]
        current_rate = r3
        achievable = needed_rate <= 1
    elif viable:
        focus_stage, needed_rate = min(
            viable,
            key=lambda x: max(0, x[1] - current_rates[x[0]])
        )
        current_rate = current_rates[focus_stage]
        achievable = needed_rate <= 1
    else:
        focus_stage = min(stage_rates, key=stage_rates.get)
        needed_rate = next(
            (req for stage, req in candidates if stage == focus_stage),
            1.0,
        )
        current_rate = current_rates[focus_stage]
        achievable = needed_rate <= 1

    if low_volume and contacts > 0 and r1 > 0 and r2 > 0:
        required_quotes = target / source_quote_sale_rate if source_quote_sale_rate > 0 else None
        required_contacts = (
            required_quotes / (r2 * r1)
            if required_quotes is not None and r1 * r2 > 0
            else None
        )
        additional_contacts = (
            max(0, required_contacts - contacts)
            if required_contacts is not None
            else None
        )
    else:
        required_quotes = None
        required_contacts = None
        additional_contacts = None

    return {
        "rates": rates,
        "bottleneck": min(stage_rates, key=stage_rates.get),
        "low_volume": low_volume,
        "current_revenue": current_revenue,
        "target_revenue": target_revenue,
        "focus_stage": focus_stage,
        "current_rate": current_rate,
        "needed_rate": needed_rate,
        "improvement_pp": max(0, (needed_rate - current_rate) * 100) if needed_rate is not None and current_rate is not None else 0,
        "achievable": achievable,
        "target": target,
        "extra_sales": extra_sales,
        "extra_revenue": extra_revenue,
        "source_factor": factor,
        "source_quote_sale_rate": source_quote_sale_rate,
        "required_quotes": required_quotes,
        "required_contacts": required_contacts,
        "additional_contacts": additional_contacts,
        "contact_to_sale": contact_to_sale,
        "contacts_per_sale": contacts_per_sale,
        "conversations_per_sale": conversations_per_sale,
        "discount": discount,
        "discount_label": discount_label(discount),
        "discount_insights": discount_insights(discount),
    }

def insights_for(stage, result, data):
    if stage == "Volume de oportunidades":
        return {
            "title": "Seu gargalo agora é volume, não falta de técnica.",
            "text": (
                "Com menos de 60 contatos por mês ou menos de 50 cotações, "
                "você tem poucas oportunidades para o funil trabalhar. "
                "Antes de tentar espremer mais conversão, vale aumentar a entrada."
            ),
            "actions": [
                ("Crie uma meta de entrada", "Acompanhe semanalmente quantos novos contatos entraram. Sem volume, fica difícil sustentar uma meta maior de vendas."),
                ("Escolha uma fonte principal", "Concentre esforço em uma origem por vez para descobrir qual delas traz contatos que realmente chegam à cotação."),
                ("Meça origem até venda", "Não compare canais apenas pelo número de contatos. O que importa é quantas cotações e vendas cada fonte gera."),
            ],
        }

    insights = {
        "Contato → conversa": {
            "title": "Você está perdendo oportunidades logo na entrada.",
            "text": "Seu funil recebe contatos, mas uma parcela relevante não chega a uma conversa. Antes de buscar ainda mais leads, vale melhorar o aproveitamento dos que já chegam.",
            "actions": [
                ("Responda rápido", "Defina um tempo máximo para o primeiro contato. Quanto mais tempo o lead espera, maior a chance de esfriar."),
                ("Teste uma abertura curta", "Evite começar falando de preço. Primeiro descubra o veículo, o uso e o motivo que levou a pessoa a pedir a cotação."),
                ("Crie uma cadência", "Um contato que não respondeu na primeira tentativa ainda não é necessariamente perdido. Teste 3 a 5 tentativas bem distribuídas."),
            ],
        },
        "Conversa → cotação": {
            "title": "Você conversa, mas deixa oportunidades sem proposta.",
            "text": "O vazamento aparece entre o interesse inicial e a apresentação da cotação. O foco deve ser transformar conversa em próximo passo concreto.",
            "actions": [
                ("Qualifique antes de cotar", "Descubra necessidade, veículo, uso e principal preocupação antes de apresentar a solução."),
                ("Conduza a conversa", "Não termine com 'qualquer coisa me chama'. Combine o envio da proposta e o próximo contato."),
                ("Registre perdas", "Anote por que a pessoa não avançou. Depois de algumas semanas, os padrões começam a aparecer."),
            ],
        },
        "Cotação → venda": {
            "title": "Seu maior vazamento está depois da cotação.",
            "text": "Você já conseguiu chegar à proposta. Agora o ganho está em transformar mais dessas oportunidades em decisões.",
            "actions": [
                ("Faça follow-up com propósito", "Não mande apenas 'e aí, conseguiu ver?'. Retome o benefício, tire uma dúvida ou descubra o que falta para decidir."),
                ("Mapeie a objeção", "Quando o cliente diz que vai pensar, descubra se a questão é preço, confiança, cobertura, comparação ou momento."),
                ("Tenha uma cadência", "Defina quando você vai falar novamente. Uma proposta sem próximo passo combinado tende a esfriar."),
            ],
        },
    }
    return insights.get(stage, insights["Cotação → venda"])

def render_logo():
    if os.path.exists("logo.png"):
        st.markdown('<div class="brand">', unsafe_allow_html=True)
        st.image("logo.png", width=180)
        st.markdown(
            '<div class="eyebrow">RAIO-X COMERCIAL</div>'
            '<div class="hero-title">Onde você está perdendo vendas?</div>'
            '<div class="hero-sub">Responda algumas perguntas e descubra onde suas vendas estão escapando — e o que você pode fazer para vender mais.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="brand"><div class="eyebrow">RAIO-X COMERCIAL</div>'
            '<div class="hero-title">Onde você está perdendo vendas?</div>'
            '<div class="hero-sub">Responda algumas perguntas e descubra onde suas vendas estão escapando — e o que você pode fazer para vender mais.</div></div>',
            unsafe_allow_html=True,
        )

def is_admin_route():
    try:
        return st.query_params.get("admin") == "1"
    except Exception:
        return False

if is_admin_route():
    render_admin()
    st.stop()

# ============================================================
# STATE
# ============================================================

for key, default in [
    ("step", 0),
    ("answers", {}),
    ("result", None),
    ("submitted", False),
    ("show_result", False),
    ("celebrate", False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown('<div class="admin-float"><a href="?admin=1" title="Área administrativa">⚙</a></div>', unsafe_allow_html=True)

render_logo()

# ============================================================
# DYNAMIC QUESTIONS
# ============================================================

def build_questions():
    questions = [
        ("contacts", "Quantas Pessoas você aborda, ou te chamam, por mês?", "Pense em WhatsApp, Instagram, Indicações Recebidas, tráfego Pago, Parcerias e Prospecção.", 0, 10, 1, "number"),
        ("conversations", "Desses contatos, com quantos você realmente conversa?", "Considere apenas quem respondeu ou teve uma conversa real com você.", 0, 10, 0, "number"),
        ("quotes", "Para quantos você chega a apresentar uma cotação ou proposta?", "Aqui vale a proposta efetivamente apresentada ao cliente.", 0, 5, 0, "number"),
    ]

    a = st.session_state.answers
    if a.get("contacts", 0) < 60 or a.get("quotes", 0) < 50:
        questions.append((
            "lead_source",
            "De onde vêm principalmente esses contatos?",
            "Como seu volume de oportunidades está baixo, queremos entender qual fonte você usa para gerar novos contatos.",
            "", None, None, "source",
        ))

    questions.append(("sales", "Quantas vendas você fecha por mês?", "Use sua média dos últimos meses para evitar que um mês fora da curva distorça o resultado.", 0, 1, 0, "number"))
    questions.append(("gain", "Quanto você ganha, em média, por venda?", "Pode ser sua comissão média ou o valor que efetivamente fica para você por venda.", 0.0, 10.0, 0.0, "money"))

    if a.get("gain", 250) < 250:
        questions.append((
            "discount",
            "Quando precisa fechar, quanto de desconto você costuma conceder?",
            "Pense na média do que você realmente abre mão para conseguir a adesão.",
            "", None, None, "discount",
        ))

    questions.append(("target", "Quantas vendas você gostaria de fazer por mês?", "Agora vamos descobrir o que precisaria mudar no seu processo para chegar lá.", 0, 1, 0, "number"))
    return questions

if not st.session_state.submitted:
    questions = build_questions()
    step = st.session_state.step

    if step >= len(questions):
        step = len(questions) - 1
        st.session_state.step = step

    key, question, helper, default, step_size, minimum, kind = questions[step]
    total = len(questions)
    progress = ((step + 1) / total) * 100

    st.markdown(
        f"""
        <div class="question-card">
            <div class="step">Pergunta {step + 1} de {total}</div>
            <div class="progress-wrap"><div class="progress-bar" style="width:{progress}%"></div></div>
            <div class="question">{question}</div>
            <div class="helper">{helper}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if kind == "money":
        value = st.number_input(
            "Sua resposta",
            min_value=float(minimum),
            step=float(step_size),
            value=None,
            key=f"q_{key}",
            format="%.2f",
            placeholder="Digite um valor",
        )
    elif kind == "source":
        options = [
            "Selecione uma opção",
            "Ações de Rua",
            "Parceiros",
            "Indicações de Associados",
            "Tráfego Pago",
            "Outros",
        ]
        value = st.selectbox(
            "Principal fonte de contatos",
            options,
            index=0,
            key="q_lead_source",
        )
        if value == "Selecione uma opção":
            value = None
    elif kind == "discount":
        discount_options = [
            ("Selecione uma opção", None),
            ("Quase nunca (0%)", 0.0),
            ("Às vezes (até 10%)", 0.10),
            ("Com frequência (até 30%)", 0.30),
            ("Frequentemente (30% a 50%)", 0.50),
            ("Muito frequentemente (50% a 70%)", 0.70),
            ("Frequentemente preciso zerar a adesão", 1.00),
        ]
        selected = st.selectbox(
            "Sua resposta",
            [label for label, _ in discount_options],
            index=0,
            key="q_discount",
        )
        value = dict(discount_options)[selected]
    else:
        value = st.number_input(
            "Sua resposta",
            min_value=int(minimum),
            step=int(step_size),
            value=None,
            key=f"q_{key}",
            placeholder="Digite um número",
        )

    c1, c2 = st.columns(2)
    with c1:
        if step > 0 and st.button("← Voltar", use_container_width=True):
            st.session_state.step -= 1
            for widget_key in [k for k in list(st.session_state.keys()) if k.startswith("q_")]:
                st.session_state.pop(widget_key, None)
            st.rerun()

    with c2:
        label = "Ver meu diagnóstico →" if step == total - 1 else "Próxima pergunta →"
        if st.button(label, type="primary", use_container_width=True):
            error = None
            if value is None:
                error = "Responda esta pergunta para continuar."
            else:
                st.session_state.answers[key] = value

            a = st.session_state.answers

            if not error and key == "conversations" and a["conversations"] > a["contacts"]:
                error = "O número de conversas não pode ser maior que o número de contatos."
            elif not error and key == "quotes" and a["quotes"] > a["conversations"]:
                error = "O número de cotações não pode ser maior que o número de conversas."
            elif not error and key == "sales" and a["sales"] > a["quotes"]:
                error = "O número de vendas não pode ser maior que o número de cotações."
            elif not error and key == "target" and a["target"] < a["sales"]:
                error = "Sua meta precisa ser igual ou maior que suas vendas atuais."

            if error:
                st.error(error)
            elif step < total - 1:
                st.session_state.step += 1
                for widget_key in [k for k in list(st.session_state.keys()) if k.startswith("q_")]:
                    st.session_state.pop(widget_key, None)
                st.rerun()
            else:
                st.session_state.submitted = True
                st.rerun()

    st.markdown(
        '<div class="mini-note">Leva menos de 2 minutos • Seus dados são usados para gerar seu diagnóstico.</div>',
        unsafe_allow_html=True,
    )

else:
    # ========================================================
    # LEAD CAPTURE
    # ========================================================
    a = st.session_state.answers
    data = {
        "contacts": int(a["contacts"]),
        "conversations": int(a["conversations"]),
        "quotes": int(a["quotes"]),
        "sales": int(a["sales"]),
        "gain": float(a["gain"]),
        "target": int(a["target"]),
        "lead_source": a.get("lead_source"),
        "discount": float(a.get("discount", 0) or 0),
    }
    result = calculate(data)
    profile = classify_profile(data, result)
    result["profile"] = profile
    st.session_state.result = result

    if not st.session_state.show_result:
        st.markdown(
            """
            <div class="question-card">
                <div class="step">Último passo</div>
                <div class="question">Seu Raio-X está pronto. Onde enviamos?</div>
                <div class="helper">Deixe seu WhatsApp para liberar o diagnóstico completo e as recomendações personalizadas.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        name = st.text_input("Seu nome", placeholder="Como podemos te chamar?")
        whatsapp = st.text_input("WhatsApp *", placeholder="(19) 99999-9999")
        city = st.text_input("Cidade", placeholder="Ex.: Campinas - SP")
        experience = st.selectbox(
            "Experiência com vendas",
            ["Menos de 1 ano", "1 a 3 anos", "3 a 5 anos", "Mais de 5 anos"],
        )
        works_protection = st.selectbox(
            "Você já trabalha com proteção veicular?",
            ["Sim", "Não"],
        )

        pain_options = [
            "Selecione uma opção",
            "Suporte aos Associados",
            "Falta de Benefícios ao Associado",
            "Pouco Suporte da Liderança",
            "Ganhos Insuficientes",
            "Promessas não Cumpridas da Associação",
        ]
        biggest_pain = st.selectbox(
            "Qual sua maior dor atualmente? *",
            pain_options,
            index=0,
            key="q_biggest_pain",
        )

        if st.button("🔓 LIBERAR MEU RAIO-X", type="primary", use_container_width=True):
            errors = []
            if not name.strip():
                errors.append("Informe seu nome.")
            if not validate_phone(whatsapp):
                errors.append("Informe um WhatsApp válido.")
            if biggest_pain == "Selecione uma opção":
                errors.append("Selecione sua maior dor atual.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                lead = {
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "name": name.strip(),
                    "whatsapp": clean_phone(whatsapp),
                    "city": city.strip(),
                    "experience": experience,
                    "works_protection": works_protection,
                    "biggest_pain": biggest_pain,
                    "contacts_month": data["contacts"],
                    "conversations_month": data["conversations"],
                    "quotes_month": data["quotes"],
                    "sales_month": data["sales"],
                    "gain_per_sale": data["gain"],
                    "discount_pct": data["discount"],
                    "discount_label": result["discount_label"],
                    "target_sales": data["target"],
                    "lead_source": data.get("lead_source"),
                    "source_conversion_factor": result["source_factor"],
                    "source_quote_sale_rate": result["source_quote_sale_rate"],
                    "required_contacts": result["required_contacts"],
                    "additional_contacts": result["additional_contacts"],
                    "rate_contact_conversation": result["rates"]["Contato → conversa"],
                    "rate_conversation_quote": result["rates"]["Conversa → cotação"],
                    "rate_quote_sale": result["rates"]["Cotação → venda"],
                    "bottleneck": result["bottleneck"],
                    "focus_stage": result["focus_stage"],
                    "needed_rate": result["needed_rate"],
                    "current_revenue": result["current_revenue"],
                    "target_revenue": result["target_revenue"],
                    "extra_revenue": result["extra_revenue"],
                    "profile_name": profile["name"],
                    "profile_level": profile["level"],
                    "rate_contact_sale": result["contact_to_sale"],
                    "contacts_per_sale": result["contacts_per_sale"],
                    "source": "raio_x_comercial",
                }

                ok, msg = save_lead(lead)
                st.session_state.lead_error = None if ok else msg
                st.session_state.lead_saved = ok
                st.session_state.lead_name = name.strip()
                st.session_state.lead_phone = clean_phone(whatsapp)
                st.session_state.show_result = True
                st.session_state.celebrate = True
                st.rerun()

        st.markdown(
            '<div class="privacy">Seu WhatsApp é necessário para liberar o diagnóstico. Não coloque senhas ou dados sensíveis.</div>',
            unsafe_allow_html=True,
        )

    if st.session_state.get("show_result"):
        if st.session_state.get("lead_error"):
            st.warning(st.session_state.lead_error)

        if st.session_state.get("celebrate"):
            st.balloons()
            st.markdown(
                """
                <div class="celebration">
                    <div class="celebration-icon">🎉</div>
                    <div class="celebration-title">SEU RAIO-X ESTÁ LIBERADO!</div>
                    <div class="celebration-sub">
                        Analisamos seu funil. Agora vamos mostrar onde está o maior vazamento
                        e o que você pode testar para vender mais.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.session_state.celebrate = False

        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-kicker">SEU PERFIL COMERCIAL</div>
                <div class="profile-name">Você é um {profile["name"]}</div>
                <div class="profile-desc">{profile["description"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("## 🔎 Seu diagnóstico")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Vendas atuais", f"{data['sales']}")
        with c2:
            st.metric("Hoje você ganha", brl(result["current_revenue"]))
        with c3:
            st.metric("Sua meta", f"{data['target']} vendas")

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Cotação → venda", pct(result["rates"]["Cotação → venda"]))
        with m2:
            st.metric("Contato → venda", pct(result["contact_to_sale"]))
        with m3:
            cps = f"{result['contacts_per_sale']:.1f}" if result["contacts_per_sale"] is not None else "—"
            st.metric("Contatos por venda", cps)

        if result["contacts_per_sale"] is not None:
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="result-label">Sua meta de prospecção</div>
                    <div style="color:#BDBDBD;margin:.5rem 0;">
                        Hoje, a cada <strong>{result["contacts_per_sale"]:.1f} contatos</strong>,
                        você fecha aproximadamente <strong>1 venda</strong>.
                        Isso transforma sua conversão em uma meta prática de abordagem.
                    </div>
                    <div class="tip-text">
                        Use esse número como referência para criar sua meta diária ou semanal de contatos.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if result["low_volume"]:
            st.markdown(
                f"""
                <div class="danger-card">
                    <div class="result-label">Principal ponto de atenção</div>
                    <div class="result-value orange">Volume de oportunidades</div>
                    <div style="color:#B8B8B8;margin-top:.45rem;">
                        Você está com <strong>{data["contacts"]} contatos</strong> e
                        <strong>{data["quotes"]} cotações</strong> por mês.
                        Antes de tentar extrair mais vendas do funil, o primeiro movimento
                        é aumentar a entrada de oportunidades.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if data.get("lead_source"):
                factor = result["source_factor"]
                st.markdown(
                    f"""
                    <div class="result-card">
                        <div class="result-label">Fonte principal informada</div>
                        <div class="result-value" style="font-size:1.45rem;">
                            {data["lead_source"]}
                        </div>
                        <div class="source-badge">
                            Cenário de conversão: {pct(factor - 1) if factor > 1 else "sem ajuste"}
                        </div>
                        <div class="tip-text" style="margin-top:.65rem;">
                            {source_message(data["lead_source"], factor)}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            if result["required_contacts"] is not None:
                st.markdown(
                    f"""
                    <div class="potential">
                        <div class="result-label">Para buscar {data["target"]} vendas/mês</div>
                        <div style="color:#BDBDBD;margin:.55rem 0;">
                            Mantendo suas conversões de contato → conversa e conversa → cotação,
                            e usando o cenário da fonte <strong>{data.get("lead_source", "selecionada")}</strong>:
                        </div>
                        <div class="potential-number">
                            {result["required_contacts"]:.0f} contatos/mês
                        </div>
                        <div style="color:#BDBDBD;">
                            Isso representa aproximadamente
                            <strong>+{result["additional_contacts"]:.0f} contatos/mês</strong>
                            em relação ao seu volume atual.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            info = insights_for("Volume de oportunidades", result, data)

        else:
            st.markdown(
                f"""
                <div class="danger-card">
                    <div class="result-label">Principal vazamento</div>
                    <div class="result-value orange">{result["bottleneck"]}</div>
                    <div style="color:#B8B8B8;margin-top:.35rem;">
                        É a etapa com menor conversão proporcional no seu funil atual.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            info = insights_for(result["bottleneck"], result, data)

        if data["gain"] < 250:
            st.markdown(
                f"""
                <div class="danger-card">
                    <div class="result-label">⚠️ Atenção à sua remuneração</div>
                    <div class="result-value orange">Você ganha {brl(data["gain"])} por venda</div>
                    <div style="color:#B8B8B8;margin-top:.45rem;">
                        Esse valor está abaixo de R$ 250 por venda. Isso pode indicar que sua estrutura atual de comissão está limitando bastante o seu potencial de ganho. Vale comparar o que outras operações de proteção veicular pagam pelo mesmo esforço comercial antes de considerar esse valor como seu teto.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if result["discount_insights"]:
            dinfo = result["discount_insights"]
            st.markdown(
                f"""
                <div class="danger-card">
                    <div class="result-label">💸 Desconto identificado</div>
                    <div class="result-value orange">{result["discount_label"]}</div>
                    <div style="color:#B8B8B8;margin-top:.45rem;">{dinfo["text"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown("### 🛠️ Como defender mais valor")
            for title, text in dinfo["actions"]:
                st.markdown(
                    f"""
                    <div class="tip-card">
                        <div class="tip-title">→ {title}</div>
                        <div class="tip-text">{text}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown('<div class="section-title">Seu funil hoje</div>', unsafe_allow_html=True)
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Contatos", f"{data['contacts']}")
        f2.metric("Conversas", f"{data['conversations']}", pct(result["rates"]["Contato → conversa"]))
        f3.metric("Cotações", f"{data['quotes']}", pct(result["rates"]["Conversa → cotação"]))
        f4.metric("Vendas", f"{data['sales']}", pct(result["rates"]["Cotação → venda"]))

        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">Conversão total do seu funil</div>
                <div class="result-value orange">{pct(result["contact_to_sale"])}</div>
                <div class="tip-text">
                    Essa é a sua conversão de <strong>contato → venda</strong>: de todas as pessoas que entram no seu funil, essa é a parcela que termina em venda.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-title">🎯 O que precisa mudar para sua meta?</div>', unsafe_allow_html=True)

        if result["low_volume"] and result["required_contacts"] is not None:
            st.markdown(
                f"""
                <div class="result-card">
                    <div class="result-label">Caminho matemático da simulação</div>
                    <div style="color:#BDBDBD;margin:.5rem 0;">
                        O primeiro ganho está em aumentar o volume de contatos.
                        Depois, acompanhe se as novas oportunidades mantêm a mesma qualidade.
                    </div>
                    <div class="tip-text">
                        A ferramenta não trata esse número como promessa de resultado:
                        ele é uma simulação baseada nas suas conversões atuais e no fator
                        de cenário da fonte escolhida.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif result["achievable"]:
            st.markdown(
                f"""
                <div class="potential">
                    <div class="result-label">Se as outras etapas ficarem iguais</div>
                    <div style="color:#BDBDBD;margin:.5rem 0;">
                        <strong>{result["focus_stage"]}</strong> precisaria sair de
                        <strong>{pct(result["current_rate"])}</strong> para
                        <strong>{pct(result["needed_rate"])}</strong>.
                    </div>
                    <div class="potential-number">+{brl(result["extra_revenue"])}/mês</div>
                    <div style="color:#BDBDBD;">
                        diferença entre suas vendas atuais e sua meta,
                        mantendo seu ganho médio por venda.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.warning(
                f"Com o volume atual, chegar a {data['target']} vendas não depende de uma única etapa. "
                "Você precisaria aumentar a entrada de oportunidades e/ou melhorar mais de uma conversão."
            )

        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">Leitura do seu resultado</div>
                <div class="question" style="font-size:1.28rem;margin-top:.3rem;">{info["title"]}</div>
                <div class="tip-text">{info["text"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 💡 3 ações para testar")
        for title, text in info["actions"]:
            st.markdown(
                f"""
                <div class="tip-card">
                    <div class="tip-title">→ {title}</div>
                    <div class="tip-text">{text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if os.path.exists("banner.png"):
            st.markdown('<div class="final-banner">', unsafe_allow_html=True)
            st.image("banner.png", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        wa_url = (
            "https://wa.me/5519989745446?text="
            "Ol%C3%A1%2C%20sou%20consultor(a)%20de%20prote%C3%A7%C3%A3o%20veicular%2C%20"
            "e%20realizei%20o%20diagn%C3%B3stico%20da%20minha%20opera%C3%A7%C3%A3o%20na%20"
            "ferramenta%20de%20Raio-X%20Comercial.%20Gostaria%20de%20saber%20como%20aumentar%20"
            "meus%20ganhos%20trabalhando%20com%20voc%C3%AAs!"
        )
        st.markdown(
            f'<a class="cta-team" href="{wa_url}" target="_blank" rel="noopener">Faça parte do meu time!</a>',
            unsafe_allow_html=True,
        )

        sim = simulate_team_earnings(data["sales"], months=12)

        st.markdown('<div class="section-title">📈 Seu potencial de ganho no meu time</div>', unsafe_allow_html=True)

        e1, e2 = st.columns(2)
        with e1:
            st.markdown(
                f"""
                <div class="earn-card">
                    <div class="earn-label">Ganho médio mensal<br>inicial</div>
                    <div class="earn-value">{brl(sim["avg_3_months"])}</div>
                    <div class="earn-sub">média dos 3 primeiros meses</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with e2:
            st.markdown(
                f"""
                <div class="earn-card">
                    <div class="earn-label">Ganho médio mensal<br>após 1 ano de operação</div>
                    <div class="earn-value">{brl(sim["month_12"])}</div>
                    <div class="earn-sub">Considerando seus clientes ativos</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        try:
            import pandas as pd
            import altair as alt

            chart_df = pd.DataFrame({
                "Mês": list(range(1, 13)),
                "Ganho (R$)": sim["monthly"],
            })

            chart = (
                alt.Chart(chart_df)
                .mark_area(
                    line={"color": "#FF6600", "strokeWidth": 3},
                    color=alt.Gradient(
                        gradient="linear",
                        stops=[
                            alt.GradientStop(color="rgba(255,102,0,0.45)", offset=0),
                            alt.GradientStop(color="rgba(255,102,0,0.02)", offset=1),
                        ],
                        x1=1, x2=1, y1=1, y2=0,
                    ),
                    interpolate="monotone",
                )
                .encode(
                    x=alt.X("Mês:O", title="Mês", axis=alt.Axis(labelAngle=0)),
                    y=alt.Y("Ganho (R$):Q", title=None, axis=alt.Axis(format=",.0f")),
                    tooltip=[
                        alt.Tooltip("Mês:O", title="Mês"),
                        alt.Tooltip("Ganho (R$):Q", title="Ganho", format=",.2f"),
                    ],
                )
                .properties(height=280)
                .configure_view(stroke=None)
                .configure_axis(
                    labelColor="#BDBDBD",
                    titleColor="#969696",
                    gridColor="#292929",
                    domainColor="#292929",
                )
            )
            st.altair_chart(chart, use_container_width=True)
        except Exception:
            st.line_chart(
                {f"Mês {i+1}": v for i, v in enumerate(sim["monthly"])},
                use_container_width=True,
            )

        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">Seu próximo teste</div>
                <div style="font-size:1.05rem;font-weight:800;color:white;margin-top:.3rem;">
                    Durante os próximos 7 dias, acompanhe especificamente
                    <span class="orange">{result["focus_stage"]}</span>.
                </div>
                <div class="tip-text" style="margin-top:.4rem;">
                    Registre quantas oportunidades entram nessa etapa, quantas avançam
                    e por que as demais não avançaram. Depois compare com seu funil atual.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.session_state.get("lead_saved"):
            st.caption("✓ Seu diagnóstico foi registrado.")
        else:
            st.caption("O diagnóstico foi calculado. O banco de leads ainda não está conectado.")

        if st.button("↺ Fazer outro diagnóstico", use_container_width=True):
            for k in [
                "step", "answers", "result", "submitted", "show_result",
                "lead_saved", "lead_name", "lead_phone", "celebrate",
            ]:
                st.session_state.pop(k, None)
            for widget_key in [k for k in list(st.session_state.keys()) if k.startswith("q_")]:
                st.session_state.pop(widget_key, None)
            st.rerun()
