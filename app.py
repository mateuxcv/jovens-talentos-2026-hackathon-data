"""Executive Streamlit interface for the Seazone Investment Decision Engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.ai_client import (
    AIClientError,
    LLMConfig,
    request_analysis,
    save_ai_log,
)
from src.engine import (
    InvestmentAssumptions,
    build_acquisition_shortlist,
    build_market_segments,
    load_datasets,
    run_sensitivity_analysis,
)
from src.prompts import AUDITOR_SYSTEM_PROMPT, build_auditor_prompt

DATA_DIR = Path(__file__).parent / "data"
STRATEGIC_SUBURBS = ("Morretes", "Centro", "Meia Praia")


st.set_page_config(
    page_title="Mesa de Convicção | Seazone IDE",
    page_icon="SZ",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

        :root {
            --ink: #102a2d;
            --muted: #607174;
            --paper: #f5f4ee;
            --card: #fffef9;
            --line: #d8ddd7;
            --teal: #087e72;
            --teal-dark: #075a55;
            --mint: #dceee8;
            --coral: #dc684f;
            --amber: #d99a2b;
        }

        html, body, [class*="css"] { font-family: "DM Sans", sans-serif; }
        .stApp { background: var(--paper); color: var(--ink); }
        h1, h2, h3 { font-family: "Manrope", sans-serif !important; letter-spacing: -0.035em; }
        h1 { color: var(--ink); }
        [data-testid="stSidebar"] { background: #102a2d; }
        [data-testid="stSidebar"] * { color: #f7f5ed !important; }
        [data-testid="stSidebar"] input { color: var(--ink) !important; }
        [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.16); }
        [data-testid="stMetric"] {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 14px;
            padding: 18px 20px;
            box-shadow: 0 8px 24px rgba(16, 42, 45, .05);
        }
        [data-testid="stMetricLabel"] { color: var(--muted); }
        [data-testid="stMetricValue"] { color: var(--ink); font-family: "Manrope", sans-serif; }
        .hero {
            border-top: 5px solid var(--teal);
            background: var(--ink);
            color: #f8f6ef;
            padding: clamp(24px, 4vw, 48px);
            border-radius: 4px 4px 22px 22px;
            margin-bottom: 28px;
            position: relative;
            overflow: hidden;
        }
        .hero:after {
            content: "";
            position: absolute;
            width: 220px;
            height: 220px;
            right: -70px;
            top: -90px;
            border: 42px solid rgba(92, 224, 195, .12);
            border-radius: 50%;
        }
        .eyebrow { color: #82d6c5; font-size: .75rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }
        .hero h1 { color: #fffef9; font-size: clamp(2rem, 5vw, 4.1rem); line-height: .98; margin: 12px 0 16px; max-width: 850px; }
        .hero p { color: #cad8d5; max-width: 760px; font-size: 1.05rem; margin: 0; }
        .verdict {
            display: inline-block;
            margin-top: 24px;
            padding: 8px 13px;
            background: rgba(220, 104, 79, .16);
            border: 1px solid #ef8e78;
            color: #ffc2b5;
            border-radius: 999px;
            font-size: .78rem;
            font-weight: 800;
            letter-spacing: .08em;
        }
        .section-kicker { color: var(--teal); font-size: .74rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; margin-top: 32px; }
        .strategy-card, .memo-card, .risk-card {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 16px;
            padding: 22px;
            min-height: 210px;
        }
        .strategy-card { border-top: 4px solid var(--teal); }
        .strategy-card h3 { margin: 5px 0 2px; }
        .strategy-role { color: var(--teal); font-weight: 800; font-size: .72rem; letter-spacing: .1em; text-transform: uppercase; }
        .strategy-number { font: 800 1.65rem "Manrope", sans-serif; color: var(--ink); margin: 18px 0 2px; }
        .strategy-detail { color: var(--muted); font-size: .84rem; }
        .memo-card { border-left: 5px solid var(--teal); }
        .risk-card { border-left: 5px solid var(--coral); }
        .callout {
            background: var(--mint);
            border: 1px solid #bedfd5;
            border-radius: 14px;
            padding: 18px 20px;
            color: var(--teal-dark);
            margin: 8px 0 18px;
        }
        .microcopy { color: var(--muted); font-size: .82rem; }
        .stButton > button {
            border-radius: 999px;
            border: 1px solid var(--teal);
            font-weight: 700;
        }
        @media (max-width: 700px) {
            .hero { padding: 24px 20px; border-radius: 0 0 16px 16px; }
            .hero h1 { font-size: 2.2rem; }
            .strategy-card, .memo-card, .risk-card { min-height: auto; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _load_data() -> dict[str, pd.DataFrame]:
    return load_datasets(DATA_DIR)


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


def _segment(metrics: pd.DataFrame, suburb: str, profile: str = "2Q") -> pd.Series:
    selected = metrics.loc[
        (metrics["suburb"] == suburb) & (metrics["profile"] == profile)
    ]
    if selected.empty:
        raise ValueError(f"Sem dados para {suburb}/{profile}")
    return selected.iloc[0]


def _strategy_card(suburb: str, role: str, row: pd.Series, description: str) -> None:
    st.markdown(
        f"""
        <div class="strategy-card">
            <div class="strategy-role">{role}</div>
            <h3>{suburb}</h3>
            <div class="strategy-number">{_percent(row["net_yield_negotiated"])} a.a.</div>
            <div class="strategy-detail">Yield líquido estimado sobre preço negociado</div>
            <p>{description}</p>
            <div class="strategy-detail">Ticket mediano {_money(row["negotiated_purchase_price"], compact=True)} · ADR {_money(row["median_adr"])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _build_ai_evidence(
    metrics: pd.DataFrame,
    shortlist: pd.DataFrame,
    assumptions: InvestmentAssumptions,
    sensitivity: pd.DataFrame,
) -> dict[str, Any]:
    selected_columns = [
        "suburb",
        "profile",
        "median_adr",
        "airbnb_listings",
        "median_asking_price",
        "sale_listings",
        "net_yield_asking",
        "net_yield_negotiated",
        "wacc_spread_negotiated",
    ]
    strategic = metrics.loc[
        metrics["suburb"].isin(STRATEGIC_SUBURBS)
        & metrics["profile"].isin(["Studio/1Q", "2Q"]),
        selected_columns,
    ].round(4)
    return {
        "veredito": "Tese de compactos/studios no Centro refutada; priorizar 2Q",
        "premissas": {
            "taxa_gestao": assumptions.management_fee_rate,
            "wacc": assumptions.wacc_rate,
            "desconto_negociacao": assumptions.negotiation_discount_rate,
            "vacancia": assumptions.vacancy_rate,
        },
        "segmentos": strategic.to_dict(orient="records"),
        "sensibilidade": dict(sensitivity.attrs),
        "shortlist": {
            "quantidade": len(shortlist),
            "custos_completos": int(shortlist["property_costs_complete"].sum()),
            "cap_rate_minimo": (
                round(float(shortlist["estimated_net_cap_rate"].min()), 4)
                if not shortlist.empty
                else None
            ),
            "cap_rate_maximo": (
                round(float(shortlist["estimated_net_cap_rate"].max()), 4)
                if not shortlist.empty
                else None
            ),
        },
        "alertas_do_dataset": [
            "snapshot estatico, sem transacoes realizadas",
            "disponibilidade nao equivale a ocupacao observada",
            "condominio e IPTU ausentes em parte dos anuncios",
        ],
    }


def _render_sidebar() -> tuple[InvestmentAssumptions, tuple[str, ...], float]:
    with st.sidebar:
        st.markdown("## Mesa de Convicção")
        st.caption("Premissas transparentes para o cenário de investimento")
        st.divider()
        management = st.slider(
            "Taxa de gestão Seazone",
            min_value=0,
            max_value=40,
            value=20,
            step=1,
            format="%d%%",
            help="Percentual da receita destinado à gestão da operação.",
        )
        wacc = st.slider(
            "Custo de oportunidade (WACC)",
            min_value=5,
            max_value=20,
            value=10,
            step=1,
            format="%d%%",
            help="Retorno anual mínimo esperado para justificar o capital.",
        )
        discount = st.slider(
            "Desconto de negociação",
            min_value=0,
            max_value=20,
            value=5,
            step=1,
            format="%d%%",
            help="Redução esperada sobre o preço anunciado no VivaReal.",
        )
        vacancy = st.slider(
            "Vacância projetada",
            min_value=10.0,
            max_value=70.0,
            value=37.5,
            step=0.5,
            format="%.1f%%",
            help="Parcela do ano em que a unidade permanece sem hóspedes.",
        )
        st.divider()
        st.markdown("### Mandato de aquisição")
        suburbs = st.multiselect(
            "Bairros elegíveis",
            options=["Centro", "Morretes"],
            default=["Centro", "Morretes"],
        )
        max_price = st.slider(
            "Preço pedido máximo",
            min_value=500_000,
            max_value=1_500_000,
            value=950_000,
            step=50_000,
            format="R$ %d",
        )
        st.caption("Perfil fixado pela tese: 2 quartos · 60 a 85 m²")
        st.divider()
        st.caption("Fonte: snapshot oficial do desafio Seazone · Itapema/SC")

    assumptions = InvestmentAssumptions(
        management_fee_rate=management / 100,
        wacc_rate=wacc / 100,
        negotiation_discount_rate=discount / 100,
        vacancy_rate=vacancy / 100,
    )
    return assumptions, tuple(suburbs), float(max_price)


def _render_hero() -> None:
    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">Seazone Investment Decision Engine · Itapema 2026</div>
            <h1>Capital com tese.<br>Não com intuição.</h1>
            <p>A Mesa de Convicção confronta receita de short-stay, preço de aquisição e risco para indicar onde o capital trabalha melhor.</p>
            <div class="verdict">TESE DE COMPACTOS NO CENTRO · REFUTADA</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_conviction(
    metrics: pd.DataFrame, assumptions: InvestmentAssumptions
) -> None:
    center_compact = _segment(metrics, "Centro", "Studio/1Q")
    center_two = _segment(metrics, "Centro")
    morretes_two = _segment(metrics, "Morretes")

    st.markdown(
        '<div class="section-kicker">01 · Decisão</div>', unsafe_allow_html=True
    )
    st.header("A Mesa de Convicção")
    cols = st.columns(4)
    cols[0].metric("Perfil recomendado", "2 quartos", "60 a 85 m²")
    cols[1].metric(
        "Líder de retorno",
        "Morretes",
        f"{_percent(morretes_two['net_yield_negotiated'])} líquido",
    )
    cols[2].metric(
        "Centro 2Q",
        _percent(center_two["net_yield_negotiated"]),
        f"ADR {_money(center_two['median_adr'])}",
    )
    compact_spread = center_compact["net_yield_negotiated"] - assumptions.wacc_rate
    cols[3].metric(
        "Compactos × WACC",
        _percent(center_compact["net_yield_negotiated"]),
        f"{compact_spread * 100:+.1f} p.p.",
        delta_color="normal",
    )

    st.markdown(
        """
        <div class="callout"><strong>Decisão recomendada:</strong> concentrar a busca em apartamentos de 2 quartos. Morretes lidera quando o objetivo é retorno; Centro permanece como alternativa de equilíbrio; Meia Praia atende uma estratégia de escala e liquidez.</div>
        """,
        unsafe_allow_html=True,
    )

    cards = st.columns(3)
    with cards[0]:
        _strategy_card(
            "Morretes",
            "Retorno",
            morretes_two,
            "Menor barreira de entrada e maior eficiência percentual do capital.",
        )
    with cards[1]:
        _strategy_card(
            "Centro",
            "Equilíbrio",
            center_two,
            "Demanda consistente e boa experiência, sem liderança em yield.",
        )
    with cards[2]:
        _strategy_card(
            "Meia Praia",
            "Escala",
            _segment(metrics, "Meia Praia"),
            "Maior mercado, com disciplina necessária no preço por metro quadrado.",
        )


def _render_viewpoint_and_audit(
    metrics: pd.DataFrame,
    shortlist: pd.DataFrame,
    assumptions: InvestmentAssumptions,
    sensitivity: pd.DataFrame,
) -> None:
    st.markdown(
        '<div class="section-kicker">02 · Choque de visões</div>',
        unsafe_allow_html=True,
    )
    st.header("Oportunidade versus risco")
    opportunity, risk = st.columns(2)
    morretes = _segment(metrics, "Morretes")
    center = _segment(metrics, "Centro")

    with opportunity:
        st.markdown(
            f"""
            <div class="memo-card">
                <div class="strategy-role">Tese de oportunidade · determinística</div>
                <h3>Comprar eficiência, não apenas diária alta</h3>
                <p>Morretes 2Q combina ADR mediana de <strong>{_money(morretes["median_adr"])}</strong> com ticket negociado mediano de <strong>{_money(morretes["negotiated_purchase_price"], compact=True)}</strong>. O resultado é yield líquido de <strong>{_percent(morretes["net_yield_negotiated"])}</strong>, contra <strong>{_percent(center["net_yield_negotiated"])}</strong> no Centro.</p>
                <p class="microcopy">Leitura: o preço de entrada compensa uma diária menor. Centro exige justificativa estratégica além do retorno percentual.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with risk:
        st.markdown(
            """
            <div class="risk-card">
                <div class="strategy-role" style="color:#b64c38">Auditoria cética</div>
                <h3>O retorno ainda precisa sobreviver ao mundo real</h3>
                <p>Disponibilidade não comprova ocupação, preço anunciado não comprova transação e custos ausentes podem elevar artificialmente o cap rate da shortlist.</p>
                <p class="microcopy">Use a IA para aprofundar esses riscos sem permitir que ela altere qualquer cálculo.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        config = LLMConfig.from_environment()
        if config is None:
            st.caption("IA opcional: configure `LLM_API_KEY` ou `OPENAI_API_KEY`.")
        if st.button(
            "Gerar parecer do auditor",
            disabled=config is None,
            width="stretch",
        ):
            evidence = _build_ai_evidence(metrics, shortlist, assumptions, sensitivity)
            prompt = build_auditor_prompt(evidence)
            try:
                with st.spinner("Auditando a tese sem recalcular os números..."):
                    response = request_analysis(AUDITOR_SYSTEM_PROMPT, prompt, config)
                    log_path = save_ai_log(AUDITOR_SYSTEM_PROMPT, prompt, response)
                st.session_state["audit_response"] = response
                st.session_state["audit_log"] = str(log_path)
            except AIClientError as exc:
                st.error(str(exc))
        if "audit_response" in st.session_state:
            st.markdown(st.session_state["audit_response"])
            st.caption(f"Parecer registrado em `{st.session_state['audit_log']}`")


def _render_sensitivity(sensitivity: pd.DataFrame) -> None:
    attrs = sensitivity.attrs
    break_even = attrs["break_even_price_change"]
    st.markdown(
        '<div class="section-kicker">03 · Limite da tese</div>', unsafe_allow_html=True
    )
    st.header("Ponto de invalidação")
    if break_even < 0:
        break_even_label = f"{abs(break_even) * 100:.1f}".replace(".", ",")
        message = (
            f"No cenário atual, Morretes já lidera em retorno. O preço mediano do "
            f"Centro precisaria cair **{break_even_label}%** para igualar "
            "o yield de Morretes."
        )
    else:
        break_even_label = f"{break_even * 100:.1f}".replace(".", ",")
        message = (
            f"Centro preserva a liderança até uma alta de **{break_even_label}%** "
            "no preço de aquisição; acima disso, Morretes assume a dianteira."
        )
    st.markdown(message)

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=sensitivity["price_change"] * 100,
            y=sensitivity["target_net_yield"] * 100,
            mode="lines",
            name="Centro 2Q",
            line={"color": "#087e72", "width": 4},
            hovertemplate="Preço: %{x:+.0f}%<br>Yield: %{y:.2f}%<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=sensitivity["price_change"] * 100,
            y=sensitivity["competitor_net_yield"] * 100,
            mode="lines",
            name="Morretes 2Q",
            line={"color": "#dc684f", "width": 3, "dash": "dash"},
            hovertemplate="Yield: %{y:.2f}%<extra></extra>",
        )
    )
    figure.add_vline(x=0, line_width=1, line_dash="dot", line_color="#849193")
    if -40 <= break_even * 100 <= 40:
        figure.add_vline(
            x=break_even * 100,
            line_width=2,
            line_dash="dot",
            line_color="#d99a2b",
            annotation_text="Ponto de equilíbrio",
            annotation_position="top",
        )
    figure.update_layout(
        height=420,
        margin={"l": 10, "r": 10, "t": 35, "b": 10},
        paper_bgcolor="#f5f4ee",
        plot_bgcolor="#fffef9",
        hovermode="x unified",
        legend={"orientation": "h", "y": 1.12, "x": 0},
        xaxis_title="Variação no preço de aquisição do Centro",
        yaxis_title="Yield líquido anual",
        xaxis_ticksuffix="%",
        yaxis_ticksuffix="%",
        font={"family": "DM Sans", "color": "#102a2d"},
    )
    st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})


