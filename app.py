import re
import os
from datetime import datetime, timezone

import streamlit as st

try:
    from supabase import create_client
except Exception:
    create_client = None


st.set_page_config(
    page_title="Raio-X Comercial | David Fernandes",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {max-width: 900px; padding-top: 2rem; padding-bottom: 3rem;}
    .hero {text-align:center; padding:1rem 0 1.5rem;}
    .hero h1 {font-size:2.5rem; margin-bottom:.25rem;}
    .hero p {font-size:1.05rem; opacity:.75;}
    .metric {font-size:1.8rem; font-weight:700;}
    .muted {opacity:.72;}
    .highlight {padding:1rem; border-radius:14px; background:rgba(255,102,0,.10); border:1px solid rgba(255,102,0,.28);}
    .success {padding:1rem; border-radius:14px; background:rgba(0,160,80,.10); border:1px solid rgba(0,160,80,.25);}
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


def get_secret(name, default=None):
    """Lê primeiro de Streamlit Secrets e depois de variável de ambiente."""
    try:
        value = st.secrets.get(name)
        if value:
            return value
    except Exception:
        pass
    return os.getenv(name, default)


def get_supabase():
    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_KEY")

    if not url or not key or create_client is None:
        return None

    try:
        return create_client(url, key)
    except Exception:
        return None


def save_lead(data):
    sb = get_supabase()
    if sb is None:
        return False, "Supabase não configurado. O diagnóstico continuará funcionando."

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

    current_revenue = sales * gain
    target_revenue = target * gain

    # Quando o volume é muito baixo, tratamos isso separadamente.
    low_volume = contacts < 60 or quotes < 50

    # Gargalo proporcional do funil.
    bottleneck = min(rates, key=rates.get)

    # Meta personalizada: calcula quanto cada etapa teria que converter,
    # mantendo as outras etapas constantes.
    candidates = []

    if contacts > 0 and r2 > 0 and r3 > 0:
        needed_r1 = target / (contacts * r2 * r3)
        candidates.append(("Contato → conversa", needed_r1))

    if contacts > 0 and r1 > 0 and r3 > 0:
        needed_r2 = target / (contacts * r1 * r3)
        candidates.append(("Conversa → cotação", needed_r2))

    if contacts > 0 and r1 > 0 and r2 > 0:
        needed_r3 = target / (contacts * r1 * r2)
        candidates.append(("Cotação → venda", needed_r3))

    current_rates = rates.copy()

    if low_volume:
        focus_stage = "Volume de oportunidades"
        current_rate = 0.0
        needed_rate = 0.0
        achievable = False
        improvement_pp = 0.0
    else:
        bottleneck_need = next(
            (x[1] for x in candidates if x[0] == bottleneck),
            None,
        )

        if bottleneck_need is not None and bottleneck_need <= 1:
            focus_stage = bottleneck
            needed_rate = bottleneck_need
        else:
            viable = [
                (stage, req)
                for stage, req in candidates
                if req <= 1
            ]

            if viable:
                focus_stage, needed_rate = min(
                    viable,
                    key=lambda x: abs(x[1] - current_rates[x[0]])
                )
            else:
                focus_stage = bottleneck
                needed_rate = bottleneck_need if bottleneck_need is not None else 1.0

        current_rate = current_rates[focus_stage]
        achievable = needed_rate <= 1
        improvement_pp = max(0, (needed_rate - current_rate) * 100)

    contacts_per_sale = (
        contacts / sales if sales > 0 else None
    )
    contact_to_sale = (
        sales / contacts if contacts > 0 else 0
    )

    return {
        "rates": rates,
        "bottleneck": bottleneck,
        "current_revenue": current_revenue,
        "target_revenue": target_revenue,
        "focus_stage": focus_stage,
        "current_rate": current_rate,
        "needed_rate": needed_rate,
        "improvement_pp": improvement_pp,
        "achievable": achievable,
        "target": target,
        "extra_sales": max(0, target - sales),
        "extra_revenue": max(0, target_revenue - current_revenue),
        "low_volume": low_volume,
        "contact_to_sale": contact_to_sale,
        "contacts_per_sale": contacts_per_sale,
    }


def explanation_for(stage):
    explanations = {
        "Contato → conversa": (
            "Seu primeiro ponto de atenção é transformar mais contatos em conversas reais. "
            "Vale revisar abordagem inicial, velocidade de resposta e qualidade dos contatos."
        ),
        "Conversa → cotação": (
            "Seu ponto de atenção está entre conversar e apresentar uma proposta. "
            "Vale revisar qualificação, condução da conversa e chamada para a cotação."
        ),
        "Cotação → venda": (
            "Seu principal ponto de atenção está na conversão das propostas. "
            "Vale revisar objeções, apresentação de valor, negociação e principalmente o follow-up."
        ),
        "Volume de oportunidades": (
            "Seu principal ponto de atenção agora é gerar mais oportunidades. "
            "Antes de tentar extrair mais conversão do funil, vale aumentar a entrada de contatos e cotações."
        ),
    }

    # Fallback defensivo: nunca deixa uma chave inesperada derrubar o app.
    return explanations.get(
        stage,
        "Seu funil apresenta uma oportunidade de melhoria. Vale analisar as etapas com menor conversão e o volume de oportunidades geradas."
    )


st.markdown("""
<div class="hero">
<h1>📊 RAIO-X COMERCIAL</h1>
<p>Descubra onde você está perdendo vendas e o que precisa ajustar para chegar na sua próxima meta.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("### Seu funil hoje")
st.caption("Use uma média mensal. Não precisa ser exato — uma boa estimativa já funciona.")

c1, c2 = st.columns(2)
with c1:
    contacts = st.number_input("Novos contatos / mês", min_value=1, step=10, value=200)
    conversations = st.number_input("Conversas iniciadas / mês", min_value=0, step=10, value=140)
    quotes = st.number_input("Cotações / propostas / mês", min_value=0, step=5, value=100)
with c2:
    sales = st.number_input("Vendas / mês", min_value=0, step=1, value=20)
    gain = st.number_input("Ganho médio por venda (R$)", min_value=0.0, step=10.0, value=250.0)
    target = st.number_input("Quantas vendas você gostaria de fazer / mês?", min_value=0, step=1, value=30)

st.markdown("### Sobre você")
c3, c4 = st.columns(2)
with c3:
    name = st.text_input("Nome")
    whatsapp = st.text_input("WhatsApp *", placeholder="(19) 99999-9999")
with c4:
    city = st.text_input("Cidade")
    experience = st.selectbox(
        "Experiência com vendas",
        ["Menos de 1 ano", "1 a 3 anos", "3 a 5 anos", "Mais de 5 anos"]
    )
    works_protection = st.selectbox(
        "Já trabalha com proteção veicular?",
        ["Sim", "Não"]
    )

st.markdown("---")

submitted = st.button("🔎 ANALISAR MEU FUNIL", type="primary", use_container_width=True)

if submitted:
    errors = []

    if not validate_phone(whatsapp):
        errors.append("Informe um WhatsApp válido para receber seu diagnóstico.")
    if conversations > contacts:
        errors.append("Conversas não podem ser maiores que novos contatos.")
    if quotes > conversations:
        errors.append("Cotações não podem ser maiores que conversas.")
    if sales > quotes:
        errors.append("Vendas não podem ser maiores que cotações.")
    if target < sales:
        errors.append("Sua meta precisa ser igual ou maior que suas vendas atuais.")
    if not name.strip():
        errors.append("Informe seu nome.")

    if errors:
        for error in errors:
            st.error(error)
    else:
        data = {
            "contacts": int(contacts),
            "conversations": int(conversations),
            "quotes": int(quotes),
            "sales": int(sales),
            "gain": float(gain),
            "target": int(target),
        }

        result = calculate(data)

        lead = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "name": name.strip(),
            "whatsapp": clean_phone(whatsapp),
            "city": city.strip(),
            "experience": experience,
            "works_protection": works_protection,
            "contacts_month": int(contacts),
            "conversations_month": int(conversations),
            "quotes_month": int(quotes),
            "sales_month": int(sales),
            "gain_per_sale": float(gain),
            "target_sales": int(target),
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

        st.success("Diagnóstico liberado! Seu WhatsApp foi registrado para podermos enviar/entregar seu resultado.")

        st.markdown("## 🔎 Seu diagnóstico")

        m1, m2, m3 = st.columns(3)
        m1.metric("Vendas atuais", f"{sales}")
        m2.metric("Ganho atual", brl(result["current_revenue"]))
        m3.metric("Meta", f"{target} vendas")

        st.markdown("### Seu funil")
        f1, f2, f3, f4 = st.columns(4)
        f1.metric("Contatos", f"{contacts}")
        f2.metric("Conversas", f"{conversations}", pct(result["rates"]["Contato → conversa"]))
        f3.metric("Cotações", f"{quotes}", pct(result["rates"]["Conversa → cotação"]))
        f4.metric("Vendas", f"{sales}", pct(result["rates"]["Cotação → venda"]))

        if result["low_volume"]:
            st.markdown(
                '<div class="highlight"><strong>⚠️ Principal ponto de atenção: Volume de oportunidades</strong><br>'
                '<span class="muted">Seu volume atual ainda é baixo para tirar uma conclusão forte apenas pelas taxas de conversão.</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f'<div class="highlight"><strong>⚠️ Principal gargalo: {result["bottleneck"]}</strong><br>'
                f'<span class="muted">É a etapa com menor conversão proporcional do seu funil.</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown("### 📈 Seus números-chave")
        k1, k2, k3 = st.columns(3)
        k1.metric("Cotação → venda", pct(result["rates"]["Cotação → venda"]))
        k2.metric("Contato → venda", pct(result["contact_to_sale"]))
        k3.metric(
            "Contatos por venda",
            "—" if result["contacts_per_sale"] is None else f"{result['contacts_per_sale']:.1f}",
        )

        st.markdown("### 🎯 Para chegar na sua meta")

        if result["low_volume"]:
            st.write(
                f"Com **{contacts} contatos** e **{quotes} cotações** por mês, o principal ajuste agora é aumentar o volume de oportunidades. "
                f"Depois disso, fica mais confiável avaliar qual etapa do funil merece maior atenção."
            )
        elif result["achievable"]:
            st.write(
                f"Se você mantiver as demais etapas como estão, sua etapa de **{result['focus_stage']}** "
                f"precisaria passar de **{pct(result['current_rate'])}** para aproximadamente "
                f"**{pct(result['needed_rate'])}**."
            )
            st.markdown(
                f'<div class="success"><strong>Meta: {target} vendas/mês</strong><br>'
                f'Isso representa <strong>+{result["extra_sales"]} vendas</strong> e '
                f'<strong>+{brl(result["extra_revenue"])}/mês</strong> em relação ao cenário atual, '
                f'se o ganho médio por venda permanecer em {brl(gain)}.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.warning(
                f"Com o volume atual de contatos, sua meta de {target} vendas não é atingível "
                f"melhorando apenas uma etapa do funil. Para chegar lá, será necessário aumentar "
                f"o volume de oportunidades e/ou melhorar mais de uma etapa."
            )

        st.markdown("### 💡 O que isso significa")
        st.write(explanation_for(result["focus_stage"]))

        if ok:
            st.caption("Seu diagnóstico foi registrado com sucesso.")
        else:
            st.caption(msg)
