from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.ci import validate_standards as validation


class RepositoryStandardsTest(unittest.TestCase):
    @staticmethod
    def contract() -> dict:
        return {"domain": "payments", "version": "v1", "entity_name": "payment_transaction",
                "classification": "critical", "description": "Executed payment movement.",
                "ownership": {"business_owner": "Product Owner", "technical_steward": "Platform Lead",
                              "approval_model": "owner_and_steward_review"},
                "keys": {"primary_key": "payment_transaction_id"},
                "controls": {"financial_reporting_relevant": True, "fraud_decision_relevant": True,
                             "required_audit_fields_inherited": True},
                "fields": [{"name": "payment_transaction_id", "type": "string", "required": True,
                            "description": "Stable identifier."},
                           {"name": "transaction_status", "type": "string", "required": True,
                            "description": "Execution status.", "allowed_values": ["booked", "declined"]}]}

    def errors(self, payload: dict) -> set[str]:
        return {e["code"] for e in validation.validate_contract(
            "specs/payments/v1/payment_transaction.yaml", payload, validation.AUDIT_FIELDS)}

    def test_governed_metadata_and_audit_inheritance_are_accepted(self) -> None:
        self.assertFalse(self.errors(self.contract()))

    def test_missing_ownership_audit_and_status_values_are_blocked(self) -> None:
        payload = self.contract()
        del payload["ownership"]["business_owner"]
        payload["controls"]["required_audit_fields_inherited"] = False
        del payload["fields"][1]["allowed_values"]
        self.assertTrue({"contract_ownership", "audit_fields_missing", "status_values"}.issubset(self.errors(payload)))

    def test_identity_field_naming_duplicate_and_primary_key_drift_are_blocked(self) -> None:
        payload = self.contract()
        payload["entity_name"] = "wrong_entity"
        payload["fields"].append(copy.deepcopy(payload["fields"][0]))
        payload["fields"][1]["name"] = "InvalidName"
        payload["keys"]["primary_key"] = "missing_key"
        self.assertTrue({"contract_identity", "duplicate_field", "field_naming", "primary_key_missing"}.issubset(self.errors(payload)))

    def test_critical_contract_cannot_be_downgraded(self) -> None:
        payload = self.contract()
        payload["classification"] = "governed"
        self.assertIn("critical_classification", self.errors(payload))

    def test_non_mapping_or_unversioned_contract_fails(self) -> None:
        for name, payload in (("specs/payments/v1/payment_transaction.yaml", []),
                              ("specs/payments/version_one/payment_transaction.yaml", self.contract())):
            with self.subTest(name=name):
                self.assertEqual(validation.validate_contract(name, payload, validation.AUDIT_FIELDS)[0]["code"], "contract_shape")

    def test_markdown_parses_references_spaces_and_directories_but_ignores_code_and_web(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                '[Guide][ref]\n\n[ref]: <guides/My Guide.md>\n\n'
                '[Folder](guides/) [Root](/guides/My%20Guide.md#section) [Web](https://example.org/missing)\n\n'
                '`[code](missing.md)`\n\n```md\n[fenced](missing.md)\n```\n', encoding="utf-8")
            errors, count = validation.validate_links(root, "README.md", {"README.md", "guides/My Guide.md"})
            self.assertEqual(errors, [])
            self.assertEqual(count, 3)

    def test_existing_but_untracked_and_outside_markdown_targets_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "private.md").write_text("Not tracked")
            (root / "README.md").write_text('[Private](private.md) [Missing](missing.md) [Outside](../../outside.md)')
            errors, count = validation.validate_links(root, "README.md", {"README.md"})
            self.assertEqual((len(errors), count), (3, 3))
            self.assertNotIn("private.md", str(errors))

    def test_invalid_baseline_stops_standards_before_reading_source(self) -> None:
        with patch.object(validation, "validate_repository", return_value={"valid": False}), \
             patch.object(validation, "tracked_paths") as inventory:
            self.assertFalse(validation.validate_standards(validation.ROOT)["valid"])
            inventory.assert_not_called()


if __name__ == "__main__":
    unittest.main()
