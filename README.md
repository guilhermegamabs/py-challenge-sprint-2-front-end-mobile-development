# Challenge Sprint 2: Visualização Operacional e Dashboards de Ativos

### FRONT END & MOBILE DEVELOPMENT

---

## Integrantes

| Nome | RM |
|---|---|
| Guilherme Gama | RM565293 |
| Bruno Fernandes Nascimento | RM552574 |
| Edgar Lódula de Assis | RM565260 |
| Júlia Aben-Athar | RM566325 |
| Igor Thiago Nakajima Vieira | RM563632 |

**Professor:** Lucas Tadeu Cunha Rios

---

Interface web desenvolvida em **Streamlit** para monitoramento operacional de motores industriais, com navegação por planta, dashboards de telemetria em tempo real, gráficos de séries temporais históricas, alertas com cores semânticas e cadastro visual da placa do motor via IA (Gemini 2.5 Flash).

Evolução do projeto da Sprint 1 — agora com persistência em SQLite, dashboards Plotly e extração de dados da placa do motor por visão computacional.

---

## Funcionalidades

| Tela | Descrição |
|---|---|
| **Navegação por Planta** | Página inicial. Seleciona Planta → Área e exibe os ativos da área em cards com status colorido (verde/amarelo/vermelho) e mini-leituras de cada sensor. |
| **Dashboard do Ativo** | Cabeçalho do equipamento + thumbnail da placa, 4 gauges Plotly (Temperatura, Vibração, Corrente, RPM) com cores dinâmicas por limites operacionais, série temporal histórica com bandas warn/crit e tabela de alertas no período. |
| **Consulta de Equipamentos** | Lista de equipamentos com filtros por Planta, Área, Fabricante e busca por TAG/Modelo. Coluna Status colorida com a última condição do ativo. |
| **Novo Equipamento** | Upload da imagem da placa do motor → extração automática via Gemini 2.5 Flash (TAG, Modelo, Fabricante, Potência, Tensão). Campos detectados marcados com ✓ IA e ausentes com ⚠ — todos editáveis pelo operador antes do cadastro. |
| **Módulo Técnico** | Ficha técnica completa do equipamento + Planta/Área + imagem da placa cadastrada. Edição inline dos dados. |
| **Dados Brutos** | Visualização das leituras ADC do sensor com conversão para unidades de engenharia (mantido da Sprint 1). |

---

## Stack

| Camada | Tecnologia |
|---|---|
| UI | Streamlit |
| Gráficos | Plotly (gauges + séries temporais) |
| Persistência | SQLite (`data/forzy.db`) |
| Visão Computacional / OCR | Google Gemini 2.5 Flash via `google-genai` |
| Processamento | pandas + numpy |

---

## Estrutura do Projeto

```
py-challenge-sprint-2-front-end-mobile-development/
├── main.py                            # entry point + init_db + roteamento de páginas
├── requirements.txt
├── .streamlit/
│   ├── config.toml                    # tema dark Forzy
│   └── secrets.toml                   # GEMINI_API_KEY (gitignored)
├── data/                              # gerado em runtime (gitignored)
│   ├── forzy.db                       # SQLite — plantas, áreas, equipamentos, leituras, limites
│   └── placas/                        # imagens das placas cadastradas
├── img/
│   ├── forzy_logo.jpg
│   ├── logo-forzy-branca.svg
│   └── logo-forzy-preta.svg
└── app/
    ├── components/
    │   ├── cabecalho.py               # header reutilizável
    │   └── status_badge.py            # pill OK / Atenção / Crítico
    ├── pages/
    │   ├── navegacao_planta.py        # tree Planta → Área → Equipamento
    │   ├── dashboard_ativo.py         # gauges + série temporal + alertas
    │   ├── consulta_equipamentos.py
    │   ├── cadastro_equipamento.py    # upload + OCR Gemini
    │   ├── modulo_tecnico.py
    │   └── dados_brutos.py
    └── services/
        ├── db.py                      # conexão SQLite + schema + seed
        ├── equipamentos.py            # CRUD de equipamentos/plantas/áreas
        ├── telemetria.py              # leituras, classificação de status, histórico, alertas
        └── ocr_placa.py               # cliente Gemini 2.5 Flash + parsing
```

---

## Modelo de Dados (SQLite)

| Tabela | Conteúdo |
|---|---|
| `plantas` | Lista de plantas industriais |
| `areas` | Áreas dentro de cada planta |
| `equipamentos` | Motores cadastrados (TAG, modelo, fabricante, potência, tensão, área, caminho da imagem da placa) |
| `leituras` | Histórico de telemetria (temperatura, vibração, corrente, RPM) com timestamp |
| `limites` | Faixas warn/crit por grandeza para classificação de status |

O seed inicial popula 3 plantas, 6 áreas, 8 equipamentos e 7 dias de histórico sintético por equipamento (8 × 10 080 leituras). EQ-003 e EQ-007 são forçados a estado crítico, EQ-005 e EQ-006 a alerta, para demonstração visual.

---

## Como rodar localmente

### Pré-requisitos

- Python 3.11 ou superior
- pip
- Chave da API do Google Gemini (https://aistudio.google.com/apikey)

### Passos

**1. Clone o repositório**
```bash
git clone git@github.com:guilhermegamabs/py-challenge-sprint-2-front-end-mobile-development.git
cd py-challenge-sprint-2-front-end-mobile-development
```

**2. Crie e ative o ambiente virtual**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Configure a chave do Gemini**

Crie o arquivo `.streamlit/secrets.toml` (não comitado):
```toml
GEMINI_API_KEY = "sua-chave-aqui"
```

Alternativa via variável de ambiente:
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY = "sua-chave-aqui"

# Linux / macOS
export GEMINI_API_KEY="sua-chave-aqui"
```

**5. Inicie o servidor**
```bash
streamlit run main.py
```

Na primeira execução o banco `data/forzy.db` é criado e populado automaticamente. O app abre em `http://localhost:8501`.

---

## Jornada do Operador (demo)

1. **Navegação por Planta** → seleciona planta e área, vê cards de equipamentos com status colorido.
2. Identifica visualmente um motor em estado crítico (borda vermelha + badge Crítico) — ex.: EQ-003.
3. **Dashboard do Ativo** → confere telemetria atual em 4 gauges, observa a tendência de aquecimento na série temporal de 7 dias e consulta a tabela de alertas.
4. **Novo Equipamento** → faz upload da imagem da placa de um motor → IA extrai TAG, Modelo, Fabricante, Potência e Tensão → operador revisa e confirma.
5. **Módulo Técnico** → consulta a ficha completa do novo equipamento com a imagem da placa associada.

