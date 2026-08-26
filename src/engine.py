"""Deterministic evidence and decision rules for the Itapema case.

The module deliberately separates observations from scenarios. Airbnb prices
are advertised nightly rates, VivaReal prices are asking prices, and occupancy
is an explicit user assumption. No LLM participates in these calculations.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

DATA_FILES = {
    "details": "Details_Itapema.csv",
    "prices": "Price_AV_Itapema.csv",
    "hosts": "Hosts_ids_Itapema.csv",
    "mesh": "Mesh_Ids_Data_Itapema.csv",
    "vivareal": "VivaReal_Itapema.csv",
}

REQUIRED_COLUMNS = {
    "details": {
        "airbnb_listing_id",
        "listing_type",
        "number_of_bedrooms",
        "owner_id",
        "aquisition_date",
    },
    "prices": {"airbnb_listing_id", "date", "price", "aquisition_date"},
    "hosts": {"owner_id", "host_snapshot_date"},
    "mesh": {"airbnb_listing_id", "suburb", "aquisition_date"},
    "vivareal": {
        "listing_id",
        "link_url",
        "listing_title",
        "listing_type",
        "sale_price",
        "yearly_iptu",
        "monthly_condo_fee",
        "usable_area",
        "bedrooms",
        "parking_spaces",
        "suburb",
        "advertiser_name",
        "aquisition_date",
    },
}

NUMERIC_COLUMNS = {
    "details": ["number_of_bedrooms", "number_of_guests"],
    "prices": ["price"],
    "vivareal": [
        "sale_price",
        "yearly_iptu",
        "monthly_condo_fee",
        "usable_area",
        "bedrooms",
        "parking_spaces",
    ],
}

SALE_BASE_SIGNATURE = [
    "_listing_title_key",
    "suburb",
    "bedrooms",
    "usable_area",
    "advertiser_name",
]
SALE_SIGNATURE = [*SALE_BASE_SIGNATURE, "_price_cluster"]


@dataclass(frozen=True)
class DecisionAssumptions:
    """Scenario assumptions and evidence gates defined before ranking."""

    occupancy_rate: float = 0.625
    days_per_year: int = 365
    min_short_stay_listings: int = 20
    min_sale_listings: int = 15
    thesis_suburb: str = "Centro"
    thesis_profile: str = "Studio/1Q"

    def __post_init__(self) -> None:
        if not 0 < self.occupancy_rate <= 1:
            raise ValueError("occupancy_rate must be greater than 0 and at most 1")
        if self.days_per_year <= 0:
            raise ValueError("days_per_year must be positive")
        if self.min_short_stay_listings <= 0 or self.min_sale_listings <= 0:
            raise ValueError("sample gates must be positive")


# Compatibility alias for earlier imports and notebooks.
InvestmentAssumptions = DecisionAssumptions


def load_datasets(data_dir: str | Path) -> dict[str, pd.DataFrame]:
    """Load the five official files while preserving long IDs as strings."""

    data_path = Path(data_dir)
    if not data_path.is_dir():
        raise FileNotFoundError(f"Data directory not found: {data_path}")

    datasets: dict[str, pd.DataFrame] = {}
    for name, filename in DATA_FILES.items():
        path = data_path / filename
        if not path.is_file():
            raise FileNotFoundError(f"Required dataset not found: {path}")
        frame = pd.read_csv(
            path,
            dtype={
                "airbnb_listing_id": "string",
                "listing_id": "string",
                "owner_id": "string",
            },
            na_values=["<NA>"],
            low_memory=False,
        )
        missing = REQUIRED_COLUMNS[name] - set(frame.columns)
        if missing:
            raise ValueError(
                f"{filename} is missing required columns: {sorted(missing)}"
            )
        datasets[name] = frame
    return datasets


def normalize_datasets(
    datasets: Mapping[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Normalize types and labels without mutating the source frames."""

    missing_datasets = set(DATA_FILES) - set(datasets)
    if missing_datasets:
        raise ValueError(f"Missing datasets: {sorted(missing_datasets)}")

    normalized = {name: frame.copy() for name, frame in datasets.items()}
    for name, columns in NUMERIC_COLUMNS.items():
        for column in columns:
            if column in normalized[name]:
                normalized[name][column] = pd.to_numeric(
                    normalized[name][column], errors="coerce"
                )

    for name, id_columns in {
        "details": ["airbnb_listing_id", "owner_id"],
        "prices": ["airbnb_listing_id"],
        "hosts": ["owner_id"],
        "mesh": ["airbnb_listing_id"],
        "vivareal": ["listing_id"],
    }.items():
        for column in id_columns:
            normalized[name][column] = normalized[name][column].astype("string")

    for name, column in (
        ("details", "aquisition_date"),
        ("prices", "date"),
        ("prices", "aquisition_date"),
        ("hosts", "host_snapshot_date"),
        ("mesh", "aquisition_date"),
        ("vivareal", "aquisition_date"),
    ):
        normalized[name][column] = pd.to_datetime(
            normalized[name][column], errors="coerce"
        )

    normalized["details"]["listing_type"] = normalized["details"][
        "listing_type"
    ].map(_ascii_lower)
    normalized["vivareal"]["listing_type"] = normalized["vivareal"][
        "listing_type"
    ].map(_ascii_lower)
    normalized["mesh"]["suburb"] = normalized["mesh"]["suburb"].map(
        _normalize_suburb
    )
    normalized["vivareal"]["suburb"] = normalized["vivareal"]["suburb"].map(
        _normalize_suburb
    )

    normalized["hosts"] = _keep_latest(
        normalized["hosts"], "owner_id", "host_snapshot_date"
    )
    normalized["vivareal"] = _keep_latest(
        normalized["vivareal"], "listing_id", "aquisition_date"
    )
    return normalized


