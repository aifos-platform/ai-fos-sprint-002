import json
from pathlib import Path


class FactGLService:
    """
    Handles saving the General Ledger fact table.
    """

    @staticmethod
    def save_fact_gl(
        financial_model_folder: Path,
        transactions: list,
    ) -> Path:

        financial_model_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            financial_model_folder
            / "fact_gl.json"
        )

        with output_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                transactions,
                file,
                indent=4,
                ensure_ascii=False,
                default=str,
            )

        return output_file