def _render_shortlist(shortlist: pd.DataFrame) -> None:
    st.markdown(
        '<div class="section-kicker">04 · Execução</div>', unsafe_allow_html=True
    )
    st.header("Shortlist prática de aquisição")
    st.caption(
        "Imóveis reais aderentes ao mandato, ordenados pelo cap rate estimado. "
        "Custos ausentes permanecem sinalizados para diligência."
    )
    if shortlist.empty:
        st.warning(
            "Nenhum imóvel atende aos filtros atuais. Amplie o preço ou os bairros."
        )
        return

    complete = int(shortlist["property_costs_complete"].sum())
    cols = st.columns(3)
    cols[0].metric("Candidatos", str(len(shortlist)))
    cols[1].metric("Com custos completos", f"{complete}/{len(shortlist)}")
    cols[2].metric(
        "Melhor cap rate estimado",
        _percent(shortlist["estimated_net_cap_rate"].max()),
    )

    display = shortlist.rename(
        columns={
            "listing_id": "ID",
            "listing_title": "Imóvel",
            "link_url": "Anúncio",
            "suburb": "Bairro",
            "usable_area": "Área",
            "parking_spaces": "Vagas",
            "sale_price": "Preço pedido",
            "negotiated_purchase_price": "Preço negociado",
            "estimated_adr": "ADR estimada",
            "property_costs_complete": "Custos completos",
            "estimated_net_cap_rate": "Cap rate líquido",
        }
    )
    display["Cap rate líquido"] = display["Cap rate líquido"] * 100
    st.dataframe(
        display[
            [
                "ID",
                "Imóvel",
                "Bairro",
                "Área",
                "Vagas",
                "Preço pedido",
                "Preço negociado",
                "ADR estimada",
                "Cap rate líquido",
                "Custos completos",
                "Anúncio",
            ]
        ],
        hide_index=True,
        width="stretch",
        column_config={
            "Anúncio": st.column_config.LinkColumn(
                "Abrir anúncio", display_text="VivaReal"
            ),
            "Área": st.column_config.NumberColumn("Área", format="%.0f m²"),
            "Vagas": st.column_config.NumberColumn("Vagas", format="%.0f"),
            "Preço pedido": st.column_config.NumberColumn(
                "Preço pedido", format="R$ %.0f"
            ),
            "Preço negociado": st.column_config.NumberColumn(
                "Preço negociado", format="R$ %.0f"
            ),
            "ADR estimada": st.column_config.NumberColumn(
                "ADR estimada", format="R$ %.0f"
            ),
            "Cap rate líquido": st.column_config.NumberColumn(
                "Cap rate líquido", format="%.2f%%"
            ),
        },
    )
    st.caption(
        "O cap rate exibido desconta gestão, condomínio e IPTU quando informados. "
        "Não inclui reforma, mobiliário, manutenção extraordinária ou impostos operacionais."
    )