def prepare_short_stay_listings(
    datasets: Mapping[str, pd.DataFrame], price_version: str = "latest"
) -> pd.DataFrame:
    """Return comparable apartment listings with one advertised-rate summary.

    Repeated observations for the same listing and stay date are snapshots, not
    independent nights. The base case keeps the latest captured price.
    """

    frames = normalize_datasets(datasets)
    prices = frames["prices"].loc[frames["prices"]["price"] > 0].copy()
    if price_version in {"latest", "earliest"}:
        prices = prices.sort_values("aquisition_date").drop_duplicates(
            ["airbnb_listing_id", "date"],
            keep="last" if price_version == "latest" else "first",
        )
    elif price_version != "all":
        raise ValueError("price_version must be 'latest', 'earliest' or 'all'")

    listing_rates = (
        prices.groupby("airbnb_listing_id", as_index=False)
        .agg(
            observed_median_rate=("price", "median"),
            observed_stay_dates=("date", "nunique"),
            first_stay_date=("date", "min"),
            last_stay_date=("date", "max"),
        )
    )
    listings = (
        frames["details"]
        .merge(
            frames["mesh"][["airbnb_listing_id", "suburb"]],
            on="airbnb_listing_id",
            how="inner",
            validate="one_to_one",
        )
        .merge(
            listing_rates,
            on="airbnb_listing_id",
            how="inner",
            validate="one_to_one",
        )
    )
    listings = listings.loc[
        (listings["listing_type"] == "apartamento")
        & listings["suburb"].notna()
        & listings["number_of_bedrooms"].notna()
    ].copy()
    listings["profile"] = listings["number_of_bedrooms"].map(_bedroom_profile)
    return listings


