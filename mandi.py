import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime


# -----------------------------
# SCRAPE LIVE MANDI PRICES
# -----------------------------
def fetch_live_mandi_prices(crop):
    """
    Scrapes Agmarknet for latest mandi prices of a crop
    """
    url = "https://agmarknet.gov.in/SearchCmmMkt.aspx"

    payload = {
        "ctl00$ddlCommodity": crop,
        "ctl00$ddlState": "0",
        "ctl00$ddlMarket": "0",
        "ctl00$txtDate": datetime.now().strftime("%d-%b-%Y"),
        "ctl00$btnSubmit": "Search"
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.post(url, data=payload, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", {"id": "cphBody_GridView1"})
    if table is None:
        return None

    rows = table.find_all("tr")[1:]
    data = []

    for row in rows:
        cols = [c.text.strip() for c in row.find_all("td")]
        if len(cols) >= 6:
            data.append({
                "mandi": cols[1],
                "price": float(cols[5]) if cols[5].isdigit() else None
            })

    df = pd.DataFrame(data).dropna()
    return df


# -----------------------------
# AGENT-3 LOGIC
# -----------------------------
def run_agent3(crop):
    crop = crop.strip().title()

    df = fetch_live_mandi_prices(crop)

    if df is None or df.empty:
        return {
            "crop": crop,
            "error": "Live mandi data unavailable",
            "recommendation": "Market data could not be fetched"
        }

    # Select best mandi
    best_row = df.loc[df["price"].idxmax()]

    # Simple trend logic (no heavy forecasting)
    avg_price = df["price"].mean()

    if best_row["price"] > avg_price:
        decision = "WAIT – Prices are higher than average"
    else:
        decision = "SELL – Prices may not improve soon"

    return {
        "crop": crop,
        "best_mandi": best_row["mandi"],
        "current_price": round(best_row["price"], 2),
        "average_price": round(avg_price, 2),
        "recommendation": decision,
        "data_source": "Agmarknet (Live)"
    }

if __name__ == "__main__":
    crop = input("Enter crop name: ")
    result = run_agent3(crop)

    print("\n📊 AGENT-3 OUTPUT")
    for k, v in result.items():
        print(f"{k}: {v}")
