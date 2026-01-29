import unittest

import pandas as pd

from app import (
    _compute_lower_level_allocation_totals,
    _select_spending_vars_for_calculation,
    build_hierarchical_display,
)


class TestLowerLevelWeights(unittest.TestCase):
    def setUp(self):
        self.var_to_node = {
            "AA": {"level": 0, "parent": None},
            "AA1": {"level": 1, "parent": "AA"},
            "AA2": {"level": 1, "parent": "AA"},
        }
        self.hierarchy_data = {"hierarchy_order": ["AA", "AA1", "AA2"]}
        self.allocation_lookup = {
            "AA": {"shared_pct": 0.2, "child_intensity": 4.0},
            "AA1": {"shared_pct": 0.1, "child_intensity": 2.0},
            "AA2": {"shared_pct": 0.9, "child_intensity": 8.0},
        }
        self.results_by_code = {
            "AA": {
                "var_code": "AA",
                "mean": 200.0,
                "quality": "A",
                "level": 0,
                "description": "All Spending",
            },
            "AA1": {
                "var_code": "AA1",
                "mean": 100.0,
                "quality": "A",
                "level": 1,
                "description": "Child One",
            },
            "AA2": {
                "var_code": "AA2",
                "mean": 100.0,
                "quality": "A",
                "level": 1,
                "description": "Child Two",
            },
        }

    def _build_results(self, var_codes):
        return [self.results_by_code[code] for code in var_codes]

    def test_lower_level_weights_changes_shared_percent(self):
        available_vars = ["AA", "AA1", "AA2"]
        max_granularity_level = 0

        vars_off = _select_spending_vars_for_calculation(
            available_vars,
            self.var_to_node,
            max_granularity_level,
            use_lower_level_weights=False,
        )
        vars_on = _select_spending_vars_for_calculation(
            available_vars,
            self.var_to_node,
            max_granularity_level,
            use_lower_level_weights=True,
        )

        results_display = self._build_results(vars_off)
        results_full = self._build_results(vars_on)

        lower_level_allocations, _ = _compute_lower_level_allocation_totals(
            results_full,
            self.var_to_node,
            self.hierarchy_data,
            self.allocation_lookup,
            n_adults=2,
            n_children=1,
            target_level=0,
        )

        display_off = build_hierarchical_display(
            results_display,
            self.var_to_node,
            self.hierarchy_data,
            allocation_lookup=self.allocation_lookup,
            n_adults=2,
            n_children=1,
            allocation_totals=None,
            use_lower_level_weights=False,
            target_level=0,
        )
        display_on = build_hierarchical_display(
            results_display,
            self.var_to_node,
            self.hierarchy_data,
            allocation_lookup=self.allocation_lookup,
            n_adults=2,
            n_children=1,
            allocation_totals=lower_level_allocations,
            use_lower_level_weights=True,
            target_level=0,
        )

        shared_pct_off = display_off.loc[0, "Shared %"]
        shared_pct_on = display_on.loc[0, "Shared %"]

        self.assertNotEqual(shared_pct_off, shared_pct_on)

    def test_weighted_rows_only_at_target_level(self):
        var_to_node = {
            "TC001": {"level": 0, "parent": None},
            "F001": {"level": 1, "parent": "TC001"},
            "F001A": {"level": 2, "parent": "F001"},
            "F001B": {"level": 2, "parent": "F001"},
        }
        hierarchy_data = {"hierarchy_order": ["TC001", "F001", "F001A", "F001B"]}
        allocation_lookup = {
            "F001": {"shared_pct": 0.3, "child_intensity": 5.0},
            "F001A": {"shared_pct": 0.2, "child_intensity": 4.0},
            "F001B": {"shared_pct": 0.4, "child_intensity": 6.0},
        }
        results_full = [
            {"var_code": "TC001", "mean": 200.0, "quality": "A", "level": 0, "description": "Total expenditure"},
            {"var_code": "F001", "mean": 200.0, "quality": "A", "level": 1, "description": "Food expenditures"},
            {"var_code": "F001A", "mean": 100.0, "quality": "A", "level": 2, "description": "Food child A"},
            {"var_code": "F001B", "mean": 100.0, "quality": "A", "level": 2, "description": "Food child B"},
        ]
        results_display = [results_full[0], results_full[1]]
        lower_level_allocations, _ = _compute_lower_level_allocation_totals(
            results_full,
            var_to_node,
            hierarchy_data,
            allocation_lookup,
            n_adults=2,
            n_children=1,
            target_level=1,
        )
        display_off = build_hierarchical_display(
            results_display,
            var_to_node,
            hierarchy_data,
            allocation_lookup=allocation_lookup,
            n_adults=2,
            n_children=1,
            allocation_totals=None,
            use_lower_level_weights=False,
            target_level=1,
        )
        display_on = build_hierarchical_display(
            results_display,
            var_to_node,
            hierarchy_data,
            allocation_lookup=allocation_lookup,
            n_adults=2,
            n_children=1,
            allocation_totals=lower_level_allocations,
            use_lower_level_weights=True,
            target_level=1,
        )
        food_row = display_on.loc[1]
        total_row = display_on.loc[0]
        for col in ["Shared %", "Child Intensity", "Shared $", "Exclusive (Adult) $", "Exclusive (Child) $"]:
            self.assertFalse(pd.isna(food_row[col]), f"{col} should be populated for level rows.")
            self.assertTrue(pd.isna(total_row[col]), f"{col} should be blank for total rows.")
        self.assertAlmostEqual(display_off.loc[1, "Shared %"], 0.3)


if __name__ == "__main__":
    unittest.main()