def prepare_sale_listings(
    datasets: Mapping[str, pd.DataFrame],
    deduplicate_content: bool = True,
    location_policy: str = "field",
) -> pd.DataFrame:
    """Return plausible residential apartment offers from VivaReal.

    Fixed plausibility bounds remove obvious unit and typing errors. They are
    deliberately broad and do not select a preferred neighborhood or profile.
    """

    frames = normalize_datasets(datasets)
    sales = frames["vivareal"].loc[
        (frames["vivareal"]["listing_type"] == "apartamento")
        & frames["vivareal"]["sale_price"].between(100_000, 20_000_000)
        & frames["vivareal"]["usable_area"].between(15, 500)
        & frames["vivareal"]["bedrooms"].notna()
        & frames["vivareal"]["suburb"].notna()
    ].copy()
    sales["asking_price_per_sqm"] = sales["sale_price"] / sales["usable_area"]
    sales = sales.loc[sales["asking_price_per_sqm"].between(3_000, 50_000)].copy()
    sales["_listing_title_key"] = sales["listing_title"].map(_ascii_lower)
    sales["url_suburb"] = sales["link_url"].map(_suburb_from_url)
    sales["location_conflict"] = sales["url_suburb"].notna() & (
        sales["url_suburb"] != sales["suburb"]
    )
    if location_policy == "consistent":
        sales = sales.loc[~sales["location_conflict"]].copy()
    elif location_policy != "field":
        raise ValueError("location_policy must be 'field' or 'consistent'")
    if deduplicate_content:
        sales = sales.sort_values([*SALE_BASE_SIGNATURE, "sale_price"])
        price_gap = sales.groupby(SALE_BASE_SIGNATURE, dropna=False)[
            "sale_price"
        ].diff()
        sales["_price_cluster"] = (
            price_gap.gt(1_000)
            .groupby([sales[column] for column in SALE_BASE_SIGNATURE], dropna=False)
            .cumsum()
        )
        sales = sales.sort_values("aquisition_date").drop_duplicates(
            SALE_SIGNATURE, keep="last"
        )
    else:
        sales["_price_cluster"] = np.arange(len(sales))
    sales["profile"] = sales["bedrooms"].map(_bedroom_profile)
    return sales.reset_index(drop=True)


def build_market_segments(
    datasets: Mapping[str, pd.DataFrame],
    assumptions: DecisionAssumptions | None = None,
    *,
    price_version: str = "latest",
    deduplicate_sales_content: bool = True,
    sale_location_policy: str = "field",
) -> pd.DataFrame:
    """Build one comparable row per neighborhood and bedroom profile."""

    assumptions = assumptions or DecisionAssumptions()
    frames = normalize_datasets(datasets)
    short_stay = prepare_short_stay_listings(datasets, price_version=price_version)
    sales = prepare_sale_listings(
        datasets,
        deduplicate_content=deduplicate_sales_content,
        location_policy=sale_location_policy,
    )

    apartment_universe = (
        frames["details"]
        .loc[
            (frames["details"]["listing_type"] == "apartamento")
            & frames["details"]["number_of_bedrooms"].notna()
        ]
        .merge(
            frames["mesh"][["airbnb_listing_id", "suburb"]],
            on="airbnb_listing_id",
            how="inner",
            validate="one_to_one",
        )
    )
    apartment_universe["profile"] = apartment_universe["number_of_bedrooms"].map(
        _bedroom_profile
    )
    universe_counts = (
        apartment_universe.groupby(["suburb", "profile"], observed=True)
        .agg(short_stay_universe=("airbnb_listing_id", "nunique"))
        .reset_index()
    )

    short_segments = (
        short_stay.groupby(["suburb", "profile"], observed=True)
        .agg(
            observed_median_rate=("observed_median_rate", "median"),
            rate_q25=("observed_median_rate", lambda values: values.quantile(0.25)),
            rate_q75=("observed_median_rate", lambda values: values.quantile(0.75)),
            short_stay_listings=("airbnb_listing_id", "nunique"),
            median_observed_dates=("observed_stay_dates", "median"),
        )
        .reset_index()
        .merge(universe_counts, on=["suburb", "profile"], how="left")
    )
    short_segments["price_coverage"] = _safe_divide(
        short_segments["short_stay_listings"],
        short_segments["short_stay_universe"],
    )

    sale_segments = (
        sales.groupby(["suburb", "profile"], observed=True)
        .agg(
            median_asking_price=("sale_price", "median"),
            asking_price_q25=("sale_price", lambda values: values.quantile(0.25)),
            asking_price_q75=("sale_price", lambda values: values.quantile(0.75)),
            median_price_per_sqm=("asking_price_per_sqm", "median"),
            median_usable_area=("usable_area", "median"),
            area_q25=("usable_area", lambda values: values.quantile(0.25)),
            area_q75=("usable_area", lambda values: values.quantile(0.75)),
            sale_listings=("listing_id", "nunique"),
        )
        .reset_index()
    )

    segments = short_segments.merge(
        sale_segments, on=["suburb", "profile"], how="outer", validate="one_to_one"
    )
    return calculate_scenario_metrics(segments, assumptions)


