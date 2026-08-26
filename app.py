"""Revenue-centric Streamlit interface for the Itapema investment decision."""

from __future__ import annotations

from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from src.engine import DecisionAssumptions, build_decision_data

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
            --teal-soft: #dff1ec;
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

        .break-result { background:var(--ink); color:#fff; padding:clamp(26px,5vw,48px); border-left:7px solid var(--lime); }
        .break-kicker { color:var(--lime); font:600 .7rem "IBM Plex Mono",monospace; letter-spacing:.1em; text-transform:uppercase; }
        .break-grid { display:grid; grid-template-columns:minmax(220px,.8fr) minmax(300px,1.4fr); gap:46px; align-items:end; margin-top:18px; }
        .break-number { color:#fff; font:600 clamp(3rem,8vw,6.5rem) "IBM Plex Mono",monospace; line-height:.9; }
        .break-copy h3 { color:#fff; font-size:1.55rem; margin:0 0 10px; }
        .break-copy p { color:#aebcb8; margin:0; }
        .break-details { display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:#374341; margin-top:30px; }
        .break-cell { background:#1a2525; padding:18px; }
        .break-cell span { display:block; color:#91a09c; font-size:.72rem; }
        .break-cell strong { display:block; color:#fff; font:600 .9rem "IBM Plex Mono",monospace; margin-top:6px; }

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

        .approval-bar { display:grid; grid-template-columns:minmax(230px,.8fr) minmax(320px,1.4fr); background:var(--teal); color:#fff; margin-top:16px; }
        .approval-status { padding:28px; border-right:1px solid rgba(255,255,255,.2); }
        .approval-status span { color:#aee0d5; font:600 .68rem "IBM Plex Mono",monospace; text-transform:uppercase; }
        .approval-status strong { display:block; color:#fff; font-size:1.45rem; margin-top:9px; }
        .approval-next { padding:28px; color:#d8efea; }
        .approval-next strong { display:block; color:#fff; margin-bottom:6px; }

        .deal-queue { background:var(--surface); border:1px solid var(--line); }
        .deal-row { display:grid; grid-template-columns:54px minmax(260px,1.4fr) 120px 120px minmax(190px,.8fr); gap:18px; align-items:center; padding:19px 20px; border-bottom:1px solid var(--line); }
        .deal-row:last-child { border-bottom:0; }
        .deal-rank { color:var(--teal); font:600 .7rem "IBM Plex Mono",monospace; }
        .deal-name { font-weight:700; font-size:.88rem; }
        .deal-name small { display:block; color:var(--muted); font-weight:400; margin-top:4px; }
        .deal-metric span { display:block; color:var(--muted); font-size:.68rem; }
        .deal-metric strong { font:600 .83rem "IBM Plex Mono",monospace; }
        .deal-flags { color:var(--red); font-size:.72rem; }
        .deal-link { display:inline-block; color:var(--ink) !important; text-decoration:none; border:1px solid var(--ink); padding:9px 11px; margin-top:9px; font:600 .65rem "IBM Plex Mono",monospace; text-transform:uppercase; }

        .footnote { color:var(--muted); font-size:.76rem; border-top:1px solid var(--line); padding-top:18px; margin-top:42px; }
        div[data-testid="stExpander"] { background:var(--surface); border-color:var(--line); border-radius:3px; }

        @media (max-width: 760px) {
            .block-container { padding-left:1rem; padding-right:1rem; }
            .topbar { align-items:flex-start; flex-direction:column; }
            .topbar-meta { flex-direction:column; gap:4px; }
            .decision-command, .break-grid, .approval-bar { grid-template-columns:1fr; }
            .compare-head, .compare-row { grid-template-columns:1fr 1fr; }
            .compare-head span:first-child, .compare-row span:first-child { grid-column:1/-1; }
            .evidence-row, .gate-row, .deal-row { grid-template-columns:1fr; gap:7px; }
            .evidence-result { text-align:left; }
            .break-details { grid-template-columns:1fr; }
            .approval-status { border-right:0; border-bottom:1px solid rgba(255,255,255,.2); }
        }
        </style>
        """
    )


@st.cache_data(show_spinner=False)
def _build_case(occupancy_rate: float) -> dict[str, object]:
    return build_decision_data(
        DATA_DIR, DecisionAssumptions(occupancy_rate=occupancy_rate)
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


def main() -> None:
    _inject_styles()

    with st.sidebar:
        st.markdown("## Cenário")
        st.caption("Premissas alteram o cenário, nunca os dados observados.")
        occupancy = st.slider(
            "Ocupação anual comum",
            min_value=30.0,
            max_value=85.0,
            value=62.5,
            step=2.5,
            format="%.1f%%",
        )
        st.divider()
        st.markdown("**Corte de evidência**")
        st.caption("20 anúncios precificados + 15 ofertas de venda por segmento")
        st.markdown("**Escopo**")
        st.caption("Apartamentos · Itapema · snapshot jan/2025")

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

    winner_name = _segment_name(winner)
    thesis_name = _segment_name(thesis)
    challenger_name = _segment_name(challenger)
    yield_gap = abs(
        float(challenger["gross_yield_scenario"] - thesis["gross_yield_scenario"])
    )
    capital_gap = float(thesis["median_asking_price"] - winner["median_asking_price"])
    revenue_gap = float(
        winner["annualized_gross_revenue_scenario"]
        - thesis["annualized_gross_revenue_scenario"]
    )
    lead = shortlist.iloc[0] if not shortlist.empty else None
    lead_action = (
        f'<a class="command-cta" href="{escape(str(lead["link_url"]))}" target="_blank">Abrir candidato #1</a>'
        if lead is not None
        else ""
    )

    st.html(
        f"""
        <div class="topbar">
          <div class="topbar-brand"><span class="topbar-mark"></span><span>Seazone Investment OS</span></div>
          <div class="topbar-meta"><span>CASE ITA-001</span><span>DATA JAN/2025</span><span>CENÁRIO {_percent(occupancy / 100)}</span></div>
        </div>
        <div class="decision-command">
          <div class="command-main">
            <div class="command-label">Próxima ação recomendada</div>
            <h1>Avançar {escape(winner_name)} para diligência.</h1>
            <p>Não é autorização de compra. É a rota com melhor eficiência de capital no cenário atual, sujeita aos gates operacionais abaixo.</p>
            <div class="command-actions">{lead_action}<a class="command-cta secondary" href="#downside">Testar downside primeiro</a></div>
            <div class="command-proof">Evidência limitada · valores anunciados · ocupação assumida</div>
          </div>
          <div class="command-value">
            <div class="value-row"><span>Capital pedido mediano menor</span><strong class="positive">{_money(capital_gap, True)}</strong></div>
            <div class="value-row"><span>Vantagem de retorno bruto de cenário</span><strong>+{str(round(yield_gap * 100, 1)).replace('.', ',')} p.p.</strong></div>
            <div class="value-row"><span>Walk-away price do segmento</span><strong>{_money(reversal['winner_max_asking_price'], True)}</strong></div>
          </div>
        </div>
        """
    )

    _stage("01", "Decisão em confronto", "A hipótese interna não recebe tratamento preferencial")
    st.html(
        f"""
        <div class="compare-shell">
          <div class="compare-head"><span>Métrica de decisão</span><span>Hipótese · {escape(thesis_name)}</span><span class="selected">Selecionado · {escape(challenger_name)}</span></div>
          <div class="compare-row"><span>Tarifa típica anunciada</span><strong>{_money(thesis['observed_median_rate'])}</strong><strong class="lead">{_money(challenger['observed_median_rate'])}</strong></div>
          <div class="compare-row"><span>Preço pedido típico</span><strong>{_money(thesis['median_asking_price'], True)}</strong><strong class="lead">{_money(challenger['median_asking_price'], True)}</strong></div>
          <div class="compare-row"><span>Receita bruta anualizada</span><strong>{_money(thesis['annualized_gross_revenue_scenario'])}</strong><strong class="lead">{_money(challenger['annualized_gross_revenue_scenario'])}</strong></div>
          <div class="compare-row"><span>Retorno bruto de cenário</span><strong>{_percent(thesis['gross_yield_scenario'])}</strong><strong class="lead">{_percent(challenger['gross_yield_scenario'])}</strong></div>
          <div class="compare-row"><span>Evidência short stay + venda</span><strong>{int(thesis['short_stay_listings'])} + {int(thesis['sale_listings'])}</strong><strong>{int(challenger['short_stay_listings'])} + {int(challenger['sale_listings'])}</strong></div>
        </div>
        <div class="action-prompt"><strong>Por que agir:</strong> o desafiante exige {_money(abs(capital_gap), True)} menos capital pedido mediano e projeta {_money(max(revenue_gap, 0))} a mais sob a ocupação assumida. Antes de avançar, tente destruir essa vantagem.</div>
        """
    )

    st.html('<div id="downside"></div>')
    if st.button("EXECUTAR DOWNSIDE TEST"):
        st.session_state["reveal_attack"] = True

    if st.session_state.get("reveal_attack", False):
        minimum = reversal["minimum_attack"]
        st.html(
            f"""
            <div class="break-result">
              <div class="break-kicker">Menor choque que elimina a liderança</div>
              <div class="break-grid">
                <div class="break-number">{_percent(abs(minimum['display_change']))}</div>
                <div class="break-copy"><h3>queda na tarifa típica de {escape(reversal['winner'])}</h3><p>Este é o ponto de empate com {escape(reversal['runner_up'])}. A recomendação é sensível o bastante para exigir validação operacional antes de comprometer capital.</p></div>
              </div>
              <div class="break-details">
                <div class="break-cell"><span>Ocupação no empate</span><strong>{_percent(reversal['winner_occupancy_at_tie'])}</strong></div>
                <div class="break-cell"><span>Queda de ocupação</span><strong>{str(round(reversal['occupancy_drop_percentage_points'], 1)).replace('.', ',')} p.p.</strong></div>
                <div class="break-cell"><span>Preço pedido limite</span><strong>{_money(reversal['winner_max_asking_price'], True)}</strong></div>
              </div>
            </div>
            """
        )

    _stage("02", "Trilha de evidências", "Promessa proporcional à prova disponível")
    evidence_html = "".join(
        [
            _evidence(
                "EV-01",
                "Tarifa anunciada",
                f"Mediana por listing após deduplicar data de estadia. Janela {audit['stay_date_min']:%d/%m} a {audit['stay_date_max']:%d/%m/%Y}.",
                f"{_money(thesis['observed_median_rate'])} → {_money(challenger['observed_median_rate'])}",
                "observado · Price_AV",
            ),
            _evidence(
                "EV-02",
                "Capital de entrada",
                "Preço pedido mediano após filtros de plausibilidade e republicações prováveis.",
                f"{_money(thesis['median_asking_price'], True)} → {_money(challenger['median_asking_price'], True)}",
                "observado · VivaReal",
            ),
            _evidence(
                "EV-03",
                "Retorno comparável",
                f"Tarifa × 365 × {_percent(occupancy / 100)} de ocupação comum ÷ preço pedido. Não é receita realizada.",
                f"{_percent(thesis['gross_yield_scenario'])} → {_percent(challenger['gross_yield_scenario'])}",
                "cálculo + premissa",
            ),
            _evidence(
                "EV-04",
                "Estabilidade",
                "Captura inicial, captura final e regra alternativa de republicação mantêm o vencedor; conflito de bairro torna um teste inelegível.",
                f"{int((robustness['winner'] == winner_name).sum())}/{int(robustness['pair_eligible'].sum())} elegíveis",
                "stress test de dados",
            ),
        ]
    )
    st.html(f'<div class="evidence-ledger">{evidence_html}</div>')

    _stage("03", "Dados originais", "Veja a fonte antes de aceitar a síntese")
    source_name = st.selectbox(
        "Escolha uma base para consultar",
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
    source_display = source_frame[list(source_columns)].rename(columns=source_columns)
    st.caption(
        f"{source_config['description']} {len(source_frame):,} registros no arquivo; "
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
        width="stretch",
        column_config=column_config,
    )
    st.download_button(
        f"BAIXAR {source_config['file']}",
        data=(DATA_DIR / source_config["file"]).read_bytes(),
        file_name=source_config["file"],
        mime="text/csv",
        width="stretch",
    )

    _stage("04", "Gates de aprovação", "O que bloqueia uma ordem de compra hoje")
    gates_html = "".join(
        [
            _gate(
                "GATE-01",
                "Ocupação real",
                "Obter histórico operacional de comparáveis. A base atual não contém reservas.",
                "ABERTO",
                "state-open",
            ),
            _gate(
                "GATE-02",
                "Preço negociável",
                "Confirmar disponibilidade e proposta. VivaReal informa somente preço pedido.",
                "ABERTO",
                "state-open",
            ),
            _gate(
                "GATE-03",
                "Operação permitida",
                "Validar convenção condominial, estágio da obra e custos recorrentes.",
                "ABERTO",
                "state-open",
            ),
            _gate(
                "GATE-04",
                "Qualidade da localização",
                "O resultado mantém direção, mas perde amostra ao excluir conflitos de bairro.",
                "PARCIAL",
                "state-partial",
            ),
        ]
    )
    st.html(f'<div class="gate-list">{gates_html}</div>')
    st.html(
        f"""
        <div class="approval-bar">
          <div class="approval-status"><span>Status do comitê</span><strong>Diligenciar, não comprar</strong></div>
          <div class="approval-next"><strong>Próxima ação</strong>Validar o primeiro candidato abaixo e só avançar se os três gates críticos forem fechados sem ultrapassar {_money(reversal['winner_max_asking_price'])}.</div>
        </div>
        """
    )

    st.html('<div id="queue"></div>')
    _stage("05", "Fila de diligência", "Menos pesquisa, próxima ação explícita")
    if shortlist.empty:
        st.warning("Nenhum anúncio atende simultaneamente à Buy Box e ao preço limite.")
    else:
        rows = []
        for index, (_, item) in enumerate(shortlist.head(5).iterrows(), start=1):
            rows.append(
                f"""
                <div class="deal-row">
                  <div class="deal-rank">#{index:02d}</div>
                  <div class="deal-name">{escape(str(item['listing_title']))}<small>{escape(str(item['suburb']))} · {item['usable_area']:.0f} m² · {item['bedrooms']:.0f}Q · {item['parking_spaces']:.0f} vaga(s)</small></div>
                  <div class="deal-metric"><span>Preço pedido</span><strong>{_money(item['sale_price'], True)}</strong></div>
                  <div class="deal-metric"><span>Retorno bruto</span><strong>{_percent(item['scenario_gross_yield'])}</strong></div>
                  <div class="deal-flags">{escape(str(item['readiness_status']))}<br>{escape(str(item['price_data_status']))}<br><a class="deal-link" href="{escape(str(item['link_url']))}" target="_blank">Abrir anúncio</a></div>
                </div>
                """
            )
        st.html(f'<div class="deal-queue">{"".join(rows)}</div>')
        st.caption(
            "A receita herda a tarifa típica do segmento, não uma previsão específica do imóvel. Preços muito abaixo da faixa típica são sinais de verificação, não vantagens assumidas."
        )

    with st.expander("Abrir metodologia e dados de auditoria"):
        st.markdown(
            f"""
            **Contrato:** apartamentos com pelo menos 20 anúncios de short stay
            precificados e 15 ofertas válidas. A base contém
            {audit['airbnb_listings']:,} anúncios Airbnb, mas somente
            {audit['priced_airbnb_listings']:,} possuem preços vinculáveis
            ({_percent(audit['price_coverage'])}).
            """
        )
        robustness_display = robustness.copy()
        robustness_display["thesis_yield"] *= 100
        robustness_display["challenger_yield"] *= 100
        st.dataframe(robustness_display, hide_index=True, width="stretch")
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

    st.html(
        '<div class="footnote">Decision support, not investment authorization. IA apoiou hipótese, crítica e comunicação; nenhum número é calculado por LLM.</div>'
    )


if __name__ == "__main__":
    main()
