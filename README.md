# Raio-X Comercial | David Fernandes

Ferramenta gratuita de diagnóstico comercial para captação e qualificação de consultores.

## O que a versão atual faz
- Uma pergunta por vez, com barra de progresso.
- Não pré-preenche respostas anteriores ao navegar/recomeçar.
- Diagnóstico de volume quando há menos de 60 contatos **ou** menos de 50 cotações.
- Pergunta condicional sobre a principal fonte de contatos.
- Simulação de conversão por origem:
  - Ações de Rua: +15%
  - Indicações de Associados: +20%
  - Parceiros: +30%
  - Tráfego Pago: +30%
- Mostra conversão cotação → venda, contato → venda e quantos contatos são necessários, em média, para gerar uma venda.
- Mostra uma meta prática de prospecção baseada no funil informado.
- Cria um perfil comercial (ex.: Consultor Avançado) a partir de volume e eficiência.
- Se o ganho médio por venda for menor que R$ 250, pergunta sobre descontos.
- Se o desconto informado for superior a 30%, apresenta recomendações para defesa de valor, SPIN Selling, atendimento síncrono e disciplina de desconto.
- Celebração visual ao liberar o diagnóstico.
- Área administrativa discreta no canto inferior, protegida por OTP enviado por SMTP.
- Área administrativa com tabela dos diagnósticos captados.

## Rodar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Secrets / SMTP
Configure os segredos no ambiente de produção. **Não publique senha SMTP ou OTP_SECRET no GitHub.**

Exemplo de estrutura do Streamlit Secrets:

```toml
OTP_SECRET = "COLOQUE_UMA_FRASE_LONGA_E_ALEATORIA"
ADMIN_EMAILS = ["seu-email-autorizado@dominio.com"]

[smtp]
host = "smtp.gmail.com"
port = 465
username = "seu-email@gmail.com"
password = "SENHA_DE_APP_DO_GMAIL"
from_email = "seu-email@gmail.com"
from_name = "Raio-X do Consultor"
```

Se `ADMIN_EMAILS` não for informado, o e-mail SMTP (`smtp.username`) será usado como único e-mail autorizado.

## Supabase
Configure:
- `SUPABASE_URL`
- `SUPABASE_KEY`

Execute o `supabase.sql` no projeto antes do primeiro teste com os novos campos.
