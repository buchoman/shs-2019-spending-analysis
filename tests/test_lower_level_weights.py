import unittest

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
        )

        shared_pct_off = display_off.loc[0, "Shared %"]
        shared_pct_on = display_on.loc[0, "Shared %"]

        self.assertNotEqual(shared_pct_off, shared_pct_on)


if __name__ == "__main__":
    unittest.main()
