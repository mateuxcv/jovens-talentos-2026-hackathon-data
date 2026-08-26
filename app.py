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
        .hero {
            background: var(--ink);
            color: #f8f6ef;
            padding: clamp(24px, 4vw, 48px);
            border-radius: 0 0 22px 22px;
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
        .decision-status {
            display: inline-block;
            margin-top: 24px;
            padding-top: 16px;
            border-top: 1px solid rgba(255,255,255,.22);
            color: #f8f6ef;
            font-size: .9rem;
            font-weight: 700;
        }
        .section-kicker { color: var(--teal); font-size: .74rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; margin-top: 32px; }
        .decision-question, .evidence-sheet, .risk-sheet {
            background: var(--card);
            border: 1px solid var(--line);
            border-radius: 14px;
        }
        .decision-question { padding: 24px 28px; margin-bottom: 12px; }
        .decision-question strong { color: var(--teal-dark); }
        .evidence-sheet { overflow: hidden; }
        .evidence-row {
            display: grid;
            grid-template-columns: 42px minmax(180px, 1.2fr) minmax(150px, .7fr) minmax(220px, 1.3fr);
            gap: 18px;
            align-items: center;
            padding: 22px 24px;
            border-bottom: 1px solid var(--line);
        }
        .evidence-row:last-child { border-bottom: 0; }
        .evidence-index { color: var(--teal); font: 800 .8rem "Manrope", sans-serif; }
        .evidence-copy strong { display: block; color: var(--ink); margin-bottom: 4px; }
        .evidence-copy span, .evidence-impact { color: var(--muted); font-size: .88rem; }
        .evidence-value { font: 800 1.35rem "Manrope", sans-serif; color: var(--ink); }
        .evidence-value span { display: block; color: var(--muted); font: 500 .76rem "DM Sans", sans-serif; margin-top: 3px; }
        .risk-sheet { padding: 22px 26px; border-left: 4px solid var(--coral); }
        .risk-sheet h3 { margin-top: 0; }
        .risk-sheet li { margin-bottom: 9px; color: var(--muted); }
        .recommendation {
            background: var(--ink);
            color: #f8f6ef;
            border-radius: 14px;
            padding: clamp(24px, 4vw, 42px);
            margin: 8px 0 22px;
        }
        .recommendation h2 { color: #fffef9; max-width: 850px; margin: 8px 0 16px; }
        .recommendation p { color: #cad8d5; max-width: 850px; }
        .recommendation-label { color: #82d6c5; font-size: .74rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
        .decision-rule { border-left: 3px solid var(--amber); padding-left: 16px; margin-top: 20px; }
        .decision-rule strong { color: #ffe0a3; }
        .shortlist-lead { border-left: 4px solid var(--teal); padding: 2px 0 2px 18px; margin: 16px 0 22px; }
        .microcopy { color: var(--muted); font-size: .82rem; }
        .stButton > button {
            border-radius: 999px;
            border: 1px solid var(--teal);
            font-weight: 700;
        }
        @media (max-width: 700px) {
            .hero { padding: 24px 20px; border-radius: 0 0 16px 16px; }
            .hero h1 { font-size: 2.2rem; }
            .evidence-row { grid-template-columns: 28px 1fr; gap: 10px; }
            .evidence-value, .evidence-impact { grid-column: 2; }
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
            <div class="eyebrow">Memorando de decisão · Itapema 2026</div>
            <h1>Onde o próximo real deve ser investido?</h1>
            <p>Uma leitura de aquisição para short-stay que conecta preço de entrada, capacidade de receita e risco operacional.</p>
            <div class="decision-status">Posição atual · Refutar compactos no Centro e avançar com apartamentos de 2 quartos</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_context(assumptions: InvestmentAssumptions) -> None:
    occupied_nights = assumptions.days_per_year * (1 - assumptions.vacancy_rate)
    st.markdown(
        '<div class="section-kicker">01 · Contexto da decisão</div>',
        unsafe_allow_html=True,
    )
    st.header("A escolha não é o bairro mais caro. É o uso mais eficiente do capital.")
    st.markdown(
        f"""
        <div class="decision-question">
            <strong>Decisão em pauta</strong><br>
            Selecionar o perfil de imóvel e a região capazes de superar um custo de capital de <strong>{_percent(assumptions.wacc_rate)}</strong>, considerando <strong>{occupied_nights:.0f} noites ocupadas por ano</strong>, gestão de <strong>{_percent(assumptions.management_fee_rate)}</strong> e negociação de <strong>{_percent(assumptions.negotiation_discount_rate)}</strong> sobre o preço anunciado.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        "Os controles ao lado mudam o cenário, não os dados observados. "
        "A recomendação é recalculada a cada alteração."
    )


def _render_conviction(
    metrics: pd.DataFrame, assumptions: InvestmentAssumptions
) -> None:
    center_compact = _segment(metrics, "Centro", "Studio/1Q")
    center_two = _segment(metrics, "Centro")
    morretes_two = _segment(metrics, "Morretes")
    meia_two = _segment(metrics, "Meia Praia")
    compact_spread = center_compact["net_yield_negotiated"] - assumptions.wacc_rate
    morretes_spread = morretes_two["net_yield_negotiated"] - assumptions.wacc_rate
    compact_gap = (
        morretes_two["net_yield_negotiated"] - center_compact["net_yield_negotiated"]
    )
    compact_wacc_read = "abaixo" if compact_spread < 0 else "acima"
    morretes_wacc_read = "supera" if morretes_spread >= 0 else "fica abaixo de"
    compact_gap_label = f"{compact_gap * 100:.1f}".replace(".", ",")
    morretes_spread_label = f"{abs(morretes_spread) * 100:.1f}".replace(".", ",")

    st.markdown(
        '<div class="section-kicker">02 · Sinais encontrados</div>',
        unsafe_allow_html=True,
    )
    st.header("Três sinais conduzem à decisão")
    st.markdown(
        f"""
        <div class="evidence-sheet">
            <div class="evidence-row">
                <div class="evidence-index">01</div>
                <div class="evidence-copy"><strong>Compactos no Centro perdem para a melhor alternativa</strong><span>{int(center_compact["airbnb_listings"])} anúncios de short-stay e {int(center_compact["sale_listings"])} imóveis à venda na amostra</span></div>
                <div class="evidence-value">{_percent(center_compact["net_yield_negotiated"])}<span>yield líquido vs. {_percent(assumptions.wacc_rate)} de WACC</span></div>
                <div class="evidence-impact">O retorno está {compact_wacc_read} do WACC e fica {compact_gap_label} p.p. atrás de Morretes 2Q. A tese interna perde prioridade econômica.</div>
            </div>
            <div class="evidence-row">
                <div class="evidence-index">02</div>
                <div class="evidence-copy"><strong>Morretes 2Q compra receita por menos</strong><span>ADR de {_money(morretes_two["median_adr"])} com ticket negociado mediano de {_money(morretes_two["negotiated_purchase_price"], compact=True)}</span></div>
                <div class="evidence-value">{_percent(morretes_two["net_yield_negotiated"])}<span>yield líquido estimado</span></div>
                <div class="evidence-impact">O retorno {morretes_wacc_read} o WACC por {morretes_spread_label} p.p. e apresenta a melhor assimetria entre entrada e receita.</div>
            </div>
            <div class="evidence-row">
                <div class="evidence-index">03</div>
                <div class="evidence-copy"><strong>Cada bairro cumpre um papel diferente</strong><span>Retorno, equilíbrio ou escala não devem ser tratados como a mesma decisão</span></div>
                <div class="evidence-value">2Q<span>perfil comum às três estratégias</span></div>
                <div class="evidence-impact">Morretes lidera em retorno ({_percent(morretes_two["net_yield_negotiated"])}); Centro equilibra demanda ({_percent(center_two["net_yield_negotiated"])}); Meia Praia oferece escala ({int(meia_two["airbnb_listings"])} listings precificados).</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_viewpoint_and_audit(
    metrics: pd.DataFrame,
    shortlist: pd.DataFrame,
    assumptions: InvestmentAssumptions,
    sensitivity: pd.DataFrame,
) -> None:
    st.markdown(
        '<div class="section-kicker">03 · Risco antes do aporte</div>',
        unsafe_allow_html=True,
    )
    st.header("O retorno projetado ainda não é uma autorização de compra")
    missing_costs = len(shortlist) - int(shortlist["property_costs_complete"].sum())
    costs_sentence = (
        f"{missing_costs} dos {len(shortlist)} candidatos atuais não informam "
        "simultaneamente condomínio e IPTU."
        if not shortlist.empty
        else "não há candidatos nos filtros atuais para avaliar a completude dos custos."
    )
    st.markdown(
        f"""
        <div class="risk-sheet">
            <h3>O que pode enfraquecer a recomendação</h3>
            <ul>
                <li><strong>Demanda inferida:</strong> as datas disponíveis no Airbnb não comprovam ocupação realizada.</li>
                <li><strong>Preço não transacionado:</strong> o VivaReal informa valor pedido; o desconto de negociação é uma premissa.</li>
                <li><strong>Custos incompletos:</strong> {costs_sentence}</li>
                <li><strong>Sazonalidade:</strong> uma fotografia concentrada do mercado não substitui uma série anual de reservas.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("Solicitar uma segunda leitura à IA"):
        st.write(
            "O auditor recebe apenas números calculados pelo motor e procura "
            "fragilidades que devem ser verificadas antes da aquisição."
        )
        config = LLMConfig.from_environment()
        if config is None:
            st.info(
                "Configure `LLM_API_KEY` ou `OPENAI_API_KEY` para ativar a análise."
            )
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
    st.subheader("A condição que pode mudar a escolha")
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


def _render_recommendation(
    metrics: pd.DataFrame,
    assumptions: InvestmentAssumptions,
    sensitivity: pd.DataFrame,
) -> None:
    morretes = _segment(metrics, "Morretes")
    center = _segment(metrics, "Centro")
    break_even = abs(sensitivity.attrs["break_even_price_change"])
    break_even_label = f"{break_even * 100:.1f}%".replace(".", ",")
    clears_wacc = morretes["net_yield_negotiated"] >= assumptions.wacc_rate
    recommendation_title = (
        "Avançar a diligência em apartamentos de 2 quartos em Morretes."
        if clears_wacc
        else "Não aprovar uma aquisição com as premissas atuais."
    )
    return_read = "supera" if clears_wacc else "fica abaixo de"
    st.markdown(
        '<div class="section-kicker">04 · Recomendação final</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div class="recommendation">
            <div class="recommendation-label">Decisão proposta ao comitê</div>
            <h2>{recommendation_title}</h2>
            <p>Morretes 2Q continua sendo a melhor alternativa relativa: entrega {_percent(morretes["net_yield_negotiated"])} de yield líquido estimado, {return_read} o WACC de {_percent(assumptions.wacc_rate)} e exige ticket mediano de {_money(morretes["negotiated_purchase_price"], compact=True)}.</p>
            <div class="decision-rule"><strong>Regra para exceções:</strong> considerar Centro 2Q quando liquidez e consistência de demanda justificarem o retorno de {_percent(center["net_yield_negotiated"])}, ou quando o preço de entrada ficar aproximadamente {break_even_label} abaixo da mediana atual.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "**Não fazer agora:** alocar o mandato principal em studios ou unidades "
        "de 1 quarto no Centro antes que o retorno supere o custo de capital e "
        "haja margem para custos não observados."
    )


def _render_shortlist(shortlist: pd.DataFrame) -> None:
    st.markdown(
        '<div class="section-kicker">05 · Próxima ação</div>', unsafe_allow_html=True
    )
    st.header("Transformar a tese em diligência")
    st.caption(
        "Imóveis reais aderentes ao mandato, ordenados pelo cap rate estimado. "
        "Custos ausentes permanecem sinalizados para diligência."
    )
    if shortlist.empty:
        st.warning(
            "Nenhum imóvel atende aos filtros atuais. Amplie o preço ou os bairros."
        )
        return

    complete_candidates = shortlist.loc[shortlist["property_costs_complete"]]
    lead = (
        complete_candidates.iloc[0]
        if not complete_candidates.empty
        else shortlist.iloc[0]
    )
    st.markdown(
        f"""
        <div class="shortlist-lead"><strong>Primeiro imóvel para diligência: ID {lead["listing_id"]}</strong><br>{lead["suburb"]} · {lead["usable_area"]:.0f} m² · {_money(lead["sale_price"])} pedidos · {_percent(lead["estimated_net_cap_rate"])} de cap rate estimado.<br><span class="microcopy">Prioridade operacional, não autorização automática de compra.</span></div>
        """,
        unsafe_allow_html=True,
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

    _render_context(assumptions)
    _render_conviction(metrics, assumptions)
    _render_viewpoint_and_audit(metrics, shortlist, assumptions, sensitivity)
    _render_sensitivity(sensitivity)
    _render_recommendation(metrics, assumptions, sensitivity)
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
