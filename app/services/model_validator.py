from pathlib import Path
import json


class ModelValidator:

    def validate_json_file(self, file_path: Path):

        if not file_path.exists():
            return {
                "exists": False,
                "record_count": 0,
                "valid": False,
            }

        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return {
            "exists": True,
            "record_count": len(data),
            "valid": True,
        }

    def validate_model(self, financial_model_folder: Path):

        files = {
            "fact_gl": "fact_gl.json",
            "dim_account": "dim_account.json",
            "dim_fund": "dim_fund.json",
            "dim_donor": "dim_donor.json",
            "dim_program": "dim_program.json",
            "dim_category": "dim_category.json",
            "dim_budget_line": "dim_budget_line.json",
            "dim_donor_line": "dim_donor_line.json",
            "dim_calendar": "dim_calendar.json",
        }

        results = {}

        for name, filename in files.items():

            results[name] = self.validate_json_file(
                financial_model_folder / filename
            )

        return results