def calculate_scenario_metrics(
    segments: pd.DataFrame, assumptions: DecisionAssumptions | None = None
) -> pd.DataFrame:
    """Apply the explicit occupancy scenario without calling it observed revenue."""

    assumptions = assumptions or DecisionAssumptions()
    required = {"observed_median_rate", "median_asking_price"}
    missing = required - set(segments.columns)
    if missing:
        raise ValueError(f"Segments are missing columns: {sorted(missing)}")

    result = segments.copy()
    result["scenario_occupied_nights"] = (
        assumptions.days_per_year * assumptions.occupancy_rate
    )
    result["annualized_gross_revenue_scenario"] = (
        result["observed_median_rate"] * result["scenario_occupied_nights"]
    )
    result["gross_yield_scenario"] = _safe_divide(
        result["annualized_gross_revenue_scenario"], result["median_asking_price"]
    )
    result["evidence_eligible"] = (
        result["short_stay_listings"].fillna(0)
        >= assumptions.min_short_stay_listings
    ) & (result["sale_listings"].fillna(0) >= assumptions.min_sale_listings)
    return result.sort_values(["suburb", "profile"], ignore_index=True)


def build_decision(
    metrics: pd.DataFrame,
    assumptions: DecisionAssumptions | None = None,
    robustness: pd.DataFrame | None = None,
) -> dict[str, object]:
    """Compare the internal thesis with the strongest eligible alternative."""

    assumptions = assumptions or DecisionAssumptions()
    thesis = _select_segment(
        metrics, _normalize_suburb(assumptions.thesis_suburb), assumptions.thesis_profile
    )
    eligible = metrics.loc[
        metrics["evidence_eligible"] & metrics["gross_yield_scenario"].notna()
    ].copy()
    if eligible.empty:
        raise ValueError("No segment passes the evidence gates")

    alternatives = eligible.loc[
        ~(
            (eligible["suburb"] == thesis["suburb"])
            & (eligible["profile"] == thesis["profile"])
        )
    ]
    if alternatives.empty:
        raise ValueError("No eligible challenger was found")
    challenger = alternatives.sort_values(
        ["gross_yield_scenario", "short_stay_listings", "sale_listings"],
        ascending=[False, False, False],
    ).iloc[0]

    thesis_wins = bool(
        thesis["evidence_eligible"]
        and thesis["gross_yield_scenario"] >= challenger["gross_yield_scenario"]
    )
    winner = thesis if thesis_wins else challenger
    runner_up = challenger if thesis_wins else thesis

    robust_same_winner = None
    robust_evidence_complete = None
    if robustness is not None and not robustness.empty:
        expected = _segment_key(winner)
        eligible_tests = robustness.loc[robustness["pair_eligible"]]
        robust_same_winner = bool(
            not eligible_tests.empty
            and (eligible_tests["winner"] == expected).all()
        )
        robust_evidence_complete = bool(robustness["pair_eligible"].all())

    if not bool(thesis["evidence_eligible"]):
        thesis_verdict = "INCONCLUSIVA"
    elif thesis_wins and robust_same_winner is False:
        thesis_verdict = "SUSTENTADA COM RESSALVAS"
    elif thesis_wins:
        thesis_verdict = "SUSTENTADA"
    elif robust_same_winner is False:
        thesis_verdict = "INCONCLUSIVA"
    else:
        thesis_verdict = "NÃO SUSTENTADA"

    reversal = find_minimum_reversal(winner, runner_up, assumptions)
    minimum_coverage = min(
        float(thesis["price_coverage"]), float(challenger["price_coverage"])
    )
    return {
        "thesis": thesis,
        "challenger": challenger,
        "winner": winner,
        "runner_up": runner_up,
        "thesis_verdict": thesis_verdict,
        "robust_same_winner": robust_same_winner,
        "robust_evidence_complete": robust_evidence_complete,
        "reversal": reversal,
        "decision_status": "DILIGENCIAR, NÃO COMPRAR",
        "evidence_strength": "LIMITADA" if minimum_coverage < 0.30 else "MODERADA",
    }


