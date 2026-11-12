"""Focused tests for the UN System Data Commons client; no live network required."""
import unittest
from unittest.mock import Mock, patch

import un_data_commons as un


class UNDataCommonsTests(unittest.TestCase):
    @patch("un_data_commons.requests.get")
    def test_indicator_resolution_uses_custom_get_endpoint(self, mock_get):
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "entities": [{
                    "node": "population",
                    "candidates": [{
                        "dcid": "Count_Person",
                        "metadata": {"sentence": "population count", "score": 0.9},
                        "typeOf": ["StatisticalVariable"],
                    }],
                }]
            },
        )
        result = un.resolve_indicators("population")
        self.assertEqual(result[0]["dcid"], "Count_Person")
        args, kwargs = mock_get.call_args
        self.assertTrue(args[0].endswith("/resolve"))
        self.assertIn(("resolver", "indicator"), kwargs["params"])

    @patch("un_data_commons.requests.get")
    def test_observation_parser_preserves_facet_provenance(self, mock_get):
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: {
                "byVariable": {
                    "Count_Person": {
                        "byEntity": {
                            "country/TZA": {
                                "orderedFacets": [{
                                    "facetId": "facet-1",
                                    "observations": [
                                        {"date": "2023", "value": 67000000}
                                    ],
                                }]
                            }
                        }
                    }
                },
                "facets": {
                    "facet-1": {
                        "importName": "ExampleDataset",
                        "provenanceUrl": "https://example.org/dataset",
                        "unit": "person",
                        "measurementMethod": "Census",
                        "observationPeriod": "P1Y",
                    }
                },
            },
        )
        frame, _ = un.fetch_observations(
            "country/TZA", "Count_Person", "ALL"
        )
        self.assertEqual(len(frame), 1)
        self.assertEqual(frame.iloc[0]["value"], 67000000)
        self.assertEqual(frame.iloc[0]["dataset"], "ExampleDataset")
        self.assertEqual(frame.iloc[0]["unit"], "person")
        params = mock_get.call_args.kwargs["params"]
        self.assertIn(("date", ""), params)
        self.assertIn(("select", "facet"), params)

    def test_empty_query_returns_no_candidates(self):
        self.assertEqual(un.resolve_indicators("  "), [])

    def test_missing_entity_is_rejected_before_request(self):
        with self.assertRaises(ValueError):
            un.fetch_observations("", "Count_Person")


if __name__ == "__main__":
    unittest.main()
