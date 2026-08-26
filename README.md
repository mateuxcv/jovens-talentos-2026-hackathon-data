> **Vídeo de apresentação:** link a adicionar antes da entrega final.

# Seazone Investment Decision Engine

### Mesa de Convicção para investimento imobiliário em short-stay

Aplicação de apoio à decisão executiva criada para o **Hackathon Jovens Talentos
Seazone 2026**. O produto transforma os dados de Airbnb e VivaReal de Itapema
(SC) em uma recomendação objetiva de alocação de capital, com premissas
auditáveis, análise de sensibilidade e uma shortlist de imóveis reais.

O objetivo não é construir mais um dashboard de mercado. O IDE foi desenhado
para responder uma pergunta de investimento:

> **Onde e em qual perfil de imóvel a Seazone deve alocar capital para operação
> de short-stay em Itapema?**

## Veredito executivo

### Tese de compactos e studios no Centro: refutada

A recomendação é priorizar **apartamentos de 2 quartos, entre 60 e 85 m²**, em
vez de concentrar capital em studios ou unidades de 1 quarto no Centro.

| Estratégia | Papel na alocação | Leitura executiva |
|---|---|---|
| **Morretes, 2Q** | Retorno | Maior yield percentual e menor ticket de entrada |
| **Centro, 2Q** | Equilíbrio | Combinação de demanda, satisfação dos hóspedes e liquidez |
| **Meia Praia, 2Q** | Escala | Maior volume de mercado e potencial de receita absoluta, com m² mais caro |

O perfil recomendado acomoda de 4 a 6 hóspedes e deve, preferencialmente,
oferecer vaga de garagem, ar-condicionado e reserva instantânea. Esses atributos
estão presentes no motor como evidências operacionais, e não como pontuações
arbitrárias geradas por IA.

## Princípios do produto

- **Números determinísticos:** ADR, receita, yield, cap rate, medianas e
  sensibilidade são calculados exclusivamente em Python com Pandas e NumPy.
- **Premissas explícitas:** nenhuma taxa operacional fica escondida na interface
  ou nos cálculos.
- **IA sem autonomia numérica:** a LLM interpreta resultados já calculados e
  atua como auditora cética; ela não cria métricas nem completa dados ausentes.
- **Decisão antes de visualização:** cada gráfico deve sustentar uma escolha de
  capital, não apenas descrever o mercado.
- **Rastreabilidade:** os imóveis recomendados mantêm o identificador e o link
  do anúncio original no VivaReal.

## Jornada da aplicação

A experiência final será organizada em quatro etapas:

1. **Premissas operacionais:** gestão, WACC, desconto de negociação e vacância.
2. **Mesa de Convicção:** veredito da tese, oportunidade e auditoria de riscos.
3. **Ponto de invalidação:** comparação dinâmica entre Centro e Morretes.
4. **Shortlist de aquisição:** imóveis reais aderentes ao mandato de 2Q.

## Metodologia

### Granularidade e joins

O preço do Airbnb possui várias observações por anúncio. Para impedir que um
listing com mais datas tenha peso maior no resultado, o motor calcula primeiro
a mediana de diária de cada imóvel e somente depois a mediana do segmento.

```text
Price_AV ── aggregate by airbnb_listing_id ──┐
                                             ├── mercado de short-stay
Details ── airbnb_listing_id ── Mesh ────────┘

VivaReal ── listing_id ── mercado de aquisição
```

- `Details` e `Mesh` possuem relação 1:1 por `airbnb_listing_id`.
- `Price_AV` possui relação N:1 com o anúncio do Airbnb.
- Snapshots repetidos de hosts e imóveis à venda são reduzidos ao registro mais
  recente.
- Bairros, booleanos, datas, identificadores e colunas numéricas são
  normalizados antes dos cálculos.

### Fórmulas

Para um segmento de bairro e tipologia:

```text
ADR do segmento = mediana das ADRs medianas de cada listing
Noites ocupadas = 365 × (1 - vacância)
Receita bruta anual = ADR × noites ocupadas
NOI antes de custos do imóvel = receita bruta × (1 - taxa de gestão)
Yield líquido sobre pedido = NOI / preço pedido
Preço negociado = preço pedido × (1 - desconto de negociação)
Yield líquido negociado = NOI / preço negociado
Spread sobre WACC = yield líquido - WACC
```

Na shortlist, condomínio e IPTU conhecidos são descontados do NOI. Quando um
desses campos não está disponível, o valor ausente não é estimado: o cálculo
considera zero e marca `property_costs_complete = False` para tornar a limitação
visível ao decisor.

### Premissas padrão

| Premissa | Valor padrão | Uso |
|---|---:|---|
| Taxa de gestão Seazone | 20,0% | Dedução sobre a receita bruta |
| WACC / custo de oportunidade | 10,0% a.a. | Taxa mínima de atratividade |
| Desconto de negociação | 5,0% | Conversão do preço pedido em preço estimado de compra |
| Vacância projetada | 37,5% | Conversão de 365 dias em noites ocupadas |

As premissas são imutáveis durante cada execução e validadas pela classe
`InvestmentAssumptions`.

## Sensibilidade e ponto de invalidação