def run_robustness_checks(
    datasets: Mapping[str, pd.DataFrame],
    assumptions: DecisionAssumptions | None = None,
) -> pd.DataFrame:
    """Re-run the decision under three defensible data treatments."""

    assumptions = assumptions or DecisionAssumptions()
    variants = [
        ("Base", "latest", True, "field"),
        ("Primeira captura", "earliest", True, "field"),
        ("Sem deduplicação de conteúdo", "latest", False, "field"),
        ("Somente bairros consistentes com a URL", "latest", True, "consistent"),
    ]
    rows: list[dict[str, object]] = []
    for label, price_version, deduplicate_sales, location_policy in variants:
        metrics = build_market_segments(
            datasets,
            assumptions,
            price_version=price_version,
            deduplicate_sales_content=deduplicate_sales,
            sale_location_policy=location_policy,
        )
        decision = build_decision(metrics, assumptions)
        thesis = decision["thesis"]
        challenger = decision["challenger"]
        pair_eligible = bool(
            thesis["evidence_eligible"] & challenger["evidence_eligible"]
        )
        winner = decision["winner"] if pair_eligible else None
        rows.append(
            {
                "test": label,
                "winner": _segment_key(winner) if winner is not None else None,
                "challenger": _segment_key(challenger),
                "thesis_yield": float(thesis["gross_yield_scenario"]),
                "challenger_yield": float(challenger["gross_yield_scenario"]),
                "gap_percentage_points": float(
                    (challenger["gross_yield_scenario"] - thesis["gross_yield_scenario"])
                    * 100
                ),
                "pair_eligible": pair_eligible,
            }
        )
    return pd.DataFrame(rows)


def find_minimum_reversal(
    winner: pd.Series,
    runner_up: pd.Series,
    assumptions: DecisionAssumptions | None = None,
) -> dict[str, object]:
    """Find the smallest one-variable shock that makes the runner-up tie."""

    assumptions = assumptions or DecisionAssumptions()
    winner_yield = float(winner["gross_yield_scenario"])
    runner_yield = float(runner_up["gross_yield_scenario"])
    if winner_yield <= 0 or runner_yield <= 0 or winner_yield < runner_yield:
        raise ValueError("winner and runner-up are invalid or out of order")

    yield_ratio = runner_yield / winner_yield
    inverse_ratio = winner_yield / runner_yield
    attacks = [
        {
            "variable": "Tarifa do vencedor",
            "direction": "queda",
            "relative_change": yield_ratio - 1,
            "display_change": -(1 - yield_ratio),
        },
        {
            "variable": "Preço do vencedor",
            "direction": "alta",
            "relative_change": inverse_ratio - 1,
            "display_change": inverse_ratio - 1,
        },
        {
            "variable": "Tarifa da tese alternativa",
            "direction": "alta",
            "relative_change": inverse_ratio - 1,
            "display_change": inverse_ratio - 1,
        },
        {
            "variable": "Preço da tese alternativa",
            "direction": "queda",
            "relative_change": yield_ratio - 1,
            "display_change": -(1 - yield_ratio),
        },
    ]
    for attack in attacks:
        attack["magnitude"] = abs(float(attack["relative_change"]))
    attacks.sort(key=lambda attack: attack["magnitude"])

    winner_occupancy_at_tie = assumptions.occupancy_rate * yield_ratio
    return {
        "winner": _segment_key(winner),
        "runner_up": _segment_key(runner_up),
        "minimum_attack": attacks[0],
        "attacks": attacks,
        "winner_occupancy_at_tie": winner_occupancy_at_tie,
        "occupancy_drop_percentage_points": (
            assumptions.occupancy_rate - winner_occupancy_at_tie
        )
        * 100,
        "winner_max_asking_price": float(
            winner["annualized_gross_revenue_scenario"] / runner_yield
        ),
        "runner_max_asking_price": float(
            runner_up["annualized_gross_revenue_scenario"] / winner_yield
        ),
    }


