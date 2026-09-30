# Raio-X Comercial — MVP v3

- Uma pergunta por vez + barra de progresso.
- Comunicação visual preta + laranja.
- Logo transparente na interface e como favicon.
- Celebração visual ao liberar o diagnóstico.
- WhatsApp obrigatório antes do resultado.
- Diagnóstico de volume quando há menos de 60 contatos ou menos de 50 cotações.
- Pergunta condicional sobre principal fonte de contatos.
- Simulação de conversão cotação → venda:
  - Tráfego Pago: +30%
  - Parceiros: +30%
  - Indicações de Associados: +20%
  - Ações de Rua: +15%
  - Outros: sem ajuste
- Cálculo do volume de contatos necessário para a meta quando o gargalo é volume.
- Conversão cotação → venda e contato → venda.
- Contatos necessários, em média, para gerar uma venda.
- Pergunta condicional sobre descontos quando o ganho médio por venda fica abaixo de R$ 250.
- Alertas e ações para remuneração baixa e desconto acima de 30%.
- Insights e ações práticas por diagnóstico.
- Supabase opcional no desenvolvimento local.

## Rodar
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Render
Configure `SUPABASE_URL` e `SUPABASE_KEY` como Environment Variables.
Nunca publique credenciais reais no GitHub.
