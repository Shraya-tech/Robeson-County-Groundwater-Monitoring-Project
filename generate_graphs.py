import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

# --- 1. User Configuration ---
# IMPORTANT: Replace these with the EXACT sheet names from your Excel file.
# The names are case-sensitive.

EXCEL_FILE_NAME = 'data.xlsx'

well_sheet_names = [
    "Alamac", "Sammy Cox", "Ballard", "Bethel Hill", "Doc Henderson",
    "James Dial", "Knapdale", "Prospect", "Sam Nobel",
    "Orum Water Tower 1", "MW1", "MW2", "Landfill"
]

airport_sheet_names = ["KFAY", "KMEB", "KLBT"]

# --- 2. Data Loading from Excel Sheets ---
print(f"Step 1: Reading sheets from '{EXCEL_FILE_NAME}'...")

# Check if the Excel file exists before proceeding
if not os.path.exists(EXCEL_FILE_NAME):
    raise SystemExit(f"Fatal Error: The file '{EXCEL_FILE_NAME}' was not found. Make sure it's in the same folder as the script.")

# Load and combine rainfall data from airport sheets
all_rain_df = pd.DataFrame()
for sheet in airport_sheet_names:
    try:
        df = pd.read_excel(EXCEL_FILE_NAME, sheet_name=sheet, usecols=['Date', 'PRCP(inches)'])
        df['datetime'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['datetime'], inplace=True)
        df = df.set_index('datetime')
        
        if all_rain_df.empty:
            all_rain_df = df[['PRCP(inches)']]
        else:
            all_rain_df = all_rain_df.join(df[['PRCP(inches)']], how='outer', rsuffix=f'_{sheet}')
    except Exception as e:
        print(f"Warning: Could not process sheet '{sheet}'. Error: {e}")

if all_rain_df.empty:
    raise SystemExit("Fatal Error: No weather data could be loaded from the specified sheets.")

all_rain_df['combined_precip'] = all_rain_df.max(axis=1)
daily_rain = all_rain_df[['combined_precip']].resample('D').sum()

# Load and process all well data from their sheets
all_wells_df = pd.DataFrame()
for sheet in well_sheet_names:
    try:
        df = pd.read_excel(EXCEL_FILE_NAME, sheet_name=sheet, usecols=['Date', 'Pot Level'])
        df['datetime'] = pd.to_datetime(df['Date'], errors='coerce')
        df.dropna(subset=['datetime', 'Pot Level'], inplace=True)
        df = df.set_index('datetime')
        daily_level = df['Pot Level'].resample('D').mean().to_frame(name=sheet)
        if all_wells_df.empty:
            all_wells_df = daily_level
        else:
            all_wells_df = all_wells_df.join(daily_level, how='outer')
    except Exception as e:
        print(f"Warning: Could not process sheet '{sheet}'. Error: {e}")

# Merge the final rainfall and well data
merged_df = daily_rain.join(all_wells_df, how='inner').fillna(method='ffill').dropna()
print("Data preparation complete.")

# --- 3. Analysis and Visualization ---
print("\nStep 2: Generating graphs...")

# Function to create and save a bar chart
def create_bar_chart(data, title, filename):
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(14, 8))
    bars = ax.bar(data.index, data.values, color='#0077b6', zorder=2)
    ax.set_title(title, fontsize=18, pad=20)
    ax.set_ylabel('Correlation Coefficient', fontsize=12)
    ax.set_xlabel('Well Name (Sheet Name)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    ax.bar_label(bars, fmt='%.2f', padding=3, fontsize=10)
    ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.7)
    ax.set_ylim(0, max(0.5, data.max() * 1.15))
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.close()
    print(f"Saved: {filename}")

# Generate and save the maximum daily correlation graph
daily_corr_results = {}
for well_sheet in well_sheet_names:
    max_corr = 0
    for lag in range(31):
        current_corr = merged_df['combined_precip'].shift(lag).corr(merged_df[well_sheet])
        if not np.isnan(current_corr) and current_corr > max_corr:
            max_corr = current_corr
    daily_corr_results[well_sheet] = max_corr

daily_corr_series = pd.Series(daily_corr_results).sort_values(ascending=False)
create_bar_chart(daily_corr_series, 'Maximum Correlation Between Daily Rainfall and Well Levels', 'correlation_max_daily.png')

print("\n Analysis Complete! Your graph has been saved.")