def build_acquisition_shortlist(
    datasets: Mapping[str, pd.DataFrame],
    decision: Mapping[str, object],
    assumptions: DecisionAssumptions | None = None,
    limit: int = 5,
) -> pd.DataFrame:
    """Select offers for diligence; this function never authorizes a purchase."""

    assumptions = assumptions or DecisionAssumptions()
    if limit <= 0:
        raise ValueError("limit must be positive")
    winner = decision["winner"]
    reversal = decision["reversal"]
    sales = prepare_sale_listings(datasets, location_policy="consistent")

    candidates = sales.loc[
        (sales["suburb"] == winner["suburb"])
        & (sales["profile"] == winner["profile"])
        & sales["usable_area"].between(
            winner["area_q25"], winner["area_q75"], inclusive="both"
        )
        & (sales["sale_price"] <= reversal["winner_max_asking_price"])
    ].copy()
    if candidates.empty:
        return _empty_shortlist()

    candidates["scenario_gross_revenue"] = float(
        winner["annualized_gross_revenue_scenario"]
    )
    candidates["scenario_gross_yield"] = _safe_divide(
        candidates["scenario_gross_revenue"], candidates["sale_price"]
    )
    condo_plausible = candidates["monthly_condo_fee"].between(50, 10_000)
    iptu_plausible = candidates["yearly_iptu"].between(100, 50_000)
    candidates["cost_data_status"] = np.where(
        condo_plausible & iptu_plausible,
        "Informados; validar",
        "Ausentes ou implausíveis",
    )
    candidates["price_data_status"] = np.where(
        candidates["sale_price"] < winner["asking_price_q25"],
        "Abaixo da faixa típica; verificar",
        "Dentro da faixa típica",
    )
    title_text = candidates["listing_title"].map(_ascii_lower)
    ready_signal = title_text.str.contains("pronto|mobiliado")
    construction_signal = title_text.str.contains("lancamento|obra|parcelad|entrega")
    candidates["readiness_status"] = np.select(
        [ready_signal, construction_signal],
        ["Indício de pronto; validar", "Possível lançamento; validar"],
        default="Estágio não informado",
    )
    candidates["diligence_status"] = "ELEGÍVEL PARA DILIGÊNCIA"
    candidates["_cost_priority"] = (condo_plausible & iptu_plausible).astype(int)
    candidates["_ready_priority"] = ready_signal.astype(int)

    output_columns = [
        "listing_id",
        "listing_title",
        "link_url",
        "suburb",
        "bedrooms",
        "usable_area",
        "parking_spaces",
        "sale_price",
        "asking_price_per_sqm",
        "scenario_gross_revenue",
        "scenario_gross_yield",
        "cost_data_status",
        "price_data_status",
        "readiness_status",
        "diligence_status",
    ]
    return (
        candidates.sort_values(
            ["_ready_priority", "_cost_priority", "sale_price"],
            ascending=[False, False, True],
        )
        .head(limit)[output_columns]
        .reset_index(drop=True)
    )


def build_data_audit(datasets: Mapping[str, pd.DataFrame]) -> dict[str, object]:
    """Expose the main coverage facts used by the skeptical audit."""

    frames = normalize_datasets(datasets)
    price_ids = set(frames["prices"]["airbnb_listing_id"].dropna())
    detail_ids = set(frames["details"]["airbnb_listing_id"].dropna())
    matched_ids = price_ids & detail_ids
    pair_counts = frames["prices"].groupby(
        ["airbnb_listing_id", "date"], dropna=False
    ).size()
    return {
        "airbnb_listings": len(detail_ids),
        "priced_airbnb_listings": len(matched_ids),
        "price_coverage": len(matched_ids) / len(detail_ids),
        "price_rows": len(frames["prices"]),
        "unique_listing_stay_dates": len(pair_counts),
        "repeated_listing_stay_dates": int((pair_counts > 1).sum()),
        "stay_date_min": frames["prices"]["date"].min(),
        "stay_date_max": frames["prices"]["date"].max(),
        "sale_offers_raw": len(datasets["vivareal"]),
        "sale_offers_clean": len(prepare_sale_listings(datasets)),
    }


