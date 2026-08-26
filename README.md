> **Vídeo de apresentação:** link a adicionar antes da entrega final.

# Quebre a Tese

Uma experiência de decisão para testar a hipótese de investimento da Seazone em
Itapema. Em vez de entregar outro dashboard, o produto coloca a tese interna
contra o melhor segmento elegível, expõe cada evidência e calcula a menor
mudança capaz de inverter o resultado.

> **Posição:** os dados não sustentam compactos no Centro como a opção mais
> eficiente sob o critério definido. Morretes 2Q lidera o cenário-base, mas a
> qualidade da evidência permite diligência, não autorização automática de
> compra.

A recomendação completa está em [`relatorio.md`](relatorio.md).

## Produto

A aplicação conduz uma deliberação em seis atos:

1. Confronta a tese interna com o melhor desafiante elegível.
2. Separa fatos observados, cálculos e premissas.
3. Exibe peças de evidência rastreáveis.
4. Procura o menor choque que derruba o vencedor.
5. Mantém objeções abertas antes do aporte.
6. Converte o resultado em Buy Box e fila de diligência.

O botão **Tentar quebrar a recomendação** é o centro da experiência. O cálculo
não usa IA: ele encontra a menor variação isolada de tarifa ou preço necessária
para levar a decisão ao empate.

## Resultado Reproduzível

Com a premissa ilustrativa de 62,5% de ocupação anual comum aos segmentos:

| Evidência | Centro Studio/1Q | Morretes 2Q |
|---|---:|---:|
| Tarifa típica anunciada | R$ 445 | R$ 464 |
| Preço pedido típico | R$ 890 mil | R$ 790 mil |
| Receita bruta anualizada de cenário | R$ 101.516 | R$ 105.850 |
| Retorno bruto de cenário | 11,4% | 13,4% |
| Anúncios de short stay precificados | 78 | 51 |
| Ofertas de venda válidas | 19 | 892 |

O resultado aponta o mesmo vencedor nos três tratamentos elegíveis; um quarto
tratamento fica inconclusivo porque deixa a tese abaixo do corte amostral. A cobertura de preços também é desigual: 66,1%
para Centro Studio/1Q e 22,3% para Morretes 2Q. Por isso, a força da evidência é
classificada como **limitada**.

### Ponto de reversão

Morretes 2Q deixa de liderar se, isoladamente:

- sua tarifa típica cair aproximadamente 14,9%;
- sua ocupação ficar cerca de 9,3 pontos percentuais abaixo do cenário comum;
- seu preço pedido típico superar aproximadamente R$ 928 mil;
- compactos no Centro forem adquiridos por aproximadamente R$ 758 mil ou menos.

Esses valores representam empate entre os dois perfis, não uma promessa de
retorno.

## Contrato Da Decisão

O motor procura o maior retorno bruto de cenário entre segmentos que tenham:

- apenas apartamentos, para manter comparabilidade entre as fontes;
- bairro e perfil de quartos presentes no Airbnb e no VivaReal;
- ao menos 20 anúncios de short stay com tarifa;
- ao menos 15 ofertas de venda válidas.

```text
Receita bruta anualizada de cenário
    = tarifa anunciada mediana × 365 × ocupação assumida

Retorno bruto de cenário
    = receita bruta anualizada de cenário / preço pedido mediano
```

A ocupação é uma premissa ajustável. Como é aplicada igualmente aos segmentos,
ela altera o nível do retorno, mas não cria artificialmente um vencedor. A
aplicação calcula separadamente qual diferença de ocupação mudaria a escolha.

## Tratamento Dos Dados

- IDs são carregados como texto para preservar os identificadores de 19 dígitos.
- `Details` e `Mesh` são unidos 1:1 por `airbnb_listing_id`.
- Preços repetidos para o mesmo anúncio e data de estadia são snapshots; o
  cenário-base mantém a captura mais recente.
- Cada anúncio recebe primeiro sua tarifa mediana; depois é calculada a mediana
  do segmento, evitando peso maior para listings com mais datas.
- O lado Airbnb é restrito a apartamentos, assim como o mercado de aquisição.
- Ofertas do VivaReal são deduplicadas por ID e por assinatura de conteúdo;
  preços até R$ 1 mil dentro da mesma assinatura são tratados como republicação.
- Áreas de 15 a 500 m², preços de R$ 100 mil a R$ 20 milhões e preço por m² de
  R$ 3 mil a R$ 50 mil formam limites amplos contra erros evidentes de unidade.
- Divergências entre bairro informado e bairro identificável na URL são testadas
  como cenário de robustez e excluídas da shortlist.
- Condomínio e IPTU não entram no ranking quando ausentes. A ausência vira uma
  pendência de diligência, nunca custo zero vantajoso.

## Testes De Robustez

O mesmo duelo é recalculado com:

- captura mais recente de cada diária;
- primeira captura de cada diária;
- ofertas do VivaReal sem deduplicação adicional de conteúdo;
- somente ofertas cujo bairro não conflita com a URL.

Os resultados completos estão em [`outputs/robustez.csv`](outputs/robustez.csv).

## Fontes E Limitações

O dataset permite observar oferta e preço anunciado, não desempenho realizado:

- somente 999 dos 4.441 anúncios Airbnb têm preços vinculáveis, cobertura de
  22,5%;
- as tarifas cobrem 105 dias, de 06/01/2025 a 20/04/2025;
- ausência de uma diária não prova reserva;
- não há ocupação, receita realizada ou duração das estadias;
- o VivaReal contém preço pedido, não preço transacionado;
- não existe ligação imóvel a imóvel entre Airbnb e VivaReal;
- custos, estágio da obra e restrições condominiais são incompletos.

Por isso, “retorno bruto de cenário” não é chamado de NOI, cap rate líquido ou
retorno realizado.

## Arquitetura

```text
data/                       CSVs originais
src/engine.py               limpeza, regras, decisão e stress test
scripts/export_evidence.py  exportação dos artefatos reproduzíveis
outputs/                    decisão, segmentos, robustez e shortlist
tests/test_engine.py        testes do contrato e das fórmulas
app.py                      experiência guiada em Streamlit
relatorio.md                recomendação final escrita
ai-log/                     export integral das conversas com IA
```

Nenhum framework multiagente é utilizado. A IA ajudou a formular hipóteses,
criticar inferências e estruturar a comunicação; os números e o veredito são
produzidos por regras Python testáveis.

## Como Executar

Requisitos: Python 3.10 ou superior e `pip`.

```bash
git clone https://github.com/mateuxcv/jt2026-mateus-victor.git
cd jt2026-mateus-victor
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

A aplicação abrirá em `http://localhost:8501`.

### Regerar Evidências

```bash
python scripts/export_evidence.py
```

### Executar Testes

```bash
python -m unittest discover -v
```

## Artefatos Gerados

- [`outputs/decisao.json`](outputs/decisao.json): contrato, tese, desafiante e
  condições de reversão.
- [`outputs/segmentos.csv`](outputs/segmentos.csv): métricas de todos os
  segmentos.
- [`outputs/robustez.csv`](outputs/robustez.csv): tratamentos alternativos.
- [`outputs/shortlist.csv`](outputs/shortlist.csv): anúncios para diligência.

## Antes Da Entrega

- [ ] Adicionar o link público do vídeo na primeira linha.
- [ ] Exportar esta sessão completa para `ai-log/` em texto ou JSON.
- [ ] Confirmar repositório e vídeo em janela anônima.

## Desafio

[Hackathon Jovens Talentos AI Builder 2026](https://seazone-tech.github.io/jovens-talentos-2026-hackathon-data/)
