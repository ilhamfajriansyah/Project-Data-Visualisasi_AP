import pandas as pd
try:
    df = pd.read_excel(r"d:\angkasapura\Mei dummy.xlsx")
    with open(r"d:\angkasapura\Project-Data-Visualisasi_AP\columns_info.txt", "w", encoding="utf-8") as f:
        f.write(", ".join(df.columns))
except Exception as e:
    with open(r"d:\angkasapura\Project-Data-Visualisasi_AP\columns_info.txt", "w", encoding="utf-8") as f:
        f.write(str(e))
