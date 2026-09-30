
import re
import os
from datetime import datetime, timezone

import streamlit as st

try:
    from supabase import create_client
except Exception:
    create_client = None


# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="Raio-X Comercial",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

ORANGE = "#FF6600"
DARK = "#090909"
DARK_2 = "#151515"
TEXT = "#F5F5F5"
MUTED = "#A7A7A7"

# ============================================================
# STYLE
# ============================================================
st.markdown(
    f"""
    <style>
        #MainMenu, footer, header {{visibility:hidden;}}

        .stApp {{
            background: #080808;
            color: {TEXT};
        }}

        .block-container {{
            max-width: 760px;
            padding-top: 1.2rem;
            padding-bottom: 4rem;
        }}

        /* Hide Streamlit chrome around inputs */
        div[data-testid="stNumberInput"] label,
        div[data-testid="stTextInput"] label,
        div[data-testid="stSelectbox"] label {{
            color: #D8D8D8 !important;
            font-weight: 600 !important;
        }}

        .brand {{
            text-align:center;
            margin-bottom: 1.5rem;
        }}

        .brand img {{
            width: 92px;
            height: 92px;
            object-fit: cover;
            border-radius: 20px;
            box-shadow: 0 0 35px rgba(255,102,0,.18);
        }}

        .eyebrow {{
            color: {ORANGE};
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .14em;
            text-transform: uppercase;
            margin-top: .8rem;
        }}

        .hero-title {{
            font-size: clamp(2rem, 7vw, 3.15rem);
            line-height: 1.03;
            font-weight: 900;
            margin: .35rem 0 .6rem;
            color: white;
        }}

        .hero-sub {{
            color: #BDBDBD;
            font-size: 1.03rem;
            line-height: 1.55;
            max-width: 620px;
            margin: 0 auto;
        }}

        .question-card {{
            background: linear-gradient(145deg, #171717, #101010);
            border: 1px solid #292929;
            border-radius: 24px;
            padding: 1.35rem 1.25rem;
            margin-top: 1.25rem;
            box-shadow: 0 15px 45px rgba(0,0,0,.22);
        }}

        .step {{
            color: {ORANGE};
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .08em;
            text-transform: uppercase;
        }}

        .question {{
            font-size: 1.5rem;
            line-height: 1.2;
            font-weight: 850;
            color: white;
            margin: .35rem 0 .4rem;
        }}

        .helper {{
            color: #969696;
            font-size: .92rem;
            line-height: 1.45;
            margin-bottom: .8rem;
        }}

        .progress-wrap {{
            background: #242424;
            height: 6px;
            border-radius: 99px;
            overflow:hidden;
            margin: .8rem 0 1.1rem;
        }}

        .progress-bar {{
            height:100%;
            background: {ORANGE};
            border-radius:99px;
        }}

        .mini-note {{
            color:#8E8E8E;
            font-size:.82rem;
            text-align:center;
            margin-top:.55rem;
        }}

        .result-card {{
            background: linear-gradient(145deg, #171717, #0E0E0E);
            border: 1px solid #2A2A2A;
            border-radius: 22px;
            padding: 1.25rem;
            margin: .9rem 0;
        }}

        .result-label {{
            color:#8F8F8F;
            font-size:.78rem;
            text-transform:uppercase;
            letter-spacing:.08em;
            font-weight:800;
        }}

        .result-value {{
            color:white;
            font-size:2rem;
            font-weight:900;
            margin-top:.15rem;
        }}

        .orange {{
            color:{ORANGE};
        }}

        .danger-card {{
            background: rgba(255,102,0,.08);
            border: 1px solid rgba(255,102,0,.38);
            border-radius: 20px;
            padding: 1.15rem;
            margin: 1rem 0;
        }}

        .tip-card {{
            background:#111;
            border:1px solid #282828;
            border-radius:18px;
            padding:1rem 1.05rem;
            margin:.65rem 0;
        }}

        .tip-title {{
            color:white;
            font-weight:800;
            margin-bottom:.25rem;
        }}

        .tip-text {{
            color:#B8B8B8;
            line-height:1.48;
            font-size:.92rem;
        }}

        .potential {{
            border:1px solid rgba(255,102,0,.45);
            background:linear-gradient(145deg, rgba(255,102,0,.13), rgba(255,102,0,.04));
            border-radius:22px;
            padding:1.25rem;
            text-align:center;
            margin:1rem 0;
        }}

        .potential-number {{
            color:{ORANGE};
            font-size:2.35rem;
            line-height:1;
            font-weight:950;
            margin:.35rem 0;
        }}

        .disclaimer {{
            color:#777;
            font-size:.76rem;
            line-height:1.4;
            margin-top:1rem;
        }}

        div.stButton > button {{
            border-radius: 14px !important;
            min-height: 48px !important;
            font-weight: 850 !important;
            border: 1px solid #333 !important;
        }}

        div.stButton > button[kind="primary"] {{
            background:{ORANGE} !important;
            border-color:{ORANGE} !important;
            color:#fff !important;
        }}

        div[data-testid="stForm"] {{
            border:0 !important;
            padding:0 !important;
        }}

        .section-title {{
            font-size:1.15rem;
            font-weight:850;
            margin:1.3rem 0 .7rem;
        }}

        .privacy {{
            text-align:center;
            color:#6F6F6F;
            font-size:.76rem;
            margin-top:.7rem;
        }}
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

    current_rates = rates.copy()
    candidates = []

    if contacts and r2 > 0 and r3 > 0:
        candidates.append(("Contato → conversa", target / (contacts * r2 * r3)))
    if contacts and r1 > 0 and r3 > 0:
        candidates.append(("Conversa → cotação", target / (contacts * r1 * r3)))
    if contacts and r1 > 0 and r2 > 0:
        candidates.append(("Cotação → venda", target / (contacts * r1 * r2)))

    viable = [(stage, req) for stage, req in candidates if req <= 1]

    if bottleneck in dict(viable):
        focus_stage = bottleneck
        needed_rate = dict(viable)[bottleneck]
    elif viable:
        focus_stage, needed_rate = min(
            viable,
            key=lambda x: max(0, x[1] - current_rates[x[0]])
        )
    else:
        focus_stage = bottleneck
        needed_rate = next(
            (req for stage, req in candidates if stage == bottleneck),
            1.0,
        )

    current_rate = current_rates[focus_stage]
    achievable = needed_rate <= 1
    extra_sales = max(0, target - sales)
    extra_revenue = max(0, target_revenue - current_revenue)

    return {
        "rates": rates,
        "bottleneck": bottleneck,
        "current_revenue": current_revenue,
        "target_revenue": target_revenue,
        "focus_stage": focus_stage,
        "current_rate": current_rate,
        "needed_rate": needed_rate,
        "improvement_pp": max(0, (needed_rate - current_rate) * 100),
        "achievable": achievable,
        "target": target,
        "extra_sales": extra_sales,
        "extra_revenue": extra_revenue,
    }


def insights_for(stage, result, data):
    insights = {
        "Contato → conversa": {
            "title": "Você está perdendo oportunidades logo na entrada.",
            "text": "Seu funil recebe contatos, mas uma parcela relevante não chega a uma conversa. Antes de buscar mais leads, vale melhorar o aproveitamento dos que já chegam.",
            "actions": [
                ("Responda rápido", "Defina um tempo máximo para o primeiro contato. Quanto mais tempo o lead espera, mais fácil é ele esfriar."),
                ("Teste uma abertura curta", "Evite começar falando de preço. Primeiro descubra o veículo, o uso e o que levou a pessoa a pedir a cotação."),
                ("Tente mais de uma vez", "Um contato que não respondeu na primeira tentativa ainda não é necessariamente um lead perdido. Crie uma sequência simples de 3 a 5 tentativas."),
            ],
        },
        "Conversa → cotação": {
            "title": "Você conversa, mas está deixando oportunidades sem proposta.",
            "text": "O gargalo aparece entre o interesse inicial e a apresentação da cotação. Isso normalmente merece atenção na qualificação e na condução da conversa.",
            "actions": [
                ("Qualifique antes de cotar", "Descubra necessidade, veículo, uso e principal preocupação antes de apresentar a solução."),
                ("Conduza para o próximo passo", "Não termine a conversa com um 'qualquer coisa me chama'. Combine explicitamente o envio e o próximo contato."),
                ("Registre os motivos de perda", "Anote por que a pessoa não avançou. Depois de algumas semanas, você começa a enxergar padrões."),
            ],
        },
        "Cotação → venda": {
            "title": "Seu maior vazamento está depois da cotação.",
            "text": "Você já conseguiu chegar à proposta. Agora o ganho está em transformar mais dessas oportunidades em decisões.",
            "actions": [
                ("Faça follow-up com propósito", "Não mande apenas 'e aí, conseguiu ver?'. Retome o benefício, tire uma dúvida ou pergunte o que falta para decidir."),
                ("Mapeie a objeção", "Quando o cliente diz que vai pensar, descubra se a questão é preço, confiança, cobertura, comparação ou momento."),
                ("Tenha uma cadência", "Defina quando você vai falar novamente. Uma proposta sem próximo passo combinado tende a esfriar."),
            ],
        },
    }

    return insights[stage]


def render_logo():
    logo_path = "logo.png"
    if os.path.exists(logo_path):
        st.markdown('<div class="brand">', unsafe_allow_html=True)
        st.image(logo_path, width=92)
        st.markdown(
            '<div class="eyebrow">RAIO-X COMERCIAL</div>'
            '<div class="hero-title">Onde seu funil está vazando?</div>'
            '<div class="hero-sub">Responda algumas perguntas e descubra qual etapa do seu processo comercial mais precisa de atenção — e o que pode acontecer se você melhorar.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="brand"><div class="eyebrow">RAIO-X COMERCIAL</div>'
            '<div class="hero-title">Onde seu funil está vazando?</div>'
            '<div class="hero-sub">Responda algumas perguntas e descubra qual etapa do seu processo comercial mais precisa de atenção.</div></div>',
            unsafe_allow_html=True,
        )


# ============================================================
# STATE
# ============================================================
if "step" not in st.session_state:
    st.session_state.step = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "result" not in st.session_state:
    st.session_state.result = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False


render_logo()

# ============================================================
# QUESTIONS — ONE AT A TIME
# ============================================================
questions = [
    ("contacts", "Quantos novos contatos você recebe por mês?", "Pense em WhatsApp, Instagram, indicação, anúncio e prospecção.", 200, 10, 1, "number"),
    ("conversations", "Desses contatos, com quantos você realmente conversa?", "Considere apenas quem respondeu ou teve uma conversa real com você.", 140, 10, 0, "number"),
    ("quotes", "Para quantos você chega a apresentar uma cotação ou proposta?", "Aqui vale a proposta efetivamente apresentada ao cliente.", 100, 5, 0, "number"),
    ("sales", "Quantas vendas você fecha por mês?", "Use sua média dos últimos meses para evitar que um mês fora da curva distorça o resultado.", 20, 1, 0, "number"),
    ("gain", "Quanto você ganha, em média, por venda?", "Pode ser sua comissão média ou o valor que efetivamente fica para você por venda.", 250.0, 10.0, 0.0, "money"),
    ("target", "Quantas vendas você gostaria de fazer por mês?", "Agora vamos descobrir o que precisaria mudar no seu funil para chegar lá.", 30, 1, 0, "number"),
]

if not st.session_state.submitted:
    step = st.session_state.step
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

    previous = st.session_state.answers.get(key, default)

    if kind == "money":
        value = st.number_input(
            "Sua resposta",
            min_value=float(minimum),
            step=float(step_size),
            value=float(previous),
            key=f"q_{key}",
            format="%.2f",
        )
    else:
        value = st.number_input(
            "Sua resposta",
            min_value=int(minimum),
            step=int(step_size),
            value=int(previous),
            key=f"q_{key}",
        )

    st.session_state.answers[key] = value

    c1, c2 = st.columns(2)

    with c1:
        if step > 0:
            if st.button("← Voltar", use_container_width=True):
                st.session_state.step -= 1
                st.rerun()

    with c2:
        label = "Ver meu diagnóstico →" if step == total - 1 else "Próxima pergunta →"
        if st.button(label, type="primary", use_container_width=True):
            # Basic consistency checks as soon as they become relevant.
            a = st.session_state.answers
            if key == "conversations" and a["conversations"] > a["contacts"]:
                st.error("O número de conversas não pode ser maior que o número de contatos.")
            elif key == "quotes" and a["quotes"] > a["conversations"]:
                st.error("O número de cotações não pode ser maior que o número de conversas.")
            elif key == "sales" and a["sales"] > a["quotes"]:
                st.error("O número de vendas não pode ser maior que o número de cotações.")
            elif key == "target" and a["target"] < a["sales"]:
                st.error("Sua meta precisa ser igual ou maior que suas vendas atuais.")
            elif step < total - 1:
                st.session_state.step += 1
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
    }
    result = calculate(data)
    st.session_state.result = result

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

    if st.button("🔓 LIBERAR MEU RAIO-X", type="primary", use_container_width=True):
        errors = []
        if not name.strip():
            errors.append("Informe seu nome.")
        if not validate_phone(whatsapp):
            errors.append("Informe um WhatsApp válido.")
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
                "contacts_month": data["contacts"],
                "conversations_month": data["conversations"],
                "quotes_month": data["quotes"],
                "sales_month": data["sales"],
                "gain_per_sale": data["gain"],
                "target_sales": data["target"],
                "rate_contact_conversation": result["rates"]["Contato → conversa"],
                "rate_conversation_quote": result["rates"]["Conversa → cotação"],
                "rate_quote_sale": result["rates"]["Cotação → venda"],
                "bottleneck": result["bottleneck"],
                "focus_stage": result["focus_stage"],
                "needed_rate": result["needed_rate"],
                "current_revenue": result["current_revenue"],
                "target_revenue": result["target_revenue"],
                "extra_revenue": result["extra_revenue"],
                "source": "raio_x_comercial",
            }

            ok, msg = save_lead(lead)
            st.session_state.lead_saved = ok
            st.session_state.lead_name = name.strip()
            st.session_state.lead_phone = clean_phone(whatsapp)
            st.session_state.show_result = True
            st.rerun()

    st.markdown(
        '<div class="privacy">Seu WhatsApp é necessário para liberar o diagnóstico. Não coloque senhas ou dados sensíveis.</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.get("show_result"):
        st.markdown("---")

        st.markdown("## 🔎 Seu diagnóstico")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Vendas atuais", f"{data['sales']}")
        with c2:
            st.metric("Hoje você ganha", brl(result["current_revenue"]))
        with c3:
            st.metric("Sua meta", f"{data['target']} vendas")

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

        # Funnel
        st.markdown('<div class="section-title">Seu funil hoje</div>', unsafe_allow_html=True)
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Contatos", f"{data['contacts']}")
        f2.metric("Conversas", f"{data['conversations']}", pct(result["rates"]["Contato → conversa"]))
        f3.metric("Cotações", f"{data['quotes']}", pct(result["rates"]["Conversa → cotação"]))
        f4.metric("Vendas", f"{data['sales']}", pct(result["rates"]["Cotação → venda"]))

        # Personalized target
        st.markdown('<div class="section-title">🎯 O que precisa mudar para sua meta?</div>', unsafe_allow_html=True)

        if result["achievable"]:
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
                        diferença potencial entre suas vendas atuais e sua meta,
                        mantendo R$ {brl(data["gain"]).replace("R$ ", "")} por venda.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.warning(
                f"Com o volume atual de contatos, chegar a {data['target']} vendas "
                "não depende de uma única etapa. Você precisaria aumentar a entrada "
                "de oportunidades e/ou melhorar mais de uma conversão."
            )

        # Better insights
        info = insights_for(result["bottleneck"], result, data)
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

        st.markdown("### 💡 3 ações para testar", unsafe_allow_html=True)
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

        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">Seu próximo teste</div>
                <div style="font-size:1.05rem;font-weight:800;color:white;margin-top:.3rem;">
                    Durante os próximos 7 dias, acompanhe especificamente a etapa
                    <span class="orange">{result["bottleneck"]}</span>.
                </div>
                <div class="tip-text" style="margin-top:.4rem;">
                    Registre quantas oportunidades entram nessa etapa, quantas avançam
                    e por que as demais não avançaram. Você vai conseguir comparar
                    o resultado com seu funil atual.
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
            for k in ["step", "answers", "result", "submitted", "show_result", "lead_saved", "lead_name", "lead_phone"]:
                st.session_state.pop(k, None)
            st.rerun()
