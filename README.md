# Raio-X Comercial — MVP v2

Ferramenta de diagnóstico comercial para consultores.

## Mudanças desta versão
- Experiência de uma pergunta por vez.
- Barra de progresso.
- Interface dark com comunicação visual preta + laranja.
- Logo incluído em `logo.png`.
- Captura de WhatsApp antes de liberar o diagnóstico.
- Diagnóstico do principal gargalo.
- Meta personalizada de vendas.
- Cálculo do potencial financeiro.
- Insights e 3 ações práticas por tipo de gargalo.
- Supabase continua opcional no desenvolvimento local.

## Rodar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
No Render, configure:
- SUPABASE_URL
- SUPABASE_KEY

Nunca publique credenciais reais no GitHub.
