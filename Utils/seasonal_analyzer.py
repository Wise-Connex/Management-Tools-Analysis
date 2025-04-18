import os
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
import warnings

# Ignore specific warnings from statsmodels
warnings.filterwarnings("ignore", message="A date index has been provided, but it has no associated frequency information")
warnings.filterwarnings("ignore", message="periodicity implies freq=M")

# --- Configuration ---
DBASE_FOLDER = 'dbase'
OUTPUT_FOLDER = 'interpolation_profiles'
FILE_PREFIX = 'CR'
YEARS_TO_ANALYZE = 20 # Analyze the last N years for seasonality

# --- Helper Functions ---

def ensure_dir(directory_path: str):
    """Creates a directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Created directory: {directory_path}")

def calculate_seasonal_profile(series: pd.Series) -> pd.DataFrame | None:
    """
    Performs seasonal decomposition and calculates the monthly distribution profile.

    Args:
        series: A pandas Series with a DatetimeIndex (monthly frequency assumed).

    Returns:
        A DataFrame with Month, SeasonalValue, and PercentageDistribution,
        or None if decomposition fails.
    """
    if series.empty or len(series) < 24: # Need at least two full cycles for decomposition
        print(f"Warning: Not enough data points ({len(series)}) for seasonal decomposition. Skipping.")
        return None

    try:
        # Ensure monthly frequency for decomposition
        series_monthly = series.asfreq('MS') # 'MS' for Month Start frequency

        # Perform seasonal decomposition (additive model is usually robust)
        # Use period=12 for monthly data
        decomposition = seasonal_decompose(series_monthly.dropna(), model='additive', period=12)
        seasonal = decomposition.seasonal

        # Get the unique seasonal pattern (first 12 values represent one cycle)
        seasonal_cycle = seasonal[:12]

        if len(seasonal_cycle) < 12:
            print(f"Warning: Decomposition resulted in less than 12 seasonal factors ({len(seasonal_cycle)}). Skipping.")
            return None

        # Calculate distribution by shifting the minimum value to 10
        min_seasonal = seasonal_cycle.min()
        shift_amount = 10 - min_seasonal
        shifted_seasonal_values = seasonal_cycle + shift_amount

        total_shifted_seasonal_value = shifted_seasonal_values.sum()

        if total_shifted_seasonal_value == 0 or total_shifted_seasonal_value < 1e-9 : # Use a small threshold for float comparison
            # Avoid division by zero/near-zero if shifted values sum to zero (highly unlikely with shift to 10)
            # Assign equal distribution if sum is effectively zero
            print("Warning: Sum of shifted seasonal values is near zero. Assigning equal distribution.")
            percentage_distribution = pd.Series([100.0 / 12.0] * 12, index=seasonal_cycle.index)
        else:
            percentage_distribution = (shifted_seasonal_values / total_shifted_seasonal_value) * 100

        # Create the output DataFrame
        profile_df = pd.DataFrame({
            'Month': range(1, 13),
            'SeasonalValue': seasonal_cycle.values,
            'PercentageDistribution': percentage_distribution.values
        })
        return profile_df

    except Exception as e:
        print(f"Error during seasonal decomposition: {e}")
        return None

# --- Main Processing Logic ---

def process_files():
    """
    Iterates through files in DBASE_FOLDER, performs seasonal analysis,
    and saves profiles to OUTPUT_FOLDER.
    """
    ensure_dir(OUTPUT_FOLDER)
    print(f"Input folder: {DBASE_FOLDER}")
    print(f"Output folder: {OUTPUT_FOLDER}")
    print(f"Analyzing files starting with: {FILE_PREFIX}")
    print(f"Using data from the last {YEARS_TO_ANALYZE} years.")

    processed_files = 0
    skipped_files = 0

    try:
        all_files = os.listdir(DBASE_FOLDER)
    except FileNotFoundError:
        print(f"Error: Input directory '{DBASE_FOLDER}' not found.")
        return

    csv_files = [f for f in all_files if f.startswith(FILE_PREFIX) and f.endswith('.csv')]

    if not csv_files:
        print(f"No files found in '{DBASE_FOLDER}' starting with '{FILE_PREFIX}'.")
        return

    print(f"Found {len(csv_files)} files to process.")

    for filename in csv_files:
        input_path = os.path.join(DBASE_FOLDER, filename)
        print(f"\nProcessing file: {filename}...")

        try:
            # Read data, assuming date is in the first column and value in the second
            # Adjust column indices/names if necessary based on actual CSV structure
            df = pd.read_csv(input_path, parse_dates=[0], index_col=0)

            if df.empty:
                print("Warning: File is empty. Skipping.")
                skipped_files += 1
                continue

            # Ensure index is DatetimeIndex
            if not isinstance(df.index, pd.DatetimeIndex):
                 raise ValueError("First column is not a valid DatetimeIndex.")

            # Select the first data column for analysis
            # This assumes the value to analyze is the first column after the index
            if df.shape[1] == 0:
                 print("Warning: No data columns found after index. Skipping.")
                 skipped_files += 1
                 continue
            series = df.iloc[:, 0]


            # Filter data for the last N years
            end_date = series.index.max()
            start_date = end_date - pd.DateOffset(years=YEARS_TO_ANALYZE)
            series_filtered = series[series.index >= start_date]

            if series_filtered.empty:
                print(f"Warning: No data available in the last {YEARS_TO_ANALYZE} years. Skipping.")
                skipped_files += 1
                continue

            # Calculate seasonal profile
            profile_df = calculate_seasonal_profile(series_filtered)

            if profile_df is not None:
                # Construct output filename (remove trailing '_0000')
                base_name = filename[:-4] # Remove '.csv'
                if base_name.endswith('_0000'):
                    output_base_name = base_name[:-5]
                else:
                    # Handle cases where filename doesn't end exactly with _0000
                    print(f"Warning: Filename '{filename}' doesn't end with '_0000'. Using base name '{base_name}' for output.")
                    output_base_name = base_name

                output_filename = f"{output_base_name}.csv"
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)

                # Save the profile
                profile_df.to_csv(output_path, index=False, float_format='%.4f')
                print(f"Successfully saved seasonal profile to: {output_path}")
                processed_files += 1
            else:
                print("Skipping file due to issues in seasonal analysis.")
                skipped_files += 1

        except FileNotFoundError:
            print(f"Error: File not found at {input_path}. Skipping.")
            skipped_files += 1
        except pd.errors.EmptyDataError:
            print(f"Error: File {filename} is empty. Skipping.")
            skipped_files += 1
        except Exception as e:
            print(f"Error processing file {filename}: {e}")
            skipped_files += 1

    print(f"\n--- Processing Summary ---")
    print(f"Successfully processed: {processed_files} files")
    print(f"Skipped/Errored:      {skipped_files} files")
    print(f"Total files checked:  {len(csv_files)}")
    print(f"Profiles saved in:    {OUTPUT_FOLDER}")

# --- Script Execution ---
if __name__ == "__main__":
    process_files() 