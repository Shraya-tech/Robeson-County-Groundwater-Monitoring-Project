import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Configuration - Ensure these match your Excel file exactly
EXCEL_FILE = 'data.xlsx'
WELL_NAME = 'Doc Henderson'
AIRPORT_NAME = 'KMEB' # Closest airport to Doc Henderson

def create_regression_visual():
    # 1. Load Data
    well_df = pd.read_excel(EXCEL_FILE, sheet_name=WELL_NAME)
    air_df = pd.read_excel(EXCEL_FILE, sheet_name=AIRPORT_NAME)

    # 2. Standardize Columns
    well_df.columns = [str(c).strip() for c in well_df.columns]
    air_df.columns = [str(c).strip() for c in air_df.columns]
    well_df.rename(columns={'Date': 'date', 'Pot Level': 'level'}, inplace=True)
    air_df.rename(columns={'Date': 'date', 'PRCP(inches)': 'rain'}, inplace=True)

    # 3. Weekly Resampling
    well_df['date'] = pd.to_datetime(well_df['date'])
    air_df['date'] = pd.to_datetime(air_df['date'])
    df = pd.merge(well_df[['date', 'level']], air_df[['date', 'rain']], on='date').dropna()
    df.set_index('date', inplace=True)
    
    # Weekly aggregation (Total rain per week, Average level per week)
    weekly_df = df.resample('W').agg({'rain': 'sum', 'level': 'mean'}).dropna()

    # 4. Find Optimal Lag (Best correlation within 12 weeks)
    best_lag = 0
    max_corr = 0
    for lag in range(13):
        corr = weekly_df['rain'].shift(lag).corr(weekly_df['level'])
        if abs(corr) > abs(max_corr):
            max_corr = corr
            best_lag = lag

    # 5. Prepare final data with the best lag
    weekly_df['rain_lagged'] = weekly_df['rain'].shift(best_lag)
    final_df = weekly_df.dropna()

    # 6. Calculate Linear Regression
    slope, intercept, r_val, p_val, std_err = stats.linregress(final_df['rain_lagged'], final_df['level'])

    # 7. Visualization
    plt.figure(figsize=(10, 7))
    sns.regplot(x='rain_lagged', y='level', data=final_df, 
                scatter_kws={'alpha':0.5, 'color':'#0077b6', 's':50}, 
                line_kws={'color':'#d62728', 'label': f'Trend: y={slope:.3f}x + {intercept:.2f}'})
    
    plt.title(f"Weekly Recharge Signal: {WELL_NAME} (Lag: {best_lag} Weeks)", fontsize=16, pad=20)
    plt.xlabel(f"Total Weekly Precipitation (Inches) - Shifted {best_lag} Weeks", fontsize=12)
    plt.ylabel("Mean Weekly Potentiometric Level (ft)", fontsize=12)
    
    # Add Statistical Box
    stats_label = f"Correlation (r): {r_val:.3f}\nR-squared: {r_val**2:.3f}\nP-value: {p_val:.4f}"
    plt.annotate(stats_label, xy=(0.05, 0.95), xycoords='axes fraction', 
                 bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="gray", alpha=0.8),
                 verticalalignment='top', fontsize=11)

    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig('doc_henderson_regression.png', dpi=300)
    print("Graph saved as 'doc_henderson_regression.png'")

if __name__ == "__main__":
    create_regression_visual()