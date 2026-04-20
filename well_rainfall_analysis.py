import pandas as pd
import numpy as np
from geopy.distance import great_circle

# --- 1. USER COORDINATES (Updated) ---
# The names (e.g., "Alamac") MUST exactly match the keys in the sheet_name_map below.

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
    "KLBT": (34.6113, -79.0595),  # Lumberton
    "KMEB": (34.7965, -79.3685),  # Laurinburg/Maxton
    "KFAY": (34.9911, -78.8871),  # Fayetteville
}

# --- 2. FILE AND SHEET NAME CONFIGURATION ---
# The name of your single Excel file.
excel_file_name = "RCGMP_data.xlsx"

# This maps the well/airport name to the EXACT name of its sheet in the Excel file.
# IMPORTANT: You must update these sheet names to match your file if they are different.
sheet_name_map = {
    # Wells
    "Alamac": "Alamac",
    "Ballard": "Ballard",
    "Bethel Hill": "Bethel Hill",
    "Doc Henderson": "Doc Henderson",
    "James Dial": "James Dial",
    "Knapdale": "Knapdale",
    "Landfill": "Landfill",
    "MW1": "MW1",
    "MW2": "MW2",
    "Orum Water Tower 1": "Orum Water Tower 1",
    "Prospect": "Prospect",
    "Sam Nobel": "Sam Nobel",
    "Sammy Cox": "Sammy Cox",
    # Airports
    "KLBT": "KLBT",
    "KMEB": "KMEB",
    "KFAY": "KFAY",
}


def find_closest_airport(well_coords, airport_coords):
    """Calculates the distance from a well to all airports and finds the closest one."""
    distances = {name: great_circle(well_coords, ap_coords).miles for name, ap_coords in airport_coords.items()}
    closest_airport = min(distances, key=distances.get)
    return closest_airport, distances[closest_airport]


def analyze_well_data(excel_file, well_sheet, airport_sheet):
    """Loads data from Excel sheets, cleans, merges, and analyzes it."""
    try:
        # Load datasets from specific sheets in the Excel file
        well_df = pd.read_excel(excel_file, sheet_name=well_sheet)
        airport_df = pd.read_excel(excel_file, sheet_name=airport_sheet)

        # --- Data Cleaning and Standardization ---
        well_df.columns = [str(col).strip() for col in well_df.columns]
        airport_df.columns = [str(col).strip() for col in airport_df.columns]

        well_df.rename(columns={'Timestamp': 'date', 'Date': 'date', 'Value': 'well_level', 'Pot Level': 'well_level', 'Pot level': 'well_level'}, inplace=True, errors='ignore')
        airport_df.rename(columns={'DATE': 'date', 'Date': 'date', 'PRCP': 'rainfall', 'PRCP (inches)': 'rainfall', 'PRCP(inches)': 'rainfall'}, inplace=True, errors='ignore')
        
        well_df['date'] = pd.to_datetime(well_df['date'], errors='coerce')
        airport_df['date'] = pd.to_datetime(airport_df['date'], errors='coerce')

        well_df['well_level'] = pd.to_numeric(well_df['well_level'], errors='coerce')
        airport_df['rainfall'] = pd.to_numeric(airport_df['rainfall'], errors='coerce')

        well_df = well_df[['date', 'well_level']].dropna()
        airport_df = airport_df[['date', 'rainfall']].dropna()

        df = pd.merge(well_df, airport_df, on='date', how='inner')
        df.set_index('date', inplace=True)

        if df.empty or df['well_level'].isnull().all() or df['rainfall'].isnull().all():
            return None, None

        # --- Time-Lagged Cross-Correlation ---
        max_lag_days = 90
        correlations = {}
        for lag in range(max_lag_days + 1):
            # We are looking for the correlation between PAST rain and FUTURE well levels.
            # Shifting the rainfall column forward simulates this lag effect.
            corr = df['rainfall'].shift(lag).corr(df['well_level'])
            if not np.isnan(corr):
                correlations[lag] = corr

        if not correlations:
            return None, None

        # Find the lag with the highest absolute correlation.
        # We expect a NEGATIVE correlation because more rain (a positive number)
        # leads to a higher water table, which means a SMALLER depth-to-water measurement.
        optimal_lag = max(correlations, key=lambda k: abs(correlations[k]))
        max_corr = correlations[optimal_lag]

        return optimal_lag, max_corr

    except Exception as e:
        print(f"  ERROR processing sheets '{well_sheet}' or '{airport_sheet}': {e}")
        return None, None


def main():
    """Main function to run the entire analysis."""
    print("--- Robeson County Groundwater Analysis (from Excel) ---")
    
    results_list = []
    well_to_airport_map = {}

    for well_name, w_coords in well_coordinates.items():
        closest_airport, distance = find_closest_airport(w_coords, airport_coordinates)
        well_to_airport_map[well_name] = {"airport": closest_airport, "distance": distance}

    print("\n--- Running Correlation Analysis ---")
    for well_name, mapping in well_to_airport_map.items():
        airport_name = mapping['airport']
        distance = mapping['distance']
        
        print(f"Analyzing: {well_name} (Closest airport: {airport_name}, {distance:.2f} miles)")

        well_sheet_name = sheet_name_map.get(well_name)
        airport_sheet_name = sheet_name_map.get(airport_name)
        
        result_data = {
            'Well Name': well_name,
            'Closest Airport': airport_name,
            'Distance (Miles)': round(distance, 2),
            'Optimal Lag (Days)': 'N/A',
            'Max Correlation': 'N/A'
        }

        if well_sheet_name and airport_sheet_name:
            optimal_lag, max_correlation = analyze_well_data(excel_file_name, well_sheet_name, airport_sheet_name)
            if optimal_lag is not None:
                result_data['Optimal Lag (Days)'] = optimal_lag
                result_data['Max Correlation'] = round(max_correlation, 4)
            else:
                print(f"  - No significant correlation found for {well_name}.")
        else:
            print(f"  ERROR: Sheet name for '{well_name}' or '{airport_name}' not found in map.")
        
        results_list.append(result_data)
        
    if results_list:
        results_df = pd.DataFrame(results_list)
        output_filename = 'correlation_results.csv'
        results_df.to_csv(output_filename, index=False)
        print("\n-------------------------------------------------")
        print(f"Analysis complete. Results saved to '{output_filename}'")
        print("-------------------------------------------------")
        print("Final Summary:")
        print(results_df.to_string())

if __name__ == "__main__":
    main()

