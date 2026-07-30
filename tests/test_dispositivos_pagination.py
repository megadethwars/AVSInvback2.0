import sys
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, ".")

from src.fastapi_app import app
from src.controllers.fastapi import dispositivos_controller as dc


def _build_row(idx: int) -> dict:
    return {
        "id": idx,
        "codigo": f"AV{idx:05d}",
        "producto": "CCU",
        "marca": "SONY",
        "modelo": "HDCU-2500",
        "serie": str(100000 + idx),
        "lugar": "LCDLF TELEMUNDO T6",
        "descripcion": "Operacion",
    }


DATASET = [_build_row(i) for i in range(1, 40)]  # 39 rows


class TestDispositivosPagination(unittest.TestCase):
    def setUp(self) -> None:
        def _override_get_db():
            yield None

        app.dependency_overrides[dc.get_db] = _override_get_db
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_offset_behaves_as_page_index(self) -> None:
        captured_offsets: list[int] = []

        def fake_filter_fields(db, offset, limit, search_value="", in_storage=0, minimal=False):
            captured_offsets.append(offset)
            return DATASET[offset : offset + limit], len(DATASET)

        with patch.object(dc.DispositivosModelSchema, "filter_fields", side_effect=fake_filter_fields):
            r0 = self.client.get(
                "/api/v1/dispositivos/filterdeviceFields",
                params={"limit": 30, "offset": 0, "value": "HDCU"},
            )
            r1 = self.client.get(
                "/api/v1/dispositivos/filterdeviceFields",
                params={"limit": 30, "offset": 1, "value": "HDCU"},
            )

        self.assertEqual(r0.status_code, 200)
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(captured_offsets, [0, 30])

    def test_pages_do_not_overlap_for_limit_30(self) -> None:
        def fake_filter_fields(db, offset, limit, search_value="", in_storage=0, minimal=False):
            return DATASET[offset : offset + limit], len(DATASET)

        with patch.object(dc.DispositivosModelSchema, "filter_fields", side_effect=fake_filter_fields):
            page0 = self.client.get(
                "/api/v1/dispositivos/filterdeviceFields",
                params={"limit": 30, "offset": 0, "value": "HDCU"},
            )
            page1 = self.client.get(
                "/api/v1/dispositivos/filterdeviceFields",
                params={"limit": 30, "offset": 1, "value": "HDCU"},
            )

        body0 = page0.json()
        body1 = page1.json()

        self.assertEqual(page0.status_code, 200)
        self.assertEqual(page1.status_code, 200)
        self.assertEqual(len(body0["data"]), 30)
        self.assertEqual(len(body1["data"]), 9)
        self.assertEqual(body0["total_rows"], 39)
        self.assertEqual(body1["total_rows"], 39)

        ids0 = {item["id"] for item in body0["data"]}
        ids1 = {item["id"] for item in body1["data"]}
        self.assertTrue(ids0.isdisjoint(ids1))


if __name__ == "__main__":
    unittest.main()
