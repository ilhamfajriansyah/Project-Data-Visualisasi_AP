from io import BytesIO

import pandas as pd


EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def dataframe_to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Export") -> bytes:
    output = BytesIO()
    safe_sheet_name = str(sheet_name or "Export")[:31]

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df = df.copy()
        export_df.to_excel(writer, index=False, sheet_name=safe_sheet_name)
        worksheet = writer.sheets[safe_sheet_name]
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions

        for cell in worksheet[1]:
            cell.font = cell.font.copy(bold=True)
            cell.alignment = cell.alignment.copy(horizontal="center")

        for column_cells in worksheet.columns:
            max_length = 0
            column_letter = column_cells[0].column_letter
            for cell in column_cells:
                value = "" if cell.value is None else str(cell.value)
                max_length = max(max_length, len(value))
            worksheet.column_dimensions[column_letter].width = min(max(max_length + 2, 12), 42)

    return output.getvalue()