O motor mantém o yield do competidor constante e varia o preço de aquisição do
segmento analisado. O ponto de equilíbrio indica quanto esse preço pode subir ou
precisa cair para igualar o retorno do concorrente.

Um crossover negativo não é mascarado: ele significa que o bairro analisado já
possui retorno inferior no cenário-base. Assim, uma preferência pelo Centro
deve ser justificada por liquidez, consistência de demanda ou qualidade da
experiência, e não por superioridade de yield.

## Shortlist de aquisição

Por padrão, um imóvel elegível deve atender aos seguintes critérios:

- apartamento de 2 quartos;
- localização no Centro ou em Morretes;
- área útil entre 60 e 85 m²;
- preço pedido de até R$ 950 mil;
- ADR estimada a partir do segmento equivalente no Airbnb.

Os candidatos são ordenados pelo cap rate líquido estimado sobre o preço
negociado. A tabela final preserva preço, área, bairro, vagas, custos conhecidos,
completude dos custos e URL do anúncio.

## Dados

Os arquivos são um snapshot estático do mercado de Itapema fornecido pela
Seazone para o desafio.

| Arquivo | Conteúdo | Chave principal |
|---|---|---|
| `Details_Itapema.csv` | Características e avaliações dos anúncios Airbnb | `airbnb_listing_id` |
| `Price_AV_Itapema.csv` | Diárias por anúncio, data de estadia e captura | `airbnb_listing_id` |
| `Hosts_ids_Itapema.csv` | Histórico e atributos dos anfitriões | `owner_id` |
| `Mesh_Ids_Data_Itapema.csv` | Coordenadas e bairro dos anúncios | `airbnb_listing_id` |
| `VivaReal_Itapema.csv` | Imóveis à venda e respectivos custos | `listing_id` |

Fonte oficial: [dataset do Hackathon Jovens Talentos 2026](https://github.com/mateuxcv/jovens-talentos-2026-hackathon-data).

## Arquitetura

```text
.
├── data/                    # CSVs originais do desafio
├── src/
│   ├── __init__.py
│   └── engine.py            # Contrato de dados e regras determinísticas
├── ai-log/                  # Histórico textual das interações com IA
├── index.html               # Enunciado original do desafio
├── README.md
└── requirements.txt
```

### API do motor

| Função | Responsabilidade |
|---|---|
| `load_datasets` | Carregar e validar os cinco schemas oficiais |
| `normalize_datasets` | Padronizar tipos, bairros e snapshots sem alterar os dados brutos |
| `build_market_segments` | Consolidar Airbnb e VivaReal por bairro e perfil |
| `calculate_investment_metrics` | Calcular receita, yields e spreads sobre WACC |
| `run_sensitivity_analysis` | Encontrar o crossover de retorno entre estratégias |
| `build_acquisition_shortlist` | Filtrar e ordenar imóveis reais para aquisição |
| `build_decision_data` | Entregar todos os dados necessários para a interface |

## Como executar

### Requisitos

- Python 3.10 ou superior
- `pip`

### Instalação

```bash
git clone https://github.com/mateuxcv/jovens-talentos-2026-hackathon-data.git
cd jovens-talentos-2026-hackathon-data
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Executar o motor

```bash
python - <<'PY'
from src.engine import build_decision_data

decision = build_decision_data("data")
print(decision["metrics"].to_string(index=False))
print(decision["shortlist"].to_string(index=False))
print(decision["sensitivity"].attrs)
PY
```

### Executar a interface

A interface Streamlit ainda está em construção. Quando `app.py` estiver
disponível, poderá ser iniciada com:

```bash
streamlit run app.py
```

## Governança da IA

A futura camada de IA receberá somente um payload estruturado produzido por
`engine.py`. Seu escopo será limitado a:

- sintetizar o parecer executivo;
- confrontar a tese com os resultados calculados;
- apontar riscos de amostragem, sazonalidade e qualidade dos dados;
- explicar por que uma recomendação muda em determinado cenário.

A LLM não poderá calcular ADR, receita, preço por m², yield, cap rate ou ponto de
invalidação. O texto produzido será armazenado em `ai-log/` para auditoria.

## Limitações conhecidas

- O dataset é um snapshot e não representa atualização em tempo real.
- Preço anunciado não é necessariamente preço efetivo de transação.
- Disponibilidade no Airbnb não equivale diretamente a ocupação realizada.
- Condomínio e IPTU possuem dados ausentes em parte dos anúncios.
- Segmentos com amostras pequenas exigem interpretação cautelosa.
- Receita projetada não contempla reformas, mobiliário, manutenção, impostos
  operacionais ou custos extraordinários não presentes na base.

## Status

- [x] Contrato e validação dos cinco datasets
- [x] Motor determinístico de métricas por segmento
- [x] Sensibilidade Centro versus Morretes
- [x] Shortlist rastreável de aquisição
- [ ] Interface executiva em Streamlit
- [ ] Parecer do auditor cético com LLM
- [ ] Exportação das sessões para `ai-log/`
- [ ] Vídeo de apresentação

## Desafio

Projeto desenvolvido para o
[Hackathon Jovens Talentos AI Builder 2026 — Seazone](https://seazone-tech.github.io/jovens-talentos-2026-hackathon-data/).
