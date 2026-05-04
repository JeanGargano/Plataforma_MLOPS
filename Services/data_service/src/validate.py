import pandas as pd
import yaml
import sys


def load_params(path: str = "/app/params.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def validate(df: pd.DataFrame, params: dict) -> None:
    """
    Valida calidad del dataset después de la ingesta.
    Lanza sys.exit(1) si falla alguna validación.
    """
    v      = params["validate"]
    p      = params["preprocess"]
    errors = []

    # 1. Cantidad mínima de filas
    if len(df) < v["min_rows"]:
        errors.append(f"Pocas filas: {len(df)}, mínimo: {v['min_rows']}")

    # 2. Columnas requeridas
    required = p["numerical_features"] + p["categorical_features"] + [p["target_column"]]
    missing  = [c for c in required if c not in df.columns]
    if missing:
        errors.append(f"Columnas faltantes: {missing}")

    # 3. Nulos excesivos por columna
    null_pct = df.isnull().mean()
    excess   = null_pct[null_pct > v["max_null_pct"]].index.tolist()
    if excess:
        errors.append(f"Columnas con >{v['max_null_pct']*100:.0f}% nulos: {excess}")

    # 4. Rango válido del target
    target = p["target_column"]
    if target in df.columns:
        out_of_range = df[
            (df[target] < v["min_consumo"]) | (df[target] > v["max_consumo"])
        ]
        if len(out_of_range) > 0:
            errors.append(
                f"{len(out_of_range)} filas con {target} fuera de "
                f"[{v['min_consumo']}, {v['max_consumo']}]"
            )

    # 5. Valores únicos en categóricas
    for col in p["categorical_features"]:
        if col in df.columns and df[col].nunique() == 0:
            errors.append(f"Columna '{col}' sin valores únicos")

    # Reporte
    if errors:
        print("VALIDACION FALLIDA:")
        for e in errors:
            print(f"  x {e}")
        sys.exit(1)
    else:
        target_col = p["target_column"]
        print("Validacion OK:")
        print(f"  Filas    : {len(df)}")
        print(f"  Columnas : {df.columns.tolist()}")
        print(f"  Target   : min={df[target_col].min():.2f} | "
              f"max={df[target_col].max():.2f} | "
              f"media={df[target_col].mean():.2f}")


if __name__ == "__main__":
    params = load_params()
    df     = pd.read_csv(params["data"]["raw_path"])
    validate(df, params)