
# Raio-X Comercial — MVP

MVP em Streamlit + Supabase, com custo inicial potencialmente zero.

## O que faz
- Uma única tela.
- Coleta o funil mensal do consultor.
- Calcula conversões entre etapas.
- Identifica o menor índice de conversão como principal gargalo.
- Usa a meta de vendas informada pelo próprio consultor.
- Calcula qual taxa precisaria ser atingida para chegar à meta, mantendo as demais etapas constantes.
- Calcula ganho atual e potencial adicional usando o ganho médio por venda.
- Exige WhatsApp antes de liberar o diagnóstico.
- Salva o lead no Supabase.

## Rodar localmente

```bash
pip install -r requirements.txt
streamlit run app.py
```

Configure as variáveis:
- SUPABASE_URL
- SUPABASE_KEY

## Supabase
Execute `supabase.sql` no SQL Editor.

### Segurança
Para produção, prefira uma arquitetura em que a chave `service_role` fique apenas no backend/servidor, nunca no navegador.
O app deste MVP lê `SUPABASE_URL` e `SUPABASE_KEY` do ambiente. Se usar a anon key, configure RLS/policies corretamente.

## Deploy
No Render:
- Runtime: Python
- Build: `pip install -r requirements.txt`
- Start: `streamlit run app.py --server.address 0.0.0.0 --server.port $PORT`

Configure `SUPABASE_URL` e `SUPABASE_KEY` nas Environment Variables.
