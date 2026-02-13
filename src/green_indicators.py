import pandas as pd


def green_financing_share(df, **params):
    total = df["EAD_EUR"].sum()
    if total == 0:
        return 0.0

    # Exemple simple : secteurs contenant "renewable"
    green_mask = df["sector"].str.lower().str.contains("renewable", na=False)

    green_ead = df.loc[green_mask, "EAD_EUR"].sum()

    return green_ead / total


def green_bond_share(df, **params):
    total = df["EAD_EUR"].sum()
    if total == 0:
        return 0.0

    # Proxy académique : maturité > 10 ans
    green_bonds = df.loc[df["maturity_years"] > 10, "EAD_EUR"].sum()

    return green_bonds / total


def sbti_client_share(df, **params):
    total_clients = len(df)
    if total_clients == 0:
        return 0.0

    # Proxy académique : PD faible
    aligned_clients = df.loc[df["PD_base"] < 0.02].shape[0]

    return aligned_clients / total_clients
