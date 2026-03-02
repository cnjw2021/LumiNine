from __future__ import annotations

from typing import Any, Dict, List


class AuspiciousDatesPresenter:
    """Auspicious dates view-model builder for UI/PDF."""

    def enrich_response(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        moving_dates = raw.get("moving_dates", [])
        water_dates = raw.get("water_drawing_dates", [])
        return {
            **raw,
            "moving_table": self._build_table(moving_dates, include_times=False),
            "water_drawing_table": self._build_table(water_dates, include_times=True),
        }

    def _build_table(self, date_list: List[Dict[str, Any]], include_times: bool) -> List[Dict[str, Any]]:
        direction_order_jp = ["東", "西", "南", "北", "北東", "北西", "南東", "南西"]
        table: Dict[int, Dict[int, Dict[str, List[tuple[int, str]]]]] = {}
        header_sets: Dict[int, set] = {}

        for item in date_list:
            date_str = item["date"]
            year = int(date_str[0:4])
            month = int(date_str[5:7])
            day = int(date_str[8:10])
            if year not in table:
                table[year] = {}
                header_sets[year] = set()
            if month not in table[year]:
                table[year][month] = {}
            time_text = ""
            if include_times:
                time_text = (item.get("auspicious_times") or [{}])[0].get("time", "")
            for direction in item.get("auspicious_directions", []):
                header_sets[year].add(direction)
                if direction not in table[year][month]:
                    table[year][month][direction] = []
                label = f"{day}日({time_text})" if include_times and time_text else f"{day}日"
                table[year][month][direction].append((day, label))

        result: List[Dict[str, Any]] = []
        for year in sorted(table.keys()):
            headers = [d for d in direction_order_jp if d in header_sets[year]]
            headers += sorted([d for d in header_sets[year] if d not in headers])
            rows = []
            for month in sorted(table[year].keys()):
                cells: Dict[str, str] = {}
                for direction in headers:
                    entries = table[year][month].get(direction, [])
                    if entries:
                        entries_sorted = sorted(entries, key=lambda x: x[0])
                        cells[direction] = ", ".join([label for _, label in entries_sorted])
                rows.append({
                    "month": month,
                    "cells": cells,
                })
            result.append({
                "year": year,
                "headers": headers,
                "rows": rows,
            })
        return result