def main() -> None:
    _inject_styles()
    assumptions, selected_suburbs, max_price = _render_sidebar()
    _render_hero()
    if not selected_suburbs:
        st.warning("Selecione ao menos um bairro no mandato de aquisição.")
        st.stop()

    try:
        datasets = _load_data()
        metrics = build_market_segments(datasets, assumptions)
        sensitivity = run_sensitivity_analysis(metrics)
        shortlist = build_acquisition_shortlist(
            datasets,
            metrics,
            assumptions,
            suburbs=selected_suburbs,
            max_asking_price=max_price,
        )
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"Não foi possível construir a decisão: {exc}")
        st.stop()

    _render_conviction(metrics, assumptions)
    _render_viewpoint_and_audit(metrics, shortlist, assumptions, sensitivity)
    _render_sensitivity(sensitivity)
    _render_shortlist(shortlist)

    with st.expander("Ver evidências completas por segmento"):
        evidence = metrics.loc[
            metrics["suburb"].isin(STRATEGIC_SUBURBS),
            [
                "suburb",
                "profile",
                "airbnb_listings",
                "sale_listings",
                "median_adr",
                "median_asking_price",
                "median_price_per_sqm",
                "net_yield_asking",
                "net_yield_negotiated",
            ],
        ].copy()
        st.dataframe(evidence, hide_index=True, width="stretch")

    st.markdown("---")
    st.caption(
        "Seazone IDE · Snapshot de mercado, não garantia de retorno. "
        "Toda aquisição exige diligência comercial, jurídica e operacional."
    )


if __name__ == "__main__":
    main()
