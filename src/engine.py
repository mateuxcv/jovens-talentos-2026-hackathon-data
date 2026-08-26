"""Deterministic investment calculations for the Itapema market.

This module is the numeric source of truth for the application. It keeps raw
market evidence separate from operating assumptions and never delegates a
calculation to the AI layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
import unicodedata

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
        "number_of_bedrooms",
        "number_of_guests",
        "amenities",
        "can_instant_book",
        "guest_satisfaction_overall",
        "owner_id",
    },
    "prices": {"airbnb_listing_id", "date", "price", "aquisition_date"},
    "hosts": {"owner_id", "host_snapshot_date"},
    "mesh": {"airbnb_listing_id", "suburb"},
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
        "aquisition_date",
    },
}

NUMERIC_COLUMNS = {
    "details": [
        "number_of_bedrooms",
        "number_of_guests",
        "number_of_reviews",
        "guest_satisfaction_overall",
    ],
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


@dataclass(frozen=True)
class InvestmentAssumptions:
    """Operating assumptions controlled by the executive UI."""

    management_fee_rate: float = 0.20
    wacc_rate: float = 0.10
    negotiation_discount_rate: float = 0.05
    vacancy_rate: float = 0.375
    days_per_year: int = 365

    def __post_init__(self) -> None:
        for name in (
            "management_fee_rate",
            "wacc_rate",
            "negotiation_discount_rate",
            "vacancy_rate",
        ):
            value = getattr(self, name)
            if not 0 <= value < 1:
                raise ValueError(f"{name} must be between 0 (inclusive) and 1")
        if self.days_per_year <= 0:
            raise ValueError("days_per_year must be positive")


def load_datasets(data_dir: str | Path) -> dict[str, pd.DataFrame]:
    """Load the five official CSV files and validate their input schemas."""

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
    """Return normalized copies while preserving every raw source file."""

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

    normalized["details"]["can_instant_book"] = _to_nullable_boolean(
        normalized["details"]["can_instant_book"]
    )
    for name, column in (
        ("prices", "date"),
        ("prices", "aquisition_date"),
        ("hosts", "host_snapshot_date"),
        ("vivareal", "aquisition_date"),
    ):
        normalized[name][column] = pd.to_datetime(
            normalized[name][column], errors="coerce"
        )

    normalized["mesh"]["suburb"] = normalized["mesh"]["suburb"].map(
        _normalize_suburb
    )
    normalized["vivareal"]["suburb"] = normalized["vivareal"]["suburb"].map(
        _normalize_suburb
    )
    normalized["vivareal"]["listing_type"] = (
        normalized["vivareal"]["listing_type"].astype("string").str.lower().str.strip()
    )

    # VivaReal and hosts contain repeated snapshots. Keep the newest evidence.
    normalized["vivareal"] = _keep_latest(
        normalized["vivareal"], "listing_id", "aquisition_date"
    )
    normalized["hosts"] = _keep_latest(
        normalized["hosts"], "owner_id", "host_snapshot_date"
    )
    return normalized


def build_market_segments(
    datasets: Mapping[str, pd.DataFrame],
    assumptions: InvestmentAssumptions | None = None,
) -> pd.DataFrame:
    """Build one comparable row per neighborhood and bedroom profile.

    Airbnb prices are first reduced to one median ADR per listing. This avoids
    giving more weight to listings with more captured dates.
    """

    assumptions = assumptions or InvestmentAssumptions()
    frames = normalize_datasets(datasets)

    listing_adr = (
        frames["prices"].loc[frames["prices"]["price"] > 0]
        .groupby("airbnb_listing_id", as_index=False)
        .agg(median_adr=("price", "median"), observed_nights=("price", "size"))
    )
    airbnb = (
        frames["details"]
        .merge(
            frames["mesh"][["airbnb_listing_id", "suburb"]],
            on="airbnb_listing_id",
            how="inner",
            validate="one_to_one",
        )
        .merge(listing_adr, on="airbnb_listing_id", how="inner", validate="one_to_one")
    )
    airbnb = airbnb.loc[
        airbnb["suburb"].notna() & airbnb["number_of_bedrooms"].notna()
    ].copy()
    airbnb["profile"] = airbnb["number_of_bedrooms"].map(_bedroom_profile)
    amenities = airbnb["amenities"].fillna("").map(_ascii_lower)
    airbnb["has_air_conditioning"] = amenities.str.contains("ar-condicionado")
    airbnb["has_parking"] = amenities.str.contains("estacionamento")
    airbnb["valid_guest_rating"] = airbnb["guest_satisfaction_overall"].where(
        airbnb["guest_satisfaction_overall"] > 0
    )

    airbnb_segments = (
        airbnb.groupby(["suburb", "profile"], observed=True)
        .agg(
            median_adr=("median_adr", "median"),
            airbnb_listings=("airbnb_listing_id", "nunique"),
            median_guests=("number_of_guests", "median"),
            median_guest_rating=("valid_guest_rating", "median"),
            instant_book_share=("can_instant_book", "mean"),
            air_conditioning_share=("has_air_conditioning", "mean"),
            parking_share=("has_parking", "mean"),
        )
        .reset_index()
    )

    sales = frames["vivareal"].loc[
        (frames["vivareal"]["listing_type"] == "apartamento")
        & (frames["vivareal"]["sale_price"] > 0)
        & (frames["vivareal"]["usable_area"] > 0)
        & frames["vivareal"]["bedrooms"].notna()
        & frames["vivareal"]["suburb"].notna()
    ].copy()
    sales["profile"] = sales["bedrooms"].map(_bedroom_profile)
    sales["asking_price_per_sqm"] = sales["sale_price"] / sales["usable_area"]
    sale_segments = (
        sales.groupby(["suburb", "profile"], observed=True)
        .agg(
            median_asking_price=("sale_price", "median"),
            median_price_per_sqm=("asking_price_per_sqm", "median"),
            median_usable_area=("usable_area", "median"),
            sale_listings=("listing_id", "nunique"),
        )
        .reset_index()
    )

    segments = airbnb_segments.merge(
        sale_segments, on=["suburb", "profile"], how="outer", validate="one_to_one"
    )
    return calculate_investment_metrics(segments, assumptions)


def calculate_investment_metrics(
    segments: pd.DataFrame,
    assumptions: InvestmentAssumptions | None = None,
) -> pd.DataFrame:
    """Apply transparent revenue, yield, negotiated-price and WACC formulas."""

    assumptions = assumptions or InvestmentAssumptions()
    required = {"median_adr", "median_asking_price"}
    missing = required - set(segments.columns)
    if missing:
        raise ValueError(f"Segments are missing columns: {sorted(missing)}")

    result = segments.copy()
    result["projected_occupied_nights"] = assumptions.days_per_year * (
        1 - assumptions.vacancy_rate
    )
    result["annual_gross_revenue"] = (
        result["median_adr"] * result["projected_occupied_nights"]
    )
    result["annual_noi_before_property_costs"] = result["annual_gross_revenue"] * (
        1 - assumptions.management_fee_rate
    )
    result["negotiated_purchase_price"] = result["median_asking_price"] * (
        1 - assumptions.negotiation_discount_rate
    )
    result["gross_yield_asking"] = _safe_divide(
        result["annual_gross_revenue"], result["median_asking_price"]
    )
    result["net_yield_asking"] = _safe_divide(
        result["annual_noi_before_property_costs"], result["median_asking_price"]
    )
    result["net_yield_negotiated"] = _safe_divide(
        result["annual_noi_before_property_costs"], result["negotiated_purchase_price"]
    )
    result["wacc_spread_asking"] = result["net_yield_asking"] - assumptions.wacc_rate
    result["wacc_spread_negotiated"] = (
        result["net_yield_negotiated"] - assumptions.wacc_rate
    )
    return result.sort_values(["suburb", "profile"], ignore_index=True)


def run_sensitivity_analysis(
    metrics: pd.DataFrame,
    target_suburb: str = "Centro",
    competitor_suburb: str = "Morretes",
    profile: str = "2Q",
    min_price_change: float = -0.40,
    max_price_change: float = 0.40,
    steps: int = 81,
) -> pd.DataFrame:
    """Compare target yield as its acquisition price changes against a peer.

    Metadata in ``result.attrs`` includes the exact break-even price change.
    A negative break-even means the target is already less profitable and its
    price would need to fall to match the competitor.
    """

    if min_price_change <= -1 or max_price_change <= min_price_change:
        raise ValueError("Invalid sensitivity price range")
    if steps < 2:
        raise ValueError("steps must be at least 2")

    target_name = _normalize_suburb(target_suburb)
    competitor_name = _normalize_suburb(competitor_suburb)
    target = _select_segment(metrics, target_name, profile)
    competitor = _select_segment(metrics, competitor_name, profile)
    required_values = [
        target["median_asking_price"],
        target["annual_noi_before_property_costs"],
        competitor["net_yield_asking"],
    ]
    if any(pd.isna(value) or value <= 0 for value in required_values):
        raise ValueError("Selected segments do not have enough data for sensitivity")

    changes = np.linspace(min_price_change, max_price_change, steps)
    target_prices = target["median_asking_price"] * (1 + changes)
    target_yields = target["annual_noi_before_property_costs"] / target_prices
    competitor_yield = float(competitor["net_yield_asking"])
    result = pd.DataFrame(
        {
            "price_change": changes,
            "target_purchase_price": target_prices,
            "target_net_yield": target_yields,
            "competitor_net_yield": competitor_yield,
            "leader": np.where(
                target_yields >= competitor_yield, target_name, competitor_name
            ),
        }
    )
    break_even_multiplier = (
        target["annual_noi_before_property_costs"]
        / competitor_yield
        / target["median_asking_price"]
    )
    result.attrs.update(
        {
            "target_suburb": target_name,
            "competitor_suburb": competitor_name,
            "profile": profile,
            "break_even_price_change": float(break_even_multiplier - 1),
            "current_leader": (
                target_name
                if target["net_yield_asking"] >= competitor_yield
                else competitor_name
            ),
        }
    )
    return result


def build_acquisition_shortlist(
    datasets: Mapping[str, pd.DataFrame],
    metrics: pd.DataFrame,
    assumptions: InvestmentAssumptions | None = None,
    suburbs: tuple[str, ...] = ("Centro", "Morretes"),
    bedrooms: int = 2,
    min_area: float = 60,
    max_area: float = 85,
    max_asking_price: float = 950_000,
    limit: int = 5,
) -> pd.DataFrame:
    """Rank real VivaReal listings that fit the acquisition mandate.

    Missing condo or IPTU values are conservatively exposed through
    ``property_costs_complete`` instead of being hidden from the decision.
    They are treated as zero only for the displayed estimate.
    """

    assumptions = assumptions or InvestmentAssumptions()
    if limit <= 0:
        raise ValueError("limit must be positive")
    if min_area <= 0 or max_area < min_area or max_asking_price <= 0:
        raise ValueError("Invalid shortlist filters")

    frames = normalize_datasets(datasets)
    sales = frames["vivareal"].copy()
    normalized_suburbs = {_normalize_suburb(value) for value in suburbs}
    candidates = sales.loc[
        (sales["listing_type"] == "apartamento")
        & sales["suburb"].isin(normalized_suburbs)
        & (sales["bedrooms"] == bedrooms)
        & sales["usable_area"].between(min_area, max_area, inclusive="both")
        & sales["sale_price"].between(1, max_asking_price, inclusive="both")
    ].copy()
    if candidates.empty:
        return _empty_shortlist()

    profile = _bedroom_profile(float(bedrooms))
    adr_map = (
        metrics.loc[metrics["profile"] == profile, ["suburb", "median_adr"]]
        .dropna()
        .set_index("suburb")["median_adr"]
    )
    candidates["estimated_adr"] = candidates["suburb"].map(adr_map)
    candidates = candidates.loc[candidates["estimated_adr"].notna()].copy()
    if candidates.empty:
        return _empty_shortlist()

    candidates["negotiated_purchase_price"] = candidates["sale_price"] * (
        1 - assumptions.negotiation_discount_rate
    )
    candidates["annual_gross_revenue"] = (
        candidates["estimated_adr"]
        * assumptions.days_per_year
        * (1 - assumptions.vacancy_rate)
    )
    candidates["property_costs_complete"] = candidates[
        ["monthly_condo_fee", "yearly_iptu"]
    ].notna().all(axis=1)
    candidates["known_annual_property_costs"] = (
        candidates["monthly_condo_fee"].fillna(0) * 12
        + candidates["yearly_iptu"].fillna(0)
    )
    candidates["estimated_annual_noi"] = (
        candidates["annual_gross_revenue"]
        * (1 - assumptions.management_fee_rate)
        - candidates["known_annual_property_costs"]
    )
    candidates["estimated_net_cap_rate"] = _safe_divide(
        candidates["estimated_annual_noi"],
        candidates["negotiated_purchase_price"],
    )
    candidates["asking_price_per_sqm"] = (
        candidates["sale_price"] / candidates["usable_area"]
    )
    output_columns = [
        "listing_id",
        "listing_title",
        "link_url",
        "suburb",
        "bedrooms",
        "usable_area",
        "parking_spaces",
        "sale_price",
        "negotiated_purchase_price",
        "asking_price_per_sqm",
        "estimated_adr",
        "annual_gross_revenue",
        "known_annual_property_costs",
        "property_costs_complete",
        "estimated_annual_noi",
        "estimated_net_cap_rate",
    ]
    return (
        candidates.sort_values(
            ["estimated_net_cap_rate", "sale_price"],
            ascending=[False, True],
        )
        .head(limit)[output_columns]
        .reset_index(drop=True)
    )


def build_decision_data(
    data_dir: str | Path,
    assumptions: InvestmentAssumptions | None = None,
) -> dict[str, object]:
    """Convenience entry point consumed by the future Streamlit application."""

    assumptions = assumptions or InvestmentAssumptions()
    datasets = load_datasets(data_dir)
    metrics = build_market_segments(datasets, assumptions)
    sensitivity = run_sensitivity_analysis(metrics)
    shortlist = build_acquisition_shortlist(datasets, metrics, assumptions)
    return {
        "assumptions": assumptions,
        "metrics": metrics,
        "sensitivity": sensitivity,
        "shortlist": shortlist,
    }


def _keep_latest(frame: pd.DataFrame, key: str, date_column: str) -> pd.DataFrame:
    return (
        frame.sort_values(date_column, na_position="first")
        .drop_duplicates(key, keep="last")
        .reset_index(drop=True)
    )


def _to_nullable_boolean(series: pd.Series) -> pd.Series:
    values = series.astype("string").str.lower().str.strip()
    return values.map({"true": True, "false": False}).astype("boolean")


def _ascii_lower(value: object) -> str:
    if pd.isna(value):
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    return "".join(char for char in text if not unicodedata.combining(char)).lower()


def _normalize_suburb(value: object) -> str | None:
    text = " ".join(_ascii_lower(value).split())
    if not text or text in {"none", "nan", "<na>"}:
        return None
    aliases = {
        "centro": "Centro",
        "meia praia": "Meia Praia",
        "meia praia - frente mar": "Meia Praia",
        "morretes": "Morretes",
        "taboleiro": "Tabuleiro dos Oliveiras",
        "tabuleiro": "Tabuleiro dos Oliveiras",
        "tabuleiro dos oliveiras": "Tabuleiro dos Oliveiras",
    }
    return aliases.get(text, text.title())


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


def _select_segment(metrics: pd.DataFrame, suburb: str | None, profile: str) -> pd.Series:
    selected = metrics.loc[
        (metrics["suburb"] == suburb) & (metrics["profile"] == profile)
    ]
    if len(selected) != 1:
        raise ValueError(f"Expected one segment for {suburb}/{profile}, found {len(selected)}")
    return selected.iloc[0]


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
            "negotiated_purchase_price",
            "asking_price_per_sqm",
            "estimated_adr",
            "annual_gross_revenue",
            "known_annual_property_costs",
            "property_costs_complete",
            "estimated_annual_noi",
            "estimated_net_cap_rate",
        ]
    )
