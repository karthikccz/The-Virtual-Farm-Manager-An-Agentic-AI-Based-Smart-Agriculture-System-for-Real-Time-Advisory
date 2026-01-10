import pandas as pd
import requests
from prophet import Prophet

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
FALLBACK_CSV = r"Daily Price (1).csv"

# -------------------------------------------------
# LIVE MANDI FETCH (BEST-EFFORT)
# -------------------------------------------------
def fetch_live_mandi_prices(crop):
    """
    Attempts to fetch live mandi prices.
    Returns None if unavailable (very common).
    """
    try:
        # NOTE: Most govt sites block scraping.
        # This is a placeholder to show intent.
        url = "https://example-mandi-api.com/prices"  # dummy
        params = {"commodity": crop}

        r = requests.get(url, params=params, timeout=5)
        r.raise_for_status()

        data = r.json()
        if not data:
            return None

        return data

    except Exception:
        return None


# -------------------------------------------------
# FALLBACK DATASET LOGIC
# -------------------------------------------------
def load_and_clean_data(csv_path):
    df = pd.read_csv(csv_path)

    df["Price Date"] = pd.to_datetime(
        df["Price Date"], format="%d-%m-%Y", errors="coerce"
    )
    df["Modal Price"] = pd.to_numeric(df["Modal Price"], errors="coerce")

    df = df.dropna(
        subset=["Price Date", "Modal Price", "Commodity", "Market"]
    )

    return df


def select_best_mandi(df, crop):
    crop_df = df[df["Commodity"].str.lower() == crop.lower()]

    if crop_df.empty:
        raise ValueError("No data found for crop")

    latest = (
        crop_df.sort_values("Price Date")
        .groupby("Market")
        .tail(1)
    )

    best = latest.loc[latest["Modal Price"].idxmax()]
    return best["Market"], best["Modal Price"]


def forecast_price(df, crop, mandi):
    mandi_df = df[
        (df["Commodity"].str.lower() == crop.lower())
        & (df["Market"] == mandi)
    ].sort_values("Price Date")

    if mandi_df.shape[0] < 2:
        return None, None

    prophet_df = mandi_df.rename(
        columns={"Price Date": "ds", "Modal Price": "y"}
    )[["ds", "y"]]

    model = Prophet(daily_seasonality=True)
    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=7)
    forecast = model.predict(future)

    current = prophet_df.iloc[-1]["y"]
    predicted = forecast.iloc[-7:]["yhat"].mean()

    return current, predicted


# -------------------------------------------------
# MAIN AGENT-3 (HYBRID)
# -------------------------------------------------
def run_agent3(crop):
    """
    Hybrid Agent-3:
    - Try live mandi data
    - If unavailable → fallback to dataset
    """

    # 1️⃣ TRY LIVE DATA
    live_data = fetch_live_mandi_prices(crop)

    if live_data:
        return {
            "crop": crop,
            "best_mandi": live_data["mandi"],
            "current_price": live_data["price"],
            "predicted_price": live_data["predicted"],
            "recommendation": live_data["decision"],
            "data_source": "live"
        }

    # 2️⃣ FALLBACK TO DATASET (ALWAYS WORKS)
    df = load_and_clean_data(FALLBACK_CSV)
    mandi, today_price = select_best_mandi(df, crop)
    current, predicted = forecast_price(df, crop, mandi)

    if predicted is None:
        decision = "SELL / WAIT unavailable (insufficient data)"
        predicted = "N/A"
    elif predicted > current:
        decision = "WAIT – Prices likely to increase"
    else:
        decision = "SELL NOW – Prices may fall"

    return {
        "crop": crop,
        "best_mandi": mandi,
        "current_price": round(today_price, 2),
        "predicted_price": round(predicted, 2) if predicted != "N/A" else predicted,
        "recommendation": decision,
        "data_source": "fallback_dataset"
    }


# -------------------------------------------------
# CLI TEST
# -------------------------------------------------
if __name__ == "__main__":
    crop = input("Enter crop name: ")
    result = run_agent3(crop)

    print("\n📊 AGENT-3 OUTPUT")
    for k, v in result.items():
        print(f"{k}: {v}")
