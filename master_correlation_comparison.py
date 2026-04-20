import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from geopy.distance import great_circle

# --- 1. CONFIGURATION ---
EXCEL_FILE_NAME = "data.xlsx"
WELLS = ["Alamac", "Sammy Cox", "Ballard", "Bethel Hill", "Doc Henderson", 
         "James Dial", "Knapdale", "Prospect", "Sam Nobel", 
         "Orum Water Tower 1", "MW1", "MW2", "Landfill"]
AIRPORTS = {"KLBT": (34.6113, -79.0595), "KMEB": (34.7965, -79.3685), "KFAY": (34.9911, -78.8871)}
WELL_COORDS = {
    "Alamac": (34.59137, -79.008), "Ballard": (34.531530, -79.291302),
    "Bethel Hill": (34.752355, -79.078892), "Doc Henderson": (34.780860, -79.287346),
    "James Dial": (34.664970, -79.280639), "Knapdale": (34.890614, -79.030412),
    "Landfill": (34.790169, -78.907980), "MW1": (34.692699, -79.199682),
    "MW2": (34.692472, -79.199518), "Orum Water Tower 1": (34.487847, -79.024239),
    "Prospect": (34.730658, -79.231222), "Sam Nobel": (34.689224, -78.972599),
    "Sammy Cox": (34.649335, -79.047803)
}

def get_closest_airport(well_name):
    distances = {name: great_circle(WELL_COORDS[well_name], loc).miles for name, loc in AIRPORTS.items()}
    return min(distances, key=distances.get)

def get_max_corr(df, rain_col, level_col, lags, threshold=0):
    corrs = []
    for lag in range(lags + 1):
        temp = df.copy()
        temp['rain_lagged'] = temp[rain_col].shift(lag)
        if threshold > 0:
            temp = temp[temp['rain_lagged'] >= threshold]
        if len(temp) > 5:
            c = temp['rain_lagged'].corr(temp[level_col])
            if not np.isnan(c): corrs.append(abs(c))
    return max(corrs) if corrs else 0

# --- 2. PROCESSING ---
results = []
for well in WELLS:
    print(f"Analyzing {well}...")
    airport = get_closest_airport(well)
    try:
        w_df = pd.read_excel(EXCEL_FILE_NAME, sheet_name=well, usecols=['Date', 'Pot Level'])
        a_df = pd.read_excel(EXCEL_FILE_NAME, sheet_name=airport, usecols=['Date', 'PRCP(inches)'])
        w_df['Date'] = pd.to_datetime(w_df['Date'])
        a_df['Date'] = pd.to_datetime(a_df['Date'])
        df = pd.merge(w_df, a_df, on='Date').dropna()

        # 1. Daily Baseline (90-day lag)
        daily = get_max_corr(df, 'PRCP(inches)', 'Pot Level', 90)
        # 2. 0.1" Filter
        filt_01 = get_max_corr(df, 'PRCP(inches)', 'Pot Level', 90, 0.1)
        # 3. 0.2" Significant
        filt_02 = get_max_corr(df, 'PRCP(inches)', 'Pot Level', 90, 0.2)
        # 4. Weekly
        df_w = df.set_index('Date').resample('W').agg({'PRCP(inches)': 'sum', 'Pot Level': 'mean'}).dropna()
        weekly = get_max_corr(df_w, 'PRCP(inches)', 'Pot Level', 12)

        results.append({"Well": well, "Daily": daily, "0.1 Filter": filt_01, "0.2 Significant": filt_02, "Weekly": weekly})
    except Exception as e:
        print(f" Error: {e}")

# --- 3. VISUALIZATION ---
df_res = pd.DataFrame(results).set_index("Well").sort_values("Weekly", ascending=False)

# Define a clean, professional color palette
colors = ['#bbdefb', '#64b5f6', '#2196f3', '#0d47a1']

ax = df_res.plot(kind='bar', figsize=(15, 8), width=0.8, color=colors)

# Title and dynamic subtitle for the 2018-2024 period
plt.title("Precipitation Comparison of 4 Analysis Methods", fontsize=20, pad=35)
plt.text(0.5, 1.02, "Study Period: 2018 – 2024 | Robeson County Groundwater Research", 
         fontsize=12, color='gray', ha='center', transform=ax.transAxes)

plt.ylabel("Correlation Coefficient (Absolute Value)", fontsize=12)
plt.xlabel("Robeson County Well", fontsize=12)
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.3)
plt.legend(title="Analysis Method", frameon=True, shadow=True)

plt.tight_layout()
plt.savefig("master_correlation_comparison.png", dpi=300)
print("Updated graph saved as 'master_correlation_comparison.png'")