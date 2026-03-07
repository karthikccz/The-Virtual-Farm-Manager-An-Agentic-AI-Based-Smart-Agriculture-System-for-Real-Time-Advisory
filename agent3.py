import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from prophet import Prophet


# ------------------------------------------------
# DATASET PATH
# ------------------------------------------------

DATASET_PATH = r"C:\Users\karth\Desktop\MAJOR\telangana_mandi_prices_dataset.csv"


# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

def load_data():

    df = pd.read_csv(DATASET_PATH)

    df["Price Date"] = pd.to_datetime(df["Price Date"], format="%d-%m-%Y")

    df["Modal Price"] = pd.to_numeric(df["Modal Price"])
    df["Arrival Quantity"] = pd.to_numeric(df["Arrival Quantity"])

    return df


# ------------------------------------------------
# DEMAND SUPPLY INDEX
# ------------------------------------------------

def demand_supply_analysis(df):

    df["DemandSupplyIndex"] = df["Modal Price"] / (df["Arrival Quantity"] + 1)

    return df


# ------------------------------------------------
# BEST MARKET SELECTION
# ------------------------------------------------

def select_best_mandi(df, crop):

    crop_df = df[df["Commodity"].str.lower() == crop.lower()]

    latest = crop_df.sort_values("Price Date").groupby("Market").tail(1)

    best = latest.loc[latest["Modal Price"].idxmax()]

    return best["Market"], best["Modal Price"]


# ------------------------------------------------
# PRICE FORECAST USING PROPHET
# ------------------------------------------------

def forecast_price(df, crop, mandi):

    mandi_df = df[
        (df["Commodity"].str.lower() == crop.lower()) &
        (df["Market"] == mandi)
    ].sort_values("Price Date")

    prophet_df = mandi_df.rename(
        columns={"Price Date": "ds", "Modal Price": "y"}
    )[["ds", "y"]]

    model = Prophet(daily_seasonality=True)

    model.fit(prophet_df)

    future = model.make_future_dataframe(periods=7)

    forecast = model.predict(future)

    current_price = prophet_df.iloc[-1]["y"]

    predicted_price = forecast.iloc[-7:]["yhat"].mean()

    return current_price, predicted_price


# ------------------------------------------------
# SIMPLE PRICE TREND GRAPH
# ------------------------------------------------

def plot_price_trend(df, crop):

    crop_df = df[df["Commodity"].str.lower() == crop.lower()]

    # average price per day
    daily_avg = crop_df.groupby("Price Date")["Modal Price"].mean().reset_index()

    plt.figure(figsize=(10,5))

    plt.plot(daily_avg["Price Date"], daily_avg["Modal Price"])

    plt.title(f"{crop} Price Trend")

    plt.xlabel("Date")
    plt.ylabel("Average Price")

    ax = plt.gca()

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()


# ------------------------------------------------
# DEMAND SUPPLY TREND GRAPH
# ------------------------------------------------

def plot_demand_supply(df, crop):

    crop_df = df[df["Commodity"].str.lower() == crop.lower()]

    daily_avg = crop_df.groupby("Price Date")["DemandSupplyIndex"].mean().reset_index()

    plt.figure(figsize=(10,5))

    plt.plot(daily_avg["Price Date"], daily_avg["DemandSupplyIndex"])

    plt.title(f"{crop} Demand-Supply Trend")

    plt.xlabel("Date")
    plt.ylabel("Demand-Supply Index")

    ax = plt.gca()

    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()


# ------------------------------------------------
# MAIN MARKET AGENT
# ------------------------------------------------
def run_agent3(crop):

    df = load_data()

    df = demand_supply_analysis(df)

    mandi, today_price = select_best_mandi(df, crop)

    current, predicted = forecast_price(df, crop, mandi)

    if predicted > current:
        decision = "WAIT – Demand expected to increase"
    else:
        decision = "SELL NOW – Supply likely high"

    # Generate graphs
    plot_price_trend(df, crop)
    plot_demand_supply(df, crop)

    return {

        "crop": crop,
        "best_mandi": mandi,
        "current_price": round(current,2),
        "predicted_price": round(predicted,2),
        "recommendation": decision

    }


# ------------------------------------------------
# TEST RUN
# ------------------------------------------------

if __name__ == "__main__":

    crop = input("Enter crop name: ")

    result = run_market_agent(crop)

    print("\n📊 MARKET AGENT OUTPUT\n")

    for k,v in result.items():
        print(k,":",v)
