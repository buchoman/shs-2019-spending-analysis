import unittest

import pandas as pd

from app import (
    _compute_lower_level_allocation_totals,
    _select_spending_vars_for_calculation,
    build_hierarchical_display,
    filter_results_by_granularity,
)


class TestLowerLevelWeights(unittest.TestCase):
    def setUp(self):
        self.var_to_node = {
            "TC001": {"level": 0, "parent": None},
            "F001": {"level": 1, "parent": "TC001"},
            "F001A": {"level": 2, "parent": "F001"},
            "F001B": {"level": 2, "parent": "F001"},
        }
        self.hierarchy_data = {"hierarchy_order": ["TC001", "F001", "F001A", "F001B"]}
        self.allocation_lookup = {
            "F001": {"shared_pct": 0.5, "child_intensity": 5.0},
            "F001A": {"shared_pct": 0.2, "child_intensity": 4.0},
            "F001B": {"shared_pct": 0.8, "child_intensity": 7.0},
        }
        self.results_by_code = {
            "TC001": {
                "var_code": "TC001",
                "mean": 200.0,
                "quality": "A",
                "level": 0,
                "description": "Total expenditure",
            },
            "F001": {
                "var_code": "F001",
                "mean": 200.0,
                "quality": "A",
                "level": 1,
                "description": "Food expenditures",
            },
            "F001A": {
                "var_code": "F001A",
                "mean": 150.0,
                "quality": "A",
                "level": 2,
                "description": "Food child A",
            },
            "F001B": {
                "var_code": "F001B",
                "mean": 50.0,
                "quality": "A",
                "level": 2,
                "description": "Food child B",
            },
        }

    def _build_results(self, var_codes):
        return [self.results_by_code[code] for code in var_codes]

    def test_lower_level_weights_changes_shared_percent(self):
        available_vars = ["TC001", "F001", "F001A", "F001B"]
        max_granularity_level = 1

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
            target_level=1,
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
            target_level=1,
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
            target_level=1,
        )

        shared_pct_off = display_off.loc[1, "Shared %"]
        shared_pct_on = display_on.loc[1, "Shared %"]

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

    def test_rollup_at_selected_level_filters_and_populates(self):
        var_to_node = {
            "TC001": {"level": 0, "parent": None},
            "F001": {"level": 1, "parent": "TC001"},
            "F001A": {"level": 2, "parent": "F001"},
            "F001A1": {"level": 3, "parent": "F001A"},
            "F001A2": {"level": 3, "parent": "F001A"},
        }
        hierarchy_data = {"hierarchy_order": ["TC001", "F001", "F001A", "F001A1", "F001A2"]}
        allocation_lookup = {
            "F001A1": {"shared_pct": 0.2, "child_intensity": 4.0},
            "F001A2": {"shared_pct": 0.4, "child_intensity": 6.0},
        }
        results_full = [
            {"var_code": "TC001", "mean": 300.0, "quality": "A", "level": 0, "description": "Total expenditure"},
            {"var_code": "F001", "mean": 300.0, "quality": "A", "level": 1, "description": "Food expenditures"},
            {"var_code": "F001A", "mean": 300.0, "quality": "A", "level": 2, "description": "Food subcategory"},
            {"var_code": "F001A1", "mean": 120.0, "quality": "A", "level": 3, "description": "Food leaf 1"},
            {"var_code": "F001A2", "mean": 180.0, "quality": "A", "level": 3, "description": "Food leaf 2"},
        ]
        target_level = 2
        results_display = filter_results_by_granularity(results_full, var_to_node, target_level)
        lower_level_allocations, _ = _compute_lower_level_allocation_totals(
            results_full,
            var_to_node,
            hierarchy_data,
            allocation_lookup,
            n_adults=2,
            n_children=1,
            target_level=target_level,
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
            target_level=target_level,
        )
        self.assertTrue(all(item["level"] <= target_level for item in results_display))
        self.assertEqual(len(display_on), len(results_display))
        level_row = display_on.loc[2]
        total_row = display_on.loc[0]
        for col in ["Shared %", "Child Intensity", "Shared $", "Exclusive (Adult) $", "Exclusive (Child) $"]:
            self.assertFalse(pd.isna(level_row[col]), f"{col} should be populated for level rows.")
            self.assertTrue(pd.isna(total_row[col]), f"{col} should be blank for total rows.")


if __name__ == "__main__":
    unittest.main()
