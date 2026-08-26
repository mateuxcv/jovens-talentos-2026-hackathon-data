"""Guided Streamlit experience for the Itapema investment decision."""

from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from src.engine import DecisionAssumptions, build_decision_data

DATA_DIR = Path(__file__).parent / "data"

st.set_page_config(
    page_title="Quebre a Tese | Itapema",
    page_icon="Q",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,600;6..72,700&display=swap');

        :root {
            --paper: #f1eee5;
            --sheet: #fbfaf5;
            --ink: #17201e;
            --muted: #68716c;
            --line: #cbc8bc;
            --signal: #d94a35;
            --signal-soft: #f3d8d0;
            --green: #0e6b58;
            --green-soft: #d9e8df;
            --acid: #d9ef72;
        }
        html, body, [class*="css"] { font-family: "IBM Plex Sans", sans-serif; }
        .stApp { background: var(--paper); color: var(--ink); }
        .block-container { max-width: 1120px; padding-top: 1.5rem; padding-bottom: 5rem; }
        h1, h2, h3 { font-family: "Newsreader", serif !important; color: var(--ink); letter-spacing: -.025em; }
        h2 { font-size: clamp(2rem, 4vw, 3.25rem) !important; line-height: 1 !important; }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"] { background: var(--ink); }
        [data-testid="stSidebar"] * { color: #f8f6ee !important; }

        .case-bar {
            display: flex; justify-content: space-between; gap: 20px; align-items: center;
            border-top: 1px solid var(--ink); border-bottom: 1px solid var(--ink);
            padding: 11px 0; margin-bottom: 34px; font: 600 .72rem "IBM Plex Mono", monospace;
            letter-spacing: .08em; text-transform: uppercase;
        }
        .hero { padding: 2.1rem 0 2.8rem; }
        .hero .eyebrow, .kicker { color: var(--signal); font: 600 .72rem "IBM Plex Mono", monospace; letter-spacing: .12em; text-transform: uppercase; }
        .hero h1 { font-size: clamp(3.2rem, 8vw, 7rem); line-height: .82; max-width: 900px; margin: 20px 0 26px; }
        .hero p { color: var(--muted); font-size: 1.08rem; max-width: 720px; }
        .verdict-stamp {
            display: inline-flex; align-items: center; gap: 10px; margin-top: 22px;
            border: 2px solid var(--signal); color: var(--signal); padding: 10px 14px;
            font: 600 .78rem "IBM Plex Mono", monospace; text-transform: uppercase;
            transform: rotate(-1deg);
        }
        .section { margin-top: 64px; }
        .section-rule { border-top: 1px solid var(--ink); padding-top: 13px; margin-bottom: 24px; display:flex; justify-content:space-between; gap:16px; }
        .section-rule span { font: 600 .7rem "IBM Plex Mono", monospace; letter-spacing: .1em; text-transform: uppercase; }

        .duel-card { background: var(--sheet); border: 1px solid var(--line); padding: 28px; min-height: 300px; position: relative; }
        .duel-card.challenger { border-top: 5px solid var(--green); }
        .duel-card.thesis { border-top: 5px solid var(--signal); }
        .duel-role { font: 600 .68rem "IBM Plex Mono", monospace; letter-spacing:.1em; text-transform:uppercase; color:var(--muted); }
        .duel-card h3 { font-size: 2rem; margin: 18px 0 26px; }
        .duel-metric { border-top: 1px solid var(--line); padding: 12px 0; display:flex; justify-content:space-between; gap:14px; }
        .duel-metric span { color:var(--muted); font-size:.84rem; }
        .duel-metric strong { font-family:"IBM Plex Mono", monospace; font-size:.9rem; text-align:right; }
        .winner-tag { display:inline-block; background:var(--acid); padding:6px 9px; font:600 .67rem "IBM Plex Mono", monospace; text-transform:uppercase; margin-top:16px; }

        .evidence { display:grid; grid-template-columns:80px minmax(210px, .9fr) minmax(200px, 1.2fr) minmax(180px, .8fr); gap:20px; align-items:start; border-top:1px solid var(--line); padding:22px 0; }
        .evidence:last-child { border-bottom:1px solid var(--line); }
        .evidence-id { font:600 .72rem "IBM Plex Mono", monospace; color:var(--signal); }
        .evidence-title { font-weight:700; }
        .evidence-copy { color:var(--muted); font-size:.9rem; }
        .evidence-value { font:600 1.15rem "IBM Plex Mono", monospace; }
        .evidence-value small { display:block; color:var(--muted); font:400 .72rem "IBM Plex Sans", sans-serif; margin-top:5px; }

        .attack-shell { background:var(--ink); color:#f7f5ed; padding:clamp(24px,5vw,52px); margin-top:22px; border-radius:2px; }
        .attack-shell h3 { color:#fff; font-size:clamp(2rem,5vw,4rem); line-height:.95; margin:12px 0 18px; max-width:850px; }
        .attack-shell p { color:#bec8c3; max-width:780px; }
        .attack-number { color:var(--acid); font:600 clamp(2.5rem,7vw,5.5rem) "IBM Plex Mono", monospace; line-height:1; margin:28px 0 8px; }
        .attack-label { color:#f7f5ed; font-size:1rem; }
        .attack-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:#53605b; margin-top:30px; }
        .attack-cell { background:#25302d; padding:18px; }
        .attack-cell span { color:#aebbb5; display:block; font-size:.76rem; }
        .attack-cell strong { color:#fff; display:block; margin-top:6px; font-family:"IBM Plex Mono",monospace; }

        .objection { display:grid; grid-template-columns:88px minmax(180px,.8fr) minmax(260px,1.4fr) 150px; gap:18px; border-top:1px solid var(--line); padding:20px 0; align-items:center; }
        .obj-id { font:600 .7rem "IBM Plex Mono",monospace; }
        .obj-title { font-weight:700; }
        .obj-copy { color:var(--muted); font-size:.88rem; }
        .status-open, .status-partial, .status-resolved { font:600 .67rem "IBM Plex Mono",monospace; text-transform:uppercase; padding:7px 9px; text-align:center; }
        .status-open { background:var(--signal-soft); color:#9d2f21; }
        .status-partial { background:#efe2b8; color:#695314; }
        .status-resolved { background:var(--green-soft); color:var(--green); }

        .decision-sheet { background:var(--sheet); border:1px solid var(--ink); padding:clamp(26px,5vw,52px); position:relative; }
        .decision-sheet:before { content:"PARECER"; position:absolute; right:20px; top:18px; color:var(--signal); border:2px solid var(--signal); padding:7px 10px; font:600 .68rem "IBM Plex Mono",monospace; transform:rotate(2deg); }
        .decision-sheet h2 { max-width:820px; margin:20px 0; }
        .decision-line { border-top:1px solid var(--line); padding:15px 0; display:grid; grid-template-columns:180px 1fr; gap:20px; }
        .decision-line span { color:var(--muted); font-size:.82rem; }
        .decision-line strong { font-size:.94rem; }

        .property-card { background:var(--sheet); border:1px solid var(--line); padding:22px; min-height:270px; }
        .property-card .rank { color:var(--signal); font:600 .7rem "IBM Plex Mono",monospace; }
        .property-card h4 { font-family:"Newsreader",serif; font-size:1.35rem; line-height:1.08; margin:15px 0; }
        .property-price { font:600 1.4rem "IBM Plex Mono",monospace; margin:16px 0 4px; }
        .property-meta { color:var(--muted); font-size:.84rem; }
        .property-status { border-top:1px solid var(--line); margin-top:16px; padding-top:13px; color:var(--signal); font:600 .68rem "IBM Plex Mono",monospace; text-transform:uppercase; }

        .method-note { border-left:3px solid var(--ink); padding:2px 0 2px 18px; color:var(--muted); font-size:.9rem; }
        .stButton > button { width:100%; min-height:56px; border-radius:0; border:1px solid var(--ink); background:var(--acid); color:var(--ink); font:700 .82rem "IBM Plex Mono",monospace; letter-spacing:.05em; }
        .stButton > button:hover { background:var(--ink); color:var(--acid); border-color:var(--ink); }
        [data-testid="stSlider"] { max-width:620px; }

        @media (max-width: 760px) {
            .block-container { padding-left:1rem; padding-right:1rem; }
            .case-bar { align-items:flex-start; flex-direction:column; gap:5px; }
            .hero h1 { font-size:3.6rem; }
            .evidence, .objection { grid-template-columns:1fr; gap:8px; }
            .attack-grid { grid-template-columns:1fr; }
            .decision-line { grid-template-columns:1fr; gap:5px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _build_case(occupancy_rate: float) -> dict[str, object]:
    assumptions = DecisionAssumptions(occupancy_rate=occupancy_rate)
    return build_decision_data(DATA_DIR, assumptions)


def _money(value: float, compact: bool = False) -> str:
    if pd.isna(value):
        return "n/d"
    if compact and abs(value) >= 1_000_000:
        return f"R$ {value / 1_000_000:.2f} mi".replace(".", ",")
    if compact and abs(value) >= 1_000:
        return f"R$ {value / 1_000:.0f} mil".replace(".", ",")
    return f"R$ {value:,.0f}".replace(",", ".")


def _percent(value: float, decimals: int = 1) -> str:
    if pd.isna(value):
        return "n/d"
    return f"{value * 100:.{decimals}f}%".replace(".", ",")


def _segment_name(segment: pd.Series) -> str:
    return f"{segment['suburb']} · {segment['profile']}"


def _section_rule(number: str, title: str, right: str = "") -> None:
    st.markdown(
        f'<div class="section section-rule"><span>{number} · {escape(title)}</span><span>{escape(right)}</span></div>',
        unsafe_allow_html=True,
    )


def _render_duel_card(segment: pd.Series, role: str, winner: bool) -> None:
    css_class = "challenger" if role == "Desafiante calculado" else "thesis"
    winner_tag = '<div class="winner-tag">lidera no cenário</div>' if winner else ""
    st.markdown(
        f"""
        <div class="duel-card {css_class}">
          <div class="duel-role">{escape(role)}</div>
          <h3>{escape(_segment_name(segment))}</h3>
          <div class="duel-metric"><span>Tarifa típica observada</span><strong>{_money(segment['observed_median_rate'])}</strong></div>
          <div class="duel-metric"><span>Preço pedido típico</span><strong>{_money(segment['median_asking_price'], compact=True)}</strong></div>
          <div class="duel-metric"><span>Retorno bruto de cenário</span><strong>{_percent(segment['gross_yield_scenario'])}</strong></div>
          <div class="duel-metric"><span>Base de evidência</span><strong>{int(segment['short_stay_listings'])} + {int(segment['sale_listings'])}</strong></div>
          {winner_tag}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_evidence(
    evidence_id: str, title: str, copy: str, value: str, nature: str
) -> None:
    st.markdown(
        f"""
        <div class="evidence">
          <div class="evidence-id">{escape(evidence_id)}</div>
          <div class="evidence-title">{escape(title)}</div>
          <div class="evidence-copy">{escape(copy)}</div>
          <div class="evidence-value">{escape(value)}<small>{escape(nature)}</small></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    _inject_styles()
    st.markdown(
        '<div class="case-bar"><span>Comitê de investimento · Caso 001</span><span>Itapema · corte de dados jan/2025</span></div>',
        unsafe_allow_html=True,
    )

    with st.expander("Contrato da decisão e premissas", expanded=False):
        st.markdown(
            "A decisão maximiza **retorno bruto de cenário** entre segmentos de "
            "apartamentos com pelo menos 20 anúncios de short stay precificados "
            "e 15 ofertas de venda válidas. A ocupação abaixo é uma premissa, não "
            "um resultado observado."
        )
        occupancy = st.slider(
            "Ocupação anual assumida para todos os segmentos",
            min_value=30.0,
            max_value=85.0,
            value=62.5,
            step=2.5,
            format="%.1f%%",
        )
    if "occupancy" not in locals():
        occupancy = 62.5

    try:
        case = _build_case(occupancy / 100)
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"Não foi possível construir a decisão: {exc}")
        st.stop()

    decision = case["decision"]
    thesis = decision["thesis"]
    challenger = decision["challenger"]
    winner = decision["winner"]
    reversal = decision["reversal"]
    shortlist = case["shortlist"]
    audit = case["audit"]
    robustness = case["robustness"]

    st.markdown(
        f"""
        <div class="hero">
          <div class="eyebrow">Quebre a tese</div>
          <h1>Uma decisão que tenta provar a si mesma errada.</h1>
          <p>A hipótese interna de compactos no Centro enfrenta o segmento mais eficiente encontrado sob o mesmo contrato. O sistema não pede confiança: expõe a evidência, procura a fragilidade e calcula o ponto de reversão.</p>
          <div class="verdict-stamp">Tese interna · {escape(str(decision['thesis_verdict']))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _section_rule("01", "O confronto", "um critério · dois caminhos")
    st.header("A tese interna contra o melhor desafiante elegível")
    gap = abs(float(challenger["gross_yield_scenario"] - thesis["gross_yield_scenario"]))
    gap_label = f"{gap * 100:.1f}".replace(".", ",")
    st.markdown(
        f"O desafiante é escolhido pelo motor, não pelo texto da apresentação. "
        f"No cenário de {_percent(occupancy / 100)} de ocupação comum, "
        f"**{escape(_segment_name(winner))}** lidera por **{gap_label} ponto(s) "
        "percentual(is)** de retorno bruto."
    )
    left, right = st.columns(2, gap="medium")
    with left:
        _render_duel_card(thesis, "Tese interna", _segment_name(winner) == _segment_name(thesis))
    with right:
        _render_duel_card(
            challenger,
            "Desafiante calculado",
            _segment_name(winner) == _segment_name(challenger),
        )

    _section_rule("02", "Peças de evidência", "observado ≠ calculado ≠ assumido")
    st.header("Cada afirmação deixa uma trilha")
    _render_evidence(
        "E-01 · MERCADO",
        "Tarifa anunciada",
        f"Mediana por anúncio após manter a captura mais recente de cada data de estadia. Janela de {audit['stay_date_min']:%d/%m} a {audit['stay_date_max']:%d/%m/%Y}.",
        f"{_money(thesis['observed_median_rate'])} vs {_money(challenger['observed_median_rate'])}",
        "OBSERVADO · Price_AV",
    )
    _render_evidence(
        "E-02 · AQUISIÇÃO",
        "Preço pedido",
        "Mediana de apartamentos comparáveis após remover IDs repetidos, republicações idênticas e erros evidentes de área ou preço por m².",
        f"{_money(thesis['median_asking_price'], True)} vs {_money(challenger['median_asking_price'], True)}",
        "OBSERVADO · VivaReal",
    )
    _render_evidence(
        "E-03 · CENÁRIO",
        "Eficiência do capital",
        f"Tarifa típica × 365 × {_percent(occupancy / 100)} de ocupação, dividida pelo preço pedido típico. Não representa receita realizada.",
        f"{_percent(thesis['gross_yield_scenario'])} vs {_percent(challenger['gross_yield_scenario'])}",
        "CALCULADO + PREMISSA",
    )
    _render_evidence(
        "E-04 · ROBUSTEZ",
        "Vencedor estável",
        "A comparação usa capturas alternativas, republicações e conflitos de bairro. Um tratamento fica inconclusivo porque a tese não alcança o corte amostral.",
        f"{int((robustness['winner'] == _segment_name(winner)).sum())}/{int(robustness['pair_eligible'].sum())} testes elegíveis",
        "TESTE DETERMINÍSTICO",
    )

    _section_rule("03", "Ataque mínimo", "a aplicação procura a falha")
    st.header("Qual é a forma mais fácil de derrubar a recomendação?")
    st.write(
        "Em vez de esconder a incerteza atrás de uma nota de confiança, o motor "
        "procura a menor mudança isolada que faria a tese alternativa empatar."
    )
    if st.button("TENTAR QUEBRAR A RECOMENDAÇÃO", type="primary"):
        st.session_state["reveal_attack"] = True

    if st.session_state.get("reveal_attack", False):
        minimum = reversal["minimum_attack"]
        st.markdown(
            f"""
            <div class="attack-shell">
              <div class="kicker">Fragilidade encontrada</div>
              <h3>A menor ruptura encontrada está na tarifa do vencedor.</h3>
              <div class="attack-number">{_percent(abs(minimum['display_change']))}</div>
              <div class="attack-label">de queda na tarifa típica de {escape(reversal['winner'])} leva a decisão ao empate.</div>
              <div class="attack-grid">
                <div class="attack-cell"><span>Ocupação do vencedor no empate</span><strong>{_percent(reversal['winner_occupancy_at_tie'])}</strong></div>
                <div class="attack-cell"><span>Queda absoluta de ocupação</span><strong>{str(round(reversal['occupancy_drop_percentage_points'], 1)).replace('.', ',')} p.p.</strong></div>
                <div class="attack-cell"><span>Preço máximo do vencedor</span><strong>{_money(reversal['winner_max_asking_price'], True)}</strong></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(
            "Ataques de uma variável por vez. Empate não significa preferência automática pela alternativa."
        )

    _section_rule("04", "Contraditório", "objeções antes do capital")
    st.header("O auditor não opina. Ele protocola o que falta provar.")
    objections = [
        (
            "OBJ-01",
            "Ocupação não observada",
            "A base não contém reservas ou receita realizada. Validar histórico operacional comparável antes da compra.",
            "ABERTA",
            "status-open",
        ),
        (
            "OBJ-02",
            "Preço não transacionado",
            "O VivaReal informa preço pedido. Confirmar disponibilidade, estágio da obra e margem de negociação.",
            "ABERTA",
            "status-open",
        ),
        (
            "OBJ-03",
            "Janela sazonal curta",
            "As tarifas cobrem 105 dias entre verão e início da baixa temporada; anualização é apenas cenário.",
            "PARCIAL",
            "status-partial",
        ),
        (
            "OBJ-04",
            "Classificação de bairro",
            f"O mesmo vencedor aparece nos {int(robustness['pair_eligible'].sum())} tratamentos elegíveis, mas a tese perde o corte amostral ao excluir divergências entre campo e URL.",
            "PARCIAL",
            "status-partial",
        ),
    ]
    for obj_id, title, copy, status, css_class in objections:
        st.markdown(
            f"""
            <div class="objection">
              <div class="obj-id">{obj_id}</div>
              <div class="obj-title">{escape(title)}</div>
              <div class="obj-copy">{escape(copy)}</div>
              <div class="{css_class}">{status}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    _section_rule("05", "Parecer", "posição explícita · aprovação condicionada")
    verdict = str(decision["thesis_verdict"])
    if verdict.startswith("SUSTENTADA"):
        thesis_read = (
            "A tese de compactos no Centro é sustentada pelo critério de "
            "eficiência do capital no cenário-base."
        )
    elif verdict == "INCONCLUSIVA":
        thesis_read = (
            "A tese de compactos no Centro permanece inconclusiva porque os "
            "testes não sustentam uma liderança robusta."
        )
    else:
        thesis_read = (
            "A tese de compactos no Centro não é sustentada pelo critério de "
            "eficiência do capital no cenário-base. Isso não prova que compactos "
            "sejam ruins; mostra que o prêmio de tarifa observado não compensa o "
            "preço pedido típico quando comparado ao melhor desafiante elegível."
        )
    st.markdown(
        f"""
        <div class="decision-sheet">
          <div class="kicker">Decisão proposta</div>
          <h2>Diligenciar {escape(_segment_name(winner))}. Não autorizar a compra ainda.</h2>
          <p>{escape(thesis_read)}</p>
          <div class="decision-line"><span>Buy Box provisória</span><strong>{escape(_segment_name(winner))} · {winner['area_q25']:.0f} a {winner['area_q75']:.0f} m²</strong></div>
          <div class="decision-line"><span>Preço limite comparativo</span><strong>Até {_money(reversal['winner_max_asking_price'])}</strong></div>
          <div class="decision-line"><span>Condição para aprovar</span><strong>Validar ocupação, custos recorrentes, condição do imóvel e preço negociável.</strong></div>
          <div class="decision-line"><span>Força da evidência</span><strong>{escape(str(decision['evidence_strength']))}: resultado estável, mas receita e transação não são observadas.</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _section_rule("06", "Fila de diligência", "imóveis não são recomendações automáticas")
    st.header("Candidatos que cabem na Buy Box")
    st.markdown(
        '<div class="method-note">A receita abaixo herda a tarifa típica do segmento, não uma previsão específica do imóvel. A ordenação usa menor preço pedido; custos ausentes nunca viram vantagem.</div>',
        unsafe_allow_html=True,
    )
    if shortlist.empty:
        st.warning("Nenhum anúncio atende simultaneamente à Buy Box e ao preço limite.")
    else:
        columns = st.columns(min(3, len(shortlist)), gap="medium")
        for index, (_, item) in enumerate(shortlist.head(3).iterrows()):
            with columns[index]:
                st.markdown(
                    f"""
                    <div class="property-card">
                      <div class="rank">DILIGÊNCIA {index + 1:02d}</div>
                      <h4>{escape(str(item['listing_title']))}</h4>
                      <div class="property-meta">{escape(str(item['suburb']))} · {item['usable_area']:.0f} m² · {item['bedrooms']:.0f} quartos · {item['parking_spaces']:.0f} vaga(s)</div>
                      <div class="property-price">{_money(item['sale_price'])}</div>
                      <div class="property-meta">{_percent(item['scenario_gross_yield'])} de retorno bruto no cenário</div>
                      <div class="property-status">{escape(str(item['readiness_status']))}<br>{escape(str(item['price_data_status']))}<br>{escape(str(item['cost_data_status']))}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.link_button("Abrir anúncio original", item["link_url"], width="stretch")

    with st.expander("Abrir memória técnica e evidências completas"):
        st.markdown("#### Cobertura e qualidade")
        st.write(
            f"A base contém {audit['airbnb_listings']:,} anúncios Airbnb; "
            f"{audit['priced_airbnb_listings']:,} possuem preços vinculáveis "
            f"({_percent(audit['price_coverage'])}). Há "
            f"{audit['repeated_listing_stay_dates']:,} pares anúncio/data recapturados; "
            "o cenário-base mantém a captura mais recente."
        )
        st.markdown("#### Testes de robustez")
        robustness_display = robustness.copy()
        robustness_display["thesis_yield"] *= 100
        robustness_display["challenger_yield"] *= 100
        st.dataframe(robustness_display, hide_index=True, width="stretch")
        st.markdown("#### Segmentos")
        evidence = case["metrics"].loc[
            case["metrics"]["evidence_eligible"],
            [
                "suburb",
                "profile",
                "short_stay_listings",
                "sale_listings",
                "price_coverage",
                "observed_median_rate",
                "median_asking_price",
                "gross_yield_scenario",
            ],
        ].copy()
        st.dataframe(evidence, hide_index=True, width="stretch")

    st.markdown("---")
    st.caption(
        "Quebre a Tese · Decisão baseada no snapshot oficial. IA apoiou formulação, crítica e comunicação; nenhum número desta interface é calculado por LLM."
    )


if __name__ == "__main__":
    main()
