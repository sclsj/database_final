import unittest
from unittest.mock import Mock
import sys
import types

mysql_module = types.ModuleType("mysql")
mysql_module.connector = Mock()
sys.modules.setdefault("mysql", mysql_module)
sys.modules.setdefault("mysql.connector", mysql_module.connector)

import csv_converter


class CsvConverterDefaultModeTests(unittest.TestCase):
    def test_is_default_export_mode_true_for_defaults(self):
        self.assertTrue(
            csv_converter.is_default_export_mode(
                columns=list(csv_converter.DEFAULT_COLUMNS),
                author_country_source=csv_converter.DEFAULT_AUTHOR_COUNTRY_SOURCE,
                list_separator=csv_converter.DEFAULT_LIST_SEPARATOR,
                within_author_separator=csv_converter.DEFAULT_WITHIN_AUTHOR_SEPARATOR,
            )
        )

    def test_is_default_export_mode_false_when_options_change(self):
        self.assertFalse(
            csv_converter.is_default_export_mode(
                columns=list(csv_converter.DEFAULT_COLUMNS),
                author_country_source="record",
                list_separator=csv_converter.DEFAULT_LIST_SEPARATOR,
                within_author_separator=csv_converter.DEFAULT_WITHIN_AUTHOR_SEPARATOR,
            )
        )


class CsvConverterDefaultQueryTests(unittest.TestCase):
    def test_fetch_default_export_rows_runs_one_query_and_maps_columns(self):
        cursor = Mock()
        cursor.fetchall.return_value = [
            (
                101,
                "ier",
                "Title A",
                2020,
                "Health",
                "Abstract",
                "RCT",
                "Method",
                "Author One|Author Two",
                "Inst 1|Inst 2",
                "Country 1|Country 2",
                "Kenya|Uganda",
                "Africa",
                "English",
                "Agency 1",
            )
        ]

        rows = csv_converter.fetch_default_export_rows(
            cursor=cursor,
            study_types=["ier", "srr"],
            list_separator="|",
            within_author_separator=";",
        )

        cursor.execute.assert_called_once()
        query, params = cursor.execute.call_args[0]
        self.assertIn("FROM records r", query)
        self.assertIn("LEFT JOIN (", query)
        self.assertEqual(
            params,
            ["|", "|", "|", ";", ";", "|", "|", "|", "|", "ier", "srr"],
        )
        self.assertEqual(rows[0]["record_id"], 101)
        self.assertEqual(rows[0]["authors"], "Author One|Author Two")
        self.assertEqual(rows[0]["research_funding_agencies"], "Agency 1")

    def test_fetch_default_export_rows_raises_on_unexpected_shape(self):
        cursor = Mock()
        cursor.fetchall.return_value = [(1, "ier")]

        with self.assertRaises(ValueError):
            csv_converter.fetch_default_export_rows(
                cursor=cursor,
                study_types=["ier"],
                list_separator="|",
                within_author_separator=";",
            )


if __name__ == "__main__":
    unittest.main()
