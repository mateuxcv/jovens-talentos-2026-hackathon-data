"""Revenue-centric Streamlit interface for the Itapema investment decision."""

from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from src.engine import (
    DecisionAssumptions,
    build_acquisition_shortlist,
    build_decision_data,
    evaluate_duel,
)

DATA_DIR = Path(__file__).parent / "data"

SOURCE_VIEWS = {
    "Anúncios do Airbnb": {
        "file": "Details_Itapema.csv",
        "description": "Características publicadas dos imóveis de short stay.",
        "columns": {
            "airbnb_listing_id": "ID do anúncio",
            "ad_name": "Título",
            "listing_type": "Tipo",
            "number_of_bedrooms": "Quartos",
            "number_of_guests": "Hóspedes",
            "number_of_reviews": "Avaliações",
            "star_rating": "Nota",
            "url": "Link original",
        },
    },
    "Tarifas anunciadas": {
        "file": "Price_AV_Itapema.csv",
        "description": "Preço anunciado por imóvel, data de estadia e captura.",
        "columns": {
            "airbnb_listing_id": "ID do anúncio",
            "date": "Data da estadia",
            "price": "Tarifa anunciada",
            "aquisition_date": "Data da captura",
        },
    },
    "Localização": {
        "file": "Mesh_Ids_Data_Itapema.csv",
        "description": "Bairro e coordenadas associados aos anúncios do Airbnb.",
        "columns": {
            "airbnb_listing_id": "ID do anúncio",
            "suburb": "Bairro",
            "latitude": "Latitude",
            "longitude": "Longitude",
            "city": "Cidade",
        },
    },
    "Anfitriões": {
        "file": "Hosts_ids_Itapema.csv",
        "description": "Experiência, avaliações e atributos dos anfitriões.",
        "columns": {
            "owner_id": "ID do anfitrião",
            "owner": "Anfitrião",
            "is_superhost": "Superhost",
            "number_of_reviews_host": "Avaliações",
            "star_rating_host": "Nota",
            "years_host": "Anos como host",
        },
    },
    "Imóveis à venda": {
        "file": "VivaReal_Itapema.csv",
        "description": "Ofertas de aquisição publicadas no VivaReal.",
        "columns": {
            "listing_id": "ID do anúncio",
            "listing_title": "Imóvel",
            "suburb": "Bairro informado",
            "bedrooms": "Quartos",
            "usable_area": "Área útil",
            "sale_price": "Preço pedido",
            "monthly_condo_fee": "Condomínio mensal",
            "yearly_iptu": "IPTU anual",
            "link_url": "Link original",
        },
    },
}

