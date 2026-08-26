from __future__ import annotations

import unittest
from pathlib import Path

import pandas as pd

from src.engine import (
    SALE_BASE_SIGNATURE,
    SALE_SIGNATURE,
    DecisionAssumptions,
    build_decision,
    build_decision_data,
    evaluate_duel,
    load_datasets,
    prepare_sale_listings,
    prepare_short_stay_listings,
)

ROOT = Path(__file__).parents[1]


class EngineIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.datasets = load_datasets(ROOT / "data")
        cls.result = build_decision_data(ROOT / "data")

    def test_repeated_price_snapshots_are_reduced_before_listing_median(self) -> None:
        listings = prepare_short_stay_listings(self.datasets)
        self.assertTrue(listings["airbnb_listing_id"].is_unique)
        self.assertLessEqual(int(listings["observed_stay_dates"].max()), 105)

    def test_near_identical_sale_republications_are_deduplicated(self) -> None:
        sales = prepare_sale_listings(self.datasets)
        self.assertFalse(sales.duplicated(SALE_SIGNATURE).any())
        ordered = sales.sort_values([*SALE_BASE_SIGNATURE, "sale_price"])
        remaining_gaps = ordered.groupby(SALE_BASE_SIGNATURE, dropna=False)[
            "sale_price"
        ].diff()
        self.assertTrue((remaining_gaps.dropna() > 1_000).all())

    def test_default_decision_is_derived_from_eligible_segments(self) -> None:
        decision = self.result["decision"]
        self.assertEqual("Centro", decision["thesis"]["suburb"])
        self.assertEqual("Studio/1Q", decision["thesis"]["profile"])
        self.assertEqual("Morretes", decision["challenger"]["suburb"])
        self.assertEqual("2Q", decision["challenger"]["profile"])
        self.assertEqual("NÃO SUSTENTADA", decision["thesis_verdict"])
        self.assertTrue(decision["robust_same_winner"])

    def test_ineligible_robustness_variant_has_no_declared_winner(self) -> None:
        robustness = self.result["robustness"]
        ineligible = robustness.loc[~robustness["pair_eligible"]]
        eligible = robustness.loc[robustness["pair_eligible"]]
        self.assertEqual(1, len(ineligible))
        self.assertTrue(ineligible["winner"].isna().all())
        self.assertEqual({"Morretes · 2Q"}, set(eligible["winner"]))

    def test_reversal_math_reaches_the_runner_up_yield(self) -> None:
        decision = self.result["decision"]
        winner = decision["winner"]
        runner_up = decision["runner_up"]
        reversal = decision["reversal"]
        attacked_rate = winner["observed_median_rate"] * (
            1 + reversal["minimum_attack"]["relative_change"]
        )
        attacked_yield = (
            attacked_rate
            * 365
            * self.result["assumptions"].occupancy_rate
            / winner["median_asking_price"]
        )
        self.assertAlmostEqual(attacked_yield, runner_up["gross_yield_scenario"])

    def test_shortlist_is_for_diligence_and_respects_price_limit(self) -> None:
        shortlist = self.result["shortlist"]
        decision = self.result["decision"]
        self.assertFalse(shortlist.empty)
        self.assertTrue(
            (shortlist["suburb"] == decision["winner"]["suburb"]).all()
        )
        self.assertTrue(
            (
                shortlist["sale_price"]
                <= decision["reversal"]["winner_max_asking_price"]
            ).all()
        )
        self.assertEqual(
            {"ELEGÍVEL PARA DILIGÊNCIA"}, set(shortlist["diligence_status"])
        )

    def test_asymmetric_scenario_can_change_the_leader(self) -> None:
        decision = self.result["decision"]
        duel = evaluate_duel(
            decision["thesis"],
            decision["challenger"],
            thesis_occupancy=0.625,
            challenger_occupancy=0.625,
            challenger_rate_change=-0.20,
        )
        self.assertEqual("Centro · Studio/1Q", duel["leader"])

    def test_budget_can_remove_the_thesis_from_the_mandate(self) -> None:
        result = build_decision_data(
            ROOT / "data",
            DecisionAssumptions(max_typical_asking_price=800_000),
        )
        self.assertEqual("FORA DO MANDATO", result["decision"]["thesis_verdict"])
        self.assertEqual("Morretes", result["decision"]["winner"]["suburb"])


class DecisionRuleTests(unittest.TestCase):
    def test_verdict_changes_when_the_thesis_leads(self) -> None:
        metrics = pd.DataFrame(
            [
                {
                    "suburb": "Centro",
                    "profile": "Studio/1Q",
                    "gross_yield_scenario": 0.12,
                    "evidence_eligible": True,
                    "short_stay_listings": 30,
                    "sale_listings": 20,
                    "price_coverage": 1.0,
                    "observed_median_rate": 400,
                    "median_asking_price": 760_000,
                    "annualized_gross_revenue_scenario": 91_250,
                },
                {
                    "suburb": "Morretes",
                    "profile": "2Q",
                    "gross_yield_scenario": 0.10,
                    "evidence_eligible": True,
                    "short_stay_listings": 30,
                    "sale_listings": 20,
                    "price_coverage": 1.0,
                    "observed_median_rate": 400,
                    "median_asking_price": 912_500,
                    "annualized_gross_revenue_scenario": 91_250,
                },
            ]
        )
        decision = build_decision(metrics, DecisionAssumptions())
        self.assertEqual("SUSTENTADA", decision["thesis_verdict"])
        self.assertEqual("Centro", decision["winner"]["suburb"])


if __name__ == "__main__":
    unittest.main()
