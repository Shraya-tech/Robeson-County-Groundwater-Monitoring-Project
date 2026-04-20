import pandas as pd
import os

# --- Step 1: File Paths ---
# The path to your data file (James Dial) on iCloud Drive
data_file_path = '/Users/shrayarajkarnikar/Library/Mobile Documents/com~apple~CloudDocs/Desktop/RCGMP/James Dial Compiled (Current).xlsx'

# --- Step 2: Load Data ---
try:
    df = pd.read_excel(data_file_path)
except FileNotFoundError:
    print(f"Error: The data file '{data_file_path}' was not found.")
    exit()

# --- Step 3: Clean and Format Data ---
df['Date/Time'] = pd.to_datetime(df['Date/Time'], errors='coerce')
df = df.set_index('Date/Time')
df['Pot level'] = pd.to_numeric(df['Pot level'], errors='coerce')

# --- Step 4: Calculate Daily Averages ---
daily_avg = df['Pot level'].resample('D').mean().to_frame()
daily_avg.index.name = 'Date only'
daily_avg.rename(columns={'Pot level': 'Daily Average'}, inplace=True)

# --- Step 5: Save Results ---
output_file_name = 'James Dial - Daily Average.xlsx'
# This will save the output file to the same folder as your script.
daily_avg.to_excel(output_file_name)

print(f" Daily averages have been calculated and saved to '{output_file_name}'.")