st.set_page_config(
    page_title="Investment OS | Itapema",
    page_icon="▰",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def _inject_styles() -> None:
    st.html(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600&family=Space+Grotesk:wght@400;500;600;700&display=swap');

        :root {
            --canvas: #eef1ee;
            --surface: #ffffff;
            --ink: #0d1718;
            --muted: #637072;
            --line: #d6dcda;
            --lime: #c8f25c;
            --teal: #0c7569;
            --red: #c74735;
            --red-soft: #f8e5e1;
            --amber: #9a6912;
            --amber-soft: #f5ebca;
        }
        html, body, [class*="css"] { font-family: "Space Grotesk", sans-serif; }
        .stApp { background: var(--canvas); color: var(--ink); }
        .block-container { max-width: 1180px; padding-top: 1.25rem; padding-bottom: 5rem; }
        h1, h2, h3, h4 { font-family: "Space Grotesk", sans-serif !important; color: var(--ink); letter-spacing: -.035em; }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"] { background: var(--ink); }
        [data-testid="stSidebar"] * { color: #f4f7f5 !important; }
        [data-testid="stSidebar"] [data-baseweb="slider"] * { color: var(--lime) !important; }

        .topbar {
            display:flex; justify-content:space-between; align-items:center; gap:18px;
            background:var(--ink); color:#fff; padding:15px 18px; margin-bottom:18px;
            font:600 .69rem "IBM Plex Mono",monospace; letter-spacing:.08em; text-transform:uppercase;
        }
        .topbar-brand { display:flex; align-items:center; gap:10px; }
        .topbar-mark { width:10px; height:10px; background:var(--lime); border-radius:2px; box-shadow:0 0 0 4px rgba(200,242,92,.12); }
        .topbar-meta { color:#aab6b3; display:flex; gap:22px; }

        .decision-command {
            background:var(--surface); border:1px solid var(--line); display:grid;
            grid-template-columns:minmax(0,1.5fr) minmax(300px,.7fr); margin-bottom:18px;
            box-shadow:0 8px 24px rgba(13,23,24,.05);
        }
        .command-main { padding:clamp(26px,5vw,54px); }
        .command-label { color:var(--teal); font:600 .72rem "IBM Plex Mono",monospace; letter-spacing:.09em; text-transform:uppercase; }
        .command-main h1 { font-size:clamp(2.4rem,5vw,4.7rem); line-height:.95; margin:16px 0 18px; max-width:760px; }
        .command-main p { color:var(--muted); font-size:1.02rem; max-width:700px; margin:0; }
        .command-actions { display:flex; flex-wrap:wrap; gap:10px; margin-top:24px; }
        .command-cta { display:inline-block; background:var(--lime); color:var(--ink) !important; border:1px solid var(--ink); padding:13px 16px; text-decoration:none !important; font:700 .69rem "IBM Plex Mono",monospace; text-transform:uppercase; }
        .command-cta.secondary { background:transparent; }
        .command-proof { color:var(--red); font:600 .66rem "IBM Plex Mono",monospace; text-transform:uppercase; margin-top:15px; }
        .command-value { background:var(--ink); color:#fff; padding:28px; display:flex; flex-direction:column; justify-content:center; }
        .value-row { padding:17px 0; border-bottom:1px solid #344042; }
        .value-row:last-child { border-bottom:0; }
        .value-row span { display:block; color:#98a8a5; font-size:.73rem; margin-bottom:6px; }
        .value-row strong { color:#fff; font:600 1.45rem "IBM Plex Mono",monospace; }
        .value-row strong.positive { color:var(--lime); }

        .stage-head { display:flex; align-items:center; gap:14px; margin:48px 0 18px; }
        .stage-index { display:flex; align-items:center; justify-content:center; width:34px; height:34px; background:var(--ink); color:var(--lime); font:600 .72rem "IBM Plex Mono",monospace; }
        .stage-copy strong { display:block; font-size:1.05rem; }
        .stage-copy span { display:block; color:var(--muted); font-size:.82rem; margin-top:2px; }

        .compare-shell { background:var(--surface); border:1px solid var(--line); }
        .compare-head, .compare-row { display:grid; grid-template-columns:minmax(180px,1.2fr) 1fr 1fr; gap:20px; align-items:center; }
        .compare-head { background:#f7f9f7; border-bottom:1px solid var(--line); padding:14px 20px; color:var(--muted); font:600 .67rem "IBM Plex Mono",monospace; text-transform:uppercase; }
        .compare-head .selected { color:var(--teal); }
        .compare-row { padding:17px 20px; border-bottom:1px solid var(--line); }
        .compare-row:last-child { border-bottom:0; }
        .compare-row span { color:var(--muted); font-size:.85rem; }
        .compare-row strong { font:600 .98rem "IBM Plex Mono",monospace; }
        .compare-row .lead { color:var(--teal); }

        .action-prompt { background:#e4e9e6; border:1px solid #cbd3d0; padding:18px 20px; margin:16px 0 10px; color:#43504d; font-size:.88rem; }
        .stButton > button { width:100%; min-height:54px; border-radius:3px; border:1px solid var(--ink); background:var(--surface); color:var(--ink); font:700 .76rem "IBM Plex Mono",monospace; letter-spacing:.05em; }
        .stButton > button:hover { background:var(--ink); color:var(--lime); border-color:var(--ink); }

        .evidence-ledger { background:var(--surface); border:1px solid var(--line); }
        .evidence-row { display:grid; grid-template-columns:82px minmax(150px,.7fr) minmax(260px,1.4fr) minmax(170px,.7fr); gap:18px; align-items:center; padding:19px 20px; border-bottom:1px solid var(--line); }
        .evidence-row:last-child { border-bottom:0; }
        .evidence-id { font:600 .68rem "IBM Plex Mono",monospace; color:var(--teal); }
        .evidence-title { font-weight:700; font-size:.9rem; }
        .evidence-copy { color:var(--muted); font-size:.82rem; }
        .evidence-result { text-align:right; font:600 .86rem "IBM Plex Mono",monospace; }
        .evidence-type { display:block; color:var(--muted); font:500 .62rem "IBM Plex Mono",monospace; margin-top:5px; text-transform:uppercase; }

        .gate-list { background:var(--surface); border:1px solid var(--line); }
        .gate-row { display:grid; grid-template-columns:84px minmax(180px,.8fr) minmax(280px,1.4fr) 125px; gap:18px; align-items:center; padding:18px 20px; border-bottom:1px solid var(--line); }
        .gate-row:last-child { border-bottom:0; }
        .gate-id { font:600 .67rem "IBM Plex Mono",monospace; color:var(--muted); }
        .gate-title { font-weight:700; font-size:.88rem; }
        .gate-copy { color:var(--muted); font-size:.81rem; }
        .state-open, .state-partial { padding:7px 9px; text-align:center; font:600 .63rem "IBM Plex Mono",monospace; text-transform:uppercase; }
        .state-open { background:var(--red-soft); color:var(--red); }
        .state-partial { background:var(--amber-soft); color:var(--amber); }

        .mandate-shell { max-width:860px; margin:44px auto 26px; }
        .mandate-label { color:var(--teal); font:600 .72rem "IBM Plex Mono",monospace; text-transform:uppercase; letter-spacing:.1em; }
        .mandate-shell h1 { font-size:clamp(2.5rem,6vw,5rem); line-height:.95; margin:15px 0; }
        .mandate-shell p { color:var(--muted); font-size:1.05rem; max-width:680px; }
        .mandate-rule { display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:var(--line); border:1px solid var(--line); margin:28px 0; }
        .mandate-rule div { background:var(--surface); padding:17px; }
        .mandate-rule span { display:block; color:var(--muted); font-size:.7rem; }
        .mandate-rule strong { display:block; margin-top:5px; font-size:.86rem; }
        .guide-strip { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:18px 0 24px; }
        .guide-step { background:var(--surface); border:1px solid var(--line); padding:14px; }
        .guide-step span { display:block; color:var(--teal); font:600 .65rem "IBM Plex Mono",monospace; }
        .guide-step strong { display:block; font-size:.82rem; margin-top:5px; }
        .hint { background:#f7f9f7; border-left:3px solid var(--lime); color:var(--muted); padding:12px 14px; margin:10px 0 16px; font-size:.81rem; }

        .lab-status { display:flex; justify-content:space-between; gap:18px; align-items:center; background:var(--ink); color:#fff; padding:18px 20px; margin-bottom:14px; }
        .lab-status span { color:#9bacaa; font-size:.74rem; }
        .lab-status strong { color:var(--lime); font:600 1rem "IBM Plex Mono",monospace; }
        .lab-card { background:var(--surface); border:1px solid var(--line); padding:20px; }
        .lab-card h4 { margin:0 0 4px; font-size:1.05rem; }
        .lab-card p { color:var(--muted); font-size:.78rem; margin-bottom:16px; }
        .lab-result { display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:var(--line); margin-top:14px; border:1px solid var(--line); }
        .lab-result div { background:var(--surface); padding:15px; }
        .lab-result span { display:block; color:var(--muted); font-size:.68rem; }
        .lab-result strong { display:block; margin-top:5px; font:600 .9rem "IBM Plex Mono",monospace; }

        .candidate-focus { background:var(--surface); border:2px solid var(--teal); padding:24px; margin-top:14px; }
        .candidate-focus h3 { font-size:1.35rem; margin:8px 0; }
        .candidate-focus p { color:var(--muted); font-size:.86rem; }
        .memo-preview { background:var(--ink); color:#fff; padding:28px; margin-top:20px; border-top:6px solid var(--lime); }
        .memo-preview h3 { color:#fff; font-size:1.55rem; margin:8px 0 18px; }
        .memo-preview p { color:#aebcb8; }
        .memo-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:#374341; }
        .memo-grid div { background:#1a2525; padding:16px; }
        .memo-grid span { display:block; color:#91a09c; font-size:.7rem; }
        .memo-grid strong { display:block; color:#fff; margin-top:5px; font:600 .86rem "IBM Plex Mono",monospace; }
        .memo-gates { color:#f2d4cd; font-size:.8rem; margin-top:16px; }
        .footnote { color:var(--muted); font-size:.76rem; border-top:1px solid var(--line); padding-top:18px; margin-top:42px; }
        div[data-testid="stExpander"] { background:var(--surface); border-color:var(--line); border-radius:3px; }

        @media (max-width: 760px) {
            .block-container { padding-left:1rem; padding-right:1rem; }
            .topbar { align-items:flex-start; flex-direction:column; }
            .topbar-meta { flex-direction:column; gap:4px; }
            .decision-command { grid-template-columns:1fr; }
            .compare-head, .compare-row { grid-template-columns:1fr 1fr; }
            .compare-head span:first-child, .compare-row span:first-child { grid-column:1/-1; }
            .evidence-row, .gate-row, .deal-row { grid-template-columns:1fr; gap:7px; }
            .evidence-result { text-align:left; }
            .mandate-rule, .lab-result, .guide-strip, .memo-grid { grid-template-columns:1fr; }
        }
        </style>
        """
    )


@st.cache_data(show_spinner=False)
def _build_case(
    occupancy_rate: float,
    max_typical_asking_price: float,
    min_short_stay_listings: int,
    min_sale_listings: int,
) -> dict[str, object]:
    return build_decision_data(
        DATA_DIR,
        DecisionAssumptions(
            occupancy_rate=occupancy_rate,
            max_typical_asking_price=max_typical_asking_price,
            min_short_stay_listings=min_short_stay_listings,
            min_sale_listings=min_sale_listings,
        ),
    )


@st.cache_data(show_spinner=False)
def _load_source(filename: str) -> pd.DataFrame:
    frame = pd.read_csv(DATA_DIR / filename, na_values=["<NA>"], low_memory=False)
    for column in ("airbnb_listing_id", "listing_id", "owner_id"):
        if column in frame:
            frame[column] = frame[column].astype("string")
    return frame


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


def _stage(number: str, title: str, subtitle: str) -> None:
    st.html(
        f"""
        <div class="stage-head">
          <div class="stage-index">{escape(number)}</div>
          <div class="stage-copy"><strong>{escape(title)}</strong><span>{escape(subtitle)}</span></div>
        </div>
        """
    )


def _evidence(
    evidence_id: str, title: str, copy: str, result: str, evidence_type: str
) -> str:
    return f"""
      <div class="evidence-row">
        <div class="evidence-id">{escape(evidence_id)}</div>
        <div class="evidence-title">{escape(title)}</div>
        <div class="evidence-copy">{escape(copy)}</div>
        <div class="evidence-result">{escape(result)}<span class="evidence-type">{escape(evidence_type)}</span></div>
      </div>
    """


def _gate(
    gate_id: str, title: str, copy: str, status: str, css_class: str
) -> str:
    return f"""
      <div class="gate-row">
        <div class="gate-id">{escape(gate_id)}</div>
        <div class="gate-title">{escape(title)}</div>
        <div class="gate-copy">{escape(copy)}</div>
        <div class="{css_class}">{escape(status)}</div>
      </div>
    """


def _set_widget_value(key: str, value: float) -> None:
    st.session_state[key] = value
    st.session_state.pop("approved_candidate", None)


def _invalidate_approval() -> None:
    st.session_state.pop("approved_candidate", None)


def _reset_mandate() -> None:
    for key in list(st.session_state):
        if key.startswith(("scenario_", "mandate_")):
            del st.session_state[key]
    st.session_state["analysis_ready"] = False


def _decision_memo(
    selected: pd.Series,
    leader_name: str,
    price_limit: float,
    budget: float,
    evidence_policy: str,
    duel: dict[str, object],
) -> str:
    return f"""# Registro de decisão · Itapema

## Decisão

Avançar o imóvel `{selected['listing_id']}` para diligência. Esta decisão não é
uma autorização de compra.

## Estratégia selecionada

- Perfil: {leader_name}
- Preço pedido do imóvel: {_money(selected['sale_price'])}
- Área útil: {selected['usable_area']:.0f} m²
- Receita bruta anualizada no cenário: {_money(selected['scenario_gross_revenue'])}
- Retorno bruto do imóvel no cenário: {_percent(selected['scenario_gross_yield'])}
- Preço comparativo máximo: {_money(price_limit)}
- Orçamento máximo do mandato: {_money(budget)}
- Política de evidência: {evidence_policy}

## Cenário aprovado

| Premissa | Tese interna | Desafiante |
|---|---:|---:|
| Ocupação | {_percent(duel['thesis']['occupancy'])} | {_percent(duel['challenger']['occupancy'])} |
| Tarifa no cenário | {_money(duel['thesis']['rate'])} | {_money(duel['challenger']['rate'])} |
| Preço comparativo | {_money(duel['thesis']['purchase_price'])} | {_money(duel['challenger']['purchase_price'])} |
| Retorno bruto | {_percent(duel['thesis']['gross_yield'])} | {_percent(duel['challenger']['gross_yield'])} |

## Gates pendentes

1. Validar ocupação e tarifa com histórico operacional comparável.
2. Confirmar disponibilidade e preço negociável.
3. Confirmar permissão para short stay, estágio, custos recorrentes, mobiliário
   e condição do imóvel.

## Fonte

Anúncio VivaReal: {selected['link_url']}

Gerado por regras determinísticas. Valores anunciados e premissas não equivalem
a desempenho realizado.
"""


def main() -> None:
    _inject_styles()
    st.html(
        '<div class="topbar"><div class="topbar-brand"><span class="topbar-mark"></span><span>Seazone Investment OS</span></div><div class="topbar-meta"><span>DECISÃO ITA-001</span><span>DADOS JAN/2025</span></div></div>'
    )

    if not st.session_state.get("analysis_ready", False):
        st.html(
            """
            <div class="mandate-shell">
              <div class="mandate-label">Novo mandato de aquisição</div>
              <h1>Qual decisão precisa caber no capital?</h1>
              <p>Defina os limites antes de ver o resultado. O motor confrontará a tese interna com todas as alternativas que passarem pelo mesmo contrato.</p>
              <div class="mandate-rule">
                <div><span>Objetivo</span><strong>Eficiência do capital</strong></div>
                <div><span>Mercado</span><strong>Itapema · apartamentos</strong></div>
                <div><span>Saída</span><strong>Perfil de compra + diligência</strong></div>
              </div>
              <div class="guide-strip">
                <div class="guide-step"><span>01</span><strong>Defina os limites</strong></div>
                <div class="guide-step"><span>02</span><strong>Compare as estratégias</strong></div>
                <div class="guide-step"><span>03</span><strong>Force a recomendação a falhar</strong></div>
                <div class="guide-step"><span>04</span><strong>Registre a decisão</strong></div>
              </div>
            </div>
            """
        )
        with st.form("mandate_form"):
            budget = st.number_input(
                "Capital máximo por imóvel",
                min_value=800_000,
                max_value=3_000_000,
                value=1_000_000,
                step=50_000,
                format="%d",
                help="Segmentos com preço típico acima deste valor ficam fora do mandato.",
            )
            occupancy = st.slider(
                "Ocupação anual para o cenário inicial",
                min_value=30.0,
                max_value=85.0,
                value=62.5,
                step=2.5,
                format="%.1f%%",
                help="É uma premissa inicial de comparação, não ocupação observada nos dados.",
            )
            evidence_policy = st.radio(
                "Política de evidência",
                options=["Padrão", "Conservadora"],
                horizontal=True,
                help="Conservadora exige 40 anúncios de short stay e 30 ofertas de venda por segmento.",
            )
            submitted = st.form_submit_button(
                "ANALISAR OPORTUNIDADES", use_container_width=True
            )
            st.caption(
                "Dica: comece com a política Padrão. Depois refaça o mandato em "
                "modo Conservador para verificar se a recomendação sobrevive."
            )
        if not submitted:
            st.stop()
        st.session_state["mandate_budget"] = float(budget)
        st.session_state["mandate_occupancy"] = float(occupancy)
        st.session_state["mandate_policy"] = evidence_policy
        st.session_state["analysis_ready"] = True
        st.rerun()

    budget = float(st.session_state["mandate_budget"])
    base_occupancy = float(st.session_state["mandate_occupancy"]) / 100
    conservative = st.session_state["mandate_policy"] == "Conservadora"
    min_short_stay = 40 if conservative else 20
    min_sales = 30 if conservative else 15
    assumptions = DecisionAssumptions(
        occupancy_rate=base_occupancy,
        max_typical_asking_price=budget,
        min_short_stay_listings=min_short_stay,
        min_sale_listings=min_sales,
    )

    try:
        case = _build_case(base_occupancy, budget, min_short_stay, min_sales)
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"O mandato não encontrou alternativas comparáveis: {exc}")
        if st.button("REDEFINIR MANDATO"):
            _reset_mandate()
            st.rerun()
        st.stop()

    decision = case["decision"]
    thesis = decision["thesis"]
    challenger = decision["challenger"]
    thesis_name = _segment_name(thesis)
    challenger_name = _segment_name(challenger)
    scenario_signature = f"{budget}:{min_short_stay}:{challenger_name}"
    if st.session_state.get("scenario_signature") != scenario_signature:
        st.session_state["scenario_signature"] = scenario_signature
        st.session_state["scenario_thesis_occupancy"] = base_occupancy * 100
        st.session_state["scenario_challenger_occupancy"] = base_occupancy * 100
        st.session_state["scenario_thesis_rate"] = 0.0
        st.session_state["scenario_challenger_rate"] = 0.0
        st.session_state["scenario_thesis_price"] = float(
            thesis["median_asking_price"]
        )
        st.session_state["scenario_challenger_price"] = float(
            challenger["median_asking_price"]
        )
        st.session_state["rejected_candidates"] = []
        st.session_state.pop("approved_candidate", None)

    duel = evaluate_duel(
        thesis,
        challenger,
        thesis_occupancy=st.session_state["scenario_thesis_occupancy"] / 100,
        challenger_occupancy=st.session_state["scenario_challenger_occupancy"] / 100,
        thesis_rate_change=st.session_state["scenario_thesis_rate"] / 100,
        challenger_rate_change=st.session_state["scenario_challenger_rate"] / 100,
        thesis_purchase_price=st.session_state["scenario_thesis_price"],
        challenger_purchase_price=st.session_state["scenario_challenger_price"],
    )
    economic_tie = duel["leader"] == "EMPATE"
    thesis_allowed = bool(thesis["evidence_eligible"]) and (
        duel["thesis"]["purchase_price"] <= budget
    )
    challenger_allowed = bool(challenger["evidence_eligible"]) and (
        duel["challenger"]["purchase_price"] <= budget
    )
    if economic_tie and thesis_allowed and challenger_allowed:
        scenario_winner = challenger
        winner_side, runner_side = "challenger", "thesis"
        operational_blocked = True
    elif duel["leader"] == thesis_name and thesis_allowed:
        scenario_winner = thesis
        winner_side, runner_side = "thesis", "challenger"
        operational_blocked = False
    elif challenger_allowed:
        scenario_winner = challenger
        winner_side, runner_side = "challenger", "thesis"
        operational_blocked = False
    elif thesis_allowed:
        scenario_winner = thesis
        winner_side, runner_side = "thesis", "challenger"
        operational_blocked = False
    else:
        scenario_winner = challenger
        winner_side, runner_side = "challenger", "thesis"
        operational_blocked = True
    winner_name = _segment_name(scenario_winner)
    winner_scenario = duel[winner_side]
    runner_scenario = duel[runner_side]
    price_limit = (
        winner_scenario["annualized_gross_revenue"] / runner_scenario["gross_yield"]
    )
    effective_price_limit = min(price_limit, budget)
    scenario_decision = {
        "winner": scenario_winner,
        "winner_scenario_gross_revenue": winner_scenario[
            "annualized_gross_revenue"
        ],
        "reversal": {"winner_max_asking_price": effective_price_limit},
    }
    shortlist = build_acquisition_shortlist(
        case["datasets"], scenario_decision, assumptions
    )
    rejected = set(st.session_state.get("rejected_candidates", []))
    available_shortlist = shortlist.loc[~shortlist["listing_id"].isin(rejected)]
    if operational_blocked:
        available_shortlist = available_shortlist.iloc[0:0]
    lead = available_shortlist.iloc[0] if not available_shortlist.empty else None
    lead_action = (
        '<a class="command-cta" href="#queue">Revisar candidato #1</a>'
        if lead is not None
        else ""
    )
    capital_gap = abs(
        float(
            duel["thesis"]["purchase_price"]
            - duel["challenger"]["purchase_price"]
        )
    )

    with st.sidebar:
        st.markdown("## Mandato ativo")
        st.metric("Capital máximo", _money(budget))
        st.metric("Ocupação inicial", _percent(base_occupancy))
        st.caption(f"Política de evidência: {st.session_state['mandate_policy']}")
        if st.button("REDEFINIR MANDATO", key="reset_mandate"):
            _reset_mandate()
            st.rerun()

    if not thesis_allowed and not challenger_allowed:
        leader_copy = "Nenhuma estratégia cabe no mandato atual."
    elif duel["leader"] == thesis_name and not thesis_allowed:
        leader_copy = (
            f"{thesis_name} lidera economicamente, mas está fora do mandato."
        )
    elif duel["leader"] == challenger_name and not challenger_allowed:
        leader_copy = (
            f"{challenger_name} lidera economicamente, mas está fora do mandato."
        )
    elif economic_tie:
        leader_copy = (
            "O cenário está empatado. Negocie preço ou valide operação antes de escolher."
        )
    else:
        leader_copy = f"{winner_name} lidera nas premissas atuais."
    eligible_return = (
        "n/d"
        if not thesis_allowed and not challenger_allowed
        else _percent(winner_scenario["gross_yield"])
    )
    st.html(
        f"""
        <div class="decision-command">
          <div class="command-main">
            <div class="command-label">Decisão recalculada em tempo real</div>
            <h1>{escape(leader_copy)}</h1>
            <p>O resultado responde ao mandato e ao laboratório de cenários. Nenhuma alteração abaixo modifica os dados observados.</p>
            <div class="command-actions">{lead_action}<a class="command-cta secondary" href="#lab">Abrir laboratório</a></div>
            <div class="command-proof">Evidência {escape(str(decision['evidence_strength']).lower())} · valores anunciados · cenário explícito</div>
          </div>
          <div class="command-value">
            <div class="value-row"><span>Retorno da estratégia elegível</span><strong class="positive">{eligible_return}</strong></div>
            <div class="value-row"><span>Vantagem atual</span><strong>{str(round(duel['yield_gap_percentage_points'], 1)).replace('.', ',')} p.p.</strong></div>
            <div class="value-row"><span>Capital máximo do mandato</span><strong>{_money(budget, True)}</strong></div>
          </div>
        </div>
        """
    )

    with st.expander("Como usar este workspace", expanded=False):
        st.markdown(
            "1. **Leia o confronto:** ele mostra por que uma estratégia lidera.\n"
            "2. **Teste sua dúvida:** altere ocupação, tarifa ou preço de cada lado.\n"
            "3. **Confira a fonte:** abra as evidências ou os CSVs originais.\n"
            "4. **Escolha um ativo:** rejeite-o ou registre seu avanço para diligência."
        )

    _stage("01", "Confronto atual", "O placar muda quando suas premissas mudam")
    st.html(
        f"""
        <div class="compare-shell">
          <div class="compare-head"><span>Métrica</span><span>Hipótese · {escape(thesis_name)}</span><span>Desafiante · {escape(challenger_name)}</span></div>
          <div class="compare-row"><span>Tarifa no cenário</span><strong>{_money(duel['thesis']['rate'])}</strong><strong>{_money(duel['challenger']['rate'])}</strong></div>
          <div class="compare-row"><span>Ocupação assumida</span><strong>{_percent(duel['thesis']['occupancy'])}</strong><strong>{_percent(duel['challenger']['occupancy'])}</strong></div>
          <div class="compare-row"><span>Preço de aquisição</span><strong>{_money(duel['thesis']['purchase_price'], True)}</strong><strong>{_money(duel['challenger']['purchase_price'], True)}</strong></div>
          <div class="compare-row"><span>Receita bruta anualizada</span><strong>{_money(duel['thesis']['annualized_gross_revenue'])}</strong><strong>{_money(duel['challenger']['annualized_gross_revenue'])}</strong></div>
          <div class="compare-row"><span>Retorno bruto</span><strong>{_percent(duel['thesis']['gross_yield'])}</strong><strong>{_percent(duel['challenger']['gross_yield'])}</strong></div>
        </div>
        <div class="action-prompt"><strong>Leitura:</strong> diferença de {str(round(duel['yield_gap_percentage_points'], 1)).replace('.', ',')} p.p. e {_money(capital_gap, True)} entre os preços usados no cenário.</div>
        """
    )

    st.html('<div id="lab"></div>')
    _stage("02", "Laboratório de cenário", "Tente fazer a recomendação perder")
    st.html(
        '<div class="hint"><strong>Dica:</strong> use o botão de choque automático para encontrar o empate ou mova os controles para testar uma hipótese própria. Cada lado pode ter premissas diferentes.</div>'
    )
    left, right = st.columns(2, gap="medium")
    with left:
        st.markdown(f"#### Hipótese: {thesis_name}")
        st.slider(
            "Ocupação da hipótese",
            30.0,
            90.0,
            step=1.0,
            key="scenario_thesis_occupancy",
            on_change=_invalidate_approval,
            help="Percentual de noites do ano assumidas como ocupadas para compactos no Centro.",
        )
        st.slider(
            "Choque na tarifa da hipótese",
            -30.0,
            30.0,
            step=1.0,
            format="%.0f%%",
            key="scenario_thesis_rate",
            on_change=_invalidate_approval,
            help="Ajuste percentual sobre a tarifa mediana observada, sem alterar o dado original.",
        )
        st.number_input(
            "Preço da hipótese",
            min_value=100_000.0,
            max_value=3_000_000.0,
            step=25_000.0,
            key="scenario_thesis_price",
            on_change=_invalidate_approval,
            help="Preço de aquisição que você quer testar para a hipótese interna.",
        )
    with right:
        st.markdown(f"#### Desafiante: {challenger_name}")
        st.slider(
            "Ocupação do desafiante",
            30.0,
            90.0,
            step=1.0,
            key="scenario_challenger_occupancy",
            on_change=_invalidate_approval,
            help="Percentual de noites do ano assumidas como ocupadas para o desafiante.",
        )
        st.slider(
            "Choque na tarifa do desafiante",
            -30.0,
            30.0,
            step=1.0,
            format="%.0f%%",
            key="scenario_challenger_rate",
            on_change=_invalidate_approval,
            help="Ajuste percentual sobre a tarifa mediana observada, sem alterar o dado original.",
        )
        st.number_input(
            "Preço do desafiante",
            min_value=100_000.0,
            max_value=3_000_000.0,
            step=25_000.0,
            key="scenario_challenger_price",
            on_change=_invalidate_approval,
            help="Preço de aquisição que você quer testar para o desafiante.",
        )

    if duel["leader"] == thesis_name:
        shock_side, shock_runner_side = "thesis", "challenger"
    else:
        shock_side, shock_runner_side = "challenger", "thesis"
    current_winner_yield = float(duel[shock_side]["gross_yield"])
    current_runner_yield = float(duel[shock_runner_side]["gross_yield"])
    relative_shock = current_runner_yield / current_winner_yield - 1
    shock_key = f"scenario_{shock_side}_rate"
    current_rate_change = float(st.session_state[shock_key]) / 100
    new_rate_change = ((1 + current_rate_change) * (1 + relative_shock) - 1) * 100
    if st.button(
        "APLICAR MENOR CHOQUE AO VENCEDOR",
        on_click=_set_widget_value,
        args=(shock_key, new_rate_change),
        disabled=not -30 <= new_rate_change <= 30,
    ):
        pass
    if not -30 <= new_rate_change <= 30:
        st.caption(
            "O empate exige um choque fora do intervalo operacional de ±30% deste laboratório."
        )
    st.html(
        f"""
        <div class="lab-result">
          <div><span>Líder atual</span><strong>{escape(str(duel['leader']))}</strong></div>
          <div><span>Menor choque de tarifa</span><strong>{str(round(abs(relative_shock) * 100, 1)).replace('.', ',')}%</strong></div>
          <div><span>Preço limite efetivo</span><strong>{_money(effective_price_limit, True)}</strong></div>
        </div>
        """
    )

    _stage("03", "Evidência verificável", "Síntese na frente, fontes sob demanda")
    audit = case["audit"]
    robustness = case["robustness"]
    evidence_html = "".join(
        [
            _evidence(
                "EV-01",
                "Tarifa anunciada",
                f"Mediana por listing; janela {audit['stay_date_min']:%d/%m} a {audit['stay_date_max']:%d/%m/%Y}.",
                f"{_money(thesis['observed_median_rate'])} → {_money(challenger['observed_median_rate'])}",
                "observado · Price_AV",
            ),
            _evidence(
                "EV-02",
                "Preço pedido",
                "Mediana após filtros de plausibilidade e republicações prováveis.",
                f"{_money(thesis['median_asking_price'], True)} → {_money(challenger['median_asking_price'], True)}",
                "observado · VivaReal",
            ),
            _evidence(
                "EV-03",
                "Cobertura",
                "Percentual dos apartamentos do perfil que possuem tarifa vinculável.",
                f"{_percent(thesis['price_coverage'])} → {_percent(challenger['price_coverage'])}",
                "qualidade da evidência",
            ),
        ]
    )
    st.html(f'<div class="evidence-ledger">{evidence_html}</div>')

    with st.expander("Consultar ou baixar os dados originais"):
        source_name = st.selectbox(
            "Base",
            options=list(SOURCE_VIEWS),
            index=0,
        )
        source_config = SOURCE_VIEWS[source_name]
        source_frame = _load_source(source_config["file"])
        source_columns = {
            column: label
            for column, label in source_config["columns"].items()
            if column in source_frame
        }
        source_display = source_frame[list(source_columns)].rename(
            columns=source_columns
        )
        st.caption(
            f"{source_config['description']} {len(source_frame):,} registros; "
            "os primeiros 100 aparecem abaixo."
        )
        column_config: dict[str, object] = {}
        if "Link original" in source_display:
            column_config["Link original"] = st.column_config.LinkColumn(
                "Link original", display_text="Abrir"
            )
        st.dataframe(
            source_display.head(100),
            hide_index=True,
            use_container_width=True,
            column_config=column_config,
        )
        st.download_button(
            f"BAIXAR {source_config['file']}",
            data=(DATA_DIR / source_config["file"]).read_bytes(),
            file_name=source_config["file"],
            mime="text/csv",
            use_container_width=True,
        )

    _stage("04", "Gates de aprovação", "Pendências que impedem compra automática")
    gates_html = "".join(
        [
            _gate(
                "GATE-01",
                "Ocupação real",
                "Obter histórico operacional de comparáveis; a base não contém reservas.",
                "ABERTO",
                "state-open",
            ),
            _gate(
                "GATE-02",
                "Preço negociável",
                "Confirmar disponibilidade e proposta; VivaReal informa preço pedido.",
                "ABERTO",
                "state-open",
            ),
            _gate(
                "GATE-03",
                "Operação permitida",
                "Validar convenção, estágio, mobiliário e custos recorrentes.",
                "ABERTO",
                "state-open",
            ),
        ]
    )
    st.html(f'<div class="gate-list">{gates_html}</div>')

    st.html('<div id="queue"></div>')
    _stage("05", "Escolha um ativo", "Transforme análise em uma ação registrada")
    if available_shortlist.empty:
        st.warning("Não há candidatos restantes para este cenário e orçamento.")
    else:
        candidate_ids = available_shortlist["listing_id"].tolist()
        candidate_map = available_shortlist.set_index("listing_id")
        selected_id = st.radio(
            "Candidatos elegíveis",
            options=candidate_ids,
            format_func=lambda listing_id: (
                f"{listing_id} · {_money(candidate_map.loc[listing_id, 'sale_price'])} · "
                f"{candidate_map.loc[listing_id, 'usable_area']:.0f} m²"
            ),
            help="Selecione um imóvel para ver o resumo antes de registrar a decisão.",
        )
        selected = candidate_map.loc[selected_id].copy()
        selected["listing_id"] = selected_id
        st.html(
            f"""
            <div class="candidate-focus">
              <div class="command-label">Candidato selecionado</div>
              <h3>{escape(str(selected['listing_title']))}</h3>
              <p>{escape(str(selected['suburb']))} · {selected['usable_area']:.0f} m² · {_money(selected['sale_price'])} pedidos · {_percent(selected['scenario_gross_yield'])} de retorno bruto no cenário.</p>
              <div class="command-proof">{escape(str(selected['readiness_status']))} · {escape(str(selected['cost_data_status']))}</div>
            </div>
            """
        )
        action_open, action_reject, action_advance = st.columns(3)
        with action_open:
            st.link_button(
                "ABRIR ANÚNCIO ORIGINAL",
                selected["link_url"],
                use_container_width=True,
            )
        with action_reject:
            if st.button("REJEITAR E VER PRÓXIMO", use_container_width=True):
                st.session_state["rejected_candidates"] = [*rejected, selected_id]
                st.session_state.pop("approved_candidate", None)
                st.rerun()
        with action_advance:
            if st.button("AVANÇAR PARA DILIGÊNCIA", use_container_width=True):
                st.session_state["approved_candidate"] = selected_id

        if st.session_state.get("approved_candidate") == selected_id:
            memo = _decision_memo(
                selected,
                winner_name,
                effective_price_limit,
                budget,
                st.session_state["mandate_policy"],
                duel,
            )
            st.success(
                "Decisão registrada: candidato enviado para diligência. Compra permanece bloqueada pelos gates abertos."
            )
            st.html(
                f"""
                <div class="memo-preview">
                  <div class="command-label">Prévia da decisão registrada</div>
                  <h3>{escape(str(selected['listing_title']))}</h3>
                  <p>{escape(winner_name)} · candidato {escape(str(selected_id))}</p>
                  <div class="memo-grid">
                    <div><span>Preço pedido</span><strong>{_money(selected['sale_price'])}</strong></div>
                    <div><span>Retorno bruto do imóvel</span><strong>{_percent(selected['scenario_gross_yield'])}</strong></div>
                    <div><span>Limite efetivo</span><strong>{_money(effective_price_limit)}</strong></div>
                  </div>
                  <div class="memo-gates">3 gates permanecem abertos: operação, preço negociável e desempenho realizado.</div>
                </div>
                """
            )
            with st.expander("Visualizar memorando completo", expanded=True):
                st.markdown(memo)
            st.download_button(
                "BAIXAR MEMORANDO DA DECISÃO",
                data=memo,
                file_name=f"diligencia-{selected_id}.md",
                mime="text/markdown",
                use_container_width=True,
            )

    with st.expander("Ver auditoria técnica completa"):
        robustness_display = robustness.copy()
        robustness_display["thesis_yield"] *= 100
        robustness_display["challenger_yield"] *= 100
        st.dataframe(
            robustness_display, hide_index=True, use_container_width=True
        )
        evidence = case["metrics"].loc[case["metrics"]["evidence_eligible"]].copy()
        st.dataframe(evidence, hide_index=True, use_container_width=True)

    st.html(
        '<div class="footnote">Decision support, not investment authorization. IA apoiou hipótese, crítica e comunicação; nenhum número é calculado por LLM.</div>'
    )


if __name__ == "__main__":
    main()
