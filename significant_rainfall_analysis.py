import pandas as pd
import numpy as np
from geopy.distance import great_circle

# --- 1. CONFIGURATION ---
RAINFALL_THRESHOLD_INCHES = 0.2

# --- 2. USER COORDINATES (High Precision) ---
well_coordinates = {
    "Alamac": (34.59137, -79.008),
    "Ballard": (34.531530, -79.291302),
    "Bethel Hill": (34.752355, -79.078892),
    "Doc Henderson": (34.780860, -79.287346),
    "James Dial": (34.664970, -79.280639),
    "Knapdale": (34.890614, -79.030412),
    "Landfill": (34.790169, -78.907980),
    "MW1": (34.692699, -79.199682),
    "MW2": (34.692472, -79.199518),
    "Orum Water Tower 1": (34.487847, -79.024239),
    "Prospect": (34.730658, -79.231222),
    "Sam Nobel": (34.689224, -78.972599),
    "Sammy Cox": (34.649335, -79.047803),
}

airport_coordinates = {
    "KLBT": (34.6113, -79.0595),
    "KMEB": (34.7965, -79.3685),
    "KFAY": (34.9911, -78.8871),
}

# --- 3. FILE AND SHEET NAME CONFIGURATION ---
excel_file_name = "RCGMP_data.xlsx"
sheet_name_map = {
    "Alamac": "Alamac", "Ballard": "Ballard", "Bethel Hill": "Bethel Hill",
    "Doc Henderson": "Doc Henderson", "James Dial": "James Dial", "Knapdale": "Knapdale",
    "Landfill": "Landfill", "MW1": "MW1", "MW2": "MW2",
    "Orum Water Tower 1": "Orum Water Tower 1", "Prospect": "Prospect",
    "Sam Nobel": "Sam Nobel", "Sammy Cox": "Sammy Cox",
    "KLBT": "KLBT", "KMEB": "KMEB", "KFAY": "KFAY",
}


def find_closest_airport(well_coords, airport_coords):
    distances = {name: great_circle(well_coords, ap_coords).miles for name, ap_coords in airport_coords.items()}
    closest_airport = min(distances, key=distances.get)
    return closest_airport, distances[closest_airport]


def clean_dataframe(df, is_well_data=True):
    """A robust function to clean and standardize either well or airport dataframes."""
    df.columns = [str(col).strip() for col in df.columns]
    
    if is_well_data:
        df.rename(columns={'Timestamp': 'date', 'Date': 'date', 'Value': 'well_level', 'Pot Level': 'well_level'}, inplace=True, errors='ignore')
        df['date'] = pd.to_datetime(df.get('date'), errors='coerce')
        df['well_level'] = pd.to_numeric(df.get('well_level'), errors='coerce')
        return df[['date', 'well_level']].dropna()
    else: # Is airport data
        df.rename(columns={'DATE': 'date', 'Date': 'date', 'PRCP': 'rainfall', 'PRCP (inches)': 'rainfall'}, inplace=True, errors='ignore')
        df['date'] = pd.to_datetime(df.get('date'), errors='coerce')
        df['rainfall'] = pd.to_numeric(df.get('rainfall'), errors='coerce')
        return df[['date', 'rainfall']].dropna()


def analyze_well_data(excel_file, well_sheet, airport_sheet):
    try:
        well_df = pd.read_excel(excel_file, sheet_name=well_sheet)
        airport_df = pd.read_excel(excel_file, sheet_name=airport_sheet)

        # Use the robust cleaning function
        well_df_cleaned = clean_dataframe(well_df, is_well_data=True)
        airport_df_cleaned = clean_dataframe(airport_df, is_well_data=False)
        
        # Merge the cleaned dataframes
        df = pd.merge(well_df_cleaned, airport_df_cleaned, on='date', how='inner').set_index('date')

        if df.empty: return None, None

        max_lag_days = 90
        correlations = {}
        for lag in range(max_lag_days + 1):
            df['lagged_rainfall'] = df['rainfall'].shift(lag)
            
            significant_rain_df = df[df['lagged_rainfall'] >= RAINFALL_THRESHOLD_INCHES].dropna()

            if len(significant_rain_df) > 10: # Require at least 10 data points for a meaningful correlation
                corr = significant_rain_df['lagged_rainfall'].corr(significant_rain_df['well_level'])
                if not np.isnan(corr):
                    correlations[lag] = corr
        
        if not correlations: return None, None
        
        optimal_lag = max(correlations, key=lambda k: abs(correlations[k]))
        max_corr = correlations[optimal_lag]
        return optimal_lag, max_corr

    except Exception as e:
        print(f"  ERROR processing sheets '{well_sheet}' or '{airport_sheet}': {e}")
        return None, None


def main():
    print(f"--- RCGMP Analysis (Significant Rainfall >= {RAINFALL_THRESHOLD_INCHES} inches) ---")
    results_list = []
    well_to_airport_map = {name: find_closest_airport(coords, airport_coordinates) for name, coords in well_coordinates.items()}

    print("\n--- Running Correlation Analysis ---")
    for well_name, (airport_name, distance) in well_to_airport_map.items():
        print(f"Analyzing: {well_name} (Closest airport: {airport_name}, {distance:.2f} miles)")
        well_sheet = sheet_name_map.get(well_name)
        airport_sheet = sheet_name_map.get(airport_name)
        
        result_data = {'Well Name': well_name, 'Closest Airport': airport_name, 'Distance (Miles)': round(distance, 2),
                       'Optimal Lag (Days)': 'N/A', 'Max Correlation': 'N/A'}

        if well_sheet and airport_sheet:
            lag, corr = analyze_well_data(excel_file_name, well_sheet, airport_sheet)
            if lag is not None:
                result_data['Optimal Lag (Days)'] = lag
                result_data['Max Correlation'] = round(corr, 4)
            else:
                print(f"  - No significant correlation found for {well_name}.")
        else:
            print(f"  ERROR: Sheet name for '{well_name}' or '{airport_name}' not found.")
        results_list.append(result_data)
        
    if results_list:
        results_df = pd.DataFrame(results_list)
        output_filename = 'correlation_results_significant_rain.csv'
        results_df.to_csv(output_filename, index=False)
        print("\n-------------------------------------------------")
        print(f"Analysis complete. Results saved to '{output_filename}'")
        print("-------------------------------------------------")
        print("Final Summary:")
        print(results_df.to_string())

if __name__ == "__main__":
    main()