def build_decision_data(
    data_dir: str | Path,
    assumptions: DecisionAssumptions | None = None,
) -> dict[str, object]:
    """Build every deterministic artifact consumed by the interface."""

    assumptions = assumptions or DecisionAssumptions()
    datasets = load_datasets(data_dir)
    metrics = build_market_segments(datasets, assumptions)
    robustness = run_robustness_checks(datasets, assumptions)
    decision = build_decision(metrics, assumptions, robustness)
    shortlist = build_acquisition_shortlist(datasets, decision, assumptions)
    return {
        "assumptions": assumptions,
        "metrics": metrics,
        "robustness": robustness,
        "decision": decision,
        "shortlist": shortlist,
        "audit": build_data_audit(datasets),
    }


def _keep_latest(frame: pd.DataFrame, key: str, date_column: str) -> pd.DataFrame:
    return (
        frame.sort_values(date_column, na_position="first")
        .drop_duplicates(key, keep="last")
        .reset_index(drop=True)
    )


def _ascii_lower(value: object) -> str:
    if pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    return "".join(char for char in text if not unicodedata.combining(char)).lower().strip()


def _normalize_suburb(value: object) -> str | None:
    text = " ".join(_ascii_lower(value).split())
    if not text or text in {"none", "nan", "<na>"}:
        return None
    aliases = {
        "centro": "Centro",
        "meia praia": "Meia Praia",
        "meia praia - frente mar": "Meia Praia",
        "morretes": "Morretes",
        "jardim praia mar": "Jardim Praiamar",
        "jardim praiamar": "Jardim Praiamar",
        "taboleiro": "Tabuleiro dos Oliveiras",
        "tabuleiro": "Tabuleiro dos Oliveiras",
        "tabuleiro dos oliveiras": "Tabuleiro dos Oliveiras",
    }
    return aliases.get(text, text.title())


def _suburb_from_url(value: object) -> str | None:
    text = _ascii_lower(value).replace("_", "-")
    aliases = {
        "meia-praia": "Meia Praia",
        "morretes": "Morretes",
        "centro": "Centro",
        "tabuleiro-dos-oliveiras": "Tabuleiro dos Oliveiras",
        "jardim-praiamar": "Jardim Praiamar",
        "alto-sao-bento": "Alto Sao Bento",
    }
    for slug, suburb in aliases.items():
        if f"-{slug}-bairros-" in text:
            return suburb
    return None


def _bedroom_profile(bedrooms: float) -> str:
    if pd.isna(bedrooms):
        raise ValueError("Bedroom count cannot be null")
    if bedrooms <= 1:
        return "Studio/1Q"
    if float(bedrooms).is_integer():
        return f"{int(bedrooms)}Q"
    return f"{bedrooms:g}Q"


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator.div(denominator.where(denominator > 0))


def _select_segment(
    metrics: pd.DataFrame, suburb: str | None, profile: str
) -> pd.Series:
    selected = metrics.loc[
        (metrics["suburb"] == suburb) & (metrics["profile"] == profile)
    ]
    if len(selected) != 1:
        raise ValueError(
            f"Expected one segment for {suburb}/{profile}, found {len(selected)}"
        )
    return selected.iloc[0]


def _segment_key(segment: pd.Series) -> str:
    return f"{segment['suburb']} · {segment['profile']}"


def _empty_shortlist() -> pd.DataFrame:
    return pd.DataFrame(
        columns=[
            "listing_id",
            "listing_title",
            "link_url",
            "suburb",
            "bedrooms",
            "usable_area",
            "parking_spaces",
            "sale_price",
            "asking_price_per_sqm",
            "scenario_gross_revenue",
            "scenario_gross_yield",
            "cost_data_status",
            "price_data_status",
            "readiness_status",
            "diligence_status",
        ]
    )
