import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
import numpy as np
import pandas as pd
import time  # Import the time module
import re
import hashlib
import seaborn as sns
import itertools
import google.generativeai as genai
import statsmodels.api as sm
import scipy.fftpack as fftpack
import markdown
#import weasyprint
import os
import csv
import io
import sys
import math
import warnings
import shutil # Make sure shutil is imported at the top of the file
import traceback
from scipy import signal
from matplotlib import ticker
from datetime import datetime, timedelta # Ensure timedelta is imported
from scipy.stats import linregress # For trend calculation
from sklearn.linear_model import LinearRegression # For potential regression/trend calculation

# Suppress the specific scikit-learn deprecation warning about force_all_finite
warnings.filterwarnings("ignore", message=".*force_all_finite.*")

#import paramiko
#from io import StringIO
from googleapiclient.discovery import build
from dotenv import load_dotenv
#from PIL import Image
from statsmodels.tsa.arima.model import ARIMA
from pmdarima.arima import auto_arima
#from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
#from statsmodels.tsa.stattools import adfuller
from statsmodels.formula.api import ols
#from IPython.display import display, Markdown
#from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from matplotlib.ticker import FuncFormatter
#from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
#from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error, mean_absolute_error
from itertools import combinations
from sklearn.metrics import r2_score  # Import r2_score function
#from enum import auto
#*** Google Books Nviewer
#import requests
import scipy.interpolate as interp
from scipy.interpolate import CubicSpline
#from mpl_toolkits.axes_grid1 import make_axes_locatable
import base64
from datetime import datetime
from urllib.parse import quote # Add this import for URL encoding filenames
#from sklearn.preprocessing import StandardScaler
#from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from statsmodels.tsa.seasonal import seasonal_decompose
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import google.api_core.exceptions
import matplotlib.patches as mpatches
import itertools
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer # Or KNNImputer, IterativeImputer
from sklearn.decomposition import PCA
import re
import PIL.Image
from IPython.display import display, Markdown, HTML


# AI Prompts imports 
from prompts import system_prompt_1, system_prompt_2, temporal_analysis_prompt_1, temporal_analysis_prompt_2, \
    cross_relationship_prompt_1, cross_relationship_prompt_2, trend_analysis_prompt_1, pca_prompt_2, \
    arima_analysis_prompt_1, arima_analysis_prompt_2, seasonal_analysis_prompt_1, seasonal_analysis_prompt_2, \
    prompt_6_single_analysis, prompt_6_correlation, prompt_conclusions_standalone, prompt_conclusions_comparative, \
    prompt_sp, prompt_abstract
# Tools Dictionary
from tools import tool_file_dic

# Change the plt.ion() line to plt.ioff() to disable interactive mode
plt.ioff()
plt.style.use('ggplot')    
    
# *************************************************************************************
#   Global Variables
# *************************************************************************************

# Colors ANSI Codes
RESET = '\033[0m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'
WHITE = '\033[37m'
GRAY = '\033[30m'

# fixed_source_colors = {
#     "Google Trends": '#4B0082',         # Dark Purple / Indigo
#     "Google Books Ngrams": '#191970',   # Dark Blue / Midnight Blue
#     "Bain - Usabilidad": '#20B2AA',     # Teal / LightSeaGreen
#     "Crossref.org": '#3CB371',          # Green / MediumSeaGreen
#     "Bain - Satisfacción": '#FFD700'    # Yellow / Gold
# }

fixed_source_colors = {
    "Google Trends": '#1f77b4',         # Muted Blue
    "Google Books Ngrams": '#ff7f0e',   # Safety Orange
    "Bain - Usabilidad": '#2ca02c',     # Cooked Asparagus Green
    "Crossref.org": '#9467bd',          # Muted Purple
    "Bain - Satisfacción": '#d62728'    # Brick Red
}
# Default color for unknown sources
default_color = '#808080' # Grey

CONTRASTING_PALETTE = [
    '#1f77b4',  # Muted Blue
    '#ff7f0e',  # Safety Orange
    '#2ca02c',  # Cooked Asparagus Green
    '#d62728',  # Brick Red
    '#9467bd',  # Muted Purple
    '#8c564b',  # Chestnut Brown
    '#e377c2',  # Raspberry Sorbet Pink
    '#7f7f7f',  # Middle Gray
    '#bcbd22',  # Curry Yellow-Green
    '#17becf'   # Muted Cyan
]

global gem_temporal_trends_sp
global gem_cross_keyword_sp
global gem_industry_specific_sp
global gem_arima_sp
global gem_seasonal_sp
global gem_fourier_sp
global gem_conclusions_sp
global csv_fourier
global csv_means_trends
global csv_means_trendsA
global csv_correlation
global csv_regression
global csv_arima
global csv_arimaA
global csv_arimaB
global csv_seasonal
global menu
global actual_menu
global actual_opt
global title_odd_charts
global title_even_charts
global wider
global all_keywords
global filename
global unique_folder
global csv_last_20_data
global csv_last_15_data
global csv_last_10_data
global csv_last_5_data
global csv_last_year_data
global csv_all_data
global trends_results
global all_kw
global current_year
global charts
global one_keyword
global dbase_options
global top_choice
global combined_dataset
global selected_keyword
global selected_sources
global earliest_date
global latest_date
global earliest_year
global latest_year
global total_years
global csv_combined_dataset
global skip_seasonal
global skip_arima
global csv_significance
global original_values
global source_trends_results
global current_selected_keyword
global pca_csv_variable
global scree_plot_filepath
source_trends_results = {}
original_values = {}
keycharts = []
csv_arimaA = []
csv_arimaB = []

# Create a 'data' folder in the current directory
data_folder = 'data'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)
    # Make the folder writable (0o777 is octal for rwxrwxrwx)
    os.chmod(data_folder, 0o777)


# *************************************************************************************
#   FUNCTIONS
# *************************************************************************************

def banner_msg (title="", color1=WHITE, color2=WHITE, margin=12, char='*'):
  qty=len(title)+margin*2
  print(f'{color2}\n\n{char*qty}\n{char*margin}{color1}{title}{color2}{char*margin}\n{char*qty}{RESET}')

# return a number in engineering notation
def eng_notation(number):
    if number is None or math.isnan(number):
        return "N/A"
    if number == 0:
        return "0"
    exponent = int(math.floor(math.log10(abs(number)) / 3) * 3)
    mantissa = number / (10 ** exponent)
    return f"{mantissa:.2f}e{exponent}"

def eng_format(x):
    if x == 0:
        return "0"
    exp = int(math.floor(math.log10(abs(x))))
    exp3 = 3 * (exp // 3)
    mantissa = x / (10**exp3)
    return f"{mantissa:.1f}E{exp3:+d}".replace("E+", "E+").replace("E-0", "E-")

def get_unique_filename(base_filename, unique_folder):
    """Helper function to get a unique filename by adding a number if file exists"""
    counter = 1
    filename = base_filename
    while os.path.exists(os.path.join(unique_folder, filename)):
        # Split filename into name and extension
        name, ext = os.path.splitext(base_filename)
        filename = f"{name}{counter}{ext}"
        counter += 1
    return filename

def gemini_prompt(
    system_prompt: str,
    prompt: str,
    image_paths: list[str] | None = None,
    m: str = 'pro',
    max_retries: int = 5,
    initial_backoff: int = 2
) -> str:
    """
    Sends a prompt, optionally with images, to the Gemini API with robust error handling and retries.

    Args:
        system_prompt: The system instruction or context for the model.
        prompt: The main user prompt text.
        image_paths: An optional list of local file paths for images to include.
        m: The model to use ('flash' or 'pro'). Automatically upgrades to 'pro' if images are provided.
        max_retries: Maximum number of retry attempts for transient API errors.
        initial_backoff: The initial time in seconds to wait before retrying.

    Returns:
        The text response from the model or a descriptive error message.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return "[Config Error] GOOGLE_API_KEY environment variable not set."

    genai.configure(api_key=api_key)

    # --- 1. Determine Model and Prepare Images ---
    use_vision_model = bool(image_paths)
    if use_vision_model:
        model_name = 'gemini-2.5-pro' # Pro model is best for vision
    else:
        model_name = 'gemini-1.5-flash-latest' if m == 'flash' else 'gemini-2.5-pro'

    prompt_parts = [f"{system_prompt}\n\n{prompt}"]
    loaded_image_count = 0

    if use_vision_model:
        if not isinstance(image_paths, list):
            return f"[Input Error] image_paths must be a list of strings, but got {type(image_paths).__name__}."
            
        for image_path in image_paths:
            try:
                if not os.path.exists(image_path):
                     raise FileNotFoundError(f"Image file not found at path: {image_path}")
                prompt_parts.append(PIL.Image.open(image_path))
                loaded_image_count += 1
            except FileNotFoundError as e:
                return f"[File Error] {e}"
            except Exception as e:
                return f"[Image Error] Failed to load image '{image_path}': {e}"

    # --- 2. Configure and Instantiate Model ---
    try:
        # Safety settings to reduce the chance of prompts being blocked.
        safety_settings = {
            "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
        }
        model = genai.GenerativeModel(model_name, safety_settings=safety_settings)
    except Exception as e:
        return f"[API Error] Failed to initialize model '{model_name}': {e}"

    # --- 3. API Call with Retry Logic ---
    retries = 0
    backoff_time = initial_backoff
    while retries < max_retries:
        try:
            image_info = f"with {loaded_image_count} image(s)" if use_vision_model else ""
            print(f"Attempt {retries + 1}/{max_retries}: Sending request to {model_name} {image_info}...")

            response = model.generate_content(prompt_parts, stream=False)
            
            # The most direct way to get the text. If the response was blocked
            # for safety or other reasons, accessing .text will raise an exception
            # which is caught below.
            print(f"{GREEN}Success: Received response from Gemini.{RESET}")
            return response.text

        # Specific exception for blocked prompts (more reliable than parsing text)
        except genai.types.generation_types.BlockedPromptError as e:
            print(f"{RED}API Error: Prompt was blocked.{RESET}")
            # This is a final state, no point in retrying.
            return f"[API Blocked] The prompt was blocked by safety filters. Details: {e}"
        
        # Exception raised if response.text can't be accessed due to no valid candidate
        except ValueError as e:
             print(f"{RED}API Error: Invalid response - likely blocked or empty. {e}{RESET}")
             # This can sometimes be transient, so we retry.
             
        # Standard transient network/server errors
        except (google.api_core.exceptions.ResourceExhausted,
                google.api_core.exceptions.DeadlineExceeded,
                google.api_core.exceptions.InternalServerError,
                google.api_core.exceptions.ServiceUnavailable) as e:
            print(f"{RED}API Error: {type(e).__name__} - {e}{RESET}")

        except Exception as e:
            # Catch any other unexpected errors during the API call
            print(f"{RED}An unexpected error occurred: {type(e).__name__} - {e}{RESET}")
            # Depending on the error, may not be retryable, but we try for robustness.

        # If an exception occurred, proceed with backoff and retry
        retries += 1
        if retries < max_retries:
            print(f"{YELLOW}Retrying in {backoff_time:.1f} seconds...{RESET}")
            time.sleep(backoff_time)
            backoff_time *= 1.5 # Increase backoff
        else:
            print(f"{RED}Max retries ({max_retries}) reached. Failing request.{RESET}")
            return f"[API Error] Max retries reached after encountering repeated errors."

    # This line should ideally not be reached
    return "[API Error] Unknown state reached after retry loop."


# def gemini_prompt(system_prompt, prompt, m='pro', max_retries=5, initial_backoff=1):
#   """
#   Send a prompt to the Gemini API with retry logic for handling timeouts and service issues.
  
#   Args:
#       system_prompt: The system instructions for the model
#       prompt: The user prompt to send to the model
#       m: Model type ('pro' or 'flash')
#       max_retries: Maximum number of retry attempts
#       initial_backoff: Initial backoff time in seconds (will increase exponentially)
      
#   Returns:
#       The text response from the model
#   """
#   system_instructions = system_prompt

#   #print('\n**************************** INPUT ********************************\n')
#   #print(f'System Instruction: \n{system_instructions} \nPrompt: \n{prompt}')

#   if m == 'pro':
#     model = 'gemini-2.5-pro-preview-05-06' # @#param {type: "string"} ["gemini-1.0-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
#   else:
#     model = 'gemini-2.5-flash-preview-04-17' # @#param {type: "string"} ["gemini-1.0-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
#   temperature = 0.31 # @#param {type: "slider", min: 0, max: 2, step: 0.05}
#   stop_sequence = '*** END ANALYSIS ***'

#   if model == 'gemini-1.0-pro' and system_instructions is not None:
#     system_instructions = None
#     print('\x1b[31m(WARNING: System instructions ignored, gemini-1.0-pro does not support system instructions)\x1b[0m')
#   if model == 'gemini-1.0-pro' and temperature > 1:
#     temperature = 1
#     print('\x1b[34m(INFO: Temperature set to 1, gemini-1.0-pro does not support temperature > 1)\x1b[0m')

#   if system_instructions == '':
#     system_instructions = None

#   # Load environment variables from a .env file (if using one)
#   load_dotenv()

#   # Retrieve the API key
#   api_key = os.getenv('GOOGLE_API_KEY')

#   if api_key is None:
#       raise ValueError("GOOGLE_API_KEY environment variable is not set")
  
#   genai.configure(api_key=api_key)
#   model_instance = genai.GenerativeModel(model, system_instruction=system_instructions)
#   config = genai.GenerationConfig(temperature=temperature, stop_sequences=[stop_sequence])
  
#   # Implement retry logic with exponential backoff
#   retry_count = 0
#   backoff_time = initial_backoff
  
#   while retry_count < max_retries:
#     try:
#       # If this isn't the first attempt, log that we're retrying
#       if retry_count > 0:
#         print(f"\x1b[33m(Retry attempt {retry_count}/{max_retries} after waiting {backoff_time}s)\x1b[0m")
      
#       # Try to generate content
#       response = model_instance.generate_content(contents=[prompt], generation_config=config)
#       return response.text
      
#     except google.api_core.exceptions.DeadlineExceeded as e:
#       # Handle timeout errors specifically
#       retry_count += 1
      
#       if retry_count >= max_retries:
#         print(f"\x1b[31mFailed after {max_retries} retries. Last error: {str(e)}\x1b[0m")
#         # Return a fallback message instead of raising an exception
#         return f"[API TIMEOUT ERROR: The request to the Gemini API timed out after {max_retries} attempts. The prompt may be too complex or the service may be experiencing issues.]"
      
#       # Calculate exponential backoff with jitter
#       jitter = random.uniform(0, 0.1 * backoff_time)  # Add up to 10% jitter
#       wait_time = backoff_time + jitter
#       print(f"\x1b[33mAPI timeout occurred. Retrying in {wait_time:.2f} seconds...\x1b[0m")
#       time.sleep(wait_time)
#       backoff_time *= 2  # Exponential backoff
      
#     except Exception as e:
#       # Handle other exceptions
#       print(f"\x1b[31mError calling Gemini API: {str(e)}\x1b[0m")
#       return f"[API ERROR: {str(e)}]"

def linear_interpolation(df, kw):
    # Extract actual data points (non-NaN values)
    actual_data = df[~df[kw].isna()]
    
    if actual_data.empty:
        return df.copy()  # Return original if no actual data
    
    x = actual_data.index  # Keep index as DatetimeIndex for actual points only
    y = actual_data[kw].values

    # Use numpy.interp for linear interpolation, but only within the range of actual data
    # Create date range only between first and last actual data points
    x_interp = pd.date_range(actual_data.index.min().date(), actual_data.index.max().date(), freq='MS')
    y_interp = np.interp(x_interp, x, y)

    # Create a new DataFrame with the interpolated values
    df_interpolated = pd.DataFrame(y_interp, index=x_interp, columns=[kw])
    
    # Preserve original values at actual data points to ensure accuracy
    for idx in actual_data.index:
        if idx in df_interpolated.index:
            df_interpolated.loc[idx, kw] = actual_data.loc[idx, kw]

    #PPRINT(f'DF INTERPOLATED:\n{df_interpolated}')
    return df_interpolated

def smooth_transition(value, min_val, max_val, transition_range=0.2):
    """
    Smoothly transition values back within bounds using a modified sigmoid function.
    transition_range determines how far from the bounds the transition starts (as a fraction of the range)
    """
    range_val = max_val - min_val
    transition_width = range_val * transition_range
    
    # Calculate the center of the valid range
    center = (max_val + min_val) / 2
    
    # Use a more gradual sigmoid curve (reduced steepness factor from 5 to 3)
    sigmoid = lambda x: 1 / (1 + np.exp(-3 * x))
    
    # Smooth transition for values approaching min
    if value < min_val + transition_width:
        # Calculate distance from minimum as a proportion of transition width
        dist_from_min = (value - min_val) / transition_width
        # Apply sigmoid scaling to make transition more gradual
        smooth_factor = sigmoid(2 * dist_from_min - 1)  # Shift sigmoid to center
        # Gradually blend between min_val and the original value
        return min_val + (transition_width * smooth_factor)
    
    # Smooth transition for values approaching max
    if value > max_val - transition_width:
        # Calculate distance from maximum as a proportion of transition width
        dist_from_max = (max_val - value) / transition_width
        # Apply sigmoid scaling to make transition more gradual
        smooth_factor = sigmoid(2 * dist_from_max - 1)  # Shift sigmoid to center
        # Gradually blend between max_val and the original value
        return max_val - (transition_width * smooth_factor)
    
    # Additional smoothing for values in the middle range
    # This helps prevent sudden transitions at the boundaries of the transition zones
    dist_from_center = abs(value - center) / (range_val / 2)
    if dist_from_center > 0.7:  # Start subtle smoothing earlier
        smooth_factor = sigmoid(3 * (1 - dist_from_center))
        target = center + np.sign(value - center) * (range_val / 2 * 0.95)  # 95% of the half-range
        return value * smooth_factor + target * (1 - smooth_factor)
    
    return value

# Global variable to store original values
original_values = {}

def cubic_interpolation(df, kw):
    # Extract actual data points (non-NaN values)
    actual_data = df[~df[kw].isna()]
    
    if actual_data.empty or len(actual_data) < 4:  # Cubic spline requires at least 4 points
        print(f"[Debug] Falling back to linear interpolation for {kw} (points: {len(actual_data)})")
        return linear_interpolation(df, kw)
    
    # Store original values if not already stored
    if kw not in original_values:
         original_values[kw] = actual_data[kw].copy()
    
    # Get the min and max values from original data for STRICT clipping
    original_min = actual_data[kw].min()
    original_max = actual_data[kw].max()
    # NO MARGIN - Clip strictly to original data range
    clip_min = original_min
    clip_max = original_max 
    
    # Ensure index is sorted AND has correct type (datetime64[ns])
    actual_data = actual_data.sort_index()
    actual_data.index = pd.to_datetime(actual_data.index)
    
    # Convert dates to numerical values (days since epoch)
    x = (actual_data.index - pd.Timestamp('1970-01-01')).days.values.astype(float)
    y = actual_data[kw].values
    
    # Create Cubic Spline
    cs = CubicSpline(x, y, bc_type='natural')

    # --- 1. Interpolate at Daily frequency --- 
    daily_date_range = pd.date_range(
        start=actual_data.index.min(), 
        end=actual_data.index.max(), 
        freq='D' 
    )
    if daily_date_range.empty and not actual_data.empty:
         daily_date_range = pd.date_range(start=actual_data.index.min(), periods=1, freq='D')
    if daily_date_range.empty:
        print(f"[Debug] Warning: Could not generate date range for {kw}. Returning empty DataFrame.")
        return pd.DataFrame(columns=df.columns, index=pd.to_datetime([]))
        
    x_interp_daily = (daily_date_range - pd.Timestamp('1970-01-01')).days.values.astype(float)
    y_interp_daily = cs(x_interp_daily)
    
    # --- 2. Clip daily values STRICTLY --- 
    y_interp_daily_clipped = np.clip(y_interp_daily, clip_min, clip_max) # Use strict min/max
    df_daily_clipped = pd.DataFrame(y_interp_daily_clipped, index=daily_date_range, columns=[kw])

    # --- 3. Force original points into DAILY data --- 
    for idx, val in actual_data[kw].items():
         # Ensure idx is a Timestamp before checking
         idx_ts = pd.Timestamp(idx)
         if idx_ts in df_daily_clipped.index:
              df_daily_clipped.loc[idx_ts, kw] = val # Overwrite daily value with exact original
         else:
              # Add original point if its exact date wasn't in the daily range
              print(f"[Debug] Adding original point {idx_ts} ({val}) explicitly to DAILY data for {kw}")
              new_row = pd.DataFrame({kw: [val]}, index=[idx_ts])
              df_daily_clipped = pd.concat([df_daily_clipped, new_row])
              
    df_daily_clipped = df_daily_clipped.sort_index()

    # --- Debug Print (Optional Daily Data) --- 
    # print(f"\n--- [Debug] Intermediate Daily Data for {kw} (Originals Forced) ---")
    # print(df_daily_clipped.to_string()) 
    # print("---------------------------------------------------------------------")

    # --- 4. Resample to MONTH START ('MS') --- 
    df_monthly = df_daily_clipped[[kw]].resample('MS').mean()

    # --- 5. Force original points into MONTHLY data (Final Pass) --- 
    # ---    AND calculate/store Z-score & SV for Menu 5 --- 
    if kw not in original_calc_details:
         original_calc_details[kw] = {} # Initialize dict for this keyword
         
    for idx, val in actual_data[kw].items():
        idx_ts = pd.Timestamp(idx).normalize() 
        
        # Calculate Z-score and SV *before* forcing into monthly data
        if menu == 5:
             try:
                  z_score = (val - 50) / 22.0 
                  fundamental_value = (z_score * 0.891609) + 3.0
                  # Store calculated values globally, keyed by timestamp
                  original_calc_details[kw][idx_ts] = {'z_score': z_score, 'sv': fundamental_value}
             except Exception as calc_e:
                  print(f"[Warning] Could not calculate Z/SV values for {kw} at {idx_ts}: {calc_e}")
                  original_calc_details[kw][idx_ts] = {'z_score': np.nan, 'sv': np.nan} # Store NaN on error
        
        # Force original value into monthly data
        if idx_ts in df_monthly.index:
             # print(f"[Debug] Forcing original {kw} point {idx_ts} ({val}) onto exact monthly index.") # Optional debug
             df_monthly.loc[idx_ts, kw] = val
        else:
             # print(f"[Debug] Adding original point {idx_ts} ({val}) explicitly to MONTHLY data for {kw} as exact index missing.") # Optional debug
             df_monthly.loc[idx_ts] = val

    df_monthly = df_monthly.sort_index()

    # --- Debug Print (Optional Monthly Data) --- 
    # print(f"\n--- [Debug] Final Monthly Data for {kw} (Originals Forced) ---")
    # print(df_monthly.to_string())
    # print("=====================================================================")

    return df_monthly

def smooth_data(data, window_size=5, transition_points=10):
    """
    Applies a weighted moving average to smooth the data, with increased smoothness
    for the first and last few data points, preserving the very first and last data points.

    Args:
    data: A list or NumPy array of data points.
    window_size: The number of data points to include in the moving average (default: 5).
    transition_points: The number of points over which to gradually increase/decrease smoothness (default: 10).

    Returns:
    A NumPy array of smoothed data points with the same shape as the original data.
    """
    data = np.array(data)
    weights = np.arange(1, window_size + 1)

    # Create a padded version of the data to handle edge cases
    padded_data = np.pad(data, (window_size // 2, window_size - 1 - window_size // 2), mode='edge')

    # Apply the weighted moving average
    smoothed_data = np.convolve(padded_data, weights / weights.sum(), mode='valid')

    # Ensure the first and last points are preserved
    smoothed_data[0] = data[0]
    smoothed_data[-1] = data[-1]

    # Create a gradual transition between original and smoothed data for the first 'transition_points'
    for i in range(1, min(transition_points, len(data) // 2)):
        alpha = (i / transition_points) ** 2  # Using a quadratic function for smoother transition
        smoothed_data[i] = (1 - alpha) * data[i] + alpha * smoothed_data[i]

        # Mirror the transition for the end of the data
        smoothed_data[-i-1] = (1 - alpha) * data[-i-1] + alpha * smoothed_data[-i-1]

    #PPRINT(f"original data\n{data}")
    #PPRINT(f"smothed data\n{smoothed_data}")
    return smoothed_data

def main_menu():
    banner_msg(" Menú principal ", YELLOW, WHITE)
    options = {
        1: "Google Trends",
        2: "Google Books Ngrams",
        3: "Bain - Usability",
        4: "Crossref.org",
        5: "Bain - Satisfaction"
    }
    for index, option in enumerate(options.values(), 1):
        print(f"{index}. {option}")
    while True:
        selection = input("\nIngrese el número de la opción a seleccionar: ")
        try:
            index = int(selection) - 1  # Subtract 1 as indices start from 0
            if 0 <= index < len(options):
                selected_option = list(options.keys())[index]
                return selected_option
            else:
                print(f"{RED}Opcin no válida.{RESET}")
        except ValueError:
            print(f"{YELLOW}Por favor, ingrese un número válido.{RESET}")

# Prompts the user to select multiple elements from a dictionary using numbers.
def get_user_selections(dictionary, option):
  """Prompts the user to select multiple elements from a dictionary using numbers.
  Args:
    dictionary: The dictionary to select from.
  Returns:
    A tuple containing the selected data file name and a list of selected strings from the last list of the dictionary.
  """
  global current_year
  
  banner_msg(" Herramientas disponibles ", YELLOW, WHITE)
  for index, key in enumerate(dictionary, 1):
    print(f"{index}. {key}")
  while True:
    selection = input("\nIngrese el número de la herramienta a seleccionar: ")
    try:
      index = int(selection) - 1  # Subtract 1 as indices start from 0
      if 0 <= index < len(dictionary):
        selected_key = list(dictionary.keys())[index]
        selected_strings = dictionary[selected_key][1]
        match option:
          case 1:
            selected_data_file_name = dictionary[selected_key][0]
          case 2:
            current_year = 2022
            selected_data_file_name = dictionary[selected_key][2]
          case 3:
            selected_data_file_name = dictionary[selected_key][3]
          case 4:
            selected_data_file_name = dictionary[selected_key][4]
          case 5:
            selected_data_file_name = dictionary[selected_key][5]
        return selected_data_file_name, selected_strings
      else:
        print(f"{RED}Indice no válido.{RESET}")
    except ValueError:
      print(f"{YELLOW}Por favor, ingrese un número válido.{RESET}")
  return selected_data_file_name, selected_strings

def bspline_interpolation(df, column):
    # Extract actual data points (non-NaN values)
    actual_data = df[~df[column].isna()]
    
    if actual_data.empty or len(actual_data) < 4:  # B-spline typically requires at least 4 points
        # Fall back to simpler interpolation if not enough points
        if len(actual_data) >= 2:
            return linear_interpolation(df, column)
        else:
            return df.copy()  # Return original if not enough points
    
    # Get the min and max values from original data
    original_min = actual_data[column].min()
    original_max = actual_data[column].max()
    
    x = actual_data.index.astype(int) / 10**9  # Convert to Unix timestamp
    y = actual_data[column].values

    # Create a B-spline interpolator that passes through all points
    # Set s=0 to force the spline to pass through all points
    tck = interp.splrep(x, y, k=3, s=0)  # s=0 ensures curve passes through all points

    # Generate interpolated values only between first and last actual data points
    start_date = actual_data.index.min()
    end_date = actual_data.index.max()
    
    # Create a list to store interpolated data
    interpolated_data = []
    
    # Generate daily points for maximum smoothness
    x_interp = pd.date_range(start=start_date, end=end_date, freq='D')
    x_interp_unix = x_interp.astype(int) / 10**9
    y_interp = interp.splev(x_interp_unix, tck)
    
    # Apply smooth transition instead of hard clipping
    y_interp = np.array([smooth_transition(val, original_min, original_max) for val in y_interp])
    
    # Handle near-zero values smoothly
    min_threshold = 0.001  # Minimum value to prevent exact zeros
    y_interp = np.where(y_interp < min_threshold, min_threshold + (y_interp * 0.1), y_interp)
    
    # Add the interpolated data
    for date, value in zip(x_interp, y_interp):
        # Only add points up to the last actual data point
        if date <= end_date:
            interpolated_data.append((date, value))

    # Create a new DataFrame with the interpolated values
    df_interpolated = pd.DataFrame(interpolated_data, columns=['date', column])
    df_interpolated.set_index('date', inplace=True)

    # Carefully preserve all original data points
    for idx in actual_data.index:
        if idx in df_interpolated.index:
            df_interpolated.loc[idx, column] = actual_data.loc[idx, column]
        else:
            # If the original point's date doesn't align with our interpolation,
            # add it explicitly to preserve it
            df_interpolated.loc[idx] = actual_data.loc[idx]

    # Sort the index to ensure proper ordering after adding original points
    df_interpolated.sort_index(inplace=True)
    
    # Ensure we don't have any points after the last actual data point
    df_interpolated = df_interpolated[df_interpolated.index <= end_date]

    return df_interpolated

def seasonal_distribution(df, column):
    '''
    Interpolates annual data to monthly data based on a predefined 
    percentage distribution profile loaded from a CSV file.

    Args:
        df (pd.DataFrame): Input DataFrame with annual data. Must contain 
                           a datetime index (representing the year, e.g., YYYY-01-01)
                           and the specified data column.
        column (str): The name of the column containing the annual values 
                      to interpolate.

    Returns:
        pd.DataFrame: A new DataFrame with monthly interpolated data, 
                      indexed by date (YYYY-MM-01), containing the 
                      interpolated values in the specified column.
                      Returns an empty DataFrame if the profile is not found.
    '''
    # Construct the profile filename based on the column name
    profile_filename_base = f"CR_{column.replace(' ', '')}_monthly_relative.csv"
    profile_path = os.path.join("interpolation_profiles", profile_filename_base)

    # Load the profile data
    try:
        profile_df = pd.read_csv(profile_path)
        # Ensure PercentageDistribution is numeric and handle potential errors
        profile_df['PercentageDistribution'] = pd.to_numeric(profile_df['PercentageDistribution'], errors='coerce')
        # Normalize percentages if they don't sum to 100
        total_percentage = profile_df['PercentageDistribution'].sum()
        if not np.isclose(total_percentage, 100.0):
            print(f"Warning: Percentages in {profile_path} sum to {total_percentage}. Normalizing.")
            profile_df['PercentageDistribution'] = (profile_df['PercentageDistribution'] / total_percentage) * 100
            
        profile_df.set_index('Month', inplace=True) # Index by month number (1-12)
    except FileNotFoundError:
        print(f"Error: Interpolation profile not found at {profile_path}. Cannot perform sample interpolation for '{column}'.")
        # Return an empty DataFrame or handle as appropriate
        return pd.DataFrame(columns=['Date', column]).set_index('Date')
    except Exception as e:
        print(f"Error loading or processing profile {profile_path}: {e}")
        return pd.DataFrame(columns=['Date', column]).set_index('Date')
        
    # Ensure the input DataFrame index is datetime
    if not pd.api.types.is_datetime64_any_dtype(df.index):
         try:
             # Attempt to convert assuming 'YYYY-01' format initially leads to YYYY-01-01
             df.index = pd.to_datetime(df.index)
         except Exception as e:
             print(f"Error converting index to datetime: {e}. Cannot perform sample interpolation.")
             return pd.DataFrame(columns=['Date', column]).set_index('Date')

    # Prepare data for interpolation
    interpolated_data = []
    
    # Iterate through each year in the input data
    for year_date, row in df.iterrows():
        annual_value = row[column]
        year = year_date.year

        # Check if annual_value is NaN or None, skip if so
        if pd.isna(annual_value):
             print(f"Warning: Skipping year {year} for column '{column}' due to NaN value.")
             continue

        # Iterate through months 1 to 12
        for month in range(1, 13):
            try:
                # Get the percentage for the current month from the profile
                percentage = profile_df.loc[month, 'PercentageDistribution']
                
                # Check if percentage is NaN (e.g., due to coerce failure)
                if pd.isna(percentage):
                    print(f"Warning: Invalid percentage for month {month} in profile {profile_path}. Using 0.")
                    percentage = 0.0

                # Calculate the interpolated monthly value
                monthly_value = annual_value * (percentage / 100.0)

                # Create the date for the interpolated month
                monthly_date = pd.Timestamp(year=year, month=month, day=1)

                # Append the result
                interpolated_data.append({'Date': monthly_date, column: monthly_value})
            except KeyError:
                 print(f"Warning: Month {month} not found in profile {profile_path}. Skipping month.")
                 continue # Skip if month is missing in profile
            except Exception as e:
                 print(f"Error during interpolation for {year}-{month} in column '{column}': {e}")
                 continue # Skip this month/year if calculation fails

    # Create the output DataFrame
    if not interpolated_data: # Handle case where no data could be interpolated
        print(f"Warning: No data was interpolated for column '{column}'.")
        return pd.DataFrame(columns=['Date', column]).set_index('Date')
        
    df_interpolated = pd.DataFrame(interpolated_data)
    df_interpolated.set_index('Date', inplace=True)
    df_interpolated.sort_index(inplace=True) # Ensure chronological order

    return df_interpolated
    
def get_file_data(filename, menu):
    # Path to the local 'dbase' folder
    local_path = "dbase/"
    
    # Construct the full path to the CSV file
    file_path = os.path.join(local_path, filename)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"El archivo {filename} no existe en la carpeta 'dbase'.")
    
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(file_path, index_col=0)  # Set the first column as index
    df.index = df.index.str.strip()  # Remove leading/trailing whitespace from index values
    
    # Convert the index to datetime format
    if menu == 2:
        if top_choice == 1 or top_choice == 3:
            # For Google Books Ngrams, assume the index is just the year
            df.index = pd.to_datetime(df.index.str.split('-').str[0], format='%Y')
        else:
            # For Google Trends, assume the index is just the year
            interpolated_data = pd.DataFrame()
            for column in df.columns:
                #interpolated = bspline_interpolation(df, column)
                interpolated = seasonal_distribution(df, column)
                interpolated_data[column] = interpolated[column]
                # Set the index to datetime format
                interpolated_data.index = pd.to_datetime(interpolated_data.index)
                
                # Ensure the index is in the correct format
                interpolated_data.index = interpolated_data.index.strftime('%Y-%m-%d')
                interpolated_data.index = pd.to_datetime(interpolated_data.index)
                
                df = interpolated_data           
            
    else:
        # For other data sources, assume 'Year-Month' format
        df.index = pd.to_datetime(df.index + '-01', format='%Y-%m-%d')
    
    if menu == 3 or menu == 5:
        # Apply bspline interpolation for menus 3 and 5
        interpolated_data = pd.DataFrame()
        for column in df.columns:
            #interpolated = bspline_interpolation(df, column)
            interpolated = cubic_interpolation(df, column)
            interpolated_data[column] = interpolated[column]
        
        # Set the index to datetime format
        interpolated_data.index = pd.to_datetime(interpolated_data.index)
        
        # Ensure the index is in the correct format
        interpolated_data.index = interpolated_data.index.strftime('%Y-%m-%d')
        interpolated_data.index = pd.to_datetime(interpolated_data.index)
        
        df = interpolated_data
    
    return df

def PPRINT(msg = None):
    print(f"Line No: {sys._getframe().f_back.f_lineno}: {msg if msg is not None else ''}")

#Generates a Markdown table of contents from the given text
def generate_markdown_toc(text):
    """
    Args:
        text (str): The text to parse for headings.
    Returns:
        str: The generated Markdown table of contents.
    """
    toc_items = []
    level = 1
    for match in re.finditer(r"^(#+)(.*)", text, re.MULTILINE):
        heading_level = len(match.group(1))
        heading_text = match.group(2).strip()
        anchor = heading_text.lower().replace(' ', '-')
        if heading_level < level:
            for _ in range(level - heading_level):
                toc_items.append("  ")
            toc_items.append("  ")
        toc_items.append(f"- <a href='#{anchor}'>{heading_text}</a>")
        level = heading_level
    return "</br>".join(toc_items)

def add_image_to_report(title, filename):
    global image_markdown
    full_path = os.path.abspath(os.path.join('./', unique_folder, filename))
    print(f"Adding image to report: {full_path}")
    if os.path.exists(full_path):
        print(f"Image file exists: {full_path}")
        with open(full_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        # Generate HTML directly
        image_markdown += f"""
        <figure>
            <img src='data:image/png;base64,{encoded_string}' style='max-width: 100%; height: auto;'>
            <figcaption>Figura: {title}</figcaption>
        </figure>
        """
    else:
        print(f"Image file does not exist: {full_path}")

# Fourier Analisys
def fourier_analisys(period='last_year_data'):
  global charts
  global image_markdown
  char='*'
  title=' Análisis de Fourier '
  qty=len(title)
  print(f'\x1b[33m\\n\\n{char*qty}\\n{title}\\n{char*qty}\x1b[0m')
  banner_msg("Análisis de Fourier",margin=1,color1=YELLOW,color2=WHITE)
  csv_fourier="\nAnálisis de Fourier,Frequency,Magnitude\n"
  for keyword in all_keywords:
      # Extract data for the current keyword
      data = trends_results[period][keyword]
      print(f"\\nPalabra clave: {keyword} ({actual_menu})\\n")
      csv_fourier += f"\nPalabra clave: {keyword}\n\n"
      # Create time vector
      time_vector = np.arange(len(data))
      #csv_fourier += f"Vector de tiempo: \\n{time_vector}\\n"
      # Ensure data is a properly aligned NumPy array
      data = np.asarray(data, dtype=float).copy()
      # Perform Fourier transform
      fourier_transform = fftpack.fft(data)
      # Calculate corresponding frequencies
      frequencies = fftpack.fftfreq(len(data))
      # Calculate magnitude (absolute value)
      magnitudes = np.abs(fourier_transform)
      # Filter for positive frequencies (and non-zero)
      positive_mask = frequencies > 0
      positive_frequencies = frequencies[positive_mask]
      positive_magnitudes = magnitudes[positive_mask]
      # Find dominant frequencies
      dominant_indices = np.argsort(positive_magnitudes)[::-1] # Sort descending
      print("Frecuencias dominantes:")
      csv_fourier += "Frecuencia,Magnitud\\n"
      for i in range(min(5, len(dominant_indices))): # Print top 5
          idx = dominant_indices[i]
          freq = positive_frequencies[idx]
          mag = positive_magnitudes[idx]
          print(f"  Frecuencia: {freq:.4f}, Magnitud: {mag:.4f}")
          csv_fourier += f"{freq:.4f},{mag:.4f}\\n"
      csv_fourier += "\\n"

  # Save the CSV data
  csv_filename = os.path.join(unique_folder, 'fourier_analysis.csv')
  try:
      with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
          f.write(csv_fourier)
      print(f"\\nDatos del análisis de Fourier guardados en: {csv_filename}")
  except Exception as e:
      print(f"Error al guardar el archivo CSV del análisis de Fourier: {e}")

# Fourier Analysis with Periodogram Plot
def fourier_analysis2(period='last_20_years_data'):
    """
    Performs Fourier analysis on time series data for specified keywords,
    generates periodogram-like bar plots, adds them to the report,
    and returns the frequency/magnitude data as a CSV-formatted string.

    Args:
        period (str): The key for the period data in trends_results
                      (e.g., 'last_20_years_data').

    Returns:
        str: A CSV-formatted string containing the frequency and magnitude data
             for all processed keywords, or None if an error occurs.
    """
    global charts
    global image_markdown
    global unique_folder
    global all_keywords
    global trends_results
    global actual_menu # Assuming this holds the source name

    if period not in trends_results:
        print(f"Error: Period '{period}' not found in trends_results.")
        return None # Return None on error
    if not all_keywords:
        print("Error: No keywords selected for analysis.")
        return None # Return None on error

    char = '*'
    title = f' Análisis de Fourier ({period}) '
    qty = len(title)
    print(f'\x1b[33m\\n\\n{char*qty}\\n{title}\\n{char*qty}\\x1b[0m')
    banner_msg(f"Análisis de Fourier y Periodograma ({period})", margin=1, color1=YELLOW, color2=WHITE)

    # Initialize csv_fourier string
    csv_fourier = "\nAnálisis de Fourier (Datos),,\n" # Keep initial header generic

    for keyword in all_keywords:
        # Extract data for the current keyword and period
        if keyword not in trends_results[period]:
            print(f"Advertencia: Palabra clave '{keyword}' no encontrada para el período '{period}'. Omitiendo.")
            continue
        data = trends_results[period][keyword]

        # Ensure data is a NumPy array and handle potential NaNs or Infs
        data = np.asarray(data, dtype=float).copy()
        data = data[np.isfinite(data)] # Remove NaNs/Infs which break FFT

        if len(data) < 2: # Need at least 2 points for FFT
            print(f"Advertencia: Datos insuficientes ({len(data)} puntos finitos) para el análisis de Fourier de '{keyword}'. Omitiendo.")
            continue

        print(f"\nProcesando Palabra clave: {keyword} ({actual_menu}) - {len(data)} puntos\n")
        # Add keyword header to csv_fourier
        # Include Period in the header now
        csv_fourier += f"\nHG: {keyword},,\nPeriodo (Meses),Frecuencia,Magnitud (sin tendencia)\n"

        # Perform Fourier transform
        fourier_transform = fftpack.fft(data)
        # Calculate corresponding frequencies
        frequencies = fftpack.fftfreq(len(data), d=1)
        # Calculate magnitude (absolute value)
        magnitudes = np.abs(fourier_transform)

        # Filter for positive frequencies
        positive_mask = (frequencies > 0) & (frequencies <= 0.5)
        positive_frequencies = frequencies[positive_mask]
        positive_magnitudes = magnitudes[positive_mask]

        if len(positive_frequencies) == 0:
            print(f"Advertencia: No se encontraron frecuencias positivas para \'{keyword}\'. Omitiendo análisis y gráfico.")
            continue

        # --- Find and Print Dominant Periods --- 
        dominant_indices = np.argsort(positive_magnitudes)[::-1]
        print("Periodos dominantes (Top 5):")
        for i in range(min(5, len(dominant_indices))):
            idx = dominant_indices[i]
            freq = positive_frequencies[idx]
            mag = positive_magnitudes[idx]
            period_val = 1.0 / freq if freq > 1e-9 else np.inf 
            time_unit = "meses" if menu != 2 else "años"
            period_in_months = period_val * 12 if menu == 2 else period_val
            if period_in_months == np.inf:
                 print(f"  Periodo: Infinito (Tendencia?), Magnitud: {mag:.4f}")
            else:
                 print(f"  Periodo: {period_in_months:.2f} meses, Magnitud: {mag:.4f}")
        print("-"*20)
        # -------------------------------------

        # 1. Detrend Data
        detrended_data = signal.detrend(data)

        # 2. Perform FFT on detrended data
        fft_detrended = fftpack.fft(detrended_data)
        magnitudes_detrended = np.abs(fft_detrended)
        
        # Use existing positive frequencies, get corresponding detrended magnitudes
        positive_magnitudes_detrended = magnitudes_detrended[positive_mask]

        # --- Populate csv_fourier (including Period) --- 
        for freq, mag_detrended in zip(positive_frequencies, positive_magnitudes_detrended):
            period_val = 1.0 / freq if freq > 1e-9 else np.inf
            # Convert period to months based on data source
            period_in_months = period_val * 12 if menu == 2 else period_val
            # Format period for CSV (handle Inf)
            period_str = f"{period_in_months:.2f}" if period_in_months != np.inf else "Inf"
            # Append Period, Frequency, Magnitude
            csv_fourier += f"{period_str},{freq:.6f},{mag_detrended:.4f}\n"
        csv_fourier += "\n"
        # -------------------------------------------

        # --- Generate Enhanced Periodogram Plot --- 
        try:
            # 3. Calculate Periods in Months
            periods_in_units = 1.0 / positive_frequencies[positive_frequencies > 1e-9] # Avoid division by zero
            valid_magnitudes = positive_magnitudes_detrended[positive_frequencies > 1e-9]

            if len(periods_in_units) == 0:
                 print(f"Advertencia: No se encontraron períodos finitos para graficar para '{keyword}'.")
                 continue

            # 4. Determine base unit and convert to months
            # Only Google Books (menu==2) is annual, others assumed monthly
            if menu == 2: # Google Books (Annual)
                periods_in_months = periods_in_units * 12
            else: # Assume Monthly (Google Trends, Crossref, Bain)
                periods_in_months = periods_in_units

            # 5. Filter Periods (Keep <= 240 months)
            period_filter_mask = periods_in_months <= 240
            filtered_periods = periods_in_months[period_filter_mask]
            filtered_magnitudes = valid_magnitudes[period_filter_mask]

            if len(filtered_periods) == 0:
                print(f"Advertencia: No se encontraron períodos <= 240 meses para graficar para '{keyword}'.")
                continue
            
            # 6. Calculate Significance Threshold (e.g., 95th percentile)
            # Using detrended magnitudes for threshold calculation
            threshold = np.percentile(filtered_magnitudes, 95) 
            
            # Identify significant peaks
            significant_mask = filtered_magnitudes >= threshold
            significant_periods = filtered_periods[significant_mask]
            significant_magnitudes = filtered_magnitudes[significant_mask]

            # --- Setup Plot --- 
            fig, ax = plt.subplots(figsize=(15, 7)) # Wider figure
            plt.style.use('ggplot') # Use ggplot style for better visuals

            # --- Plot Data using Stem Plot --- 
            # Plot non-significant points
            markerline, stemlines, baseline = ax.stem(
                filtered_periods[~significant_mask], 
                filtered_magnitudes[~significant_mask],
                linefmt='grey', markerfmt='o', basefmt='k-', 
                label='Componentes no Significativos'
            )
            plt.setp(markerline, markersize=4, color='grey')
            plt.setp(stemlines, linewidth=0.5, color='grey')

            # Plot significant points
            markerline_sig, stemlines_sig, baseline_sig = ax.stem(
                significant_periods, 
                significant_magnitudes,
                linefmt='r-', markerfmt='ro', basefmt='k-', 
                label=f'Componentes Significativos (>{threshold:.2f})'
            )
            plt.setp(markerline_sig, markersize=6, color='red')
            plt.setp(stemlines_sig, linewidth=1, color='red')

            # --- X-axis Log Scale and Limits --- 
            ax.set_xscale('log') # Apply logarithmic scale
            ax.set_xlim(left=2, right=240) # Limit from 2 to 240 months
            
            # Use LogFormatter for better tick labels on log scale
            ax.xaxis.set_major_formatter(ticker.ScalarFormatter())
            # Remove explicit tick setting - let log scale handle it
            # ax.set_xticks([3, 6, 12, 24, 36, 60, 120, 240]) 
            ax.get_xaxis().set_minor_formatter(ticker.NullFormatter())

            # --- Highlight Expected Periods --- 
            expected_periods = {
                3: 'Trimestral', 
                6: 'Semestral', 
                12: 'Anual'
            }
            for p, label in expected_periods.items():
                if p >= ax.get_xlim()[0] and p <= ax.get_xlim()[1]:
                     ax.axvline(x=p, color='blue', linestyle='--', linewidth=0.8, label=f'{label} ({p} meses)')

            # --- Plot Noise Threshold --- 
            ax.axhline(y=threshold, color='purple', linestyle=':', linewidth=1, label=f'Umbral Significancia (95%: {threshold:.2f})')

            # --- Adjust Y-axis (Optional: Log scale or limit if needed) ---
            # Example: Limit Y axis if highest peak is too dominant
            # max_y = np.max(filtered_magnitudes)
            # if max_y > threshold * 10: # If max peak is 10x threshold
            #      ax.set_ylim(top=threshold * 5) # Limit Y to 5x threshold
            # Or use log scale for Y:
            # ax.set_yscale('log')

            # --- Add Peak Labels --- 
            for p, m in zip(significant_periods, significant_magnitudes):
                ax.text(p, m, f' {p:.1f}m', va='bottom', ha='center', fontsize=8, color='red')

            # --- Improve Titles and Labels --- 
            ax.set_title(f'Periodograma Mejorado: "{keyword}" ({actual_menu} - {period})', fontsize=14)
            ax.set_xlabel('Período del Ciclo (Meses) - Escala Logarítmica', fontsize=10)
            ax.set_ylabel('Magnitud Espectral (Datos Detrended)', fontsize=10)
            ax.grid(True, which='major', axis='y', linestyle='--', alpha=0.6)
            ax.grid(True, which='major', axis='x', linestyle=':', alpha=0.4)
            plt.xticks(rotation=45, ha='right')

            # --- Add Legend --- 
            ax.legend(fontsize=8)

            plt.tight_layout()
            plot_title = f'Periodograma Mejorado para {keyword} ({actual_menu})'
            plot_filename_base = f"periodogram_enhanced_{keyword}_{period}.png" # New filename
            plot_filename = get_unique_filename(plot_filename_base, unique_folder)
            full_plot_path = os.path.join(unique_folder, plot_filename)
            plt.savefig(full_plot_path)
            print(f"Gráfico del periodograma mejorado guardado en: {full_plot_path}")
            add_image_to_report(plot_title, plot_filename)
            plt.close(fig)
        except Exception as e:
            print(f"Error al generar o guardar el gráfico del periodograma mejorado para '{keyword}': {e}")
            import traceback
            traceback.print_exc()
            if 'fig' in locals() and plt.fignum_exists(fig.number):
                 plt.close(fig)
        # -------------------------------------

    # Return the accumulated CSV data string
    return csv_fourier

def seasonal_analysis(period='last_20_years_data'):
    global charts
    global csv_seasonal
    global image_markdown
    global skip_seasonal  
     
    # Assuming 'trends_results' is a dictionary
    data = pd.DataFrame(trends_results[period])
    banner_msg(f'Análisis Estacional {actual_menu}',margin=1,color1=YELLOW,color2=WHITE)
    # Handle 'isPartial' column (if present)
    if 'isPartial' in data.columns:
        data = data.drop('isPartial', axis=1)
    # Ensure the index is datetime
    if 'date' in data.columns:
        data['date'] = pd.to_datetime(data['date'])
        data.set_index('date', inplace=True)
    else:
        data.index = pd.to_datetime(data.index)
    # Get all numeric columns (keywords)
    all_keywords = data.select_dtypes(include=[np.number]).columns.tolist()
    skip_seasonal = [False for _ in range(len(all_keywords))]
    csv_seasonal = ""# Analyze each keyword
    n=0
    for keyword in all_keywords:
        def decompose_series(series):
            if menu == 2:
                # For annual data, we can't perform seasonal decomposition
                print(f"Seasonal decomposition not applicable for annual data ({keyword})")
                skip_seasonal[n] = True
                return None
            else:
                if len(series) < 24:
                    print(f"Not enough data points for seasonal decomposition ({keyword})")
                    skip_seasonal[n] = True
                    return None
                decomposition = sm.tsa.seasonal_decompose(series, model='additive', period=12)
                seasonal = decomposition.seasonal
                return seasonal

        print(f"\nAnalizando {keyword} ({actual_menu}):")
        csv_seasonal += f'\nAnalyzing {keyword} ({actual_menu}):,Values\n\n'
        # Extract the series for the keyword
        series = data[keyword]
        # Decompose the time series
        seasonal = decompose_series(series)
        
        if seasonal is None:
            continue  # Skip to the next keyword if decomposition is not possible

        seasonal_index = seasonal / series.mean()
        print(seasonal_index)
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            csv_seasonal+=seasonal_index.to_csv(index=True)
        # Prepare for plot formatting
        plt.figure(figsize=(12, 2))
        plt.plot(seasonal_index, color='green')
        plt.title(f'Indice Estacional de {keyword} ({actual_menu})')
        # Set major and minor tick locators and formatters
        years = YearLocator()
        months = MonthLocator()
        years_fmt = DateFormatter('%Y')
        month_fmt = DateFormatter('')  # Abbreviated month name
        ax = plt.gca()
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(years_fmt)
        ax.xaxis.set_minor_locator(months)
        ax.xaxis.set_minor_formatter(month_fmt)
        # Set x-axis limits to start and end with data
        plt.xlim(seasonal_index.index.min(), seasonal_index.index.max())
        # Customize remaining plot elements
        plt.xlabel('Años')
        plt.ylabel('Índice')
        plt.grid(True)
        # Save the plot to the unique folder
        base_filename = f'{filename}_season_{keyword[:3]}.png'
        image_filename=get_unique_filename(base_filename, unique_folder)
        plt.savefig(os.path.join(unique_folder, image_filename), bbox_inches='tight')
        add_image_to_report(f'Índice Estacional para {keyword}', image_filename)
        charts += f'Índice de Estacional para {keyword} ({image_filename})\n\n'
        # Remove plt.show() to prevent graph windows from appearing
        plt.close()
    csv_seasonal="".join(csv_seasonal)
    return

# This function finds the best ARIMA (p, d, q) parameters for a given time series data.
def find_best_arima_params(data):
  """
  This function finds the best ARIMA (p, d, q) parameters for a given time series data.
  Args:
      data (pandas.Series): The time series data to analyze.
  Returns:
      tuple: A tuple containing the best values for (p, d, q), information criterion used, and the fitted model.
  """
  # Ensure data is a pandas Series
  if not isinstance(data, pd.Series):
      data = pd.Series(data)

  # Remove any infinite values and interpolate NaNs
  data = data.replace([np.inf, -np.inf], np.nan).interpolate()

  # Check for stationarity using Dickey-Fuller test (optional)
  from statsmodels.tsa.stattools import adfuller
  result = adfuller(data)
  if result[1] > 0.05:
    print("Los datos no son estacionarios. Considere diferenciar.")

  # Use auto_arima from pmdarima
  stepwise_model = auto_arima(data, start_p=1, d=None, start_q=1, start_P=1, Start_Q=1,
                              max_p=5, max_d=5, max_q=5, max_P=5, max_Q=5, D=10, max_D=10,
                              m=1,  # Set m=1 for non-seasonal data
                              seasonal=False,  # Set seasonal=False for non-seasonal data
                              error_action='ignore',  # Ignore warnings
                              trace=True,  # Print details during search
                              suppress_warnings=True)  # Suppress warnings

  # Return the parameters, information criterion, and fitted model
  return stepwise_model.order, stepwise_model.aic, stepwise_model

# Fit ARIMA model
def arima_model(mb=24, mf=60, ts=18, p=0, d=1, q=2, auto=True):
  global charts
  global image_markdown
  global csv_arimaA
  global csv_arimaB
  global csv_arima
  global skip_arima
  skip_arima = [False for _ in range(len(all_keywords))]    
  csv_arimaA = ["" for _ in range(len(all_keywords))]
  csv_arimaB = ["" for _ in range(len(all_keywords))]
  
  print('\n\n--------------------- MODELO ARIMA ---------------------\n')
  csv_arima = "\nMODELO ARIMA\n"
  # Assuming 'trends_results' is a dictionary
  data = pd.DataFrame(trends_results['last_20_years_data'])
  # Handle 'isPartial' column (if present)
  if 'isPartial' in data.columns:
      data = data.drop('isPartial', axis=1)

  # Clean the data: remove inf and nan values
  data = data.replace([np.inf, -np.inf], np.nan).dropna()

  train = data[:-ts]
  test = data[-ts:]

  # Set frequency information (optional)
  try:
      train.index = pd.to_datetime(train.index, format="%Y-%m-%d")  # Assuming daily frequency
      if menu != 2:
          train = train.resample('M').mean()  # Resample to monthly frequency
  except pd.errors.ParserError:
      print("Couldn't infer datetime format. Please provide a format string (e.g., '%Y-%m-%d')")

  # Fit ARIMA models to each numeric column
  numeric_columns = train.select_dtypes(include=['int64', 'float64'])
  n=0
  for col in numeric_columns:
      banner_msg(f' Modelo ARIMA para: {col} {actual_menu} ',margin=1,color1=YELLOW,color2=WHITE)
      csv_arimaA[n] = f"\n\nFitting ARIMA model for {col} ({actual_menu})\n"
      
      # Check if the column has enough non-zero values
      if (train[col] != 0).sum() <= 10:  # Adjust this threshold as needed
          print(f"Skipping {col} due to insufficient non-zero values")
          skip_arima[n] = True
          csv_arimaA[n] += f"Skipping {col} due to insufficient non-zero values\n"
          continue

      try:
          best_params, best_aic, best_model = find_best_arima_params(train[col])
          if auto:
              p, d, q = best_params  # Unpack the tuple
              print(f"Los mejores parámetros de ARIMA encontrados: p={p}, d={d}, q={q}")
          
          # Fit ARIMA model
          model = ARIMA(train[col], order=(p, d, q))
          results = model.fit()
          print(results.summary())
          csv_arimaA[n] += f'\n<blockquote>{results.summary()}</blockquote>'
          csv_arima += csv_arimaA[n]
          # Prepare data for plotting (last 24 months)
          last_months = train[col].iloc[-mb:]
          
          # Make predictions using the statsmodels ARIMA model with confidence intervals
          predictions = results.forecast(steps=mf)
          
          # Get confidence intervals from the statsmodels ARIMA model
          pred_conf = results.get_forecast(steps=mf)
          conf_int = pred_conf.conf_int()
          
          # Calculate RMSE and MAE
          actual = test[col]
          predicted = predictions
          if len(predictions) > len(test[col]):
            predicted = predictions[:len(test[col])]
          
          # Try using squared parameter if available, otherwise calculate RMSE manually
          try:
              rmse = mean_squared_error(actual, predicted, squared=False)
          except TypeError:
              # For older scikit-learn versions that don't support the squared parameter
              mse = mean_squared_error(actual, predicted)
              rmse = np.sqrt(mse)
              
          mae = mean_absolute_error(actual, predicted)
          print(f"Predicciones para {col} ({actual_menu}):\n{predictions}")
          print(f"\nError Cuadrático Medio Raíz (ECM Raíz) RMSE: {rmse}\nError Absoluto Medio (EAM) MAE: {mae}\n")

          csv_arimaB[n] = f"\nPredictions for {col} ({actual_menu}):,\n"
          csv_arimaB[n] += f"Date,Values\n{predictions.to_csv(index=True)}"
          csv_arimaB[n] += f"\nRMSE, MAE\n{rmse},{mae}"
          csv_arima += csv_arimaB[n]
          n += 1
          
          # Combine actual data and predictions for plotting
          data_to_plot = pd.concat([last_months, predictions])
          # Create the plot
          fig, ax = plt.subplots(figsize=(12, 8))  # Adjust figure size as needed
          # Plot data actual
          data_actual_line, = ax.plot(data_to_plot.index, data_to_plot, label='Data Actual')
          # Plot predictions with dashed line and blue color
          predictions_line, = ax.plot(predictions.index, predictions, label='Predicciones', linestyle='--', color='blue')
          # Plot test data with scatter and alpha
          test_scatter = ax.scatter(test.index, test[col], label='Data Test', alpha=0.4, marker='*')
          # Fill between for confidence interval
          ci_fill = ax.fill_between(predictions.index, 
                                   conf_int.iloc[:, 0],  # Lower bound
                                   conf_int.iloc[:, 1],  # Upper bound
                                   alpha=0.1, color='b', label='Intervalo de Confidencia')
          # Add labels and title
          ax.set_title(f"Modelo ARIMA para {col} ({actual_menu})")
          ax.set_xlabel('Meses - Años')
          ax.set_ylabel(col)
          # Set up the x-axis to show years
          years = mdates.YearLocator()
          months = mdates.MonthLocator()
          years_fmt = mdates.DateFormatter('%Y')
          # Set major ticks to years
          ax.xaxis.set_major_locator(years)
          ax.xaxis.set_major_formatter(years_fmt)
          # Set minor ticks to months
          ax.xaxis.set_minor_locator(months)
          # Ensure x-axis starts and ends with data points
          ax.set_xlim(data_to_plot.index[0], data_to_plot.index[-1])
          # Add vertical lines for each year with fine style
          for year in ax.xaxis.get_majorticklocs():
              ax.axvline(x=year, color='black', linestyle='--', linewidth=0.5, alpha=0.5)
          # Rotate and align the tick labels
          plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
          # Use a more precise date string for the axis label
          ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
          # Create legend
          ax.legend([data_actual_line, predictions_line, test_scatter, ci_fill],
                    ['Data Actual', 'Predicciones', 'Data Test', 'Intervalo de Confidencia'],
                    loc='upper left')
          # Set y-axis limits based on top_choice
          if top_choice == 2:
              buffer = 10  # 10% buffer for 0-100 scale
              ax.set_ylim(-buffer, 100 + buffer)  # Fix Y-axis scale to 0-100 with buffer
          else:
              ax.autoscale(axis='y')  # Let matplotlib automatically determine the best y-axis scale
            #   train_min = train[col].min()
            #   train_max = train[col].max()
            #   buffer = (train_max - train_min) * 0.1  # Add a 10% buffer
            #   ax.set_ylim(train_min - buffer, train_max + buffer)
          #plt.autoscale(ax=ax)  # Fine-tune based on actual data
          # Adjust layout to prevent cutoff of tick labels
          fig.tight_layout()
          # Save the plot
          base_filename = f'{filename}_arima_{col[:3]}.png'
          image_filename=get_unique_filename(base_filename, unique_folder)
          plt.savefig(os.path.join(unique_folder, image_filename), bbox_inches='tight')
          add_image_to_report(f'Modelo ARIMA para {col}', image_filename)
          charts += f'Modelo ARIMA para {col} ({image_filename})\n\n'
          # Remove plt.show() to prevent graph windows from appearing
          plt.close()
      except Exception as e:
          print(f"Error fitting ARIMA model for {col}: {str(e)}")
          csv_arima += f"Error fitting ARIMA model for {col}: {str(e)}\n"
          continue

  return csv_arima

# Searches the keyword-term dictionary for the given keyword and returns its corresponding term.
def search_keyword_term_dict(keyword_term_dict, keyword):
    """
    Args:
        keyword_term_dict: A dictionary mapping keywords to their corresponding terms.
        keyword: The keyword to search for.
    Returns:
        The corresponding term if found, or None if not found.
    """
    # Handle case-insensitive search by converting both keyword and dictionary keys to lowercase
    keyword = keyword.lower()
    lowercase_dict = {key.lower(): value for key, value in keyword_term_dict.items()}
    # Check if the keyword exists in the lowercase dictionary
    if keyword in lowercase_dict:
        return lowercase_dict[keyword]
    else:
        return None

def remove_ispartial(mean):
  if 'isPartial' in mean.index:
      ispartial = mean['isPartial']
      cleaned_mean = mean.drop('isPartial')
      return cleaned_mean, ispartial
  return mean, None

#  Calculates the mean of the Google Trends data and normalizes it.
def process_data(data):
  """
  Args:
    data: A pandas DataFrame containing the Google Trends data.
  Returns:
    A pandas Series containing the normalized mean values.
  """
  #if menu == 2:
  mean = data.mean()
  #else:
    #mean = round(data.mean(), 2)
  return mean

#  Fetches and processes Google Trends data for different time periods.
def process_file_data(all_kw, d_filename):
  global combined_dataset
  global combined_dataset2
  global menu
  global earliest_year
  global latest_year
  global total_years
  
  # Ensure menu has a default value if not set
  if 'menu' not in globals() or menu is None:
    menu = 1  # Default value, adjust as needed
    
  menu2 = menu
  if top_choice == 1:
    # Group data and calculate means
    all_data = get_file_data(d_filename, menu2)
  if top_choice == 2:
    # Use combined_dataset2 instead of combined_dataset when in cross-source analysis mode
    all_data = combined_dataset2

  # Calculate the earliest and latest years in the dataset
  earliest_year = all_data.index.min().year
  latest_year = all_data.index.max().year
  total_years = latest_year - earliest_year + 1

  if top_choice == 1:
    if menu == 2:
        last_20_years = all_data[-20:]
        last_15_years = last_20_years[-15:]
        last_10_years = last_20_years[-10:]
        last_5_years = last_20_years[-5:]
        last_year = last_20_years[-1:]
    else:
        last_20_years = all_data[-20*12:]
        last_15_years = last_20_years[-15*12:]
        last_10_years = last_20_years[-10*12:]
        last_5_years = last_20_years[-5*12:]
        last_year = last_20_years[-1*12:]
  else:
    if 2 in selected_sources:
        last_20_years = all_data[-20:]
        last_15_years = last_20_years[-15:]
        last_10_years = last_20_years[-10:]
        last_5_years = last_20_years[-5:]
        last_year = last_20_years[-1:]
    else:
        last_20_years = all_data[-20*12:]
        last_15_years = last_20_years[-15*12:]
        last_10_years = last_20_years[-10*12:]
        last_5_years = last_20_years[-5*12:]
        last_year = last_20_years[-1*12:]

  # mean_last_20_B = process_data(last_20_years_B)
  mean_all = process_data(all_data)
  mean_last_20 = process_data(last_20_years)
  mean_last_15 = process_data(last_15_years)
  mean_last_10 = process_data(last_10_years)
  mean_last_5 = process_data(last_5_years)
  mean_last_year = process_data(last_year)

  # Return results as a dictionary including the new year-related values
  return {
      'all_data': all_data,
      'mean_all': mean_all,
      'last_20_years_data': last_20_years,
      'mean_last_20': mean_last_20,
      'last_15_years_data': last_15_years,
      'mean_last_15': mean_last_15,
      'last_10_years_data': last_10_years,
      'mean_last_10': mean_last_10,
      'last_5_years_data': last_5_years,
      'mean_last_5': mean_last_5,
      'last_year_data': last_year,
      'mean_last_year': mean_last_year,
      'earliest_year': earliest_year,
      'latest_year': latest_year,
      'total_years': total_years,
  }

  # Replaces all spaces in each element of an array with newlines.
def replace_spaces_with_newlines(array):
  """
  Args:
    array: The input array.
  Returns:
    A new array with spaces replaced by newlines.
  """
  new_array = []
  for element in array:
    new_element = element.replace(' ', '\n')
    new_element = new_element.replace('\n-\n', '\n')
    new_array.append(new_element)
  return new_array

# This function applies a simple moving average to smooth the data.
def smooth_data(data, window_size=5, transition_points=10):
    """
    Applies a weighted moving average to smooth the data, with increased smoothness
    for the first and last few data points, preserving the very first and last data points.

    Args:
    data: A list or NumPy array of data points.
    window_size: The number of data points to include in the moving average (default: 5).
    transition_points: The number of points over which to gradually increase/decrease smoothness (default: 10).

    Returns:
    A NumPy array of smoothed data points with the same shape as the original data.
    """
    data = np.array(data)
    weights = np.arange(1, window_size + 1)

    # Create a padded version of the data to handle edge cases
    padded_data = np.pad(data, (window_size // 2, window_size - 1 - window_size // 2), mode='edge')

    # Apply the weighted moving average
    smoothed_data = np.convolve(padded_data, weights / weights.sum(), mode='valid')

    # Ensure the first and last points are preserved
    smoothed_data[0] = data[0]
    smoothed_data[-1] = data[-1]

    # Create a gradual transition between original and smoothed data for the first 'transition_points'
    for i in range(1, min(transition_points, len(data) // 2)):
        alpha = (i / transition_points) ** 2  # Using a quadratic function for smoother transition
        smoothed_data[i] = (1 - alpha) * data[i] + alpha * smoothed_data[i]

        # Mirror the transition for the end of the data
        smoothed_data[-i-1] = (1 - alpha) * data[-i-1] + alpha * smoothed_data[-i-1]

    #PPRINT(f"original data\n{data}")
    #PPRINT(f"smothed data\n{smoothed_data}")
    return smoothed_data

# --- Prerequisite: Assume 'source_trends_results' is populated before calling ---
# Example structure for source_trends_results (needs to be created elsewhere):
# source_trends_results = {
#     'all_data': {'Google Trends': pd.Series(...), 'Google Books': pd.Series(...), ...},
#     'mean_all': {'Google Trends': 15.5, 'Google Books': 0.8, ...},
#     'last_20_years_data': {'Google Trends': pd.Series(...), 'Google Books': pd.Series(...), ...},
#     'mean_last_20': {'Google Trends': 18.2, 'Google Books': 0.7, ...},
#     # ... other periods (15, 10, 5 years)
# }
# Assume selected_keyword, selected_sources, filename, unique_folder,
# earliest_date, latest_date are also available globally.

# --- NEW Helper function for source-based line plots ---
def setup_source_subplot(ax, data_dict, mean_dict, title, ylabel, colors, source_list, period_start_date, period_end_date):
    """
    Sets up a subplot showing time series data for multiple sources.
    Uses provided start/end dates for accurate x-axis limits.
    """
    print(f"  Setting up source line plot: {title} - {ylabel}")
    # --- Restore global min/max and plot_min_max calculation ---
    global_min = float('inf')
    global_max = float('-inf')
    plot_min_max = {} # Initialize the dictionary

    # Calculate global min/max across sources for this period
    for source in source_list:
        if source in data_dict and not data_dict[source].empty:
            series = data_dict[source]
            try:
                # Check if series contains numeric data before calculating min/max
                if pd.api.types.is_numeric_dtype(series):
                    plot_min = series.min()
                    plot_max = series.max()
                    # Ensure plot_min and plot_max are valid numbers
                    if pd.notna(plot_min) and pd.notna(plot_max):
                         plot_min_max[source] = (plot_min, plot_max)
                         global_min = min(global_min, plot_min)
                         global_max = max(global_max, plot_max)
                    else:
                         print(f"[Warning] Non-numeric or NaN values found in min/max for source {source}. Skipping min/max.")
                else:
                    print(f"[Warning] Non-numeric data type for source {source}. Cannot calculate min/max.")

            except Exception as e:
                print(f"[Warning] Could not calculate plot min/max for source {source}: {e}")
        else:
             print(f"[Warning] Data for source {source} is missing or empty for min/max calc.")
    # -------------------------------------------------------------

    if not plot_min_max: # This check should now work correctly
         print("[Warning] No valid source data found for plot limits. Using default 0-100.")
         global_min, global_max = 0, 100 # Fallback    # ... (global min/max calculation remains the same) ...

    if not plot_min_max:
         print("[Warning] No valid source data found for plot limits. Using default 0-100.")
         global_min, global_max = 0, 100 # Fallback

    buffer = (global_max - global_min) * 0.1 if global_max > global_min else 10
    y_min_limit = global_min - buffer
    y_max_limit = global_max + buffer * 1.5

    legend_handles = []
    legend_labels = []
    for source in source_list:
        if source in data_dict and not data_dict[source].empty:
            series_data_to_plot = data_dict[source]
            # Use fixed colors with a default fallback
            color = colors.get(source, default_color)
            line, = ax.plot(series_data_to_plot.index, series_data_to_plot, label=source, color=color)
            legend_handles.append(line)
            legend_labels.append(source)
        else:
            print(f"[Warning] Data for plotting source '{source}' is missing or empty.")

    # --- Formatting ---
    ax.grid(True, which='major', linestyle='--', linewidth=0.3, color='grey', alpha=0.1)
    ax.set_ylim(bottom=y_min_limit, top=y_max_limit)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_title(title, fontsize=16)

    # --- X-Axis date formatting using PASSED DATES ---
    # Ensure dates are valid Timestamps
    if not isinstance(period_start_date, pd.Timestamp):
        period_start_date = pd.Timestamp(period_start_date)
    if not isinstance(period_end_date, pd.Timestamp):
        period_end_date = pd.Timestamp(period_end_date)

    # Set precise limits based on the period being plotted
    ax.set_xlim(mdates.date2num(period_start_date), mdates.date2num(period_end_date))

    # Determine appropriate locators based on the period duration
    period_duration_days = (period_end_date - period_start_date).days

    if period_duration_days <= 3 * 365: # 1-3 years
        year_locator = mdates.YearLocator(base=1)
        month_locator = mdates.MonthLocator()
        ax.xaxis.set_major_locator(year_locator)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_minor_locator(month_locator)
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b')) # Show month names
    elif period_duration_days <= 10 * 365: # 4-10 years
        year_locator = mdates.YearLocator(base=1) # Yearly major ticks
        month_locator = mdates.MonthLocator(bymonth=[1, 7]) # Semi-annual minor ticks
        ax.xaxis.set_major_locator(year_locator)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_minor_locator(month_locator)
        ax.xaxis.set_minor_formatter(FuncFormatter(lambda x, pos: '|' if mdates.num2date(x).month==7 else '')) # Tick marks only
    else: # > 10 years
        year_locator = mdates.YearLocator(base=5) # 5-year major ticks
        minor_year_locator = mdates.YearLocator(base=1) # Yearly minor ticks
        ax.xaxis.set_major_locator(year_locator)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_minor_locator(minor_year_locator)
        ax.xaxis.set_minor_formatter(FuncFormatter(lambda x, pos: '')) # No minor labels

    ax.tick_params(axis='both', which='major', labelsize=8)
    ax.tick_params(axis='x', which='major', labelrotation=45, pad=10) # Added padding
    ax.tick_params(axis='both', which='minor', labelsize=6)
    ax.tick_params(axis='x', which='minor', labelrotation=45)

    return ax, legend_handles, legend_labels


# --- NEW Helper function for source-based bar plots ---
def setup_source_bar_subplot(ax, mean_dict, title, y_max, x_pos, colors, source_list):
    """ Sets up bar subplot using fixed colors """
    print(f"  Setting up source bar plot: {title}")
    means_to_plot = []
    colors_to_plot = []
    labels_to_plot = []

    for source in source_list:
        mean_val = mean_dict.get(source, 0)
        means_to_plot.append(mean_val)
        # Use fixed colors with default fallback
        colors_to_plot.append(colors.get(source, default_color))
        labels_to_plot.append(source.replace(" ", "\n"))

    # ... (rest of bar plot formatting remains the same) ...
    ax.grid(True, which='major', linestyle='--', linewidth=0.5, color='grey', alpha=0.1)
    bar_container = ax.bar(x_pos, means_to_plot, align='center', color=colors_to_plot)
    ax.bar_label(bar_container, fmt='%.2f') # Adjust format as needed

    # ... (formatting) ...
    ax.set_title(title, fontsize=16)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels_to_plot, rotation=0, ha='center', fontsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)

    buffer = y_max * 0.1 if y_max > 0 else 1
    ax.set_ylim(0, y_max + buffer)

    plt.setp(ax.get_yticklabels(), rotation=45, ha='right')

    return ax

# --- The new main comparison function ---
def relative_comparison2():
    global source_trends_results
    global selected_sources # Contains numbers like [1, 2, 4]
    global dbase_options  # Maps numbers to friendly names
    global charts
    global selected_keyword
    global filename
    global unique_folder
    global earliest_date
    global latest_date
    global fixed_source_colors

    # Basic check
    if not source_trends_results or not selected_sources:
        print("Error: source_trends_results or selected_sources not available for relative_comparison2.")
        print("DEBUG: Failing the 'if not source_trends_results or not selected_sources' check.")
        return

    print(f"\nInside relative_comparison2: Starting source comparison charts for keyword: '{selected_keyword}'...")

    fig = plt.figure(figsize=(24, 40))

    num_sources = len(selected_sources)
    friendly_source_names = [dbase_options.get(key, f"Unknown Source {key}") for key in selected_sources]
    x_pos = np.arange(num_sources)

    # --- Define Full Period Order including 1 year ---
    period_order = ['all_data', 'last_20_years_data', 'last_15_years_data', 'last_10_years_data', 'last_5_years_data', 'last_1_year_data']
    # Filter based on available keys in source_trends_results to avoid errors
    available_periods_data_keys = [p for p in period_order if p in source_trends_results]
    num_periods_to_plot = len(available_periods_data_keys)
    # -------------------------------------------------

    if num_periods_to_plot == 0:
        print("Error: No data periods found in source_trends_results.")
        plt.close(fig) # Close the figure if erroring out
        return

    # --- Use FIXED colors ---
    source_colors = fixed_source_colors
    # -----------------------

    # Calculate the overall maximum mean value
    max_y_value = 0
    for period_key in source_trends_results:
        if period_key.startswith('mean_'):
            means = source_trends_results[period_key]
            if means:
                 try: # Add try-except for safety if values aren't numbers
                     current_max = max(means.values())
                     max_y_value = max(max_y_value, current_max)
                 except ValueError:
                     print(f"Warning: Non-numeric value found in means for period {period_key}")
                     pass # Or handle differently

    # --- Adjust Grid Spec ---
    total_rows = num_periods_to_plot + 1 # +1 for title/space
    gs = fig.add_gridspec(total_rows, 10, height_ratios=[0.1] + [1] * num_periods_to_plot) # Adjusted title height ratio
    # ---

    axODD = slice(0, 7)
    axEVEN = slice(8, 10)
    title_odd_base = f'Comparison of Sources for "{selected_keyword}"\nOver Time'
    title_even_base = f'Average Value per Source for "{selected_keyword}"\nFor the Period'

    plot_row_index = 1
    legend_handles, legend_labels = [], []

    # --- Loop through AVAILABLE periods ---
    current_year = latest_date.year # Needed for date calculation
    earliest_year_in_data = earliest_date.year # Needed for date calculation

    for period_data_key in available_periods_data_keys: # Use the filtered list
        # Determine mean key and period duration (handle 'all' and 'last_1_year')
        period_years_str = 'all'
        if period_data_key == 'all_data':
            mean_key = 'mean_all'
            period_start = earliest_date
            period_end = latest_date
        elif period_data_key == 'last_1_year_data':
            mean_key = 'mean_last_1'
            start_year = max(earliest_year_in_data, current_year - 1)
            period_start = pd.Timestamp(f"{start_year}-01-01")
            period_end = latest_date # Or pd.Timestamp(f"{start_year}-12-31")
            period_years_str = '1'
        else: # 5, 10, 15, 20 years
             try:
                 years = int(period_data_key.split('_')[1])
                 mean_key = f'mean_last_{years}'
                 start_year = max(earliest_year_in_data, current_year - years)
                 period_start = pd.Timestamp(f"{start_year}-01-01")
                 period_end = latest_date
                 period_years_str = str(years)
             except (IndexError, ValueError):
                 print(f" Skipping period: Could not parse years from key '{period_data_key}'")
                 continue # Skip if key format is unexpected

        # Check if mean key also exists
        if mean_key not in source_trends_results:
            print(f" Skipping period: Mean key '{mean_key}' not found for data key '{period_data_key}'")
            continue

        print(f" Processing period: {period_data_key} (Row {plot_row_index})")
        period_data = source_trends_results[period_data_key]
        period_means = source_trends_results[mean_key]

        # Define Y-label
        if period_data_key == 'all_data':
             total_years = period_end.year - period_start.year
             ylabel = f'Full Period ({total_years} years)\n{period_start.year}-{period_end.year}'
        else:
             ylabel = f'{period_years_str}-Year Period\n{period_start.year}-{period_end.year}'

        ax_line = fig.add_subplot(gs[plot_row_index, axODD])
        ax_bar = fig.add_subplot(gs[plot_row_index, axEVEN])

        current_title_odd = title_odd_base if plot_row_index == 1 else ''
        current_title_even = title_even_base if plot_row_index == 1 else ''

        # Call helpers with friendly names and period dates
        try:
            _, handles, labels = setup_source_subplot(
                ax_line, period_data, period_means, current_title_odd, ylabel,
                source_colors, friendly_source_names,
                period_start, period_end # Pass calculated period dates
            )
            if plot_row_index == 1 and handles: # Store legend info only if successful
                legend_handles, legend_labels = handles, labels
        except Exception as e:
             print(f"Error calling setup_source_subplot for {period_data_key}: {e}")

        try:
            # Use fixed colors in bar plot helper as well
            setup_source_bar_subplot(
                ax_bar, period_means, current_title_even, max_y_value, x_pos, source_colors, friendly_source_names
            )
        except Exception as e:
             print(f"Error calling setup_source_bar_subplot for {period_data_key}: {e}")

        plot_row_index += 1
        print(f"  Finished processing row {plot_row_index-1}") # Debug print

    # --- Add overall Legend ---
    if friendly_source_names:
        # Create legend handles manually using the fixed colors
        legend_patch_handles = [mpatches.Patch(color=source_colors.get(name, default_color), label=name) for name in friendly_source_names]
        fig.legend(handles=legend_patch_handles, loc='lower center', bbox_to_anchor=(0.5, 0.01), # Adjusted y position
                   ncol=min(num_sources, 5), fontsize=10)
    else:
        print("Warning: No legend items generated for the plot.")

    # ... (Final Layout and Save) ...
    try:
        # Use constrained_layout for better automatic spacing
        fig.set_constrained_layout_pads(w_pad=0.1, h_pad=0.1, hspace=0.05, wspace=0.05) # Fine-tune padding
        fig.set_constrained_layout(True)

        base_filename = f'{selected_keyword}_source_comparison_overtime.png'
        image_filename = get_unique_filename(base_filename, unique_folder)
        save_path = os.path.join(unique_folder, image_filename)
        plt.savefig(save_path, bbox_inches='tight')
        print(f" Source comparison plot saved to: {save_path}")

        chart_title = f"Comparison of Data Sources for '{selected_keyword}'"
        add_image_to_report(chart_title, image_filename)
        charts += f"{chart_title} ({image_filename})\n\n"

    except Exception as e:
        print(f"Error during plot layout/saving/reporting: {e}")
    finally:
        plt.close(fig)

    print(f"\nSource comparison charts attempted for '{selected_keyword}'. Check logs for warnings/errors.")


# Create Charts
def relative_comparison():
    global charts
    global title_odd_charts
    global title_even_charts
    global image_markdown
    global keycharts
    global current_year
    global earliest_year
    global latest_year
    global total_years
    
    print(f"\nCreando gráficos de comparación relativa...")

    fig = plt.figure(figsize=(24, 30))  # Reduced height from 35 to 30

    x_pos = np.arange(len(all_keywords))

    # Define colors here
    colors = plt.cm.rainbow(np.linspace(0, 1, 5))
    colors[2] = [0, 0.5, 0, 1]
    #colors = ['#FF0000', '#0000FF', '#00FF00', '#FF00FF', '#00FFFF', '#FFA500', '#800080', '#008000', '#FF69B4', '#4B0082'][:len(all_keywords)]  # Red, Blue, Green, Magenta, Cyan, Orange, Purple, Dark Green, Pink, Indigo
    window_size = 10

    # Calculate the maximum y-value across all datasets
    all_means = [
        trends_results['mean_all'], # if menu == 2 or menu == 4 else None,
        trends_results['mean_last_20'],
        trends_results['mean_last_15'],
        trends_results['mean_last_10'],
        trends_results['mean_last_5']
    ]
    max_y_value = max(mean.max() for mean in all_means if mean is not None)
    
    if top_choice == 1:
        # Determine the number of rows in the gridspec
        total_rows = 6 if menu == 2 or menu == 4 or menu == 3 or menu == 5 else 5
    else:
        len_years = latest_date.year - earliest_date.year
        total_rows = 7 if len_years > 20 else 6
        
    # Create grid spec with 10 columns and the determined number of rows
    gs = fig.add_gridspec(total_rows, 10, height_ratios=[0.2] + [1] * (total_rows - 1))

    # Define slices for odd and even subplots
    axODD = slice(0, 7)  # Line graph takes 7 columns
    axEVEN = slice(8, 10)  # Bar graph takes 3 columns, leaving one column (7) blank

    if top_choice == 1:
        # ********* OVER TIME CHART TITLES **********
        if menu == 1:
          title_odd_charts = 'Interés relativo\na lo largo del tiempo'
          title_even_charts = 'Interés relativo\npara el período'
        if menu == 2:
          title_odd_charts = 'Publicaciones Generales relativas\na lo largo del tiempo'
          title_even_charts = 'Publicaciones Generales relativas\npara el período'
        if menu == 3:
          title_odd_charts = 'Usabilidad relativa\na lo largo del tiempo'
          title_even_charts = 'usabilidad relativa\npara el período'
        if menu == 4:
          title_odd_charts = 'Publicaciones Especializadas relativas\na lo largo del tiempo'
          title_even_charts = 'Publicaciones Especializadas elativas\npara el período'
        if menu == 5:
          title_odd_charts = 'Satisfacción por el uso\na lo largo del tiempo'
          title_even_charts = 'Satisfacción por el uso\npara el período'
    else:
        # ********* OVER TIME CHART TITLES **********
        if 1 in selected_sources:
          keycharts.append('Interes') 
        if 2 in selected_sources:
          keycharts.append('Publicaciones Generales') 
        if 3 in selected_sources:
          keycharts.append('Usabilidad')  
        if 4 in selected_sources:
          keycharts.append('Publicaciones Especializadas')  
        if 5 in selected_sources:
          keycharts.append('Satisfacción')
            
        title_charts = ', '.join(keycharts)  
        title_odd_charts = f'{title_charts}\na lo largo del tiempo para {actual_menu}'
        title_even_charts = f'{title_charts}\nen el período para {actual_menu}'  

    if top_choice == 1:
        if total_years > 20:
            gs = fig.add_gridspec(6, 10, height_ratios=[0.2] + [1] * (6 - 1))
        elif total_years > 15:
            gs = fig.add_gridspec(5, 10, height_ratios=[0.2] + [1] * (5 - 1))
        elif total_years > 10:
            gs = fig.add_gridspec(4, 10, height_ratios=[0.2] + [1] * (4 - 1))
        elif total_years > 5:
            gs = fig.add_gridspec(3, 10, height_ratios=[0.2] + [1] * (3 - 1))
        
        
    if top_choice == 1:
        i = 1
        # all data
        if total_years > 20:
            ax1 = fig.add_subplot(gs[i, axODD])
            ax2 = fig.add_subplot(gs[i, axEVEN])
            setup_subplot(ax1, trends_results['all_data'], trends_results['mean_all'], title_odd_charts, f'Período de {total_years} años\n({earliest_year}-{latest_year})', window_size, colors)
            setup_bar_subplot(ax2, trends_results['mean_all'], title_even_charts, max_y_value, x_pos, colors)
            i += 1
            title_odd_charts = ''
            title_even_charts = ''

        # Last 20-years
        if total_years > 15:
            ax3 = fig.add_subplot(gs[i, axODD])
            ax4 = fig.add_subplot(gs[i, axEVEN])
            setup_subplot(ax3, trends_results['last_20_years_data'], trends_results['mean_last_20'], title_odd_charts, f'Período de 20 años\n({latest_year - 20}-{latest_year})', window_size, colors)
            setup_bar_subplot(ax4, trends_results['mean_last_20'], title_even_charts, max_y_value, x_pos, colors)
            i += 1
            title_odd_charts = ''
            title_even_charts = ''

        # Last 15-years
        if total_years > 10:
            ax5 = fig.add_subplot(gs[i, axODD])
            ax6 = fig.add_subplot(gs[i, axEVEN])
            setup_subplot(ax5, trends_results['last_15_years_data'], trends_results['mean_last_15'], title_odd_charts, f'Período de 15 años\n({latest_year - 15}-{latest_year})', window_size, colors)
            setup_bar_subplot(ax6, trends_results['mean_last_15'], title_even_charts, max_y_value, x_pos, colors)
            i += 1
            title_odd_charts = ''
            title_even_charts = ''
            
        # Last 10-years
        if total_years > 5:
            ax7 = fig.add_subplot(gs[i, axODD])
            ax8 = fig.add_subplot(gs[i, axEVEN])
            setup_subplot(ax7, trends_results['last_10_years_data'], trends_results['mean_last_10'], title_odd_charts, f'Período de 10 años\n({latest_year - 10}-{latest_year})', window_size, colors)
            setup_bar_subplot(ax8, trends_results['mean_last_10'], title_even_charts, max_y_value, x_pos, colors)
            i += 1
            title_odd_charts = ''
            title_even_charts = ''
                        
        # Last 5-years
        ax9 = fig.add_subplot(gs[i, axODD])
        ax10 = fig.add_subplot(gs[i, axEVEN])
        setup_subplot(ax9, trends_results['last_5_years_data'], trends_results['mean_last_5'], title_odd_charts, f'Período de 5 años\n({latest_year - 5}-{latest_year})', window_size, colors)
        setup_bar_subplot(ax10, trends_results['mean_last_5'], title_even_charts, max_y_value, x_pos, colors)
    else:
        current_year = latest_date.year
        i = 1
        # all data
        if len_years >= 20:
            ax1 = fig.add_subplot(gs[i, axODD])
            ax2 = fig.add_subplot(gs[i, axEVEN])
            setup_subplot(ax1, trends_results['all_data'], trends_results['mean_all'], title_odd_charts, f'Período de {len_years} años\n({current_year-earliest_date.year}-{latest_date.year})', window_size, colors)
            setup_bar_subplot(ax2, trends_results['mean_all'], title_even_charts, max_y_value, x_pos, colors)
            i += 1
            title_odd_charts = ''
            title_even_charts = ''
            # Last 20-years
            ax3 = fig.add_subplot(gs[i, axODD])
            ax4 = fig.add_subplot(gs[i, axEVEN])
            setup_subplot(ax3, trends_results['last_20_years_data'], trends_results['mean_last_20'], title_odd_charts, f'Período de 20 años\n({current_year - 20}-{current_year})', window_size, colors)
            setup_bar_subplot(ax4, trends_results['mean_last_20'], title_even_charts, max_y_value, x_pos, colors)
            i += 1
        else:
            ax3 = fig.add_subplot(gs[i, axODD])
            ax4 = fig.add_subplot(gs[i, axEVEN])
            setup_subplot(ax3, trends_results['last_20_years_data'], trends_results['mean_last_20'], title_odd_charts, f'Período de {len_years} años\n({current_year-earliest_date.year}-{latest_date.year})', window_size, colors)
            setup_bar_subplot(ax4, trends_results['mean_last_20'], title_even_charts, max_y_value, x_pos, colors)
            i += 1
            
        # Last 15-years
        ax5 = fig.add_subplot(gs[i, axODD])
        ax6 = fig.add_subplot(gs[i, axEVEN])
        setup_subplot(ax5, trends_results['last_15_years_data'], trends_results['mean_last_15'], '', f'Período de 15 años\n({current_year - 15}-{current_year})', window_size, colors)
        setup_bar_subplot(ax6, trends_results['mean_last_15'], '', max_y_value, x_pos, colors)
        i += 1

        # Last 10-years
        ax7 = fig.add_subplot(gs[i, axODD])
        ax8 = fig.add_subplot(gs[i, axEVEN])
        setup_subplot(ax7, trends_results['last_10_years_data'], trends_results['mean_last_10'], '', f'Período de 10 años\n({current_year - 10}-{current_year})', window_size, colors)
        setup_bar_subplot(ax8, trends_results['mean_last_10'], '', max_y_value, x_pos, colors)
        i += 1

        # Last 5-years
        ax9 = fig.add_subplot(gs[i, axODD])
        ax10 = fig.add_subplot(gs[i, axEVEN])
        setup_subplot(ax9, trends_results['last_5_years_data'], trends_results['mean_last_5'], '', f'Período de 5 años\n({current_year - 5}-{current_year})', window_size, colors)
        setup_bar_subplot(ax10, trends_results['mean_last_5'], '', max_y_value, x_pos, colors)


    # Add legend at the bottom, outside of the plots
    if total_years > 20:
        handles, labels = ax1.get_legend_handles_labels()
    elif total_years > 15:
        handles, labels = ax3.get_legend_handles_labels()
    elif total_years > 10:
        handles, labels = ax5.get_legend_handles_labels()
    elif total_years > 5:
        handles, labels = ax7.get_legend_handles_labels()
        
    labels = [f"{label} ({actual_menu})" for label in labels]
    fig.legend(handles, labels, loc='lower right', bbox_to_anchor=(0.55, 0.05),
                ncol=len(all_keywords), fontsize=12)

    # Adjust the layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.95, bottom=0.1, hspace=0.3, wspace=0.4)  # Reduced wspace from 0.5 to 0.4

    # Save the plot to the unique folder
    base_filename = f'{filename}_overtime.png'
    image_filename=get_unique_filename(base_filename, unique_folder)
    plt.savefig(os.path.join(unique_folder, image_filename), bbox_inches='tight')
    if menu == 1:
      add_image_to_report(f"Interés relativo en {', '.join(all_keywords)}", image_filename)
      charts += f"Interés relativo en {', '.join(all_keywords)} ({image_filename})\n\n"
    if menu == 2:
      add_image_to_report(f"Publicaciones Generales sobre {', '.join(all_keywords)}", image_filename)
      charts += f"Publicaciones Generales sobre {', '.join(all_keywords)} ({image_filename})\n\n"
    if menu == 3:
      add_image_to_report(f"Usabilidad de {', '.join(all_keywords)}", image_filename)
      charts += f"Usabilidad de {', '.join(all_keywords)} ({image_filename})\n\n"
    if menu == 4:
      add_image_to_report(f"Publicaciones Especializadas sobre {', '.join(all_keywords)}", image_filename)
      charts += f"Publicaciones Especializadas sobre {', '.join(all_keywords)} ({image_filename})\n\n"
    if menu == 5:
      add_image_to_report(f"Indice de Satisfacción de {', '.join(all_keywords)}", image_filename)
      charts += f"Indice de Satisfacción de {', '.join(all_keywords)} ({image_filename})\n\n"
    # Remove plt.show() to prevent graph windows from appearing
    plt.close()

    print(f"\nGráficos de comparación relativa creados.")

def setup_subplot(ax, data, mean, title, ylabel, window_size=10, colors=None, is_last_year=False):
    global menu
    global top_choice
    global all_keywords
    global original_values # Ensure original_values is accessible
    global original_calc_details # <-- Access the new global

    if colors is None:
        colors = plt.cm.rainbow(np.linspace(0, 1, len(all_keywords)))

    # Calculate global min and max across all series (use raw data before any potential extra smoothing)
    global_min = float('inf')
    global_max = float('-inf')
    plot_min_max = {} # Store min/max of plotted data for y-axis limits

    for i, kw in enumerate(all_keywords):
         if kw in data and not data[kw].empty:
             try:
                 # Min/max of the data actually being plotted (interpolated/resampled)
                 plot_min = data[kw].min()
                 plot_max = data[kw].max()
                 plot_min_max[kw] = (plot_min, plot_max)
                 global_min = min(global_min, plot_min)
                 global_max = max(global_max, plot_max)
             except Exception as e:
                 print(f"[Warning] Could not calculate plot min/max for {kw}: {e}")
         else:
             print(f"[Warning] Data for {kw} is missing or empty when calculating global min/max.")

    if not plot_min_max: # If no valid data was found at all
         print("[Warning] No valid data found to determine plot limits. Using default 0-100.")
         global_min, global_max = 0, 100

    buffer = (global_max - global_min) * 0.1 if global_max > global_min else 10 # Add buffer, handle flat data
    y_min_limit = max(0, global_min - buffer)
    y_max_limit = global_max + buffer * 1.5 # Extra buffer top for labels

    # Plot the data and original points
    for i, kw in enumerate(all_keywords):
        plot_label = kw # Default label
        min_orig, max_orig = None, None
        if kw in original_values and not original_values[kw].empty:
             try:
                  min_orig = original_values[kw].min()
                  max_orig = original_values[kw].max()
                  # Add original min/max to legend label
                  plot_label = f"{kw} (Orig Min: {min_orig:.1f}, Orig Max: {max_orig:.1f})"
             except Exception as e:
                  print(f"[Warning] Could not get original min/max for legend for {kw}: {e}")

        if kw in data and not data[kw].empty:
            # --- Apply smoothing CONDITIONALLY based on menu --- 
            series_data = data[kw]
            if menu in [1, 2, 4]: # Apply smoothing for GT, GB, CR
                # Ensure data is numpy array for smoothing function
                data_array = np.array(series_data)
                # Check if enough data points exist for the smoothing window
                if len(data_array) >= window_size: 
                     smoothed_array = smooth_data(data_array, window_size)
                     # Ensure smoothed data retains the original index for plotting
                     series_data_to_plot = pd.Series(smoothed_array, index=series_data.index)
                else:
                     print(f"[Warning] Not enough data points ({len(data_array)}) to apply smoothing with window {window_size} for {kw}. Plotting raw interpolated data.")
                     series_data_to_plot = series_data # Plot raw interpolated if not enough points
            else: # For menus 3 and 5 (Bain), plot the interpolated data directly
                series_data_to_plot = series_data
            # ----------------------------------------------------

            # Use the potentially smoothed data for plotting the line
            ax.plot(series_data_to_plot.index, series_data_to_plot, label=plot_label, color=colors[i])

            # Add original points and their labels
            if kw in original_values:
                orig_data = original_values[kw]
                mask = (orig_data.index >= data.index.min()) & (orig_data.index <= data.index.max())
                filtered_data = orig_data[mask]
                if not filtered_data.empty:
                    ax.scatter(filtered_data.index, filtered_data, color=colors[i], s=60, alpha=0.5, zorder=5)
                    label_offset = (y_max_limit - y_min_limit) * 0.015
                    for idx, val in filtered_data.items():
                         # --- Use Pre-calculated Z/SV values for Labels (Menu 5) ---
                         idx_ts = pd.Timestamp(idx).normalize() # Use normalized timestamp for lookup
                         label_text = f'{val:.1f}' # Default label

                         # Retrieve pre-calculated Z/SV values if available
                         if menu == 5 and kw in original_calc_details and idx_ts in original_calc_details.get(kw, {}):
                              calc_data = original_calc_details[kw][idx_ts]
                              z_score = calc_data.get('z_score', np.nan)
                              sv = calc_data.get('sv', np.nan)
                              # Check if values are valid (not NaN) before formatting
                              if not pd.isna(z_score) and not pd.isna(sv):
                                   label_text = f'{val:.1f} (Z:{z_score:.2f}, SV:{sv:.2f})'
                              else:
                                   # Optionally print warning if values were expected but are NaN
                                   print(f"[Warning] Z/SV data missing or NaN for {kw} at {idx_ts}, using default label.")
                         # ---------------------------------------------------------
                         ax.text(idx, val + label_offset, label_text, fontsize=7, ha='center', va='bottom', color=colors[i], zorder=6)

            # --- Yearly Calculations ---
            if top_choice != 2 and menu != 2:
                if menu == 4:
                    yearly_sums = []
                    years = data.index.year.unique()
                    for year in years[1:]:
                        end_date = f"{year}-01-01"
                        start_date = f"{year-1}-01-01"
                        sum_data = data[kw][(data.index >= start_date) & (data.index < end_date)]
                        yearly_sum = sum_data.sum() if not sum_data.empty else 0
                        if not pd.isna(yearly_sum):
                             yearly_sums.append((pd.Timestamp(f'{year}-01-01'), yearly_sum))

                    if yearly_sums:
                        ax2 = ax.twinx()
                        bar_positions, bar_heights = zip(*yearly_sums)
                        ax2.bar(bar_positions, bar_heights, width=300, alpha=0.05, color='red', align='edge') # Reduced alpha
                        ax2.set_ylabel('Suma anual', color='red', fontsize=10)
                        ax2.tick_params(axis='y', labelcolor='red', labelsize=8)
                        ax2.set_ylim(bottom=0)
                else:
                    yearly_means = []
                    years = data.index.year.unique()
                    for idx_yr, year in enumerate(years):
                        start_date = f"{year-1}-07-01"
                        end_date = f"{year}-07-01"
                        if idx_yr == 0:
                            start_date = data.index.min().strftime('%Y-%m-%d')
                        mean_data = data[kw][(data.index >= start_date) & (data.index < end_date)]
                        yearly_mean = mean_data.mean() if not mean_data.empty else np.nan
                        if not pd.isna(yearly_mean):
                             yearly_means.append((pd.Timestamp(f'{year}-01-01'), yearly_mean))

                    if yearly_means:
                         bar_positions, bar_heights = zip(*yearly_means)
                         ax.bar(bar_positions, bar_heights, width=300, alpha=0.05, color='red', align='edge') # Reduced alpha
        else:
             print(f"[Warning] Data for plotting keyword '{kw}' is missing or empty.")


    # Grid lines
    ax.grid(True, which='major', linestyle='--', linewidth=0.3, color='grey', alpha=0.1)

    # Set y-axis limits using calculated limits
    ax.set_ylim(bottom=y_min_limit, top=y_max_limit)

    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_title(title, fontsize=16)

    # --- X-Axis formatting remains the same ---
    def format_month(x, pos):
      dt = mdates.num2date(x)
      if dt.month == 1:
           return ''
      elif dt.month == 7:
          ax.axvline(x, color='lightgrey',linestyle ='--', linewidth=0.3)
          return '|'
      else:
          return ''

    def format_month2(x, pos):
        dt = mdates.num2date(x)
        if dt.month != 1:
             ax.axvline(x, color='lightgrey',linestyle ='dotted', linewidth=0.3)
             return str(dt.month)
        else:
            return ''

    if is_last_year:
        year_locator = mdates.YearLocator()
        ax.xaxis.set_major_locator(year_locator)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_minor_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_formatter(FuncFormatter(format_month2))
        start_dt = pd.Timestamp(f'{data.index.year.min()}-01-01')
        end_dt = pd.Timestamp(f'{data.index.year.max()}-12-31')
        ax.set_xlim(mdates.date2num(start_dt), mdates.date2num(end_dt))
    else:
        years = sorted(data.index.year.unique())
        year_locator = mdates.YearLocator(base=1)
        ax.xaxis.set_major_locator(year_locator)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[1, 7]))
        ax.xaxis.set_minor_formatter(FuncFormatter(format_month))
        start_dt = pd.Timestamp(f'{data.index.year.min()}-01-01')
        end_dt = pd.Timestamp(f'{data.index.year.max()}-12-31')
        ax.set_xlim(mdates.date2num(start_dt), mdates.date2num(end_dt))


    ax.tick_params(axis='both', which='major', labelsize=8)
    ax.tick_params(axis='x', which='major', labelrotation=45)
    ax.tick_params(axis='both', which='minor', labelsize=6)
    ax.tick_params(axis='x', which='minor', labelrotation=45)

    # Add legend (using the modified labels)
    ax.legend(loc='best', fontsize='small')

    return ax

def setup_bar_subplot(ax, mean, title, y_max, x_pos, colors):
    mean, ispartial = remove_ispartial(mean)  # Assuming this handles partial data

    # Grid lines for major ticks only
    ax.grid(True, which='major', linestyle='--', linewidth=0.5, color='grey', alpha=0.1)

    # Create bar plot with corresponding value labels
    bar_container = ax.bar(x_pos, mean[:len(all_keywords)], align='center', color=colors[:len(all_keywords)])  

    # Add value labels using `bar_label`
    ax.bar_label(bar_container, fmt=eng_format)

    ax.set_title(title, fontsize=16)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(replace_spaces_with_newlines(all_keywords), rotation=0, ha='center', fontsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)

    # Set y-axis limit to the global maximum value with a small buffer
    buffer = y_max * 0.1  # 10% buffer
    ax.set_ylim(0, y_max + buffer)

    # Adjust y-axis limits to avoid clipping labels
    plt.setp(ax.get_yticklabels(), rotation=45, ha='right')
    plt.tight_layout()

# Calculates the yearly average of a N-year period.
def calculate_yearly_average(data):
  """
  Args:
    data: A list of lists, where each inner list represents a year's data.
  Returns:
    The average of the yearly averages, rounded to 2 decimal places.
  """
  yearly_averages = []
  for year_data in data:
    yearly_average = np.mean(year_data)
    yearly_averages.append(yearly_average)

  if menu == 2:
      overall_average = np.mean(np.float64(yearly_averages))
  else:
      overall_average = round(np.mean(yearly_averages), 2)
  return overall_average

# --- Helper function definitions (inserted here) ---

def calculate_period_averages(series, periods_years=[1, 5, 10, 15, 20]):
    """Calculates mean averages for the last N years for a series."""
    results = {}
    # Return NaNs if series is empty or index isn't datetime
    if series.empty or not isinstance(series.index, pd.DatetimeIndex):
        for p in periods_years:
             results[f'{p} Year Avg'] = np.nan
        results['Overall Avg'] = np.nan # Add Overall Avg key even if empty
        return results

    end_date = series.index.max()
    # Ensure periods don't go beyond the data range
    # Handle case where index might not be sorted (though it should be)
    min_date = series.index.min()
    max_years_in_data = (end_date - min_date).days / 365.25

    for p in periods_years:
        if p > max_years_in_data + 1: # Add buffer for year boundary
            mean_val = np.nan # Not enough data for this period
        else:
            start_date = end_date - pd.DateOffset(years=p) + pd.Timedelta(days=1) # Inclusive start
            # Select data within the period
            period_data = series[series.index >= start_date]
            # Calculate mean, handles NaNs internally. Returns NaN for empty slice.
            mean_val = period_data.mean()
        results[f'{p} Year Avg'] = mean_val
    # Add overall average
    results['Overall Avg'] = series.mean()

    return results

def calculate_combined_trend_metrics(series, mast_years=3, nadt_years=5):
    """
    Calculates trend metrics (NADT, MAST) for a series, adapted from check_trends2 logic.

    Args:
        series (pd.Series): Input time series data with a DatetimeIndex.
        mast_years (int): Number of recent years to use for MAST calculation.
        nadt_years (int): Number of recent years to use for NADT calculation.

    Returns:
        dict: Dictionary with 'Trend NADT' and 'Trend MAST'.
    """
    trends = {'Trend NADT': np.nan, 'Trend MAST': np.nan}
    series_clean = series.dropna()
    series_name = str(series.name) # Ensure name is string

    if series_clean.shape[0] < 3 or not isinstance(series_clean.index, pd.DatetimeIndex):
        return trends # Not enough data or wrong index type

    end_date = series_clean.index.max()

    # --- Trend NADT (Normalized Annual Deviation) ---
    # Based on Std Dev / Mean over the last 'nadt_years' years
    try:
        start_date_nadt = end_date - pd.DateOffset(years=nadt_years) + pd.Timedelta(days=1)
        nadt_data = series_clean[series_clean.index >= start_date_nadt]

        if nadt_data.shape[0] > 1: # Need at least 2 points for std dev
            mean_nadt = nadt_data.mean()
            std_nadt = nadt_data.std()
            if not pd.isna(mean_nadt) and not pd.isna(std_nadt) and abs(mean_nadt) > 1e-9: # Avoid division by zero/small number
                trends['Trend NADT'] = std_nadt / abs(mean_nadt)
            elif abs(mean_nadt) <= 1e-9 and std_nadt == 0:
                trends['Trend NADT'] = 0.0 # No deviation, zero mean -> NADT is 0
            # else: remains np.nan if mean is near zero but std dev exists, or if calculation failed

    except Exception as e:
        print(f"  - Warning: Could not calculate NADT trend for '{series_name}': {e}")

    # --- Trend MAST (Moving Average Smoothed Trend) ---
    # Based on slope of linear regression on smoothed data over last 'mast_years' years
    try:
        start_date_mast = end_date - pd.DateOffset(years=mast_years) + pd.Timedelta(days=1)
        mast_data = series_clean[series_clean.index >= start_date_mast]

        # Apply smoothing (e.g., 3-point rolling average, adjust window as needed)
        smoothed = mast_data.rolling(window=3, center=True, min_periods=1).mean().dropna()

        if smoothed.shape[0] >= 2: # Need at least 2 points for regression
            # Use numerical representation of time for regression (e.g., days since start)
            x = (smoothed.index - smoothed.index.min()).days.values
            y = smoothed.values

            # Using scipy's linregress for simplicity (returns slope directly)
            slope, intercept, r_value, p_value, std_err = linregress(x, y)

            trends['Trend MAST'] = slope # Storing slope per day as calculated
        # else: remains np.nan if not enough points after smoothing

    except Exception as e:
        print(f"  - Warning: Could not calculate MAST trend for '{series_name}': {e}")

    return trends


def format_analysis_to_csv(analysis_results):
    """Helper function to format the list of dicts into a CSV string."""
    global top_choice # Need top_choice to determine header Key name
    if not analysis_results:
        return None
    try:
        output = io.StringIO()
        # Ensure consistent header order, including 'Keyword'/'Source' first
        # Determine if keys are keywords or sources based on top_choice
        key_header = 'Fuente de Datos' if top_choice == 2 else 'Keyword'
        base_headers = [key_header, 'Overall Avg']
        period_headers = [f'{p} Year Avg' for p in [20, 15, 10, 5, 1]] # Specific order
        trend_headers = ['Trend NADT', 'Trend MAST']
        headers = base_headers + period_headers + trend_headers

        # Create a temporary list to hold renamed dicts
        processed_results = []
        if analysis_results: # Check if list is not empty
             for item in analysis_results:
                  temp_item = item.copy()
                  if 'Keyword' in temp_item and key_header != 'Keyword':
                       temp_item[key_header] = temp_item.pop('Keyword')
                  processed_results.append(temp_item)
        else: # Handle empty analysis_results case
            # No rows to write, but write header
            pass # Header written below

        writer = csv.DictWriter(output, fieldnames=headers, quoting=csv.QUOTE_MINIMAL, extrasaction='ignore')
        writer.writeheader()
        if processed_results: # Only write rows if there are any
             writer.writerows(processed_results) # Use the processed list

        csv_data = output.getvalue()
        print("Combined analysis results formatted to CSV.")
        return csv_data
    except Exception as e:
        print(f"Error: Could not format combined analysis results to CSV: {e}")
        return f"Error creating combined analysis CSV: {e}" # Return error string

# --- End of inserted helper functions ---

def plot_and_analyze_combined_trends(combined_df, title="Comparative Trends Analysis", apply_smoothing=False, window_size=5, filename_prefix="combined_trends"):
    """
    Plots trends of all columns in a DataFrame, handling NaNs, and calculates
    period averages and trend metrics similar to check_trends2. Saves plot and
    returns plot filename and analysis CSV.

    Args:
        combined_df (pd.DataFrame): DataFrame with a datetime index and columns to plot.
        title (str): The title for the plot and analysis.
        apply_smoothing (bool): Whether to apply smoothing to the data before plotting.
        window_size (int): The window size for smoothing if apply_smoothing is True.
        filename_prefix (str): Prefix for the output plot filename.


    Returns:
        tuple: (str, str) - Short path to the saved plot image (for reporting), CSV string of analysis results.
               Returns (None, None) if fundamental errors occur.
               Returns (None, csv_output) if plotting fails but analysis succeeded.
    """
    # Access global unique_folder for saving plots
    # Make sure these globals are accessible where this function is called
    global unique_folder, charts, image_markdown, fixed_source_colors, default_color

    # --- Input Validation ---
    if not isinstance(combined_df, pd.DataFrame) or combined_df.empty:
         print("Error plot_analyze_combined: Input must be a non-empty pandas DataFrame.")
         return None, None

    if not isinstance(combined_df.index, pd.DatetimeIndex):
        try:
            combined_df.index = pd.to_datetime(combined_df.index)
            print("Info plot_analyze_combined: Converted DataFrame index to DatetimeIndex.")
        except Exception as e:
            print(f"Error plot_analyze_combined: DataFrame index is not DatetimeIndex and conversion failed: {e}")
            return None, None

    # --- Initialization ---
    fig, ax = plt.subplots(figsize=(14, 7))
    analysis_results = []
    # Use a perceptually uniform colormap
    # colors = plt.cm.viridis(np.linspace(0, 1, len(combined_df.columns)))
    any_data_plotted = False
    plot_filename_short = None # Initialize short plot filename


    print("Analyzing and plotting combined trends...")
    # --- Loop through Columns ---
    for i, column_name in enumerate(combined_df.columns):
        # Ensure column_name is a string for safety
        col_name_str = str(column_name)
        series = combined_df[column_name]
        series.name = col_name_str # Set name for warnings/calculations

        # --- Analysis (uses original series with NaNs) ---
        print(f"  Analyzing: {col_name_str}")
        # Calculate averages for standard periods + overall
        averages = calculate_period_averages(series, periods_years=[1, 5, 10, 15, 20])
        # Calculate specific trends
        trends = calculate_combined_trend_metrics(series)
        analysis_results.append({
            'Keyword': col_name_str, # Use string name ('Keyword' or 'Fuente de Datos' handled in format_analysis_to_csv)
            **averages,
            **trends
        })

        # --- Plotting (uses dropna() specifically for plot) ---
        series_for_plot = series.dropna()

        if series_for_plot.empty:
            print(f"  - Skipping plot for column with no valid data: {col_name_str}")
            continue # Skip plotting but keep analysis results

        print(f"  - Plotting: {col_name_str}")
        any_data_plotted = True
        plot_label = col_name_str
        data_to_plot = series_for_plot # Default to raw data

        if apply_smoothing:
            try:
                smoothed_series = series_for_plot.rolling(window=window_size, center=True, min_periods=1).mean()
                data_to_plot = smoothed_series
                plot_label = f"{col_name_str} (Smoothed {window_size})"
            except Exception as e:
                 print(f"  - Warning: Could not smooth data for {col_name_str}: {e}. Plotting raw data.")

        source_color = fixed_source_colors.get(col_name_str, default_color)

        ax.plot(data_to_plot.index, data_to_plot.values, label=plot_label, color=source_color, linewidth=1.5)


    # --- Finalize Plot ---
    if any_data_plotted:
        ax.set_title(title, fontsize=16)
        ax.set_xlabel("Date", fontsize=12)
        # Assuming the combined data is normalized if sources are mixed
        y_label = "Value / Trend"
        if top_choice == 2:
             y_label += " (Normalized)"
        ax.set_ylabel(y_label, fontsize=12)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.legend(loc='best', fontsize='small')
        try:
            fig.autofmt_xdate() # Auto-format date labels for better readability
            # Optional: Add specific date formatting if needed
            # ax.xaxis.set_major_locator(mdates.YearLocator(5)) # Example: Major tick every 5 years
            # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            # ax.xaxis.set_minor_locator(mdates.YearLocator(1)) # Example: Minor tick every year
        except Exception as e:
            print(f"Warning: Could not auto-format date axis: {e}")

        plt.tight_layout()

        # --- Save Plot ---
        try:
            # Create a somewhat readable but unique part for the filename
            cols_part = "_".join([str(c).replace(' ','_').replace('/','-') for c in combined_df.columns])[:50] # Limit length
            base_filename = f"{filename_prefix}_{cols_part}.png"

            # Ensure get_unique_filename exists and uses unique_folder
            plot_filename_short = get_unique_filename(base_filename, unique_folder) # Get short filename
            full_plot_path = os.path.join(unique_folder, plot_filename_short) # Construct full path for saving
            plt.savefig(full_plot_path)
            print(f"Combined trend plot saved to: {full_plot_path}")

            # Add image to report structure using the short filename
            add_image_to_report(title, plot_filename_short) # Use the short filename for report markdown
            # Update charts list (assuming 'charts' is a global string or list)
            if isinstance(charts, str):
                 charts += f'{title} ({plot_filename_short})\n\n'
            elif isinstance(charts, list):
                 charts.append({'title': title, 'filename': plot_filename_short})
            # Update image_markdown (assuming global string)
            image_markdown += f"![{title}]({quote(plot_filename_short)})\n\n" # Use URL encoding for filename

        except NameError as ne:
             print(f"Error: Global variable like 'unique_folder', 'charts', or 'image_markdown' not found. Cannot save plot or update report variables. {ne}")
             plot_filename_short = None # Ensure filename is None if save fails
        except Exception as e:
            print(f"Error: Could not save plot or update report variables: {e}")
            plot_filename_short = None # Ensure filename is None if save fails
        finally:
            plt.close(fig) # Always close the figure
    else:
         print("Error: No data available to plot after handling NaNs.")
         plt.close(fig) # Close the empty figure
         plot_filename_short = None # No plot generated

    # --- Format Analysis Results ---
    csv_output = format_analysis_to_csv(analysis_results)

    # Return short filename (for report list) or None, and the CSV data
    return plot_filename_short, csv_output, analysis_results

# --- End of plot_and_analyze_combined_trends ---

# Replace the previous plot_combined_averages_bars function with this one

def plot_combined_averages_bars(analysis_results_list, title="Análisis Comparativo de Medias por Periodo"):
    """
    Creates a grouped bar chart comparing period averages across different sources/keywords,
    with group widths proportional to the period length and overlapping trend lines.
    All text elements are in Spanish.

    Args:
        analysis_results_list (list): List of dictionaries with averages and trends.
        title (str): The title for the plot (should ideally be passed in Spanish).

    Returns:
        str: The short filename of the saved plot image, or None if plotting fails.
    """
    global unique_folder, charts, image_markdown, top_choice, total_years # Need globals

    if not analysis_results_list:
        print("Error plot_combined_bars: No analysis results provided.")
        return None

    try:
        # --- Data Preparation ---
        df = pd.DataFrame(analysis_results_list)
        key_column = 'Fuente de Datos' if top_choice == 2 else 'Keyword' # Keep original key names for data lookup

        if key_column not in df.columns:
             print(f"Error plot_combined_bars: Key column '{key_column}' not found.")
             if top_choice == 2 and 'Keyword' in df.columns:
                  key_column = 'Keyword'
                  print(f"Warning: Falling back to use 'Keyword' column.")
             else: return None
        df = df.set_index(key_column)

        # --- Define Periods and Relative Widths ---
        overall_period_years = total_years if 'total_years' in globals() and total_years > 0 else 20

        # English names used internally for mapping and data lookup
        period_map_en = {
            'Overall Avg': overall_period_years,
            '20 Year Avg': 20, '15 Year Avg': 15, '10 Year Avg': 10, '5 Year Avg': 5, '1 Year Avg': 1
        }
        # Spanish names for display on the chart
        period_map_es = {
            'Overall Avg': 'Media Total',
            '20 Year Avg': 'Media 20 Años', '15 Year Avg': 'Media 15 Años', '10 Year Avg': 'Media 10 Años',
            '5 Year Avg': 'Media 5 Años', '1 Year Avg': 'Media 1 Año'
        }

        # Order columns based on period_map_en keys for plotting logic
        ordered_avg_columns = [col for col in period_map_en.keys() if col in df.columns]
        if not ordered_avg_columns:
             print("Error plot_combined_bars: No average columns matching period_map found.")
             return None

        df_avg = df[ordered_avg_columns]
        df_plot = df_avg.transpose().loc[ordered_avg_columns] # Ensure transpose keeps order

        num_sources = len(df_plot.columns)
        num_periods = len(df_plot.index)
        if num_sources == 0 or num_periods == 0: return None

        # --- Calculate Bar Positions and Widths Manually ---
        max_period_width_years = max(period_map_en.values())
        # Total available width on x-axis for all groups (adjust if needed)
        total_groups_x_width = 0.95 # Use slightly more width maybe
        # Define how much influence the proportional width has (0=uniform, 1=fully proportional)
        proportionality_factor = 0.7 # e.g., 70% proportional, 30% uniform tendency

        x_centers_per_source = {source: [] for source in df_plot.columns}
        group_center_ticks = []
        current_x_position = 0

        fig, ax = plt.subplots(figsize=(max(16, num_periods * num_sources * 0.4), 7))
        # colors = plt.cm.viridis(np.linspace(0, 1, num_sources))

        # Calculate the width if all groups were uniform
        uniform_group_width = total_groups_x_width / num_periods if num_periods > 0 else 0

        for period_name_en in df_plot.index:
            years = period_map_en.get(period_name_en, 1)

            # Calculate the purely proportional width component
            proportional_group_width = total_groups_x_width * (years / max_period_width_years)

            # Blend proportional and uniform widths
            blended_group_width = (proportionality_factor * proportional_group_width +
                                   (1 - proportionality_factor) * uniform_group_width)

            # Calculate width for each bar within this blended group width
            bar_width = blended_group_width / num_sources if num_sources > 0 else 0

            # --- Sanity check: ensure bar_width is reasonable ---
            # Avoid excessively small or large widths that might cause rendering issues
            min_sensible_bar_width = 0.005 # Adjust as needed
            max_sensible_bar_width = 0.2   # Adjust as needed
            bar_width = max(min_sensible_bar_width, min(bar_width, max_sensible_bar_width))
            # Recalculate blended_group_width based on clamped bar_width if needed for gaps
            blended_group_width = bar_width * num_sources

            # Calculate the center of the current group
            group_center = current_x_position + blended_group_width / 2
            group_center_ticks.append(group_center)

            # Calculate starting x position for the first bar in this group
            start_bar_pos = current_x_position # Bars start at the beginning of the group space now

            for i, source_name in enumerate(df_plot.columns):
                 # Center of the bar is start + half_width + index*width
                bar_center = start_bar_pos + (i + 0.5) * bar_width
                x_centers_per_source[source_name].append(bar_center)

                value = pd.to_numeric(df_plot.loc[period_name_en, source_name], errors='coerce')
                value = 0 if pd.isna(value) else value

                # Plot bar centered at bar_center
                source_color = fixed_source_colors.get(source_name, default_color)
                ax.bar(bar_center, value, width=bar_width * 0.95, label=source_name if period_name_en == df_plot.index[0] else "", color=source_color, align='center') # Use slight gap within bars

            # Update the starting position for the next group, adding a gap
            # Gap can be relative to the base width or a fixed small value
            group_gap = total_groups_x_width * 0.20 # Small gap between groups
            current_x_position += blended_group_width + group_gap

        # --- Plot Trend Lines ---
        line_colors = plt.cm.cool(np.linspace(0, 1, num_sources))
        for i, source_name in enumerate(df_plot.columns):
            x_coords = x_centers_per_source[source_name]
            y_coords = pd.to_numeric(df_plot[source_name], errors='coerce')
            valid_indices = ~y_coords.isna()
            if valid_indices.any():
                 source_color = fixed_source_colors.get(source_name, default_color)
                 ax.plot(np.array(x_coords)[valid_indices], y_coords[valid_indices],
                         color=source_color, linestyle='--', marker='o', markersize=4,
                         linewidth=1.5, alpha=0.7)

        # --- Formatting (Spanish) ---
        y_label_es = 'Valor Promedio'
        if top_choice == 2:
             y_label_es += ' (Normalizado)'
        ax.set_ylabel(y_label_es, fontsize=12)
        ax.set_title(title, fontsize=16, pad=20)
        ax.set_xticks(group_center_ticks)
        x_tick_labels_es = [period_map_es.get(en_name, en_name) for en_name in df_plot.index]
        ax.set_xticklabels(x_tick_labels_es, rotation=45, ha='right')
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        legend_title_es = "Fuentes" if top_choice == 2 else "Palabras Clave"
        ax.legend(by_label.values(), by_label.keys(), title=legend_title_es, loc='best', fontsize='small')
        ax.grid(True, which='major', axis='y', linestyle='--', linewidth=0.5, alpha=0.7)
        ax.axhline(0, color='grey', linewidth=0.8)
        # Adjust x-axis limits slightly to give padding
        # Use total_groups_x_width which is defined earlier
        ax.set_xlim(group_center_ticks[0] - total_groups_x_width*0.6, current_x_position)
        fig.tight_layout()


        # --- Save Plot ---
        plot_filename_short = None
        try:
            cols_part = "_".join([str(c).replace(' ','_').replace('/','-') for c in df_plot.columns])[:50]
            base_filename = f"combined_avg_bars_blendwidth_es_{cols_part}.png" # Add _es to filename
            plot_filename_short = get_unique_filename(base_filename, unique_folder)
            full_plot_path = os.path.join(unique_folder, plot_filename_short)
            plt.savefig(full_plot_path)
            print(f"Combined averages variable width bar chart (ES) saved to: {full_plot_path}")

            report_title = title + " (Barras Ancho Variable)" # Add note for report list
            add_image_to_report(report_title, plot_filename_short)
            if isinstance(charts, str): charts += f'{report_title} ({plot_filename_short})\n\n'
            elif isinstance(charts, list): charts.append({'title': report_title, 'filename': plot_filename_short})
            image_markdown += f"![{report_title}]({quote(plot_filename_short)})\n\n"

        except NameError as ne:
             print(f"Error plot_combined_bars_varwidth: Globals missing. {ne}")
             plot_filename_short = None
        except Exception as e:
            print(f"Error plot_combined_bars_varwidth: Could not save plot/update report. {e}")
            plot_filename_short = None
        finally:
            plt.close(fig)

        return plot_filename_short

    except Exception as e:
        print(f"Error generating combined averages variable width bar chart (ES): {e}")
        traceback.print_exc()
        if 'fig' in locals() and plt.fignum_exists(fig.number): plt.close(fig)
        return None

# --- End of plot_combined_averages_bars (Variable Width Version - Spanish) ---

# Check Trends
def check_trends2(kw):
    global charts
    global image_markdown
    global current_year
    global actual_menu
    global menu
    global trends_results
    global earliest_year
    global latest_year
    global total_years
    global trend_analysis_text  # NEW: Global variable for text output
    
    # NEW: Initialize a list to capture all output
    trend_output = []
    
    # NEW: Define a custom print function that captures output
    def capture_print(*args, **kwargs):
        # Convert all arguments to strings and join with spaces
        output = ' '.join(str(arg) for arg in args)
        # Add to our capture list
        trend_output.append(output)
        # Also print to console as normal
        print(*args, **kwargs)
    
    data = trends_results['last_20_years_data']
    mean = trends_results['mean_last_20']
    if top_choice == 2:
        actual_menu = selected_keyword
        if kw == 'Google Trends':
            menu = 1
        elif kw == 'Google Books Ngrams':
            menu = 2
        elif kw == 'Bain - Usabilidad':
            menu = 3
        elif kw == 'Crossref.org':
            menu = 4
        else:
            menu = 5

    if top_choice == 1:
        banner_msg(title=' Herramienta: ' + kw.upper() + ' (' + actual_menu + ') ', margin=1,color1=YELLOW, color2=WHITE)
        trend_output.append(f"Herramienta: {kw.upper()} ({actual_menu})")
    else:
        banner_msg(title=' Fuente de Datos: ' + kw.upper() + ' (' + actual_menu + ') ', margin=1,color1=YELLOW, color2=WHITE)
        trend_output.append(f"Fuente de Datos: {kw.upper()} ({actual_menu})")

    # Set years2 based on menu
    if menu == 3 or menu == 5:
        years2 = -42
    elif menu == 4:
        years2 = 2 
    else:
        years2 = 0
        
    # Create the figure and axes BEFORE any bar creation
    fig, ax = plt.subplots(figsize=(10,6))
    
    # Calculate averages
    if top_choice == 1:
        if menu == 2:
            avg_all = calculate_yearly_average(trends_results['all_data'][kw])
            avg_20 = calculate_yearly_average(trends_results['all_data'][-20:][kw])
            avg_15 = calculate_yearly_average(trends_results['all_data'][-15:][kw])
            avg_10 = calculate_yearly_average(trends_results['all_data'][-10:][kw])
            avg_5 = calculate_yearly_average(trends_results['all_data'][-5:][kw])
            avg_1 = calculate_yearly_average(trends_results['all_data'][-1:][kw])
        else:
            avg_all = None  # We won't use this for other menu options
            avg_20 = calculate_yearly_average(trends_results['last_20_years_data'][kw])
            avg_15 = calculate_yearly_average(trends_results['last_15_years_data'][kw])
            avg_10 = calculate_yearly_average(trends_results['last_10_years_data'][kw])
            avg_5 = calculate_yearly_average(trends_results['last_5_years_data'][kw])
            avg_1 = calculate_yearly_average(trends_results['last_year_data'][kw])
    else:
        if 2 in selected_sources:
            avg_all = calculate_yearly_average(trends_results['all_data'][kw])
            avg_20 = calculate_yearly_average(trends_results['all_data'][-20:][kw])
            avg_15 = calculate_yearly_average(trends_results['all_data'][-15:][kw])
            avg_10 = calculate_yearly_average(trends_results['all_data'][-10:][kw])
            avg_5 = calculate_yearly_average(trends_results['all_data'][-5:][kw])
            avg_1 = calculate_yearly_average(trends_results['all_data'][-1:][kw])
        else:
            avg_all = None  # We won't use this for other menu options
            avg_20 = calculate_yearly_average(trends_results['last_20_years_data'][kw])
            avg_15 = calculate_yearly_average(trends_results['last_15_years_data'][kw])
            avg_10 = calculate_yearly_average(trends_results['last_10_years_data'][kw])
            avg_5 = calculate_yearly_average(trends_results['last_5_years_data'][kw])
            avg_1 = calculate_yearly_average(trends_results['last_year_data'][kw])
        
    means = {}
    means[kw] = [avg_all, avg_20, avg_15, avg_10, avg_5, avg_1]

    # Base width
    base_width = 0.35

    # Adjust years base on earliest and latest dates...
    if top_choice == 2:
        years_range = int((latest_date - earliest_date).days / 365.25) 
        years2 = 0
        current_year = latest_date.year
        if years_range < 20:
            years2 = years_range
        else:
            years2 = 20
        
    # Calculate relative widths
    if top_choice == 1:
        if total_years > 20:
            # Create arrays for all time periods
            bar_widths = []
            bar_positions = []
            years_list = []
            avgs = []
            colors = ['lightgrey', 'lightsteelblue', 'steelblue', 'dodgerblue', 'darkblue', 'midnightblue']
            position_offset = 0
            
            # Add all_data bar if available
            if avg_all is not None:
                avg_all_width = base_width * total_years / 20 * 2
                bar_widths.append(avg_all_width)
                bar_positions.append(position_offset)
                years_list.append(total_years)
                avgs.append(avg_all)
                position_offset += avg_all_width/1.55
            
            # Add 20-year bar if available
            if avg_20 is not None and total_years >= 20:
                avg_20_width = base_width * 20 / 20 * 2
                bar_widths.append(avg_20_width)
                bar_positions.append(position_offset)
                years_list.append(20)
                avgs.append(avg_20)
                position_offset += avg_20_width
            
            # Add 15-year bar if available
            if avg_15 is not None and total_years >= 15:
                avg_15_width = base_width * 15 / 20 * 2
                bar_widths.append(avg_15_width)
                bar_positions.append(position_offset)
                years_list.append(15)
                avgs.append(avg_15)
                position_offset += avg_15_width
            
            # Add 10-year bar if available
            if avg_10 is not None and total_years >= 10:
                avg_10_width = base_width * 10 / 20 * 2
                bar_widths.append(avg_10_width)
                bar_positions.append(position_offset)
                years_list.append(10)
                avgs.append(avg_10)
                position_offset += avg_10_width
            
            # Add 5-year bar if available
            if avg_5 is not None and total_years >= 5:
                avg_5_width = base_width * 5 / 20 * 2
                bar_widths.append(avg_5_width)
                bar_positions.append(position_offset)
                years_list.append(5)
                avgs.append(avg_5)
                position_offset += avg_5_width
            
            # Always add 1-year bar
            if avg_1 is not None:
                avg_1_width = base_width * 1 / 20 * 2.5
                bar_widths.append(avg_1_width)
                bar_positions.append(position_offset)
                years_list.append(1)
                avgs.append(avg_1)
            
            # Trim colors to match the number of bars
            colors = colors[:len(bar_widths)]
            
            # Create the bars with consistent arrays
            rects = []
            for pos, width, avg, year, color in zip(bar_positions, bar_widths, avgs, years_list, colors):
                if avg is not None:
                    if year == total_years:
                        label = f'Media {total_years} Años ({earliest_year} - {latest_year}): {eng_notation(avg)}'
                    else:
                        label = f'Media {year} Años: {eng_notation(avg)}'
                    rects.append(ax.bar(pos, avg, width, label=label, color=color))
        elif total_years > 15:
            # Create arrays for time periods
            bar_widths = []
            bar_positions = []
            years_list = []
            avgs = []
            colors = ['lightsteelblue', 'steelblue', 'dodgerblue', 'darkblue', 'midnightblue']
            position_offset = 0
            
            # Add 20-year or total_years bar
            avg_20_width = base_width * total_years / 20 * 2
            bar_widths.append(avg_20_width)
            bar_positions.append(position_offset)
            years_list.append(total_years)
            avgs.append(avg_20)
            position_offset += avg_20_width
            
            # Add 15-year bar if available
            if avg_15 is not None:
                avg_15_width = base_width * 15 / 20 * 2
                bar_widths.append(avg_15_width)
                bar_positions.append(position_offset)
                years_list.append(15)
                avgs.append(avg_15)
                position_offset += avg_15_width
            
            # Add 10-year bar if available
            if avg_10 is not None:
                avg_10_width = base_width * 10 / 20 * 2
                bar_widths.append(avg_10_width)
                bar_positions.append(position_offset)
                years_list.append(10)
                avgs.append(avg_10)
                position_offset += avg_10_width
            
            # Add 5-year bar if available
            if avg_5 is not None:
                avg_5_width = base_width * 5 / 20 * 2
                bar_widths.append(avg_5_width)
                bar_positions.append(position_offset)
                years_list.append(5)
                avgs.append(avg_5)
                position_offset += avg_5_width
            
            # Always add 1-year bar
            if avg_1 is not None:
                avg_1_width = base_width * 1 / 20 * 2.5
                bar_widths.append(avg_1_width)
                bar_positions.append(position_offset)
                years_list.append(1)
                avgs.append(avg_1)
            
            # Trim colors to match the number of bars
            colors = colors[:len(bar_widths)]
            
            # Create the bars with consistent arrays
            rects = []
            for pos, width, avg, year, color in zip(bar_positions, bar_widths, avgs, years_list, colors):
                if avg is not None:
                    label = f'Media {year} Años ({earliest_year} - {latest_year}): {eng_notation(avg)}'
                    rects.append(ax.bar(pos, avg, width, label=label, color=color))
        elif total_years > 10:
            # Create arrays for time periods
            bar_widths = []
            bar_positions = []
            years_list = []
            avgs = []
            colors = ['steelblue', 'dodgerblue', 'darkblue', 'midnightblue']
            position_offset = 0
            
            # Add 15-year or total_years bar
            avg_15_width = base_width * total_years / 20 * 2
            bar_widths.append(avg_15_width)
            bar_positions.append(position_offset)
            years_list.append(total_years)
            avgs.append(avg_15)
            position_offset += avg_15_width
            
            # Add 10-year bar if available
            if avg_10 is not None:
                avg_10_width = base_width * 10 / 20 * 2
                bar_widths.append(avg_10_width)
                bar_positions.append(position_offset)
                years_list.append(10)
                avgs.append(avg_10)
                position_offset += avg_10_width
            
            # Add 5-year bar if available
            if avg_5 is not None:
                avg_5_width = base_width * 5 / 20 * 2
                bar_widths.append(avg_5_width)
                bar_positions.append(position_offset)
                years_list.append(5)
                avgs.append(avg_5)
                position_offset += avg_5_width
            
            # Always add 1-year bar
            if avg_1 is not None:
                avg_1_width = base_width * 1 / 20 * 2.5
                bar_widths.append(avg_1_width)
                bar_positions.append(position_offset)
                years_list.append(1)
                avgs.append(avg_1)
            
            # Trim colors to match the number of bars
            colors = colors[:len(bar_widths)]
            
            # Create the bars with consistent arrays
            rects = []
            for pos, width, avg, year, color in zip(bar_positions, bar_widths, avgs, years_list, colors):
                if avg is not None:
                    label = f'Media {year} Años ({earliest_year} - {latest_year}): {eng_notation(avg)}'
                    rects.append(ax.bar(pos, avg, width, label=label, color=color))
        elif total_years > 5:
            # Create arrays for time periods
            bar_widths = []
            bar_positions = []
            years_list = []
            avgs = []
            colors = ['dodgerblue', 'darkblue', 'midnightblue']
            position_offset = 0
            
            # Add 10-year or total_years bar
            avg_10_width = base_width * total_years / 20 * 2
            bar_widths.append(avg_10_width)
            bar_positions.append(position_offset)
            years_list.append(total_years)
            avgs.append(avg_10)
            position_offset += avg_10_width
            
            # Add 5-year bar if available
            if avg_5 is not None:
                avg_5_width = base_width * 5 / 20 * 2
                bar_widths.append(avg_5_width)
                bar_positions.append(position_offset)
                years_list.append(5)
                avgs.append(avg_5)
                position_offset += avg_5_width
            
            # Always add 1-year bar
            if avg_1 is not None:
                avg_1_width = base_width * 1 / 20 * 2.5
                bar_widths.append(avg_1_width)
                bar_positions.append(position_offset)
                years_list.append(1)
                avgs.append(avg_1)
            
            # Trim colors to match the number of bars
            colors = colors[:len(bar_widths)]
            
            # Create the bars with consistent arrays
            rects = []
            for pos, width, avg, year, color in zip(bar_positions, bar_widths, avgs, years_list, colors):
                if avg is not None:
                    label = f'Media {year} Años ({earliest_year} - {latest_year}): {eng_notation(avg)}'
                    rects.append(ax.bar(pos, avg, width, label=label, color=color))
        else:
            # For very short time series (5 years or less)
            bar_widths = []
            bar_positions = []
            years_list = []
            avgs = []
            colors = ['darkblue', 'midnightblue']
            position_offset = 0
            
            # Add 5-year or total_years bar
            if avg_5 is not None:
                avg_5_width = base_width * total_years / 20 * 2
                bar_widths.append(avg_5_width)
                bar_positions.append(position_offset)
                years_list.append(total_years)
                avgs.append(avg_5)
                position_offset += avg_5_width
            
            # Always add 1-year bar
            if avg_1 is not None:
                avg_1_width = base_width * 1 / 20 * 2.5
                bar_widths.append(avg_1_width)
                bar_positions.append(position_offset)
                years_list.append(1)
                avgs.append(avg_1)
            
            # Trim colors to match the number of bars
            colors = colors[:len(bar_widths)]
            
            # Create the bars with consistent arrays
            rects = []
            for pos, width, avg, year, color in zip(bar_positions, bar_widths, avgs, years_list, colors):
                if avg is not None:
                    label = f'Media {year} Años ({earliest_year} - {latest_year}): {eng_notation(avg)}'
                    rects.append(ax.bar(pos, avg, width, label=label, color=color))
    else:
        # For source analysis (top_choice == 2)
        if years_range > 20:
            # Create arrays for all time periods
            bar_widths = []
            bar_positions = []
            years_list = []
            avgs = []
            colors = ['lightgrey', 'lightsteelblue', 'steelblue', 'dodgerblue', 'darkblue', 'midnightblue']
            position_offset = 0
            
            # Add all_data bar if available
            if avg_all is not None:
                avg_all_width = base_width * years_range / 20 * 2
                bar_widths.append(avg_all_width)
                bar_positions.append(position_offset)
                years_list.append(years_range)
                avgs.append(avg_all)
                position_offset += avg_all_width/1.55
            
            # Add 20-year bar if available
            if avg_20 is not None:
                avg_20_width = base_width * 20 / 20 * 2
                bar_widths.append(avg_20_width)
                bar_positions.append(position_offset)
                years_list.append(20)
                avgs.append(avg_20)
                position_offset += avg_20_width
            
            # Add 15-year bar if available
            if avg_15 is not None:
                avg_15_width = base_width * 15 / 20 * 2
                bar_widths.append(avg_15_width)
                bar_positions.append(position_offset)
                years_list.append(15)
                avgs.append(avg_15)
                position_offset += avg_15_width
            
            # Add 10-year bar if available
            if avg_10 is not None:
                avg_10_width = base_width * 10 / 20 * 2
                bar_widths.append(avg_10_width)
                bar_positions.append(position_offset)
                years_list.append(10)
                avgs.append(avg_10)
                position_offset += avg_10_width
            
            # Add 5-year bar if available
            if avg_5 is not None:
                avg_5_width = base_width * 5 / 20 * 2
                bar_widths.append(avg_5_width)
                bar_positions.append(position_offset)
                years_list.append(5)
                avgs.append(avg_5)
                position_offset += avg_5_width
            
            # Always add 1-year bar
            if avg_1 is not None:
                avg_1_width = base_width * 1 / 20 * 2.5
                bar_widths.append(avg_1_width)
                bar_positions.append(position_offset)
                years_list.append(1)
                avgs.append(avg_1)
            
            # Trim colors to match the number of bars
            colors = colors[:len(bar_widths)]
            
            # Create the bars with consistent arrays
            rects = []
            for pos, width, avg, year, color in zip(bar_positions, bar_widths, avgs, years_list, colors):
                if avg is not None:
                    label = f'Media {year} Años ({current_year-year} - {current_year}): {eng_notation(avg)}'
                    rects.append(ax.bar(pos, avg, width, label=label, color=color))
        else:
            # For shorter time series
            bar_widths = []
            bar_positions = []
            years_list = []
            avgs = []
            colors = ['lightsteelblue', 'steelblue', 'dodgerblue', 'darkblue', 'midnightblue']
            position_offset = 0
            
            # Add years2 bar (which might be less than 20)
            if avg_20 is not None:
                avg_20_width = base_width * years2 / 20 * 2
                bar_widths.append(avg_20_width)
                bar_positions.append(position_offset)
                years_list.append(years2)
                avgs.append(avg_20)
                position_offset += avg_20_width
            
            # Add 15-year bar if available and applicable
            if avg_15 is not None and years2 >= 15:
                avg_15_width = base_width * 15 / 20 * 2
                bar_widths.append(avg_15_width)
                bar_positions.append(position_offset)
                years_list.append(15)
                avgs.append(avg_15)
                position_offset += avg_15_width
            
            # Add 10-year bar if available and applicable
            if avg_10 is not None and years2 >= 10:
                avg_10_width = base_width * 10 / 20 * 2
                bar_widths.append(avg_10_width)
                bar_positions.append(position_offset)
                years_list.append(10)
                avgs.append(avg_10)
                position_offset += avg_10_width
            
            # Add 5-year bar if available and applicable
            if avg_5 is not None and years2 >= 5:
                avg_5_width = base_width * 5 / 20 * 2
                bar_widths.append(avg_5_width)
                bar_positions.append(position_offset)
                years_list.append(5)
                avgs.append(avg_5)
                position_offset += avg_5_width
            
            # Always add 1-year bar
            if avg_1 is not None:
                avg_1_width = base_width * 1 / 20 * 2.5
                bar_widths.append(avg_1_width)
                bar_positions.append(position_offset)
                years_list.append(1)
                avgs.append(avg_1)
            
            # Trim colors to match the number of bars
            colors = colors[:len(bar_widths)]
            
            # Create the bars with consistent arrays
            rects = []
            for pos, width, avg, year, color in zip(bar_positions, bar_widths, avgs, years_list, colors):
                if avg is not None:
                    label = f'Media {year} Años ({current_year-year} - {current_year}): {eng_notation(avg)}'
                    rects.append(ax.bar(pos, avg, width, label=label, color=color))
        
    # Create the bar graph - MOVED HERE before any bar creation

        # ... existing code ...

    # Set the x-axis labels and title
    # SIMPLE SOLUTION: Create labels directly from positions
    years_list = [str(year) for year in years_list]  # Convert all to strings for consistency
    
    # Ensure positions and labels match exactly
    if len(bar_positions) != len(years_list):
        # Just use position indices as labels if there's a mismatch
        years_list = [str(i+1) for i in range(len(bar_positions))]
    
    ax.set_xticks(bar_positions)
    ax.set_xticklabels(years_list)
    ax.set_ylabel('Media')
    if top_choice == 1:
        ax.set_title(f'Media a lo largo del tiempo de:\n{kw} según {actual_menu}')
    else:
        ax.set_title(f'Media a lo largo del tiempo de:{actual_menu}\n{kw}')

    # Add labels over each bar
    def add_labels(rects):
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width() / 2, height, eng_notation(height),
                    ha='center', va='bottom', fontsize=8, color='black')

    for rect in rects:
        add_labels(rect)

    # Move the legend outside the plot
    legend = ax.legend(loc='upper center', fontsize=9, bbox_to_anchor=(0.5, -0.15), ncol=2)

    # Save the plot to the unique folder
    base_filename = f'{filename}_means_{kw[:3]}.png'
    image_filename = get_unique_filename(base_filename, unique_folder)
    plt.savefig(os.path.join(unique_folder, image_filename), bbox_inches='tight')
    add_image_to_report(f'Medias de {kw}', image_filename)
    charts += f'Medias de {kw} ({image_filename})\n\n'

    # Show the plot
    if menu == 2:
        plt.yscale('log')
    # Remove plt.show() to prevent graph windows from appearing
    plt.close()

    # Calculate trends
    trend_20 = round(((avg_1 - trends_results['mean_last_20'][kw]) / trends_results['mean_last_20'][kw]) * 100, 2)
    capture_print('')
    capture_print(f'Tendencia Normalizada de Desviación Anual (20 años): {trend_20}')

    # Calculate the moving average for the last 5 years (adjust as needed)
    last_20_years_data = trends_results['last_20_years_data'][kw]
    moving_avg = last_20_years_data.rolling(window=12).mean()  # 12-month moving average

    # Compare the last value of the moving average to the 20-year average
    trend2_20 = round(((moving_avg.iloc[-1] - avg_20) / avg_20) * 100, 2)
    capture_print(f'Tendencia Suavizada por Media Móvil (20 años): {trend2_20}')
    capture_print('')

    # ENHANCED CODE: Determine the appropriate reference period based on available data
    # First check if we have data longer than 20 years
    if 'all_data' in trends_results and kw in trends_results['all_data'] and avg_all is not None:
        # Calculate how many years of data we have in all_data
        all_data_years = len(trends_results['all_data'][kw])
        
        # Use all available data if it's more than 20 years
        if all_data_years > 20:
            reference_period = all_data_years
            reference_data = trends_results['all_data'][kw]
            reference_avg = avg_all
            capture_print(f"Usando serie histórica completa: {reference_period} años")
        else:
            # Default to 20 years if available
            reference_period = 20
            reference_data = trends_results['last_20_years_data'][kw]
            reference_avg = avg_20
    # If all_data isn't available or doesn't have more than 20 years, use the best available shorter period
    elif total_years >= 20:
        reference_period = 20
        reference_data = trends_results['last_20_years_data'][kw]
        reference_avg = avg_20
    elif total_years >= 15:
        reference_period = 15
        reference_data = trends_results['last_15_years_data'][kw]
        reference_avg = avg_15
    elif total_years >= 10:
        reference_period = 10
        reference_data = trends_results['last_10_years_data'][kw]
        reference_avg = avg_10
    elif total_years >= 5:
        reference_period = 5
        reference_data = trends_results['last_5_years_data'][kw]
        reference_avg = avg_5
    else:
        reference_period = total_years
        reference_data = last_20_years_data  # Use whatever data we have
        reference_avg = avg_1  # In this case, trend analysis won't be very meaningful
    
    # Recalculate trend based on the appropriate reference period
    trend_adjusted = round(((avg_1 - reference_avg) / reference_avg) * 100, 2) if reference_avg > 0 else 0
    
    capture_print(f'Tendencia Normalizada de Desviación Anual ({reference_period} años): {trend_adjusted}')

    # Calculate the moving average with an appropriate window size
    if reference_period > 50:
        window_size = 24  # 2-year moving average for very long series
    elif reference_period > 30:
        window_size = 18  # 1.5-year moving average for long series
    elif reference_period > 20:
        window_size = 12  # 1-year moving average for medium series
    else:
        window_size = max(3, min(12, len(reference_data)//4))  # Adaptive window for shorter series
        
    moving_avg = reference_data.rolling(window=window_size).mean()
    
    # Compare the last value of the moving average to the reference average
    trend2_adjusted = round(((moving_avg.iloc[-1] - reference_avg) / reference_avg) * 100, 2) if reference_avg > 0 else 0
    capture_print(f'Tendencia Suavizada por Media Móvil ({reference_period} años, ventana={window_size} meses): {trend2_adjusted}')
    capture_print('')

    trends = {}
    trends[kw] = [trend_20, trend2_adjusted]

    # Define the variable based on the menu selection
    if menu == 2 or menu == 4 :
        interest_var = "las publicaciones"
    elif menu == 3:
        interest_var = "la utilización"
    elif menu == 5:
        interest_var = "la satisfacción"
    else:
        interest_var = "el interés"

    # For very long time series, mention the start year
    if reference_period > 20:
        start_year = current_year - reference_period
        capture_print(f'{interest_var.capitalize()} promedio histórico ({start_year}-{current_year}, {reference_period} años) para "{kw.upper()}" fue {eng_notation(reference_avg)}.')
    else:
        capture_print(f'{interest_var.capitalize()} promedio de los últimos {reference_period} años para "{kw.upper()}" fue {eng_notation(reference_avg)}.')
        
    capture_print(f'{interest_var.capitalize()} del último año para "{kw.upper()}" comparado con el promedio histórico resulta con una tendencia de {trend_adjusted}%.')

    trend = trend_adjusted
    yearsago = reference_period
    mean_value = mean[kw]

    # Adjusted logic based on 1-100 index range
    if mean_value > 75:
        if abs(trend) <= 5:
            capture_print(f'{interest_var.capitalize()} por "{kw.upper()}" es muy alto y estable durante los últimos {yearsago} años.')
        elif trend > 5:
            capture_print(f'{interest_var.capitalize()} por "{kw.upper()}" es muy alto y está aumentando durante los últimos {yearsago} años.')
        else:
            capture_print(f'{interest_var.capitalize()} por "{kw.upper()}" es muy alto pero está disminuyendo durante los últimos {yearsago} años.')
    elif mean_value > 50:
        if abs(trend) <= 10:
            capture_print(f'{interest_var.capitalize()} por "{kw.upper()}" es alto y relativamente estable durante los últimos {yearsago} años.')
        elif trend > 10:
            capture_print(f'{interest_var.capitalize()} por "{kw.upper()}" es alto y está aumentando significativamente durante los últimos {yearsago} años.')
        else:
            capture_print(f'{interest_var.capitalize()} por "{kw.upper()}" es alto pero está disminuyendo significativamente durante los últimos {yearsago} años.')
    elif mean_value > 25:
        if abs(trend) <= 15:
            capture_print(f'{interest_var.capitalize()} por "{kw.upper()}" es moderado y muestra algunas fluctuaciones durante los últimos {yearsago} años.')
        elif trend > 15:
            capture_print(f'{interest_var.capitalize()} por "{kw.upper()}" es moderado pero está en tendencia creciente durante los últimos {yearsago} años.')
        else:
            capture_print(f'{interest_var.capitalize()} por "{kw.upper()}" es moderado pero muestra una tendencia decreciente durante los últimos {yearsago} años.')
    else:
        if trend > 50:
            capture_print(f'{interest_var.capitalize()} por "{kw.upper()}" es bajo pero está creciendo rápidamente durante los últimos {yearsago} años.')
        elif trend > 0:
            capture_print(f'{interest_var.capitalize()} por "{kw.upper()}" es bajo pero muestra un ligero crecimiento durante los últimos {yearsago} años.')
        elif trend < -50:
            capture_print(f'{interest_var.capitalize()} por "{kw.upper()}" es bajo y está disminuyendo rápidamente durante los últimos {yearsago} años.')
        else:
            capture_print(f'{interest_var.capitalize()} por "{kw.upper()}" es bajo y muestra una ligera disminución durante los últimos {yearsago} años.')

    # Comparison last year vs. reference period
    if reference_avg == 0:
        capture_print(f'No había {interest_var} medible por "{kw.upper()}" hace {yearsago} años.')
    elif trend2_adjusted > 50:
        capture_print(f'{interest_var.capitalize()} del último año es mucho más alto en comparación con hace {yearsago} años. Ha aumentado en un {trend2_adjusted}%.')
    elif trend2_adjusted > 15:
        capture_print(f'{interest_var.capitalize()} del último año es considerablemente más alto en comparación con hace {yearsago} años. Ha aumentado en un {trend2_adjusted}%.')
    elif trend2_adjusted < -50:
        capture_print(f'{interest_var.capitalize()} del último año es mucho más bajo en comparación con hace {yearsago} años. Ha disminuido en un {abs(trend2_adjusted)}%.')
    elif trend2_adjusted < -15:
        capture_print(f'{interest_var.capitalize()} del último año es considerablemente más bajo en comparación con hace {yearsago} años. Ha disminuido en un {abs(trend2_adjusted)}%.')
    else:
        capture_print(f'{interest_var.capitalize()} del último año es comparable al de hace {yearsago} años. Ha cambiado en un {trend2_adjusted}%.')
    capture_print('')

    # NEW: Store the captured output in the global variable
    trend_analysis_text[kw] = '\n'.join(trend_output)
    
    try:
        # Initialize statistics dictionary for all ranges
        statistics = {}
        
        # Define the ranges to analyze
        ranges = {
            'last_20': trends_results['last_20_years_data'][kw],
            'last_15': trends_results['last_15_years_data'][kw],
            'last_10': trends_results['last_10_years_data'][kw],
            'last_5': trends_results['last_5_years_data'][kw]
        }
        
        # Add all_data only if total_years > 20
        if total_years > 20 and 'all_data' in trends_results and kw in trends_results['all_data']:
            ranges['all_data'] = trends_results['all_data'][kw]
        
        # Calculate statistics for each range
        for range_name, data in ranges.items():
            if data is not None:
                data_array = np.array(data, dtype=float)
                
                # Calculate standard deviation
                std_dev = float(np.std(data_array))
                
                # Find peaks using scipy.signal.find_peaks
                from scipy.signal import find_peaks
                peaks, _ = find_peaks(data_array, distance=20, prominence=0.5)
                
                # Get top 3 peaks by value
                peak_values = data_array[peaks]
                peak_indices = peaks[np.argsort(peak_values)[-3:]]
                
                # Store peak information
                peak_info = []
                for idx in peak_indices:
                    peak_info.append({
                        'value': float(data_array[idx]),
                        'index': int(idx)
                    })
                
                # Calculate range and percentiles
                data_range = float(np.max(data_array) - np.min(data_array))
                percentiles = {
                    'p25': float(np.percentile(data_array, 25)),
                    'p50': float(np.percentile(data_array, 50)),
                    'p75': float(np.percentile(data_array, 75))
                }
                
                statistics[range_name] = {
                    'standard_deviation': std_dev,
                    'peaks': peak_info,
                    'range': data_range,
                    'min_value': float(np.min(data_array)),
                    'max_value': float(np.max(data_array)),
                    'percentiles': percentiles
                }
        
        # Create AI-readable structured text
        ai_structured_text = "\n[STATISTICAL_ANALYSIS]\n"
        
        # Display the analysis header
        capture_print("\nStatistical Analysis:")
        capture_print("=" * 50)
        
        for range_name, stats in statistics.items():
            # Format range name for display
            display_name = range_name.replace('_', ' ').title()
            
            # Display section header
            capture_print(f"\n{display_name} Analysis:")
            capture_print("-" * 30)
            
            # Display standard deviation
            capture_print(f"Standard Deviation: {stats['standard_deviation']:.4f}")
            
            # Display peaks
            capture_print("\nPeaks Information:")
            for i, peak in enumerate(stats['peaks'], 1):
                capture_print(f"Peak {i}: value={peak['value']:.4f}, index={peak['index']}")
            
            # Display range analysis
            capture_print("\nRange Analysis:")
            capture_print(f"Total Range: {stats['range']:.4f}")
            capture_print(f"Min Value: {stats['min_value']:.4f}")
            capture_print(f"Max Value: {stats['max_value']:.4f}")
            
            # Display percentiles
            capture_print("\nPercentile Distribution:")
            capture_print(f"P25: {stats['percentiles']['p25']:.4f}")
            capture_print(f"P50: {stats['percentiles']['p50']:.4f}")
            capture_print(f"P75: {stats['percentiles']['p75']:.4f}")
            
            capture_print("\n" + "=" * 50)
            
            # Add to AI-readable text
            ai_structured_text += f"\n{range_name.upper()} Analysis:\n"
            ai_structured_text += f"Standard_Deviation: {stats['standard_deviation']:.4f}\n\n"
            ai_structured_text += "Peaks_Information:\n"
            ai_structured_text += chr(10).join(f"Peak_{i+1}: value={p['value']:.4f}, index={p['index']}" 
                                             for i, p in enumerate(stats['peaks']))
            ai_structured_text += "\n\n"
            ai_structured_text += "Range_Analysis:\n"
            ai_structured_text += f"- Total_Range: {stats['range']:.4f}\n"
            ai_structured_text += f"- Min_Value: {stats['min_value']:.4f}\n"
            ai_structured_text += f"- Max_Value: {stats['max_value']:.4f}\n\n"
            ai_structured_text += "Percentile_Distribution:\n"
            ai_structured_text += f"- P25: {stats['percentiles']['p25']:.4f}\n"
            ai_structured_text += f"- P50: {stats['percentiles']['p50']:.4f}\n"
            ai_structured_text += f"- P75: {stats['percentiles']['p75']:.4f}\n"
            ai_structured_text += "-" * 50 + "\n"
        
        ai_structured_text += "[END_STATISTICAL_ANALYSIS]"
        
        # Append the structured text to existing analysis_text
        trend_analysis_text[kw] += "\n" + ai_structured_text
        
    except Exception as e:
        error_msg = f"\nError in statistical analysis: {str(e)}"
        capture_print(error_msg)
        trend_analysis_text[kw] += error_msg
    
    return {
        'means': means[kw],
        'trends': trends[kw],
        'analysis_text': trend_analysis_text[kw],
        'statistics': statistics
    }

def create_unique_filename(keywords, top_choice, max_length=20):
    global actual_opt
    # Concatenate keywords
    shorter = [keyword[:3] for keyword in keywords if len(keyword) >= 3]
    joined = "_".join(shorter)
    # Remove non-alphanumeric characters and convert to lowercase
    cleaned = joined #re.sub(r'[^a-zA-Z0-9]', '', joined).lower()
    # Truncate to max_length
    truncated = cleaned[:max_length]
    # Create a unique identifier using timestamp and hash
    timestamp = int(time.time())
    hash_object = hashlib.md5(str(timestamp).encode())
    unique_id = hash_object.hexdigest()[:8]  # Use first 8 characters of the hash
    # Combine truncated name with unique identifier
    if top_choice == 2:
        actual_opt = 'AA'
    filename = f"{actual_opt}_{truncated}_{unique_id}"
    #print(filename)
    return filename

#Calculates the trend for a given period.
def calculate_trend(trend_data, period):
  """
  Args:
    trend_data: A dictionary containing trend data.
    period: The period for which to calculate the trend (e.g., 'last_20', 'last_year').
  Returns:
    A pandas DataFrame containing the mean keyword value and trend.
  """
  mean_kw = trend_data[f'mean_{period}']
  if 'isPartial' in mean_kw:
    del mean_kw['isPartial']
  mean_last_year = trend_data['mean_last_year']
  if 'isPartial' in mean_last_year:
    del mean_last_year['isPartial']
  trend_values = (mean_last_year / mean_kw) - 1
  # Create a list of keyword names
  keywords = list(mean_kw.index)
  # Create a DataFrame with keyword names as a separate column
  rdf = pd.DataFrame({'keyword': keywords, 'mean_kw': mean_kw, 'trend': trend_values})
  return rdf

def plot_source_correlation_heatmap(combined_df, keyword, base_filename_prefix="source_correlation_heatmap"):
    """
    Generates and saves a correlation heatmap between data sources for a single keyword.

    Args:
        combined_df (pd.DataFrame): DataFrame with sources as columns and time index,
                                     containing data for the specified keyword.
        keyword (str): The keyword being analyzed.
        base_filename_prefix (str): Prefix for the output image file name.
    """
    global charts, image_markdown, unique_folder, filename # Ensure globals are accessible

    if combined_df is None or not isinstance(combined_df, pd.DataFrame) or combined_df.empty:
        print("  [Warning] Combined dataset is empty or invalid. Skipping source heatmap.")
        return

    if len(combined_df.columns) < 2:
        print("  [Info] Need at least two sources for a source correlation heatmap. Skipping.")
        return

    print(f"  Generating Source Correlation Heatmap for Keyword: '{keyword}'...")

    try:
        # 1. Calculate the correlation matrix between sources (columns)
        # Ensure only numeric columns are used and handle potential NaNs before correlation
        numeric_df = combined_df.select_dtypes(include=np.number)
        # Drop rows where *any* source has NaN for fair comparison, or use pairwise?
        # Using pairwise='complete.obs' handles NaNs more gracefully for correlation matrix
        source_corr_matrix = numeric_df.corr(method='pearson', min_periods=10) # require 10 periods

        if source_corr_matrix.empty or source_corr_matrix.isnull().all().all():
             print(f"    {YELLOW}[Warning] Could not calculate valid source correlation matrix for '{keyword}'. Skipping heatmap.{RESET}")
             return

        # 2. Generate the heatmap
        plt.figure(figsize=(8, 8))
        sns.heatmap(source_corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5,
                    annot_kws={"size": 8}) # Using viridis colormap

        num_sources = len(source_corr_matrix.columns)
        tick_fontsize = 8 if num_sources < 7 else 6
        plt.xticks(fontsize=tick_fontsize, rotation=45, ha='right')
        plt.yticks(fontsize=tick_fontsize, rotation=0)

        plt.title(f'Mapa de Calor de Correlación entre Fuentes\nKeyword: "{keyword}"', pad=20, fontsize=12)
        plt.tight_layout()

        # 3. Save the plot
        # Sanitize keyword for filename
        sanitized_keyword = re.sub(r'[^\w\-]+', '_', keyword)
        base_filename = f'{filename}_{sanitized_keyword}_{base_filename_prefix}.png'
        image_filename = get_unique_filename(base_filename, unique_folder)
        full_path = os.path.join(unique_folder, image_filename)

        plt.savefig(full_path, bbox_inches='tight', dpi=150)
        print(f"    Source heatmap saved to: {image_filename}")

        # 4. Add to report structures
        report_title = f'Mapa de Calor de Correlación entre Fuentes ({keyword})'
        add_image_to_report(report_title, image_filename)
        if isinstance(charts, str):
            charts += f'{report_title} ({image_filename})\n\n'
        elif isinstance(charts, list):
            charts.append({'title': report_title, 'filename': image_filename})

    except Exception as e:
        print(f"    {RED}[Error] Failed to generate or save source heatmap for '{keyword}': {e}{RESET}")
        import traceback
        traceback.print_exc()
    finally:
        if 'plt' in locals() and plt.get_fignums():
             plt.close()


# Performs various analysis on keyword trend data.
def analyze_trends(trend):
    """
    Args:
        trend: A dictionary containing keyword trend data.
    Returns:
        A dictionary containing analysis results.
    """
    global charts
    global image_markdown
    global one_keyword
    # Extract relevant data
    mean_last_20 = trend['mean_last_20']
    if 'isPartial' in mean_last_20:
      del mean_last_20['isPartial']
    mean_last_year = trend['mean_last_year']
    if 'isPartial' in mean_last_year:
      del mean_last_year['isPartial']

    #print(trend['mean_last_year'])

    # Calculate trend
    trend_values = (mean_last_year / mean_last_20) - 1

    # Create a DataFrame for analysis
    rdf = pd.DataFrame({'mean_kw': mean_last_20, 'trend': trend_values})

    # Calculates the mean for each keyword column in the DataFrame.
    def calculate_mean_for_keywords(df1):
      """
      Args:
        df: The input DataFrame.
      Returns:
        A new DataFrame with the calculated means.
      """
      mean_df = df1.mean(axis=0).to_frame(name='mean')
      mean_df.index.name = 'keyword'
      if top_choice == 2:
        mean_df.index.name = 'Fuente de Datos'
      return mean_df

    result_df = calculate_mean_for_keywords(trend['last_20_years_data'])

    # Converts a dictionary of Series to a DataFrame.
    def dictionary_to_dataframe(data_dict):
      """
      Args:
        data_dict: A dictionary where keys are column names and values are Series.
      Returns:
        A DataFrame.
      """
      df1 = pd.DataFrame(data_dict)
      return df1

    #Calculates pairwise correlations between all columns in a DataFrame.
    def calculate_pairwise_correlations(df1):
      """
      Args:
        df: The input DataFrame.
      Returns:
        A DataFrame of correlation coefficients.
      """
      corr_matrix = df1.corr()
      return corr_matrix

    # Removes the 'isPartial' column from a dictionary of Series.
    def rem_isPartial(data):
      """
      Args:
        data: A dictionary where keys are column names and values are Series.
      Returns:
        A new dictionary without the 'isPartial' column.
      """
      new_data = data.copy()
      if 'isPartial' in new_data:
        new_data.pop('isPartial')
      return new_data

    if not one_keyword:
        # Correlation Analysis
        trend_data = rem_isPartial(trend['last_20_years_data'])
        df = dictionary_to_dataframe(trend_data)
        correlation_matrix = calculate_pairwise_correlations(df)
        char='*'
        title=' Correlación '
        qty=len(title)
        print(f'\x1b[33m\n\n{char*qty}\n{title}\n{char*qty}\x1b[0m\n')
        print(correlation_matrix)
        print(type(correlation_matrix))
        csv_correlation=correlation_matrix.to_csv(index=True, header=True)

        #Correlation Heat Map
        plt.figure(figsize=(7, 7))
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm')
        plt.xticks(fontsize=8)
        plt.yticks(fontsize=8)
        plt.title(f'Correlación para {actual_menu}', pad=20)    
        char='*'
        title=' Correlación - Mapa de Calor '
        qty=len(title)
        print(f'\x1b[33m\n\n{char*qty}\n{title}\n{char*qty}\x1b[0m')
        # Save the plot to the unique folder
        image_filename = f'{filename}_heatmap.png'
        plt.savefig(os.path.join(unique_folder, image_filename), bbox_inches='tight')
        add_image_to_report('Mapa de Calor de Correlación', image_filename)
        charts += f'Mapa de Calor ({image_filename})\n\n'
        # Remove plt.show() to prevent graph windows from appearing
        plt.close()

        # Regression analysis
        # Extract the last 20 years data
        char='*'
        title=' Análisis de Regresión '
        qty=len(title)
        print(f'\x1b[33m\n\n{char*qty}\n{title}\n{char*qty}\x1b[0m')
        print('\nNota: La primera variable es la variable dependiente\n      y el resto son las variables independientes para cada combinación\n      ej: (dependiente, independiente1, independiente2...)\n')
        csv_output = ''
        data = pd.DataFrame(trend['last_20_years_data'])
        if 'isPartial' in data.columns:
          data = data.drop('isPartial', axis=1)
        # print(type(data))
        # print(data)
        data.index = pd.to_datetime(data.index)
        # Get all possible combinations of keywords
        keywords = data.columns
        # Only generate pairs of combinations
        all_combinations = list(combinations(keywords, 2))
        csv_output = "Pair, Value\n"
        # Perform regression for each combination
        for combo in all_combinations:
            X = data[list(combo)[1:]].values
            y = data[list(combo)[0]].values
            model = LinearRegression()
            model.fit(X, y)
            coefficients = model.coef_
            intercept = model.intercept_
            # Calculate R-squared
            r_squared = r2_score(y, model.predict(X))  # Use r2_score to calculate R-squared value
            print(f"\nRegresión para: {combo}")
            print("Coeficientes:", coefficients)
            print("Intersección:", intercept)
            print("R-cuadrado:", r_squared)  # Print the calculated R-squared value
            # Include titles for each regression result within the CSV
            csv_output += f'\nRegression for: "{combo}"\n'
            csv_output += "Coefficients:, "
            csv_output += ", ".join([str(c) for c in coefficients]) + "\n"  # Join coefficients with commas
            csv_output += "Intercept:, " + str(intercept) + "\n"
            csv_output += "R-squared:, " + str(r_squared) + "\n\n"  # Add double newline for separation
        csv_regression = csv_output

        # Creates scatter plots for all possible combinations of up to 5 keywords.
        def create_scatter_plots(df, max_keywords=5):
            """
            Args:
                df: The DataFrame containing the keyword data.
                max_keywords: The maximum number of keywords to consider.
            """
            global charts
            global image_markdown
            
            columns = df.columns
            # Only generate pairs of combinations
            combinations = itertools.combinations(columns, 2)
            
            for combo in combinations:
                # Create scatter plot for each pair
                fig, ax = plt.subplots(figsize=(7, 7))
                ax.scatter(df[combo[0]], df[combo[1]])
                ax.set_xlabel(combo[0])
                ax.set_ylabel(combo[1])
                
                plt.tight_layout()
                plt.title(f'Gráfico de Dispersión para {actual_menu}', pad=20)
                base_filename = f'{filename}_scatter_{combo[0][:3]}{combo[1][:3]}.png'
                image_filename=get_unique_filename(base_filename, unique_folder)
                plt.savefig(os.path.join(unique_folder, image_filename), bbox_inches='tight')
                add_image_to_report(f'Gráfico de Dispersión para {", ".join(combo)}', image_filename)
                charts += f'Gráfico de Dispersión para {", ".join(combo)} ({image_filename})\n\n'
                # Remove plt.show() to prevent graph windows from appearing
                plt.close()

        data = rem_isPartial(trends_results['last_20_years_data'])
        char='*'
        title=' Diagrama de Dispersión '
        qty=len(title)
        print(f'\x1b[33m\n\n{char*qty}\n{title}\n{char*qty}\x1b[0m')
        create_scatter_plots(data)
    else:
        csv_correlation = None
        csv_regression = None
        print('Se requieren al menos dos variables para realizar los cálculos de correlación y regresión')
    return {
      'correlation': csv_correlation,
      'regression': csv_regression,
    }

# Helper function to format polynomial equations
def format_polynomial_equation(coeffs):
    """Formats polynomial coefficients into a readable equation string."""
    terms = []
    degree = len(coeffs) - 1
    for i, coeff in enumerate(coeffs):
        power = degree - i
        # Skip coefficients that are very close to zero
        if abs(coeff) < 1e-6:
            continue

        # Format coefficient with sign and precision
        if i == 0:
            # First term doesn't need a leading '+' sign unless it's the only term
            term = f"{coeff:.3f}"
        else:
            # Subsequent terms get a sign explicitly
            term = f" {coeff:+.3f}" # Shows '+' for positive, '-' for negative

        # Add variable 'x' and power if power > 0
        if power > 0:
            term += "x"
            if power > 1:
                term += f"^{power}"
        terms.append(term)

    # Handle the case where all coefficients are zero or near-zero
    if not terms:
        return "y = 0"

    # Combine terms, ensure leading sign is handled if first term was negative
    equation = "y = " + "".join(terms).strip()

    # Optional: Nicer formatting like removing '1.000x' to 'x' can be added
    # Be careful with replacing '1.000' as it might match parts of other numbers
    equation = re.sub(r'(\s|\b)1\.000x', r'\1x', equation) # Replace ' 1.000x' or '1.000x' at start
    equation = re.sub(r'\+ -', '- ', equation) # Clean up '+ -' combinations

    return equation

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer # Or KNNImputer, IterativeImputer
from sklearn.decomposition import PCA
import plotly.graph_objects as go
import numpy as np
import os
import re# Main analysis function
# Main analysis function
def analyze_source_correlations_regressions(combined_datasets, selected_sources, keywords, source_colors=None):
    """
    Performs correlation and regression analysis between pairs of data sources for given keywords.

    Generates scatter plots with regression lines (linear, quadratic, cubic, polynomial deg 4)
    and calculates correlation (R) and regression metrics (R-squared, equation coefficients).
    Saves plots to the specified directory and returns results as DataFrames.

    Args:
        combined_datasets (dict): Dictionary where keys are keywords and values are pandas DataFrames.
                                  Each DataFrame must have aligned time index and columns for selected sources.
                                  Data in these columns should ideally be normalized.
        selected_sources (list): List of source names to analyze (e.g., ['google_books', 'google_trends']).
        keywords (list): List of keywords to analyze.
        source_colors (dict, optional): Dictionary mapping source names to colors. Uses defaults if None.

    Returns:
        tuple: A tuple containing:
            - list: Filenames of the generated plots.
            - pd.DataFrame: DataFrame with correlation results (Keyword, Source_A, Source_B, Correlation_R).
                                Name: csv_correlation
            - pd.DataFrame: DataFrame with regression results (Keyword, Source_A, Source_B, Regression_Type,
                                Degree, R_Squared, Coefficients, Equation). Name: csv_regression
    """
    print(f"\n--- Iniciando Análisis de Correlación y Regresión ---") # Translated
    print(f"Fuentes a analizar: {selected_sources}") # Translated
    print(f"Palabras Clave: {keywords}") # Translated

    all_plot_filenames = []
    correlation_results = []
    regression_results = []

    # Use provided source_colors or setup defaults
    if source_colors is None:
        print("Advertencia: Diccionario source_colors no proporcionado. Usando colores por defecto de matplotlib.") # Translated warning
        prop_cycle = plt.rcParams['axes.prop_cycle']
        default_colors = prop_cycle.by_key()['color']
        source_colors = {source: default_colors[i % len(default_colors)] for i, source in enumerate(selected_sources)}
    elif not isinstance(source_colors, dict):
        print("Advertencia: source_colors proporcionado no es un diccionario. Usando colores por defecto.") # Translated warning
        prop_cycle = plt.rcParams['axes.prop_cycle']
        default_colors = prop_cycle.by_key()['color']
        source_colors = {source: default_colors[i % len(default_colors)] for i, source in enumerate(selected_sources)}


    # 2. Ensure the global unique_folder exists
    global unique_folder
    if 'unique_folder' not in globals() or not unique_folder:
        print(f"Error: Variable global 'unique_folder' no definida. Los gráficos no se pueden guardar.") # Translated error
        can_save_plots = False
    else:
        try:
            os.makedirs(unique_folder, exist_ok=True)
            abs_output_dir = os.path.abspath(unique_folder)
            print(f"Directorio de salida para gráficos: {abs_output_dir}") # Translated
            can_save_plots = True
        except OSError as e:
            print(f"Error al crear directorio de salida '{unique_folder}': {e}. Los gráficos no se guardarán.") # Translated error
            can_save_plots = False

    # 3. Generate all permutations of sources for A vs B plots
    source_pairs = list(itertools.permutations(selected_sources, 2))
    print(f"Se generaron {len(source_pairs)} pares de fuentes para el análisis.") # Translated

    # 4. Loop through each keyword
    for keyword in keywords:
        print(f"\nProcesando palabra clave: '{keyword}'") # Translated
        if keyword not in combined_datasets:
            print(f"  Advertencia: Palabra clave '{keyword}' no encontrada en el diccionario combined_datasets. Omitiendo.") # Translated
            continue

        # Ensure the value associated with the keyword is a DataFrame
        if not isinstance(combined_datasets[keyword], pd.DataFrame):
             print(f"  Advertencia: Los datos para la palabra clave '{keyword}' no son un DataFrame de pandas. Omitiendo.") # Translated
             continue

        df_keyword = combined_datasets[keyword]

        # 5. Loop through each source pair (source_a -> x, source_b -> y)
        for source_a, source_b in source_pairs:
            x_source_name = source_a
            y_source_name = source_b
            print(f"  Analizando par: Y={y_source_name} vs X={x_source_name}") # Translated

            # Check if both sources exist as columns
            if x_source_name not in df_keyword.columns:
                print(f"    Advertencia: Fuente '{x_source_name}' (Eje X) no encontrada en los datos para la palabra clave '{keyword}'. Omitiendo par.") # Translated
                continue
            if y_source_name not in df_keyword.columns:
                print(f"    Advertencia: Fuente '{y_source_name}' (Eje Y) no encontrada en los datos para la palabra clave '{keyword}'. Omitiendo par.") # Translated
                continue

            # 6. Prepare data
            df_pair = df_keyword[[x_source_name, y_source_name]].copy().dropna()

            min_points_for_analysis = 5
            if len(df_pair) < min_points_for_analysis:
                print(f"    Advertencia: No hay suficientes puntos de datos superpuestos ({len(df_pair)} < {min_points_for_analysis}) para '{keyword}' entre {x_source_name} y {y_source_name}. Omitiendo par.") # Translated
                continue

            x_data = df_pair[x_source_name].values
            y_data = df_pair[y_source_name].values

            if np.std(x_data) < 1e-6 or np.std(y_data) < 1e-6:
                 print(f"    Advertencia: Los datos para '{x_source_name}' o '{y_source_name}' son constantes o casi constantes. Omitiendo regresión/correlación para este par.") # Translated
                 continue

            # 7. Calculate Pearson Correlation
            try:
                correlation_coefficient = df_pair[x_source_name].corr(df_pair[y_source_name])
                if pd.isna(correlation_coefficient):
                     print(f"    Advertencia: El cálculo de la correlación resultó en NaN para '{keyword}' ({y_source_name} vs {x_source_name}). Omitiendo par.") # Translated
                     continue

                correlation_results.append({
                    'Keyword': keyword,
                    'Source_A': x_source_name,
                    'Source_B': y_source_name,
                    'Correlation_R': correlation_coefficient
                })
                print(f"    Correlación R: {correlation_coefficient:.4f}") # Translated
            except Exception as e:
                print(f"    Error al calcular la correlación para '{keyword}' ({y_source_name} vs {x_source_name}): {e}. Omitiendo correlación.") # Translated
                correlation_coefficient = np.nan

            # 8. Set up Plot
            fig, ax = plt.subplots(figsize=(12, 8))
            scatter_color = source_colors.get(y_source_name, '#808080')
            ax.scatter(x_data, y_data, alpha=0.6, label=f'Puntos de Datos ({len(x_data)})', color=scatter_color, s=25) # Translated label

            x_plot = np.linspace(np.min(x_data), np.max(x_data), 200)

            # 9. Perform Regressions
            regression_degrees = {'Linear': 1, 'Quadratic': 2, 'Cubic': 3, 'Polynomial(4)': 4}
            num_reg_lines = len(regression_degrees)
            reg_colors = [CONTRASTING_PALETTE[i % len(CONTRASTING_PALETTE)] for i in range(num_reg_lines)]

            print("    Calculando regresiones:") # Translated
            regression_success = False
            for i, (name, degree) in enumerate(regression_degrees.items()):
                if len(x_data) <= degree:
                     print(f"      Omitiendo regresión {name} (grado {degree}): requiere > {degree} puntos, encontrados {len(x_data)}.") # Translated
                     continue

                try:
                    with warnings.catch_warnings(record=True) as w:
                        warnings.simplefilter("always")
                        coeffs = np.polyfit(x_data, y_data, degree)
                        if any(issubclass(warn.category, np.RankWarning) for warn in w):
                             print(f"      RankWarning encontrado durante la regresión {name} (grado {degree}). Los resultados pueden no ser fiables debido a una matriz mal condicionada.") # Translated

                    poly_eqn = np.poly1d(coeffs)
                    y_pred = poly_eqn(x_data)
                    y_plot = poly_eqn(x_plot)
                    r_squared = r2_score(y_data, y_pred)
                    equation_str = format_polynomial_equation(coeffs)
                    print(f"      {name} (R²={r_squared:.4f}): {equation_str}") # No translation needed for formula

                    regression_results.append({
                        'Keyword': keyword,
                        'Source_A': x_source_name,
                        'Source_B': y_source_name,
                        'Regression_Type': name,
                        'Degree': degree,
                        'R_Squared': r_squared,
                        'Coefficients': list(coeffs),
                        'Equation': equation_str
                    })

                    pearson_r_text = f"R={correlation_coefficient:.3f}, " if not pd.isna(correlation_coefficient) else ""
                    regression_type_es = {'Linear': 'Lineal', 'Quadratic': 'Cuadrática', 'Cubic': 'Cúbica', 'Polynomial(4)': 'Polinomial(4)'}.get(name, name) # Translate type for label
                    label_text = f'{regression_type_es} ({pearson_r_text}R²={r_squared:.3f})\n{equation_str}' # Translated type
                    ax.plot(x_plot, y_plot, label=label_text, color=reg_colors[i], linewidth=2.5, alpha=0.9)
                    regression_success = True

                except np.linalg.LinAlgError as lae:
                     print(f"      Error durante la regresión {name} para '{keyword}' ({y_source_name} vs {x_source_name}): Error de álgebra lineal - {lae}. Omitiendo este grado.") # Translated
                except Exception as e:
                    print(f"      Error inesperado durante la regresión {name} para '{keyword}' ({y_source_name} vs {x_source_name}): {e}. Omitiendo este grado.") # Translated

            # 10. Finalize and Save Plot
            if regression_success or not pd.isna(correlation_coefficient):
                plot_title = f'Análisis de Regresión: {y_source_name} vs {x_source_name}\nPalabra Clave: "{keyword}"' # Translated
                ax.set_title(plot_title, fontsize=14, wrap=True)
                ax.set_xlabel(f'{x_source_name} (Valor Normalizado)', fontsize=12) # Translated
                ax.set_ylabel(f'{y_source_name} (Valor Normalizado)', fontsize=12) # Translated
                if regression_success:
                    ax.legend(loc='best', fontsize=9)
                ax.grid(True, linestyle=':', alpha=0.6)
                plt.tight_layout(pad=1.5)

                sanitized_keyword = re.sub(r'[^\w\-]+', '_', keyword)
                base_filename = f"regression_{sanitized_keyword}_{y_source_name}_vs_{x_source_name}.png"

                if can_save_plots:
                    try:
                        unique_filename_relative = get_unique_filename(base_filename, unique_folder)
                        full_plot_path = os.path.join(unique_folder, unique_filename_relative)
                        plt.savefig(full_plot_path, bbox_inches='tight', dpi=150)
                        all_plot_filenames.append(unique_filename_relative)
                        print(f"    Gráfico guardado: {os.path.basename(full_plot_path)}") # Translated

                        # Add image to report markdown
                        add_image_to_report(plot_title, unique_filename_relative) # Added previously

                    except NameError:
                         print(f"    Error al guardar gráfico: Función 'get_unique_filename' no encontrada.") # Translated
                    except Exception as e:
                        print(f"    Error al guardar gráfico {base_filename}: {e}") # Translated
                else:
                     print("    Directorio de salida inválido o no definido, gráfico no guardado.") # Translated
            else:
                 print("    No hay resultados válidos de correlación o regresión para graficar.") # Translated

            plt.close(fig)

        # End loop for source pairs
    # End loop for keywords

    # 11. Convert results lists to Pandas DataFrames
    if correlation_results:
        df_correlation = pd.DataFrame(correlation_results)
    else:
        df_correlation = pd.DataFrame(columns=['Keyword', 'Source_A', 'Source_B', 'Correlation_R'])

    if regression_results:
        df_regression = pd.DataFrame(regression_results)
    else:
        df_regression = pd.DataFrame(columns=['Keyword', 'Source_A', 'Source_B', 'Regression_Type',
                                              'Degree', 'R_Squared', 'Coefficients', 'Equation'])

    csv_correlation = df_correlation
    csv_regression = df_regression

    print(f"\n--- Análisis de Correlación y Regresión Completado ---") # Translated
    print(f"Se generaron {len(all_plot_filenames)} gráficos.") # Translated
    if not csv_correlation.empty:
        print(f"Resumen de resultados de correlación (primeras 5 filas):\n{csv_correlation.head().to_string()}") # Translated
    else:
        print("No se generaron resultados de correlación.") # Translated

    if not csv_regression.empty:
        print(f"\nResumen de resultados de regresión (primeras 5 filas):\n{csv_regression.head().to_string()}") # Translated
    else:
        print("No se generaron resultados de regresión.") # Translated

    # 12. Return plot filenames and dataframes
    return all_plot_filenames, csv_correlation, csv_regression


def perform_pca_analysis(source_columns: list, keyword: str, unique_folder: str) -> tuple[str | None, str | None]: # Added keyword parameter
    """
    Performs Principal Component Analysis (PCA) on selected data sources for a specific keyword.
    Uses global combined_dataset and fixed_source_colors.
    Saves plots using get_unique_filename within unique_folder and
    adds plots to the report using add_image_to_report.

    Args:
        source_columns: List of source *names* (column names) to analyze.
        keyword: The specific keyword (management tool) being analyzed. # Added keyword arg description
        unique_folder: The specific directory path where analysis outputs should be saved.

    Returns:
        A tuple containing:
        - pca_csv_variable (str | None): PCA component scores as a CSV formatted string, or None on error.
        - pca_explanation (str | None): Text explanation of the PCA results and file paths, or None on error.
    """
    # Declare intention to use necessary globals (only if needed for modification, read-only access is fine)
    global combined_dataset, fixed_source_colors, get_unique_filename, add_image_to_report, pca_csv_variable, loadings_plot_filepath, scree_plot_filepath

    analysis_type_name = "PCA" # Used for base filenames

    # --- 1. Validate Input ---
    if not isinstance(source_columns, list) or len(source_columns) < 2:
        error_msg = "Error: PCA requires a list of at least two source names."
        print(error_msg)
        return None, error_msg
    if not keyword or not isinstance(keyword, str): # Added validation for keyword
        error_msg = "Error: A valid keyword string must be provided for PCA titles."
        print(error_msg)
        return None, error_msg

    print(f"--- Iniciando PCA para Keyword '{keyword}': {', '.join(source_columns)} ---") # Updated print
    print(f"    Output folder: {unique_folder}")

    # --- Define output filenames using the utility ---
    pca_data_filename_relative = ""
    scree_plot_filename_relative = ""
    loadings_plot_filename_relative = ""
    pca_data_filepath = ""
    scree_plot_filepath = ""
    loadings_plot_filepath = ""
    try:
        # Clean source names for filename stability
        cleaned_names = sorted([re.sub(r'[^\w\-]+', '_', name) for name in source_columns])
        cleaned_keyword = re.sub(r'[^\w\-]+', '_', keyword) # Clean keyword for filename
        base_csv_filename = f"{analysis_type_name}_{cleaned_keyword}_components_{'_'.join(cleaned_names)}.csv"
        pca_data_filename_relative = get_unique_filename(base_csv_filename, unique_folder)
        pca_data_filepath = os.path.join(unique_folder, pca_data_filename_relative)

        base_scree_filename = f"{analysis_type_name}_{cleaned_keyword}_scree_plot_{'_'.join(cleaned_names)}.png"
        scree_plot_filename_relative = get_unique_filename(base_scree_filename, unique_folder)
        scree_plot_filepath = os.path.join(unique_folder, scree_plot_filename_relative)

        base_loadings_filename = f"{analysis_type_name}_{cleaned_keyword}_loadings_plot_{'_'.join(cleaned_names)}.png"
        loadings_plot_filename_relative = get_unique_filename(base_loadings_filename, unique_folder)
        loadings_plot_filepath = os.path.join(unique_folder, loadings_plot_filename_relative)
    except NameError:
        error_msg = "Error: Utility function 'get_unique_filename' not defined."
        print(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Error setting up filenames: {e}"
        print(f"Error generating filenames: {e}")
        return None, error_msg

    # --- 2. Data Preparation ---
    data_scaled_df = None # Initialize
    try:
        # Access global combined_dataset using the provided source_columns names
        data_for_pca = combined_dataset[source_columns].copy()
    except NameError:
        error_msg = "Error: Global 'combined_dataset' not defined."
        print(error_msg)
        return None, error_msg
    except KeyError as e:
        error_msg = f"Error: Column '{e}' not found in combined_dataset."
        print(error_msg)
        return None, error_msg
    except Exception as e:
        error_msg = f"Error accessing data: {e}"
        print(f"Error accessing data from combined_dataset: {e}")
        return None, error_msg

    # Handle Missing Values (Placeholder: Mean Imputation)
    # !! Review this imputation strategy carefully for time series data !!
    if data_for_pca.isnull().values.any():
        print("    Advertencia: Se encontraron valores faltantes. Aplicando imputación de media.") # Translated
        try:
            imputer = SimpleImputer(strategy='mean')
            data_imputed = imputer.fit_transform(data_for_pca)
            data_imputed_df = pd.DataFrame(data_imputed, index=data_for_pca.index, columns=data_for_pca.columns)
        except Exception as e:
            error_msg = f"Error during imputation: {e}"
            print(f"    Error durante la imputación: {e}")
            return None, error_msg
    else:
        data_imputed_df = data_for_pca # No imputation needed

    # Standardize the data
    try:
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data_imputed_df)
        data_scaled_df = pd.DataFrame(data_scaled, index=data_imputed_df.index, columns=data_imputed_df.columns)
    except Exception as e:
        error_msg = f"Error during standardization: {e}"
        print(f"    Error durante la estandarización: {e}")
        return None, error_msg


    # --- 3. PCA Execution ---
    pca_df = None # Initialize
    pca = None # Initialize
    explained_variance_ratio = [] # Initialize
    cumulative_variance = [] # Initialize
    loadings = np.array([]) # Initialize
    n_components = 0 # Initialize
    try:
        n_components = data_scaled_df.shape[1]
        pca = PCA(n_components=n_components)
        principal_components = pca.fit_transform(data_scaled_df)

        pc_columns = [f'PC{i+1}' for i in range(n_components)]
        pca_df = pd.DataFrame(data=principal_components, columns=pc_columns, index=data_scaled_df.index)

        # Get results needed later
        explained_variance_ratio = pca.explained_variance_ratio_
        cumulative_variance = np.cumsum(explained_variance_ratio)
        loadings = pca.components_

    except Exception as e:
        error_msg = f"Error during PCA execution: {e}"
        print(f"    Error durante la ejecución de PCA: {e}")
        return None, error_msg


    # --- 4. Store PCA Results ---
    pca_csv_variable = None
    try:
        # Save to CSV file using the generated path
        pca_df.to_csv(pca_data_filepath)
        print(f"    Datos de componentes PCA guardados en: {pca_data_filename_relative}") # Translated

        # Store as CSV string variable
        pca_csv_variable = pca_df.to_string()
    except Exception as e:
        print(f"    Error guardando datos PCA: {e}") # Translated
        # Mark data as potentially unsaved, but continue plotting


    # --- 5. Analysis & Visualization ---
    # Access global fixed_source_colors (or appropriate name)
    local_source_colors_dict = {} # Default to empty dict
    try:
        # Ensure the global variable exists and is a dictionary
        if 'fixed_source_colors' in globals() and isinstance(fixed_source_colors, dict):
            local_source_colors_dict = fixed_source_colors
        else:
             print("    Advertencia: Global 'fixed_source_colors' no es un diccionario válido. Usando colores por defecto.") # Translated
    except NameError:
        print("    Advertencia: Global 'fixed_source_colors' no encontrada. Usando colores por defecto.") # Translated


    # --- 5a. Scree Plot ---
    scree_plot_title = f'PCA Varianza Explicada para "{keyword}"<br>({", ".join(source_columns)})' # Translated & updated
    try:
        fig_scree = go.Figure()
        scree_bar_color = local_source_colors_dict.get(source_columns[0], '#1f77b4')
        scree_line_color = local_source_colors_dict.get(source_columns[1] if n_components > 1 else source_columns[0], '#ff7f0e')

        fig_scree.add_trace(go.Bar(
            x=[f'PC{i+1}' for i in range(n_components)], y=explained_variance_ratio,
            name='Varianza Individual', marker_color=scree_bar_color, # Translated
            hovertemplate='PC%{x}: %{y:.2%}<extra></extra>'
        ))
        fig_scree.add_trace(go.Scatter(
            x=[f'PC{i+1}' for i in range(n_components)], y=cumulative_variance,
            name='Varianza Acumulada', mode='lines+markers', marker_color=scree_line_color, # Translated
            yaxis='y2', hovertemplate='Hasta PC%{x}: %{y:.2%}<extra></extra>' # Translated
        ))
        fig_scree.update_layout(
            title=scree_plot_title, # Use updated title
            xaxis_title='Componente Principal', # Translated
            yaxis_title='Ratio de Varianza Explicada', yaxis=dict(tickformat=".0%"), # Translated
            yaxis2=dict(title='Ratio de Varianza Acumulada', overlaying='y', side='right', range=[0, 1.05], tickformat=".0%"), # Translated
            legend=dict(yanchor="middle", y=0.5, xanchor="right", x=0.98), # Corrected 'center' to 'middle'
            template='plotly_white', hovermode='x unified'
        )
        # Save plot using the generated path
        fig_scree.write_image(scree_plot_filepath, width=800, height=500)
        print(f"    Gráfico Scree guardado: {scree_plot_filename_relative}") # Translated
        # Add to report markdown using the utility function
        add_image_to_report(scree_plot_title, scree_plot_filename_relative)
    except Exception as e:
        print(f"    Error generando/guardando/añadiendo gráfico scree: {e}") # Adjusted error message

    # --- 5b. Loadings Plot ---
    loadings_plot_title = f'PCA Gráfico de Cargas PC1 vs PC2 para "{keyword}"<br>({", ".join(source_columns)})' # Translated & updated
    try:
        fig_loadings = go.Figure()
        # Check if loadings is not empty before calculating max
        if loadings.size > 0:
             max_abs_loading = np.max(np.abs(loadings[:2, :]))
             # Avoid division by zero or near-zero
             loading_scale_factor = 1.5 / max_abs_loading if max_abs_loading > 1e-9 else 1
             max_val = np.max(np.abs(loadings[:2, :] * loading_scale_factor)) * 1.15
        else:
             max_abs_loading = 1
             loading_scale_factor = 1
             max_val = 1.5 * 1.15 # Default range if no loadings

        for i, var_name in enumerate(data_scaled_df.columns):
            # Use .get() safely on the dictionary
            color = local_source_colors_dict.get(var_name, '#000000')
            # Ensure loadings has enough dimensions before accessing elements
            loading_x = loadings[0, i] if loadings.shape[0] > 0 and loadings.shape[1] > i else 0
            loading_y = loadings[1, i] if loadings.shape[0] > 1 and loadings.shape[1] > i else 0
            scaled_x = loading_x * loading_scale_factor
            scaled_y = loading_y * loading_scale_factor

            fig_loadings.add_trace(go.Scatter(
                x=[0, scaled_x], y=[0, scaled_y], mode='lines+markers+text',
                name=var_name, text=['', var_name], textposition='middle right',
                line=dict(color=color, width=2), marker=dict(color=color, size=10, symbol='arrow-bar-up', angleref='previous'),
                hoverinfo='text', hovertext=f'{var_name}<br>Carga PC1: {loading_x:.3f}<br>Carga PC2: {loading_y:.3f}' # Translated
            ))

        fig_loadings.add_shape(type="line", x0=-max_val, y0=0, x1=max_val, y1=0, line=dict(color="rgba(0,0,0,0.3)", width=1, dash="dot"))
        fig_loadings.add_shape(type="line", x0=0, y0=-max_val, x1=0, y1=max_val, line=dict(color="rgba(0,0,0,0.3)", width=1, dash="dot"))

        pc1_var_str = f"{explained_variance_ratio[0]:.1%}" if n_components > 0 and len(explained_variance_ratio) > 0 else "N/A"
        pc2_var_str = f"{explained_variance_ratio[1]:.1%}" if n_components > 1 and len(explained_variance_ratio) > 1 else "N/A"

        fig_loadings.update_layout(
            title=loadings_plot_title, # Use updated title
            xaxis_title=f'Componente Principal 1 ({pc1_var_str} Varianza)', # Translated
            yaxis_title=f'Componente Principal 2 ({pc2_var_str} Varianza)', # Translated
            xaxis=dict(zeroline=False, range=[-max_val, max_val]),
            yaxis=dict(zeroline=False, range=[-max_val, max_val]),
            legend_title_text='Fuentes de Datos', template='plotly_white', width=800, height=700, # Translated
            annotations=[dict(x=0, y=0, showarrow=False, text='')]
        )
        fig_loadings.update_yaxes(scaleanchor="x", scaleratio=1)

        # Save plot using the generated path
        fig_loadings.write_image(loadings_plot_filepath)
        print(f"    Gráfico de Cargas guardado: {loadings_plot_filename_relative}") # Translated
        # Add to report markdown using the utility function
        add_image_to_report(loadings_plot_title, loadings_plot_filename_relative)
    except Exception as e:
        print(f"    Error generando/guardando/añadiendo gráfico de cargas: {e}") # Adjusted error message

    # --- 6. Generate Explanation Text ---
    # Safely access variance ratios
    pc1_var_exp = explained_variance_ratio[0] if n_components > 0 and len(explained_variance_ratio) > 0 else 0
    pc2_var_exp = explained_variance_ratio[1] if n_components > 1 and len(explained_variance_ratio) > 1 else 0
    cum_var_pc2 = cumulative_variance[1] if n_components > 1 and len(cumulative_variance) > 1 else (cumulative_variance[0] if n_components > 0 and len(cumulative_variance) > 0 else 0)

    # Use relative paths in the explanation
    pca_explanation = f"""
### Resultados del Análisis de Componentes Principales (PCA) para "{keyword}"

Se realizó PCA sobre los datos estandarizados de las series temporales ({', '.join(source_columns)}) para identificar patrones subyacentes de variación relacionados con "{keyword}".

*   **Varianza Explicada:** Consulte el gráfico de sedimentación (scree plot) `{scree_plot_filename_relative}`. Muestra que PC1 explica {pc1_var_exp:.1%} y PC2 explica {pc2_var_exp:.1%} de la varianza. La varianza acumulada hasta PC2 es {cum_var_pc2:.1%}.
*   **Cargas (Loadings):** El gráfico de cargas `{loadings_plot_filename_relative}` (mostrado en el informe) visualiza cómo las fuentes de datos originales contribuyen a los dos primeros componentes principales. Las flechas que apuntan en direcciones similares sugieren fuentes que varían juntas en este espacio 2D. Las flechas más largas indican una mayor influencia en estos componentes.
*   **Datos de Componentes:** Los datos transformados (puntuaciones de los componentes principales) se guardaron en `{pca_data_filename_relative}` y también están disponibles en la variable CSV devuelta por la función.
""" # Updated explanation title and intro sentence

    print(f"--- PCA para Keyword '{keyword}' ({', '.join(source_columns)}) completado ---") # Updated print
    return pca_csv_variable, pca_explanation


# *************************************************************************************
# INIT VARIABLES
# *************************************************************************************
def init_variables():
    # Declare all necessary globals that were set *before* this call
    global top_choice # Still needed for conditional logic perhaps? Review usage.
    global csv_last_20_data, csv_last_15_data, csv_last_10_data, csv_last_5_data
    global csv_last_year_data, csv_all_data, csv_means_trends, trends_results
    global current_year, charts, image_markdown # General resets
    global trend_analysis_text # Reset dictionary
    global original_values, original_calc_details # Reset dictionaries
    global dbase_options
    
    dbase_options = {
        1: "Google Trends",
        2: "Google Books Ngrams",
        3: "Bain - Usabilidad",
        4: "Crossref.org",
        5: "Bain - Satisfacción"
    }

    # Reset dictionaries
    original_values = {}
    original_calc_details = {}

    image_markdown = "\n\n# Gráficos\n\n"
    plt.style.use('ggplot')
    current_year = datetime.now().year
    charts=""

    # Reset analysis text dictionary
    trend_analysis_text = {}

    # Reset potential results from previous runs (important!)
    trends_results = None
    csv_last_20_data = None
    csv_last_15_data = None
    csv_last_10_data = None
    csv_last_5_data = None
    csv_last_year_data = None
    csv_all_data = None
    csv_means_trends = None

    # REMOVED the logic dependent on all_keywords
    # REMOVED the conditional call to process_file_data
    # REMOVED the filename/folder creation

# *************************************************************************************
# RESULTS
# *************************************************************************************

def results():
    global csv_fourier
    global csv_means_trends
    global csv_correlation
    global csv_regression
    global csv_arima
    global csv_seasonal
    global all_keywords # List of keywords or sources
    global csv_means_trendsA # Header/Title for Means/Trends section
    global combined_dataset # Input for combined analysis
    global combined_dataset2 # Seems unused here? Keep for now.
    global csv_significance # Text analysis from check_trends2
    global csv_combined_analysis # New global for combined results CSV
    global top_choice # To know if single or combined mode
    global actual_menu # Used for plot titles etc.
    global trends_results # Needed for single keyword check_trends2 call
    global selected_keyword

    # Initialize new global
    csv_combined_analysis = None

    # *************************************************************************************
    # Part 1 - Tendencias y Medias
    # *************************************************************************************

    banner_msg(' Part 1 - Tendencias y Medias ', color2=GREEN)

    if top_choice == 2:
        # --- Combined Dataset Analysis ---
        print("Performing combined dataset analysis (Means & Trends)...")
        # Ensure selected_keyword is defined before use
        current_selected_keyword = ""
        if 'selected_keyword' in globals() and selected_keyword:
            current_selected_keyword = selected_keyword
        else:
            print("Warning: Global 'selected_keyword' not found or empty for combined analysis title.")

        if combined_dataset is not None and not combined_dataset.empty:
                # 1. Generate Line plot and Calculate Averages/Trends
                line_plot_title = f"Análisis Comparativo de Tendencias para '{current_selected_keyword}'" if current_selected_keyword else "Análisis Comparativo de Tendencias"
                # Capture all 3 return values now
                line_plot_filename, csv_combined_analysis_data, analysis_results_raw = plot_and_analyze_combined_trends(
                    combined_dataset,
                    title=line_plot_title,
                    apply_smoothing=True, # Optionally apply smoothing to the line plot
                    window_size=3
                )
                # Store the calculated CSV data
                csv_combined_analysis = csv_combined_analysis_data # Assign to global

                # 2. Generate Bar plot using the calculated results
                if analysis_results_raw:
                    bar_plot_title = f"Comparativo de Medias por Periodo para '{current_selected_keyword}'" if current_selected_keyword else "Comparativo de Medias por Periodo"
                    # Call the new bar plot function
                    plot_combined_averages_bars(analysis_results_raw, title=bar_plot_title)
                else:
                    print("Warning: No raw analysis results returned from trends function; cannot generate bar chart.")

                # Set the header/title for the combined analysis section in reports
                csv_means_trendsA = "Combined Analysis - Means and Trends\n</br> Trend NADT: Normalized Annual Desviation\n</br> Trend MAST: Moving Average Smoothed Trend\n\n"
                # Indicate that detailed CSV is in csv_combined_analysis
                csv_means_trends = csv_combined_analysis
                csv_significance = "# Combined analysis doesn't generate single-keyword significance text.\n"
                all_keywords = combined_dataset.columns.tolist() # Store the list of sources/columns
        else:
                print("Error: Combined dataset is empty or not loaded. Skipping combined analysis.")
                csv_combined_analysis = "# Error: Combined dataset empty.\n"
                csv_means_trends = "# Error: Combined dataset empty.\n"
                csv_means_trendsA = "Error: Combined dataset empty.\n"
                csv_significance = "# Error: Combined dataset empty.\n"
                all_keywords = []

    else:
        # --- Single Keyword Analysis ---
        print("Performing single keyword analysis (Means & Trends)...")
        csv_string = io.StringIO()
        csv_writer = csv.writer(csv_string)
        # Define header matching the expected output from check_trends2's results dict
        # IMPORTANT: Ensure check_trends2 returns 'means' and 'trends' in this order
        # Example header: Check check_trends2 return dict keys/order if issues arise
        header = ['Keyword', 'Overall Avg', '20 Year Avg', '15 Year Avg', '10 Year Avg', '5 Year Avg', '1 Year Avg', 'Trend NADT', 'Trend MAST']
        csv_writer.writerow(header)

        all_analysis_text = []
        if not all_keywords:
             print("Warning: No keywords selected for single keyword analysis.")
        else:
            for kw in all_keywords:
                try:
                    # check_trends2 calculates averages, trends (NADT/MAST) and returns them
                    results_check = check_trends2(kw) # Assuming this returns a dict

                    # Extract means and trends safely, providing defaults
                    # Ensure the order matches the header defined above!
                    means_row = results_check.get('means', [np.nan]*6) # Default to NaNs if key missing
                    trends_row = results_check.get('trends', [np.nan]*2) # Default to NaNs if key missing

                    # Combine keyword, means, and trends for the row
                    row_data = [kw] + means_row + trends_row
                    csv_writer.writerow(row_data)

                    # Append analysis text
                    all_analysis_text.append(f"--- {kw} ---\n{results_check.get('analysis_text', 'No analysis text available.')}")

                except Exception as e:
                    print(f"Error processing keyword '{kw}' in check_trends2: {e}")
                    # Write a row indicating error for this keyword
                    csv_writer.writerow([kw] + ['Error'] * (len(header) - 1))
                    all_analysis_text.append(f"--- {kw} ---\nError during analysis: {e}")


        csv_data = csv_string.getvalue()
        csv_means_trendsA = "Means and Trends (Single Keywords)\n</br> Trend NADT: Normalized Annual Desviation\n</br> Trend MAST: Moving Average Smoothed Trend\n\n"
        csv_means_trends = csv_data # This now holds the CSV for single keywords
        csv_significance = "\n\n".join(all_analysis_text)
        # csv_combined_analysis remains None as it's single keyword mode

    # *************************************************************************************
    # Part 2 - Comparación a lo largo del tiempo
    # *************************************************************************************

    banner_msg(' Part 2 - Comparación a lo largo del tiempo ', color2=GREEN)
    if top_choice == 2:
    #******
        print("\nCalculating trends across sources using combined_dataset...")
        global source_trends_results
        source_trends_results = {} # Initialize/clear it here as well

        # Make sure required globals are accessible
        global earliest_date
        global latest_date
        global selected_sources # Contains numbers like [1, 2, 4]
        global dbase_options  # Maps numbers to friendly names like {1: "Google Trends", ...}

        if combined_dataset is not None and not combined_dataset.empty and dbase_options:
            # Ensure index is datetime
            if not pd.api.types.is_datetime64_any_dtype(combined_dataset.index):
                try:
                    combined_dataset.index = pd.to_datetime(combined_dataset.index)
                    print("Converted combined_dataset index to datetime.")
                except Exception as e:
                    print(f"Error converting combined_dataset index to datetime: {e}")
                    # Handle error appropriately

            # Recalculate date range from the actual combined_dataset being used
            earliest_date = combined_dataset.index.min()
            latest_date = combined_dataset.index.max()
            current_year = latest_date.year
            earliest_year_in_data = earliest_date.year

            print(f" Combined dataset date range: {earliest_date.date()} to {latest_date.date()}")

            # --- Calculate total_years_available FIRST ---
            total_years_available = current_year - earliest_year_in_data + 1 # Add 1 to include start/end years
            print(f" Total years available in data: {total_years_available}")
            # ---------------------------------------------

            # Define periods based on available data range
            available_periods_years = []
            # --- Now use the calculated variable ---
            if total_years_available >= 1: available_periods_years.append('all')
            if total_years_available >= 1: available_periods_years.append(1)
            if total_years_available >= 5: available_periods_years.append(5)
            if total_years_available >= 10: available_periods_years.append(10)
            if total_years_available >= 15: available_periods_years.append(15)
            if total_years_available >= 20: available_periods_years.append(20)
            # --------------------------------------

            print(f" Periods to calculate based on availability: {available_periods_years}")

            # --- Calculate for each period ---
            for period_years in available_periods_years:
                start_date = None # Initialize
                end_date = latest_date # Usually end at the latest date

                if period_years == 'all':
                    start_date = earliest_date
                    data_key = 'all_data'
                    mean_key = 'mean_all'
                elif period_years == 1:                         # <<< ADD 1 YEAR Condition
                    start_year = max(earliest_year_in_data, current_year - period_years) # Should calculate correctly
                    start_date = pd.Timestamp(f"{start_year}-01-01") # Start of the last year
                    # Optional: Set end_date for 1 year precisely if needed
                    # end_date = pd.Timestamp(f"{start_year}-12-31") # End of the last year
                    data_key = 'last_1_year_data'
                    mean_key = 'mean_last_1'
                else: # 5, 10, 15, 20 years
                    start_year = max(earliest_year_in_data, current_year - period_years)
                    start_date = pd.Timestamp(f"{start_year}-01-01")
                    data_key = f'last_{period_years}_years_data'
                    mean_key = f'mean_last_{period_years}'

                print(f"  Calculating for period: {period_years} years ({start_date.year if start_date else 'N/A'}-{end_date.year})")

                # Slice the data for the period
                # Ensure start_date is valid before slicing
                if start_date is None:
                    print(f"   Skipping period {period_years}, invalid start date.")
                    continue

                period_data_full = combined_dataset[(combined_dataset.index >= start_date) & (combined_dataset.index <= end_date)]

                period_data_by_source = {}
                period_means_by_source = {}

                if not period_data_full.empty:
                    # Iterate through selected source KEYS (numbers, e.g., 1, 2, 4)
                    for source_key in selected_sources:
                        # Get the user-friendly name using the source_key from dbase_options
                        # This friendly name IS the actual column name in combined_dataset
                        actual_column_name = dbase_options.get(source_key, None)

                        if actual_column_name is None:
                            print(f"    Warning: Source key '{source_key}' not found in dbase_options. Skipping.")
                            continue # Skip this source if the key is invalid

                        # Use the friendly name (actual_column_name) to access the column
                        if actual_column_name in period_data_full.columns:
                            source_series = period_data_full[actual_column_name].dropna()
                            if not source_series.empty:
                                # Store data using the friendly name (actual_column_name) as the key
                                period_data_by_source[actual_column_name] = source_series
                                try:
                                    mean_val = source_series.mean()
                                    # Store mean using the friendly name (actual_column_name) as the key
                                    period_means_by_source[actual_column_name] = mean_val if not pd.isna(mean_val) else 0.0
                                except Exception as e:
                                    print(f"    Warning: Could not calculate mean for {actual_column_name} in period {period_years}: {e}")
                                    period_means_by_source[actual_column_name] = 0.0
                            else:
                                print(f"    Warning: No non-NaN data for source '{actual_column_name}' in period {period_years}.")
                                period_data_by_source[actual_column_name] = pd.Series(dtype='float64')
                                period_means_by_source[actual_column_name] = 0.0
                        else:
                            # This warning now means the friendly name wasn't found as a column
                            print(f"    Warning: Column '{actual_column_name}' (derived from key '{source_key}') not found in combined dataset for period {period_years}.")
                            period_data_by_source[actual_column_name] = pd.Series(dtype='float64') # Still store empty data under the expected name
                            period_means_by_source[actual_column_name] = 0.0

                # Store results for the period
                source_trends_results[data_key] = period_data_by_source
                source_trends_results[mean_key] = period_means_by_source

            print("Finished calculating trends across sources from combined_dataset.")
        else:
            if combined_dataset is None or combined_dataset.empty:
                print("Error: combined_dataset is empty or None.")
            if not dbase_options:
                print("Error: dbase_options is not available.")
            print("Cannot calculate source trends.")

        print("-" * 20) # Separator for clarity
        print(f"DEBUG: Type of source_trends_results: {type(source_trends_results)}")
        print(f"DEBUG: Value of source_trends_results: {source_trends_results}")
        print(f"DEBUG: Type of selected_sources: {type(selected_sources)}")
        print(f"DEBUG: Value of selected_sources: {selected_sources}")
        print("-" * 20)
        
        # --- NOW you can safely call relative_comparison2 ---
        if source_trends_results and selected_sources: # Check BOTH dict and list are not empty
            print("\nCalling relative_comparison2...")
            relative_comparison2()
        else:
            print("\nSkipping relative_comparison2 due to:")
            if not source_trends_results:
                print(" - source_trends_results is empty.")
            if not selected_sources:
                print(" - selected_sources is empty.")
                
    #****** end of top_choice == 2
    
    else:
        try:
            relative_comparison()
        except Exception as e:
            print(f"Error during relative comparison: {e}")
            traceback.print_exc()


    # *************************************************************************************
    # Part 3 - Correlación - Regresión
    # *************************************************************************************

    banner_msg(' Part 3 - Correlación - Regresión ', color2=GREEN)
    # Ensure trends_results is available; might need recalculation or loading if not persistent
    # if 'trends_results' in globals() and trends_results:
    #     # analyze_trends expects the 'trends_results' structure
    #     # It calculates correlation/regression based on 'last_20_years_data' within trends_results
    #     analysis = analyze_trends(trends_results)
    #     if top_choice == 2 or (top_choice == 1 and len(all_keywords) < 2) : # Check if combined or single keyword mode < 2 keywords
    #          one_keyword = True # Treat combined mode or single < 2 keywords as 'one_keyword' for this section
    #          csv_correlation = None
    #          csv_regression = None
    #          print('Análisis de Correlación y Regresión requiere al menos dos variables (keywords/fuentes). Omitido.')
    #     else:
    #          one_keyword = False
    #          csv_correlation = analysis.get('correlation') # Safely get results
    #          csv_regression = analysis.get('regression')
    # Check if combined_dataset is not None *and* not empty
    if top_choice == 2 and (combined_dataset is not None and not combined_dataset.empty) and selected_sources and current_selected_keyword and dbase_options:
        print("\nCalling analyze_source_correlations_regressions...")

        # --- Prepare arguments for the function ---
        # 1. Create list of source *names* from the numbers in selected_sources
        source_names_to_analyze = [dbase_options[num] for num in selected_sources if num in dbase_options]
        if not source_names_to_analyze:
             print("  Error: Could not map selected source numbers to names. Skipping regression.")
        else:
             # 2. Create the dictionary structure expected by combined_datasets argument
             #    Key: the single selected keyword; Value: the combined DataFrame
             # Ensure 'current_selected_keyword' is defined and holds the keyword string
             datasets_for_analysis = {current_selected_keyword: combined_dataset}

             # 3. Create a list containing the single keyword
             keyword_list_for_analysis = [current_selected_keyword]
             # --- End Argument Preparation ---

             # Call the function with the correctly formatted arguments
             regression_plot_files, df_corr, df_regr = analyze_source_correlations_regressions(
                 combined_datasets=datasets_for_analysis,      # Pass the DICTIONARY
                 selected_sources=source_names_to_analyze,     # Pass the LIST OF NAMES
                 keywords=keyword_list_for_analysis,          # Pass the LIST WITH THE KEYWORD
                 source_colors=fixed_source_colors           # Pass your color dictionary
             )

             # Store the results (e.g., assign DataFrames to global csv_correlation, csv_regression)
             csv_correlation = df_corr
             csv_regression = df_regr             
             
             # Call the source correlation heatmap function
             print("\nGenerating Source Correlation Heatmap...") # Optional: Add a print statement
             plot_source_correlation_heatmap(combined_dataset, selected_keyword)

             # You can use regression_plot_files list later for adding to the report if needed
             print(f"\nGenerated {len(regression_plot_files)} regression plots.")
             
             # ***** PCA Analysis *****

             keyword_for_pca = None # Variable to hold the keyword we'll use

             # 1. Try to get keyword from 'selected_keyword' global if it exists and is valid
             if 'selected_keyword' in globals() and selected_keyword:
                 keyword_for_pca = selected_keyword
             # 2. If not found above, try to get it from 'current_selected_keyword' global
             elif 'current_selected_keyword' in globals() and current_selected_keyword:
                 keyword_for_pca = current_selected_keyword

             # 3. Now, check if we successfully found a keyword to use
             if keyword_for_pca:
                 print(f"    Iniciando análisis PCA para keyword: '{keyword_for_pca}'") # Info message
                 pca_data_str, pca_expl = perform_pca_analysis(
                    source_columns=source_names_to_analyze, # Pass the list of names
                    keyword=keyword_for_pca,                # Pass the found keyword
                    unique_folder=unique_folder
                 )

                 if pca_data_str is not None:
                    # Store pca_data_str if needed (e.g., in memory or a database)
                    # pca_expl already contains the explanation text
                    # The plots have been added to the report via add_image_to_report
                    # append_to_report_text(pca_expl) # Assuming a function to add text to the report
                    print("Análisis PCA añadido al informe.") # Translated
                 else:
                    # Handle the error - pca_expl might contain the error message
                    error_message = f"El análisis PCA falló para '{keyword_for_pca}' (fuentes: {source_names_to_analyze}): {pca_expl}" # Updated error message
                    print(error_message)
                    # append_to_report_text(f"\n**Error:** {error_message}\n") # Add error to report
             else:
                 # This else block now means neither global variable held a valid keyword
                 print("Error: No se pudo realizar el análisis PCA porque falta una keyword válida ('selected_keyword' o 'current_selected_keyword').") # Updated error message

       
    elif top_choice == 2: # Add an else if to explain why it might be skipped
         # Print reasons if the condition failed
         print("\nSkipping source correlation/regression analysis because:")
         if combined_dataset is None or combined_dataset.empty:
              print(" - Combined dataset is missing or empty.")
         if not selected_sources:
              print(" - No sources were selected.")
         if 'current_selected_keyword' not in globals() or not current_selected_keyword: # Check definition
              print(" - Keyword ('current_selected_keyword') was not selected or defined.")
         if 'dbase_options' not in globals() or not dbase_options:
              print(" - dbase_options dictionary is not available.")

    else:
        # This part handles the case where top_choice is not 2
        print("Warning: Skipping source correlation/regression analysis (not applicable mode or missing data).")
        # Assign None to prevent potential errors later if these vars are expected
        csv_correlation = None
        csv_regression = None

    # *************************************************************************************
    # Part 4 - Modelo ARIMA
    # *************************************************************************************

    banner_msg(' Part 4 - Modelo ARIMA ', color2=GREEN)
    try:
        # Ensure arima_model can handle combined data (might need adaptation)
        # Currently seems designed for single keyword; might need kw loop or adaptation
        if top_choice == 1 and all_keywords:
            # Example: Run ARIMA for the first keyword if in single mode
            # Or loop through all_keywords if desired
            print(f"Running ARIMA for first keyword: {all_keywords[0]}")
            csv_arima = arima_model(mb=120, mf=36, ts=18, p=2, d=1, q=0) # Pass kw
        elif top_choice == 2:
             print("ARIMA model execution skipped in combined data source mode.")
             csv_arima = "# ARIMA skipped in combined mode.\n"
        else:
             print("ARIMA model skipped (no keywords or combined mode).")
             csv_arima = "# ARIMA skipped.\n"
    except Exception as e:
        print(f"Error during ARIMA modeling: {e}")
        traceback.print_exc()
        csv_arima = f"# Error during ARIMA: {e}\n"


    # *************************************************************************************
    # Part 5 - Análisis Estacional
    # *************************************************************************************

    banner_msg(' Part 5 - Análisis estacional ', color2=GREEN)
    try:
        # Similar to ARIMA, check if seasonal_analysis needs adaptation for combined mode
        if top_choice == 1 and all_keywords:
            print(f"Running Seasonal Analysis for first keyword: {all_keywords[0]}")
            seasonal_analysis('last_10_years_data') # Pass kw
        elif top_choice == 2:
             print("Seasonal Analysis skipped in combined data source mode.")
             # csv_seasonal might need to be handled/set here if it's expected later
             global csv_seasonal # Ensure it's global if setting
             csv_seasonal = "# Seasonal analysis skipped in combined mode.\n"
        else:
             print("Seasonal Analysis skipped (no keywords or combined mode).")
             csv_seasonal = "# Seasonal analysis skipped.\n"

    except Exception as e:
        print(f"Error during seasonal analysis: {e}")
        traceback.print_exc()
        # Handle csv_seasonal setting on error if necessary


    # *************************************************************************************
    # Part 6 - Fourier Analisys
    # *************************************************************************************

    banner_msg(' Part 6 - Análisis de Fourier ', color2=GREEN)
    try:
        # Check if fourier_analysis2 needs adaptation for combined mode
        if top_choice == 1 and all_keywords:
            print(f"Running Fourier Analysis for first keyword: {all_keywords[0]}")
            csv_fourier=fourier_analysis2('last_20_years_data') # Pass kw
        elif top_choice == 2:
             print("Fourier Analysis skipped in combined data source mode.")
             csv_fourier = "# Fourier skipped in combined mode.\n"
        else:
             print("Fourier Analysis skipped (no keywords or combined mode).")
             csv_fourier = "# Fourier skipped.\n"
    except Exception as e:
        print(f"Error during Fourier analysis: {e}")
        traceback.print_exc()
        csv_fourier = f"# Error during Fourier: {e}\n"

    print("\n--- Results function finished ---")


    
# *************************************************************************************
# AI Analysis
# *************************************************************************************
def ai_analysis():
    global gem_temporal_trends_sp
    global gem_cross_keyword_sp
    global gem_industry_specific_sp
    global gem_arima_sp
    global gem_seasonal_sp
    global gem_fourier_sp
    global gem_conclusions_sp
    global csv_combined_data
    global csv_correlation
    global csv_regression
    global gem_summary_sp
    global csv_all_data
    global pca_csv_variable
    global scree_plot_filepath

    if top_choice == 1 or top_choice == 3:
        if total_years < 20:
            csv_all_data = ""

    banner_msg(' Part 7 - Análisis con IA ', color2=GREEN)

    gem_temporal_trends_sp = ""
    gem_cross_keyword_sp = ""
    gem_industry_specific_sp = ""
    gem_arima_sp = ""
    gem_seasonal_sp = ""
    gem_fourier_sp = ""
    gem_conclusions_sp = ""
    gem_summary_sp = ""

    if top_choice == 1 or top_choice == 3:
        f_system_prompt = system_prompt_1.format(dbs=actual_menu)
    elif top_choice == 2:
        sel_sources = ", ".join(dbase_options[source] for source in selected_sources)
        f_system_prompt = system_prompt_2.format(selected_sources=sel_sources)
        csv_combined_data = combined_dataset.to_csv(index=True)
    else:
        sel_sources = ", ".join(dbase_options[source] for source in selected_sources)
        f_system_prompt = system_prompt_2.format(selected_sources=sel_sources)
        csv_combined_data = combined_dataset.to_csv(index=True)

    # Add the selected_sources parameter to the format call
    if top_choice == 1 or top_choice == 3:
        p_sp = prompt_sp.format(all_kws=all_keywords, selected_sources="")
    else:
        p_sp = prompt_sp.format(all_kws=all_kw, selected_sources=sel_sources)

    n=0
    n+=1
    
    
    if top_choice == 1:
        p_1 = temporal_analysis_prompt_1.format(dbs=actual_menu, all_kw=all_kw, \
                          csv_all_data=csv_all_data, csv_significance=csv_significance, \
                          csv_last_20_data=csv_last_20_data, csv_last_15_data=csv_last_15_data, csv_last_10_data=csv_last_10_data, \
                          csv_last_5_data=csv_last_5_data, csv_last_year_data=csv_last_year_data, \
                          csv_means_trends=csv_means_trends)        
    else:
        p_1 = temporal_analysis_prompt_2.format(selected_sources=sel_sources, all_kw=all_kw, \
                          csv_combined_data=csv_combined_data, csv_means_trends=csv_means_trends)
    
    print(f'\n\n\n{n}. Analizando tendencias temporales...')
    print("Enviando solicitud a la API de Gemini (esto puede tardar un momento)...")
    gem_temporal_trends=gemini_prompt(f_system_prompt,p_1)
    
    # Only proceed with translation if we got a valid response
    if not gem_temporal_trends.startswith("[API"):
        prompt_spanish=f'{p_sp} {gem_temporal_trends}'
        print("Traduciendo respuesta...")
        gem_temporal_trends_sp=gemini_prompt(f_system_prompt,prompt_spanish)
    else:
        # If there was an API error, don't try to translate the error message
        gem_temporal_trends_sp = f"Error en el análisis: {gem_temporal_trends}"
    
    #display(Markdown(gem_temporal_trends_sp))
    print(gem_temporal_trends_sp)
    
    
    if not one_keyword or top_choice == 2:
      n+=1
      if top_choice == 1:
        p_2 = cross_relationship_prompt_1.format(dbs=actual_menu, csv_corr_matrix=csv_correlation, csv_regression=csv_regression)
        print(f'\n\n\n{n}. Analizando relaciones entre palabras clave...')
      else:
        # Optimize the correlation matrix if it's too large
        if len(csv_correlation) > 50000:  # If correlation matrix is large
            print(f"\x1b[33mWarning: Correlation matrix is large ({len(csv_correlation)/1024:.1f}KB). Truncating to reduce API timeout risk.\x1b[0m")
            # Simplify by keeping only the header and a subset of rows
            csv_lines = csv_correlation.split('\n')
            if len(csv_lines) > 100:
                truncated_corr = '\n'.join(csv_lines[:50]) + '\n...[data truncated]...\n' + '\n'.join(csv_lines[-50:])
                csv_corr_for_prompt = truncated_corr
            else:
                csv_corr_for_prompt = csv_correlation
        else:
            csv_corr_for_prompt = csv_correlation
            
        # Optimize the combined dataset if it's too large
        if len(csv_combined_data) > 50000:
            # Already handled in the next section, use the same approach
            csv_lines = csv_combined_data.split('\n')
            header = csv_lines[0]
            data_lines = csv_lines[1:]
            subset_size = min(len(data_lines), 1000)  # Limit to ~1000 rows
            first_chunk = data_lines[:subset_size//2]
            last_chunk = data_lines[-(subset_size//2):]
            truncated_csv = header + '\n' + '\n'.join(first_chunk) + '\n...[data truncated]...\n' + '\n'.join(last_chunk)
            csv_data_for_prompt = truncated_csv
        else:
            csv_data_for_prompt = csv_combined_data
            csv_regression_for_prompt = csv_regression.to_string()
            
        p_2 = cross_relationship_prompt_2.format(dbs=sel_sources, all_kw=all_kw, 
                                               csv_corr_matrix=csv_correlation, 
                                               csv_combined_data=csv_combined_data, csv_regression=csv_regression_for_prompt)        
        print(f'\n\n\n{n}. Analizando relaciones entre fuentes de datos...')  
      
      print("Enviando solicitud a la API de Gemini (esto puede tardar un momento)...")
      gem_cross_keyword=gemini_prompt(f_system_prompt,p_2)
      
      # Only proceed with translation if we got a valid response
      if not gem_cross_keyword.startswith("[API"):
          prompt_spanish=f'{p_sp} {gem_cross_keyword}'
          print("Traduciendo respuesta...")
          gem_cross_keyword_sp=gemini_prompt(f_system_prompt,prompt_spanish)
      else:
          # If there was an API error, don't try to translate the error message
          gem_cross_keyword_sp = f"Error en el análisis: {gem_cross_keyword}"
          
      #display(Markdown(gem_cross_keyword_sp))
      print(gem_cross_keyword_sp)
    else:
      gem_cross_keyword=""
      csv_correlation=""
      csv_regression=""
    
    n+=1
    if top_choice == 1 or top_choice == 3:
      p_3 = trend_analysis_prompt_1.format(all_kw=all_keywords, dbs=actual_menu, csv_means_trends=csv_means_trends, analisis_temporal_ai=gem_temporal_trends)
      print(f'\n\n\n{n}. Investigando Patrones de Tendencia General...')
    else:
      # Optimize the prompt to reduce its size and complexity
      # 1. Limit the CSV data size by truncating if necessary
      max_csv_size = 100000  # Limit CSV size to ~100KB
      if len(csv_combined_data) > max_csv_size:
          print(f"\x1b[33mWarning: Combined dataset CSV is large ({len(csv_combined_data)/1024:.1f}KB). Truncating to reduce API timeout risk.\x1b[0m")
          # Keep header row and truncate the rest
          csv_lines = csv_combined_data.split('\n')
          header = csv_lines[0]
          # Take a subset of lines (first 20% and last 20% to maintain time series context)
          data_lines = csv_lines[1:]
          subset_size = min(len(data_lines), int(max_csv_size / 50))  # Approximate number of lines to keep
          first_chunk = data_lines[:subset_size//2]
          last_chunk = data_lines[-(subset_size//2):]
          truncated_csv = header + '\n' + '\n'.join(first_chunk) + '\n...[data truncated]...\n' + '\n'.join(last_chunk)
          csv_for_prompt = truncated_csv
      else:
          csv_for_prompt = csv_combined_data
      
      # 2. Create the optimized prompt
      p_3 = pca_prompt_2.format(all_kw=all_kw, pca_csv_variable=pca_csv_variable)
      print(f'\n\n\n{n}. Investigando patrones de tendencias entre las fuentes de datos...')  
    
    # Use the optimized gemini_prompt function with retry logic
    print("Enviando solicitud a la API de Gemini (esto puede tardar un momento)...")
    gem_industry_specific=gemini_prompt(f_system_prompt, p_3,image_paths=[loadings_plot_filepath, scree_plot_filepath])
    
    # Only proceed with translation if we got a valid response (not an error message)
    if not gem_industry_specific.startswith("[API"):
        prompt_spanish=f'{p_sp} {gem_industry_specific}'
        print("Traduciendo respuesta...")
        gem_industry_specific_sp=gemini_prompt(f_system_prompt, prompt_spanish)
    else:
        # If there was an API error, don't try to translate the error message
        gem_industry_specific_sp = f"Error en el análisis: {gem_industry_specific}"
    
    #display(Markdown(gem_industry_specific_sp))
    print(gem_industry_specific_sp)

    if skip_arima[0]==False:
        n+=1
        if top_choice == 1:
            p_4 = arima_analysis_prompt_1.format(all_kw=all_keywords, dbs=actual_menu, arima_results=csv_arima, csv_means_trends=csv_means_trends, \
                                                analisis_temporal_ai=gem_temporal_trends, analisis_tendencias_ai=gem_industry_specific)
            print(f'\n\n\n{n}. Analizando el rendimiento del modelo ARIMA...')
        else:
            # Optimize ARIMA results if they're too large
            if len(csv_arima) > 50000:
                print(f"\x1b[33mWarning: ARIMA results are large ({len(csv_arima)/1024:.1f}KB). Truncating to reduce API timeout risk.\x1b[0m")
                csv_lines = csv_arima.split('\n')
                header = csv_lines[0]
                data_lines = csv_lines[1:]
                subset_size = min(len(data_lines), 1000)  # Limit to ~1000 rows
                truncated_arima = header + '\n' + '\n'.join(data_lines[:subset_size])
                csv_arima_for_prompt = truncated_arima
            else:
                csv_arima_for_prompt = csv_arima
                
            p_4 = arima_analysis_prompt_2.format(selected_sources=sel_sources, selected_keyword=actual_menu, arima_results=csv_arima_for_prompt)        
            print(f'\n\n\n{n}. Analizando el rendimiento del modelo ARIMA entre las fuentes de datos...')     

        print("Enviando solicitud a la API de Gemini (esto puede tardar un momento)...")
        gem_arima=gemini_prompt(f_system_prompt,p_4)
        
        # Only proceed with translation if we got a valid response
        if not gem_arima.startswith("[API"):
            prompt_spanish=f'{p_sp} {gem_arima}'
            print("Traduciendo respuesta...")
            gem_arima_sp=gemini_prompt(f_system_prompt,prompt_spanish)
        else:
            # If there was an API error, don't try to translate the error message
            gem_arima_sp = f"Error en el análisis: {gem_arima}"
            
        #display(Markdown(gem_arima_sp))
        print(gem_arima_sp)

    if skip_seasonal[0]==False:
        n+=1
        if top_choice == 1:
            if skip_arima[0]==True:
                gem_arima=""
            p_5 = seasonal_analysis_prompt_1.format(all_kw=all_keywords, dbs=actual_menu, csv_seasonal=csv_seasonal, \
                                                    analisis_temporal_ai=gem_temporal_trends, analisis_tendencias_ai=gem_industry_specific, \
                                                    analisis_arima_ai=gem_arima)
            print(f'\n\n\n{n}. Interpretando patrones estacionales...')
        else:
        # Optimize seasonal data if it's too large
            if len(csv_seasonal) > 50000:
                print(f"\x1b[33mWarning: Seasonal analysis data is large ({len(csv_seasonal)/1024:.1f}KB). Truncating to reduce API timeout risk.\x1b[0m")
                csv_lines = csv_seasonal.split('\n')
                header = csv_lines[0]
                data_lines = csv_lines[1:]
                subset_size = min(len(data_lines), 1000)  # Limit to ~1000 rows
                truncated_seasonal = header + '\n' + '\n'.join(data_lines[:subset_size])
                csv_seasonal_for_prompt = truncated_seasonal
            else:
                csv_seasonal_for_prompt = csv_seasonal
                
            # Reuse the optimized correlation matrix from earlier
            if 'csv_corr_for_prompt' not in locals():
                csv_corr_for_prompt = csv_correlation
                
            p_5 = seasonal_analysis_prompt_2.format(selected_keyword=actual_menu, selected_sources=sel_sources, \
                                                    csv_seasonal=csv_seasonal_for_prompt, \
                                                    csv_correlation=csv_corr_for_prompt)        
            print(f'\n\n\n{n}. Interpretando patrones estacionales entre las fuentes de datos...')

        print("Enviando solicitud a la API de Gemini (esto puede tardar un momento)...")
        gem_seasonal=gemini_prompt(f_system_prompt,p_5)
        
        # Only proceed with translation if we got a valid response
        if not gem_seasonal.startswith("[API"):
            prompt_spanish=f'{p_sp} {gem_seasonal}'
            print("Traduciendo respuesta...")
            gem_seasonal_sp=gemini_prompt(f_system_prompt,prompt_spanish)
        else:
            # If there was an API error, don't try to translate the error message
            gem_seasonal_sp = f"Error en el análisis: {gem_seasonal}"
        
        #display(Markdown(gem_seasonal_sp))
        print(gem_seasonal_sp)

    n+=1
    if top_choice == 1:
      if skip_arima[0]==True:
          gem_arima=""
      if skip_seasonal[0]==True:
          gem_seasonal=""
      p_6 = prompt_6_single_analysis.format(all_kw=all_keywords, dbs=actual_menu, csv_fourier=csv_fourier, \
                                    analisis_temporal_ai=gem_temporal_trends, analisis_tendencias_ai=gem_industry_specific, \
                                    analisis_arima_ai=gem_arima, analisis_estacional_ai=gem_seasonal)
      print(f'\n\n\n{n}. Analizando patrones cíclicos...')
    else:
      # Optimize Fourier analysis data if it's too large
      if len(csv_fourier) > 50000:
          print(f"\x1b[33mWarning: Fourier analysis data is large ({len(csv_fourier)/1024:.1f}KB). Truncating to reduce API timeout risk.\x1b[0m")
          csv_lines = csv_fourier.split('\n')
          header = csv_lines[0]
          data_lines = csv_lines[1:]
          subset_size = min(len(data_lines), 1000)  # Limit to ~1000 rows
          truncated_fourier = header + '\n' + '\n'.join(data_lines[:subset_size])
          csv_fourier_for_prompt = truncated_fourier
      else:
          csv_fourier_for_prompt = csv_fourier
          
      # Reuse the optimized combined dataset from earlier if available
      if 'csv_data_for_prompt' not in locals():
          # If not already optimized, check if it needs optimization
          if len(csv_combined_data) > 50000:
              csv_lines = csv_combined_data.split('\n')
              header = csv_lines[0]
              data_lines = csv_lines[1:]
              subset_size = min(len(data_lines), 1000)  # Limit to ~1000 rows
              first_chunk = data_lines[:subset_size//2]
              last_chunk = data_lines[-(subset_size//2):]
              truncated_csv = header + '\n' + '\n'.join(first_chunk) + '\n...[data truncated]...\n' + '\n'.join(last_chunk)
              csv_data_for_prompt = truncated_csv
          else:
              csv_data_for_prompt = csv_combined_data
      
      p_6 = prompt_6_correlation.format(selected_keyword=actual_menu, \
                                      selected_sources=sel_sources, \
                                      csv_fourier=csv_fourier_for_prompt, csv_combined_data=csv_data_for_prompt)        
      print(f'\n\n\n{n}. Analizando patrones cíclicos entre las fuentes de datos...')
    
    print("Enviando solicitud a la API de Gemini (esto puede tardar un momento)...")
    gem_fourier=gemini_prompt(f_system_prompt,p_6)
    
    # Only proceed with translation if we got a valid response
    if not gem_fourier.startswith("[API"):
        prompt_spanish=f'{p_sp} {gem_fourier}'
        print("Traduciendo respuesta...")
        gem_fourier_sp=gemini_prompt(f_system_prompt,prompt_spanish)
    else:
        # If there was an API error, don't try to translate the error message
        gem_fourier_sp = f"Error en el análisis: {gem_fourier}"
        
    #display(Markdown(gem_fourier_sp))
    print(gem_fourier_sp)

    n+=1
    if top_choice == 1 or top_choice == 3:
      p_conclusions = prompt_conclusions_standalone.format(all_kw=all_keywords, dbs=actual_menu, \
          temporal_trends=gem_temporal_trends, tool_relationships=gem_cross_keyword, industry_patterns=gem_industry_specific, \
          arima_predictions=gem_arima, seasonal_analysis=gem_seasonal, cyclical_patterns=gem_fourier)
    else:
      p_conclusions = prompt_conclusions_comparative.format(all_kw=actual_menu, selected_sources=sel_sources, \
          temporal_trends=gem_temporal_trends, tool_relationships=gem_cross_keyword, industry_patterns=gem_industry_specific, \
          arima_predictions=gem_arima, seasonal_analysis=gem_seasonal, cyclical_patterns=gem_fourier)          
    
    print(f'\n\n\n{n}. Sintetizando hallazgos y sacando conclusiones...')
    print("Enviando solicitud a la API de Gemini (esto puede tardar un momento)...")
    gem_conclusions=gemini_prompt(f_system_prompt,p_conclusions)
    
    # Only proceed with translation if we got a valid response
    if not gem_conclusions.startswith("[API"):
        prompt_spanish=f'{p_sp} {gem_conclusions}'
        print("Traduciendo respuesta...")
        gem_conclusions_sp=gemini_prompt(f_system_prompt,prompt_spanish)
    else:
        # If there was an API error, don't try to translate the error message
        gem_conclusions_sp = f"Error en el análisis: {gem_conclusions}"
        
    #display(Markdown(gem_conclusions_sp))
    print(gem_conclusions_sp)
    
    n+=1
    p_summary = f'{prompt_abstract} \n {gem_temporal_trends} \n {gem_cross_keyword} \n {gem_industry_specific} \
        \n {gem_arima} \n {gem_seasonal} \n {gem_fourier} \n {gem_conclusions}'      
    
    print(f'\n\n\n{n}. Generando Resumén...\n')
    print("Enviando solicitud a la API de Gemini (esto puede tardar un momento)...")
    gem_summary=gemini_prompt(f_system_prompt,p_summary)
    
    # Only proceed with translation if we got a valid response
    if not gem_summary.startswith("[API"):
        prompt_spanish=f'{p_sp} {gem_summary}'
        print("Traduciendo respuesta...")
        gem_summary_sp=gemini_prompt("",prompt_spanish)
    else:
        # If there was an API error, don't try to translate the error message
        gem_summary_sp = f"Error en el análisis: {gem_summary}"
        
    #display(Markdown(gem_conclusions_sp))
    print(gem_summary_sp)    



def csv2table(csv_data, header_line=0):
    csv_lines = csv_data.strip().split('\n')
    if not csv_lines:
        return ""
    
    headers = csv_lines[header_line].split(',')
    # Create HTML table with proper structure and CSS for page flow
    table = "<div class='table-wrapper' style='page-break-inside: auto;'>\n"
    table += "<table class='data-table' style='page-break-inside: auto; page-break-after: auto;'>\n"
    table += "<thead style='display: table-header-group;'>\n"
    table += "<tr>" + "".join([f"<th>{h}</th>" for h in headers]) + "</tr>\n"
    table += "</thead>\n"
    table += "<tbody style='display: table-row-group;'>\n"
    
    # Add data rows
    for i, line in enumerate(csv_lines):
        if i != header_line:  # Skip the header line
            values = line.split(',')
            table += "<tr style='page-break-inside: avoid; page-break-after: auto;'>" + "".join([f"<td>{v}</td>" for v in values]) + "</tr>\n"
    
    table += "</tbody>\n</table>\n</div>\n\n"
    return table
    
def report_pdf():
    global data_txt
    global charts
    global csv_means_trends
    global image_markdown
    global all_keywords
    global actual_menu
    global top_choice
    global earliest_year
    global latest_year
    global total_years
    
    # Find the cover image path from portada-combined.csv
    cover_image_path = None
    current_tool = ""
    
    # Add a boolean flag to track if the report has a cover
    has_cover = False
    
    print("\n--- DEBUG: Report PDF Cover Page Generation ---")
    
    if top_choice == 1:
        current_tool = all_keywords[0] if isinstance(all_keywords, list) and all_keywords else ""
        print(f"DEBUG: Using tool from all_keywords: '{current_tool}'")
    else:
        current_tool = actual_menu
        print(f"DEBUG: Using tool from actual_menu: '{current_tool}'")
    
    # Determine which data source we're using
    data_source_code = ""
    data_source_name = ""
    if menu == 1:
        data_source_code = "GT"  # Google Trends
        data_source_name = "Google Trends"
    elif menu == 2:
        data_source_code = "GB"  # Google Books Ngrams
        data_source_name = "Google Books Ngram"
    elif menu == 3:
        data_source_code = "BU"  # Bain - Usability
        data_source_name = "Bain & Company - Usability"
    elif menu == 4:
        data_source_code = "CR"  # Crossref.org
        data_source_name = "Crossref.org"
    elif menu == 5:
        data_source_code = "BS"  # Bain - Satisfaction
        data_source_name = "Bain & Company - Satisfaction"
    # Add other data sources as needed
    
    print(f"DEBUG: Using data source code: '{data_source_code}'")
    print(f"DEBUG: Using data source name: '{data_source_name}'")
    
    # Read the CSV file to find the cover image
    import pandas as pd
    import os
    
    # Path to the CSV file
    csv_path = 'pub-assets/portada-combined.csv'
    
    # Read the CSV file
    if os.path.exists(csv_path):
        print(f"DEBUG: CSV file exists at: {csv_path}")
        try:
            portada_df = pd.read_csv(csv_path)
            print(f"DEBUG: CSV loaded, contains {len(portada_df)} rows")
            print(f"DEBUG: CSV columns: {portada_df.columns.tolist()}")
            
            # Print a few sample tool names from CSV for verification
            sample_tools = portada_df['Herramienta'].unique()[:5].tolist()
            print(f"DEBUG: Sample tools in CSV: {sample_tools}")
            
            # Find the matching rows for the current tool
            matching_rows = portada_df[portada_df['Herramienta'] == current_tool]
            
            print(f"DEBUG: Found {len(matching_rows)} matching rows for tool: '{current_tool}'")
            
            # Get the Cod value from the matching row
            cod_value = ""
            if not matching_rows.empty:
                # Look for a row with the matching data source code
                data_source_matches = matching_rows[matching_rows['Cód'].str.endswith(data_source_code, na=False)]
                
                if not data_source_matches.empty:
                    # Get the Cod value from the first matching row
                    cod_value = data_source_matches.iloc[0]['Cód']
                    print(f"DEBUG: Found Cod value: {cod_value}")
                    # Get the file path from the first matching row with the correct data source
                    file_info = data_source_matches.iloc[0]['File']
                    cover_image_path = os.path.join('pub-assets', file_info)
                    print(f"DEBUG: Found cover image for data source '{data_source_code}': {cover_image_path}")
                    # Set has_cover to True since we found a valid cover image
                    has_cover = True
                else:
                    # If no specific match for the data source, fall back to the first matching row
                    file_info = matching_rows.iloc[0]['File']
                    cover_image_path = os.path.join('pub-assets', file_info)
                    print(f"DEBUG: No specific cover for data source '{data_source_code}', using default: {cover_image_path}")
                
                # Check if the file exists
                if not os.path.exists(cover_image_path):
                    print(f"ERROR: Cover image not found at: {cover_image_path}")
                    # Try with and without 'pub-assets' prefix
                    alt_path = file_info
                    if os.path.exists(alt_path):
                        print(f"DEBUG: Found image at alternate path: {alt_path}")
                        cover_image_path = alt_path
                        # Set has_cover to True since we found a valid cover image
                        has_cover = True
                    else:
                        print(f"ERROR: Also tried alternate path with no success: {alt_path}")
                        cover_image_path = None
                else:
                    print(f"DEBUG: Found cover image at: {cover_image_path}")
                    # Set has_cover to True since we found a valid cover image
                    has_cover = True
            else:
                print(f"WARNING: No matching tool found in CSV. Available tools: {portada_df['Herramienta'].unique().tolist()[:10]}")
        except Exception as e:
            print(f"ERROR: Error finding cover image: {str(e)}")
            import traceback
            traceback.print_exc()
    else:
        print(f"ERROR: CSV file not found at: {csv_path}")
    
    # Create data section in HTML directly (not markdown)
    data_txt = ''
    
    # We no longer need the CSS styles in data_txt since we're adding them directly to WeasyPrint
    
    data_txt += "<div class='page-break'></div>\n"
    data_txt += "<h1>Datos</h1>\n"
    if top_choice == 1:
        data_txt += "<h2>Herramientas Gerenciales:</h2>\n"
        data_txt += "<p>" + ", ".join(all_keywords) + "</p>\n"
    else:
        data_txt += "<h2>Herramientas Gerenciales:</h2>\n"
        data_txt += "<p>" + actual_menu + "</p>\n"
        data_txt += "<h3>Fuentes de Datos:</h3>\n"
        data_txt += "<p>" + ", ".join(all_keywords) + "</p>\n"
    data_txt += "\n"
    data_txt += f"<h2>Datos de {actual_menu}</h2>\n"
    
    if top_choice == 1:
        year_adjust = 0
        period = "Mensual"
        if menu == 2:
            period = "Anual"
        if total_years > 20:
            data_txt += f"<h3>{total_years} años ({period}) ({earliest_year} - {latest_year})</h3>\n"
            data_txt += csv2table(csv_all_data)
        data_txt += f"<h3>20 años ({period}) ({latest_year-20} - {latest_year})</h3>\n"
        data_txt += csv2table(csv_last_20_data)
        data_txt += f"<h3>15 años ({period}) ({latest_year-15} - {latest_year})</h3>\n"
        data_txt += csv2table(csv_last_15_data)
        data_txt += f"<h3>10 años ({period}) ({latest_year-10} - {latest_year})</h3>\n"
        data_txt += csv2table(csv_last_10_data)
        data_txt += f"<h3>5 años ({period}) ({latest_year-5} - {latest_year})</h3>\n"
        data_txt += csv2table(csv_last_5_data)
    else:
        data_txt += csv2table(csv_combined_data)     
    data_txt += "\n\n\n"
    data_txt += "<div class='page-break'></div>\n"  # Add page break here
    data_txt += "<h2>Datos Medias y Tendencias</h2>\n"
    data_txt += f"<h3>Medias y Tendencias ({latest_year-20} - {latest_year})</h3>\n"
    data_txt += csv_means_trendsA
    data_txt += csv2table(csv_means_trends)
    if not one_keyword:
        data_txt += f"<h3>Correlación</h3>\n"
        data_txt += csv2table(csv_correlation)        
        data_txt += f"<h3>Regresión</h3>\n"
        data_txt += csv2table(csv_regression)
    if not skip_arima[0]:
        data_txt += f"<h2>ARIMA</h2>\n"
        for n in range(len(csv_arimaA)):
            data_txt += csv_arimaA[n]
            data_txt += csv2table(csv_arimaB[n])
    if not skip_seasonal[0]:
        data_txt += f"<h2>Estacional</h2>\n"
        data_txt += csv2table(csv_seasonal)
    data_txt += f"<h2>Fourier</h2>\n"
    data_txt += csv2table(csv_fourier)
    data_txt += "<div class='page-break'></div>\n"  # Add another page break here
    
    # Set up years for title
    # if menu == 2:
    #     start_year = current_year-70+year_adjust
    #     end_year = current_year-year_adjust
    # elif menu == 4:
    #     start_year = current_year-74
    #     end_year = current_year
    # else:
    #     start_year = current_year-20
    #     end_year = current_year
    start_year = earliest_year
    end_year = latest_year
        
    # Generate table of contents from markdown sections
    # First, create a temporary markdown document with all the headings
    # temp_markdown = ""
    # temp_markdown += "# Resumen Ejecutivo\n"
    # temp_markdown += "# Tendencias Temporales\n"
    # if not one_keyword:
    #     temp_markdown += "# Análisis Cruzado de Palabras Clave\n"
    # temp_markdown += "# Análisis Específico de la Industria\n"
    # temp_markdown += "# Análisis ARIMA\n"
    # temp_markdown += "# Análisis Estacional\n"
    # temp_markdown += "# Análisis de Fourier\n"
    # temp_markdown += "# Conclusiones\n"
    # temp_markdown += "# Datos\n"
    
    # # Generate TOC from the temporary markdown
    # toc_html = generate_markdown_toc(temp_markdown)
    
    # Build the complete HTML document
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Análisis Estadístico de Herramientas Gerenciales</title>
        <style>
            /* Page size and margins */
            @page {{
                size: 8.5in 11in;
                margin: 1.25in;
            }}
            
            /* Base document styles */
            body {{
                font-family: "Times New Roman", Times, serif;
                font-size: 12pt;
                line-height: 1.5;
                color: #000000;
                margin: 0; /* Remove body margin since @page handles it */
                padding: 0;
                background-color: #ffffff;
                counter-reset: page 39;  /* Start at 40 (39 + 1) */
                width: 100%;
            }}

            /* Reset for title page elements */
            .title-page * {{
                margin: 0;
                padding: 0;
                position: static;
            }}
            
            /* Title page as a container */
            .title-page {{
                position: relative;
                height: 11in;
                width: 8.5in;
                padding: 0;
                margin: 0 auto;
                box-sizing: border-box;
                left: -1.25in; /* Shift left by 1.25 inches */
                top: -1.25in; /* Shift up by 1.25 inch */
                counter-increment: page 0;  /* Ensure title page doesn't increment counter */
            }}
            
            /* Title positioning */
            .title-page h1 {{
                position: absolute !important;
                top: 5in !important;
                left: 0 !important;
                width: 100% !important;
                text-align: center !important;
                font-size: 24pt !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            
            /* Subtitle positioning */
            .title-page .subtitle {{
                position: absolute !important;
                top: 5.7in !important;
                left: 0 !important;
                width: 100% !important;
                text-align: center !important;
                font-size: 14pt !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            
            /* Authors positioning */
            .title-page .authors {{
                position: absolute !important;
                bottom: 2.5in !important;
                left: 0 !important;
                width: 100% !important;
                text-align: center !important;
                font-size: 14pt !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            
            /* Date positioning */
            .title-page .date {{
                position: absolute !important;
                bottom: 1.5in !important;
                left: 0 !important;
                width: 100% !important;
                text-align: center !important;
                font-size: 12pt !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            
            /* Content sections */
            .toc, #resumen-ejecutivo, #tendencias-temporales,
            #analisis-cruzado-de-palabras-clave, #analisis-especifico-de-la-industria,
            #analisis-arima, #analisis-estacional, #analisis-de-fourier,
            #conclusiones, #graficos, #datos {{
                padding: 0;
                margin: 0;
                width: 100%;
            }}

            /* Table of contents */
            .toc {{
                margin: 2cm 0;
                counter-reset: page 5;  /* Set to 6 (5 + 1) */
                counter-increment: page 0;  /* Ensure it stays at 6 */
            }}

            .toc h2 {{
                text-align: center;
                font-size: 14pt;
                margin-bottom: 1cm;
            }}

            /* Headings */
            h1, h2, h3, h4, h5, h6 {{
                font-family: "Times New Roman", Times, serif;
                font-weight: bold;
                margin-top: 1em;
                margin-bottom: 0.5em;
            }}

            h1 {{
                font-size: 16pt;
                text-align: center;
                margin-top: 2em;
            }}

            h2 {{
                font-size: 14pt;
            }}

            h3 {{
                font-size: 12pt;
            }}

            /* Paragraphs */
            p {{
                text-align: justify;
                margin-bottom: 1em;
                width: 100%;
            }}

            /* Page numbering */
            @page {{
                @bottom-right {{
                    content: counter(page);
                }}
            }}

            /* Page breaks */
            .page-break {{
                page-break-after: always;
                counter-increment: page;
                height: 0;
                display: block;
            }}

            /* Reset page counter for main content */
            #resumen-ejecutivo {{
                counter-reset: page 39;  /* Start at 40 (39 + 1) */
            }}

            /* Set TOC page number */
            .toc {{
                counter-reset: page 5;  /* Set to 6 (5 + 1) */
                counter-increment: page 0;  /* Ensure it stays at 6 */
            }}

            /* Tables */
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 1.5em 0;
                page-break-inside: avoid;
                font-size: 9px;  /* Added this line to make all tables have smaller font */
            }}

            th, td {{
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }}

            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}

            .table-wrapper {{
                width: 100%;
                max-width: none;
                overflow-x: auto;
                margin-bottom: 1em;
                padding: 0;
            }}

            .data-table {{
                font-size: 10pt;
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
            }}

            .data-table th {{
                padding: 5px 2px;
                vertical-align: bottom;
                text-align: left;
                font-size: 10pt;
                /* Change white-space to normal to allow wrapping */
                white-space: normal;
                /* Add word-wrap for better control */
                word-wrap: break-word;
                /* Optional: add a max height if needed */
                max-height: 50px;
            }}

            .data-table td {{
                padding: 5px 2px;
                font-size: 9pt;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}

            /* Table captions */
            .table-caption {{
                font-style: italic;
                text-align: center;
                margin-top: 0.5em;
                caption-side: bottom;
                font-size: 10pt;
            }}

            /* Figures and images */
            figure {{
                text-align: center;
                margin: 1.5em 0;
                page-break-inside: avoid;
            }}

            img {{
                max-width: 100%;
                height: auto;
                display: block;
                margin: 1.5em auto;
                page-break-inside: avoid;
            }}

            figcaption {{
                font-style: italic;
                text-align: center;
                margin-top: 0.5em;
                font-size: 10pt;
            }}

            /* Abstract section */
            .abstract {{
                margin: 2em 0;
                font-size: 11pt;
            }}

            .abstract h2 {{
                text-align: center;
                font-size: 12pt;
                font-weight: bold;
            }}

            .abstract p {{
                text-align: justify;
            }}

            /* References and citations */
            .references {{
                margin-top: 2em;
            }}

            .references h2 {{
                text-align: center;
            }}

            .references ol {{
                padding-left: 1em;
            }}

            .references li {{
                text-indent: -1em;
                padding-left: 1em;
                margin-bottom: 0.5em;
            }}

            /* Footer */
            .footer {{
                margin-top: 2em;
                border-top: 1px solid #000;
                padding-top: 1em;
                font-size: 9pt;
            }}

            /* Print-specific styles */
            @media print {{
                body {{
                    font-size: 12pt;
                }}
                
                a {{
                    text-decoration: none;
                    color: #000000;
                }}
                
                .table-wrapper {{
                    overflow-x: visible;
                }}
                
                .data-table {{
                    font-size: 9pt;
                    page-break-inside: avoid;
                }}
                
                img {{
                    max-width: 100% !important;
                }}
                
                h1, h2, h3, h4, h5, h6 {{
                    page-break-after: avoid;
                    page-break-inside: avoid;
                }}
                
                p {{
                    orphans: 3;
                    widows: 3;
                }}
            }}
        </style>
    </head>
    <body>
"""

    # Only include the title page if has_cover is False
    if not has_cover:
        html_content += f"""
        <!-- Title Page -->
        <div class="title-page">
            <h1>Análisis de {', '.join(all_keywords)}</h1>
            <div class="subtitle">({actual_menu}) ({str(start_year)} - {str(end_year)})</div>
            <div class="authors">Diomar Anez & Dimar Anez</div>
            <div class="date">{datetime.now().strftime("%d de %B de %Y")}</div>
        </div>
        <div class="page-break"></div>
"""
    else:
        html_content += f"""
"""

    # Continue with the rest of the HTML content
    html_content += f"""
        <!-- Main Content - Convert markdown sections to HTML -->
        <div class="main-content">
            <div id="resumen-ejecutivo" style="counter-reset: page 32;">
                <h1>Resumen Ejecutivo</h1>
                {markdown.markdown(gem_summary_sp, extensions=["tables"])}
            </div>
            <div class="page-break"></div>
            
            <div id="tendencias-temporales">
                <h1>Tendencias Temporales</h1>
                {markdown.markdown(gem_temporal_trends_sp, extensions=["tables"])}
            </div>
            <div class="page-break"></div>
            """
    
    if not one_keyword:
        html_content += f"""
        <div id="analisis-cruzado-de-palabras-clave">
            <h1>Análisis Cruzado de Palabras Clave</h1>
            {markdown.markdown(gem_cross_keyword_sp, extensions=["tables"])}
        </div>
        <div class="page-break"></div>
        """
    
    html_content += f"""
        <div id="tendencias-generales-y-contextuales">
            <h1>Tendencias Generales y Contextuales</h1>
            {markdown.markdown(gem_industry_specific_sp, extensions=["tables"])}
        </div>
        <div class="page-break"></div>
        """
        
    if skip_arima[0]==False:
        html_content += f"""
        <div id="analisis-arima">
            <h1>Análisis ARIMA</h1>
            {markdown.markdown(gem_arima_sp, extensions=["tables"])}
        </div>
        <div class="page-break"></div>
        """
        
    if skip_seasonal[0]==False:
        html_content += f"""
        <div id="analisis-estacional">
            <h1>Análisis Estacional</h1>
            {markdown.markdown(gem_seasonal_sp, extensions=["tables"])}
        </div>
        <div class="page-break"></div>
        """
    
    html_content += f"""            
        <div id="analisis-de-fourier">
            <h1>Análisis de Fourier</h1>
            {markdown.markdown(gem_fourier_sp, extensions=["tables"])}
        </div>
        <div class="page-break"></div>
        
        <div id="conclusiones">
            <h1>Conclusiones</h1>
            {markdown.markdown(gem_conclusions_sp, extensions=["tables"])}
        </div>
        <div class="page-break"></div>
        
        <!-- Anexos Page -->
        <div class="title-page">
            <h1>ANEXOS</h1>
            <div class="subtitle">* Gráficos *</br>* Datos *</div>
        </div>
        <div class="page-break"></div>
        
        <!-- Images -->
        <div id="graficos">
            <h1>Gráficos</h1>
            {image_markdown}
        </div>
        
        <!-- Data Section -->
        <div id="datos">
            {data_txt}
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <p>(c) 2024 - {current_year} Diomar Anez & Dimar Anez</p>
            <p>Contacto: <a href="https://www.solidum360.com">SOLIDUM</a> & <a href="https://www.wiseconnex.com">WISE CONNEX</a></p>
            <p>Todas las librerías utilizadas están bajo la debida licencia de sus autores y dueños de los derechos de autor. 
            Algunas secciones de este reporte fueron generadas con la asistencia de Gemini AI. 
            Este reporte está licenciado bajo la Licencia MIT. Para obtener más información, consulta <a href="https://opensource.org/licenses/MIT/">https://opensource.org/licenses/MIT/</a></p>
            <p>Reporte generado el {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
    </body>
    </html>
    """

    # No need to replace page breaks or add them after figures since we're now using proper HTML structure
    
    pdf_path = os.path.join(unique_folder, f'{filename}.pdf')
    content_pdf_path = os.path.join(unique_folder, f'{filename}_content.pdf')
    print(f"Saving PDF to: {pdf_path}")
    print(f"Number of figures in report: {html_content.count('<figure>')}")
    
    # Create custom CSS for page size and margins
    from weasyprint import HTML, CSS
    
    # CSS for content pages only (no cover page)
    content_css = CSS(string=f'''
        /* Regular pages */
        @page {{
            size: 8.5in 11in;
            margin: 0.75in;
            @top-left {{ 
                content: "{data_source_name}"; 
                font-size: 8pt;
            }}
            @top-right {{ 
                content: "{cod_value}"; 
                font-size: 8pt;
            }}
            @bottom-right {{ 
                content: "Página " counter(page) ""; 
                font-size: 8pt;
            }}
            @bottom-left {{ 
                content: "{current_tool}"; 
                font-size: 8pt;
                font-style: italic;
            }}
        }}
        
        /* Base document styles */
        body {{
            font-family: "Times New Roman", Times, serif;
            font-size: 12pt;
            line-height: 1.5;
            color: #000000;
            margin: 0;
            padding: 0;
            background-color: #ffffff;
            width: 100%;
        }}

        /* Page numbering */
        @page :first {{
            counter-reset: page 40;  /* Start at 40 */
        }}

        /* Page breaks */
        .page-break {{
            page-break-after: always;
            counter-increment: page;
            height: 0;
            display: block;
        }}

        /* Title page */
        .title-page {{
            counter-increment: none;
        }}

        /* Table of contents */
        .toc {{
            counter-reset: page 5;  /* Set to 6 (5 + 1) */
            counter-increment: none;
        }}

        /* Main content */
        #resumen-ejecutivo {{
            counter-reset: page 39;  /* Start at 40 (39 + 1) */
        }}

        /* Tables */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1.5em 0;
            page-break-inside: avoid;
        }}

        th, td {{
            border: 1px solid black;
            padding: 8px;
            text-align: left;
        }}

        th {{
            background-color: #f2f2f2;
            font-weight: bold;
        }}

        .table-wrapper {{
            width: 100%;
            max-width: none;
            overflow-x: auto;
            margin-bottom: 1em;
            padding: 0;
        }}

        .data-table {{
            font-size: 10pt;
            width: 100%;
            border-collapse: collapse;
            table-layout: fixed;
        }}

        .data-table th {{
            padding: 5px 2px;
            vertical-align: bottom;
            text-align: left;
            font-size: 10pt;
            white-space: normal;
            word-wrap: break-word;
            max-height: 50px;
        }}

        .data-table td {{
            padding: 5px 2px;
            font-size: 9pt;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        /* Table captions */
        .table-caption {{
            font-style: italic;
            text-align: center;
            margin-top: 0.5em;
            caption-side: bottom;
            font-size: 10pt;
        }}

        /* Figures and images */
        figure {{
            text-align: center;
            margin: 1.5em 0;
            page-break-inside: avoid;
        }}

        img {{
            max-width: 100%;
            height: auto;
            display: block;
            margin: 1.5em auto;
            page-break-inside: avoid;
        }}

        figcaption {{
            font-style: italic;
            text-align: center;
            margin-top: 0.5em;
            font-size: 10pt;
        }}

        /* Footer */
        .footer {{
            margin-top: 2em;
            border-top: 1px solid #000;
            padding-top: 1em;
            font-size: 9pt;
        }}

        /* Print-specific styles */
        @media print {{
            body {{
                font-size: 12pt;
            }}
            
            a {{
                text-decoration: none;
                color: #000000;
            }}
            
            .table-wrapper {{
                overflow-x: visible;
            }}
            
            .data-table {{
                font-size: 9pt;
                page-break-inside: avoid;
            }}
            
            img {{
                max-width: 100% !important;
            }}
            
            h1, h2, h3, h4, h5, h6 {{
                page-break-after: avoid;
                page-break-inside: avoid;
            }}
            
            p {{
                orphans: 3;
                widows: 3;
            }}
        }}
    ''')
    
    print(f"DEBUG: About to generate content PDF with WeasyPrint")
    
    # First generate the content PDF without cover
    HTML(string=html_content).write_pdf(content_pdf_path, stylesheets=[content_css])
    print(f"DEBUG: Content PDF generated at: {content_pdf_path}")
    
    # Generate a PDF with TOC based on the content PDF
    content_with_toc_path = os.path.join(unique_folder, f'{filename}_with_toc.pdf')
    try:
        print(f"DEBUG: Generating TOC from content PDF")
        generate_pdf_toc(content_pdf_path, content_with_toc_path, has_cover)
        # If successful, use the content with TOC
        if os.path.exists(content_with_toc_path):
            print(f"DEBUG: Successfully generated PDF with TOC")
            # Remove the original content PDF and use the one with TOC
            os.remove(content_pdf_path)
            content_pdf_path = content_with_toc_path
    except Exception as e:
        print(f"ERROR: Failed to generate TOC: {str(e)}")
        import traceback
        traceback.print_exc()
        # Continue with the original content PDF if TOC generation fails
        print(f"DEBUG: Continuing with original content PDF without dynamic TOC")
    
    # Now create a separate cover PDF and merge them
    if cover_image_path:
        print(f"DEBUG: Creating cover PDF with image: {cover_image_path}")
        # Check if image exists and is accessible
        if os.path.exists(cover_image_path) and os.access(cover_image_path, os.R_OK):
            try:
                # Import necessary libraries for PDF manipulation
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import letter
                from PyPDF2 import PdfReader, PdfWriter
                import io
                
                # Create a PDF with just the cover image
                cover_pdf_buffer = io.BytesIO()
                c = canvas.Canvas(cover_pdf_buffer, pagesize=letter)
                
                # Draw the image at full page size without margins
                c.drawImage(cover_image_path, 0, 0, width=8.5*72, height=11*72)
                c.save()
                
                print(f"DEBUG: Cover PDF created in memory")
                
                # Merge the cover with content PDF
                cover_pdf = PdfReader(io.BytesIO(cover_pdf_buffer.getvalue()))
                content_pdf = PdfReader(content_pdf_path)
                
                output = PdfWriter()
                
                # Add cover page first
                output.add_page(cover_pdf.pages[0])
                print(f"DEBUG: Added cover page to output PDF")
                
                # Set the flag to indicate the report has a cover
                has_cover = True
                
                # If we have a cover, look for the intro PDF to add after the cover
                if has_cover and 'cod_value' in locals():
                    # Construct the path to the intro PDF using the report code
                    intro_pdf_path = os.path.join('pub-assets', 'Intro-A', f'{cod_value}-INTRO-A.pdf')
                    print(f"DEBUG: Looking for intro PDF: {intro_pdf_path}")
                    
                    # Check if the intro PDF exists and is accessible
                    if os.path.exists(intro_pdf_path) and os.access(intro_pdf_path, os.R_OK):
                        try:
                            # Open the intro PDF
                            intro_pdf = PdfReader(intro_pdf_path)
                            
                            # Add all pages from the intro PDF
                            for page in intro_pdf.pages:
                                output.add_page(page)
                                
                            print(f"DEBUG: Successfully added intro PDF: {intro_pdf_path} ({len(intro_pdf.pages)} pages)")
                        except Exception as e:
                            print(f"ERROR: Failed to add intro PDF: {str(e)}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print(f"WARNING: Intro PDF not found or not accessible: {intro_pdf_path}")
                
                # If we have a TOC, add it after the cover (and intro if present) but before the content
                if os.path.exists(content_with_toc_path):
                    # The content_pdf already has the TOC at the beginning, so we need to:
                    # 1. Extract just the TOC pages (typically just 1 page)
                    # 2. Then add the content pages separately
                    
                    # Determine how many pages are in the TOC
                    # We'll assume the first 1-2 pages are TOC (adjust if needed)
                    toc_page_count = 1  # Default to 1 page for TOC
                    
                    # Add TOC pages after cover
                    toc_pdf = PdfReader(content_with_toc_path)
                    for i in range(min(toc_page_count, len(toc_pdf.pages))):
                        output.add_page(toc_pdf.pages[i])
                    print(f"DEBUG: Added {toc_page_count} TOC pages after cover")
                    
                    # After TOC is added, look for the intro-B PDF to add after the TOC
                    if has_cover and 'cod_value' in locals():
                        # Construct the path to the intro-B PDF using the report code
                        intro_b_pdf_path = os.path.join('pub-assets', 'Intro-B', f'{cod_value}-INTRO-B.pdf')
                        print(f"DEBUG: Looking for intro-B PDF: {intro_b_pdf_path}")
                        
                        # Check if the intro-B PDF exists and is accessible
                        if os.path.exists(intro_b_pdf_path) and os.access(intro_b_pdf_path, os.R_OK):
                            try:
                                # Open the intro-B PDF
                                intro_b_pdf = PdfReader(intro_b_pdf_path)
                                
                                # Add all pages from the intro-B PDF
                                for page in intro_b_pdf.pages:
                                    output.add_page(page)
                                    
                                print(f"DEBUG: Successfully added intro-B PDF: {intro_b_pdf_path} ({len(intro_b_pdf.pages)} pages)")
                            except Exception as e:
                                print(f"ERROR: Failed to add intro-B PDF: {str(e)}")
                                import traceback
                                traceback.print_exc()
                        else:
                            print(f"WARNING: Intro-B PDF not found or not accessible: {intro_b_pdf_path}")
                    
                    # Add content pages (skipping TOC pages)
                    for i in range(toc_page_count, len(content_pdf.pages)):
                        output.add_page(content_pdf.pages[i])
                    print(f"DEBUG: Added {len(content_pdf.pages) - toc_page_count} content pages")
                else:
                    # No TOC was generated
                    
                    # Even without TOC, look for the intro-B PDF to add before content
                    if has_cover and 'cod_value' in locals():
                        # Construct the path to the intro-B PDF using the report code
                        intro_b_pdf_path = os.path.join('pub-assets', 'Intro-B', f'{cod_value}-INTRO-B.pdf')
                        print(f"DEBUG: Looking for intro-B PDF (no TOC case): {intro_b_pdf_path}")
                        
                        # Check if the intro-B PDF exists and is accessible
                        if os.path.exists(intro_b_pdf_path) and os.access(intro_b_pdf_path, os.R_OK):
                            try:
                                # Open the intro-B PDF
                                intro_b_pdf = PdfReader(intro_b_pdf_path)
                                
                                # Add all pages from the intro-B PDF
                                for page in intro_b_pdf.pages:
                                    output.add_page(page)
                                    
                                print(f"DEBUG: Successfully added intro-B PDF: {intro_b_pdf_path} ({len(intro_b_pdf.pages)} pages)")
                            except Exception as e:
                                print(f"ERROR: Failed to add intro-B PDF: {str(e)}")
                                import traceback
                                traceback.print_exc()
                        else:
                            print(f"WARNING: Intro-B PDF not found or not accessible: {intro_b_pdf_path}")
                    
                    # Add all content pages
                    for page in content_pdf.pages:
                        output.add_page(page)
                    print(f"DEBUG: Added {len(content_pdf.pages)} content pages (no TOC)")
                
                # If we have a cover, extract data source code and append back PDF
                if has_cover:
                    # Use the data_source_code that's already defined in the function
                    # (no need to extract it from the cover filename)
                    
                    # Correct path for back PDF files (using relative path)
                    back_pdf_path = os.path.join('pub-assets/Back', f"{data_source_code}-BACK.pdf")
                    
                    print(f"DEBUG: Looking for back PDF: {back_pdf_path}")
                    
                    if os.path.exists(back_pdf_path) and os.access(back_pdf_path, os.R_OK):
                        try:
                            # Open the back PDF
                            back_pdf = PdfReader(back_pdf_path)
                            
                            # Add all pages from the back PDF
                            for page in back_pdf.pages:
                                output.add_page(page)
                                
                            print(f"DEBUG: Successfully added back PDF: {back_pdf_path}")
                        except Exception as e:
                            print(f"ERROR: Failed to add back PDF: {str(e)}")
                    else:
                        print(f"WARNING: Back PDF not found or not accessible: {back_pdf_path}")
                
                # Write the final PDF
                with open(pdf_path, "wb") as output_stream:
                    output.write(output_stream)
                
                print(f"DEBUG: Final merged PDF saved to: {pdf_path}")
                
                # Remove the temporary content PDF
                if os.path.exists(content_pdf_path):
                    os.remove(content_pdf_path)
                    print(f"DEBUG: Removed temporary content PDF")
                
            except Exception as e:
                print(f"ERROR: Failed to create cover PDF: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # If merging fails, just use the content PDF
                if os.path.exists(content_pdf_path):
                    import shutil
                    shutil.move(content_pdf_path, pdf_path)
                    print(f"DEBUG: Fallback - using content PDF as final output")
        else:
            print(f"ERROR: Cover image exists but cannot be read or accessed: {cover_image_path}")
            # If cover image is inaccessible, just use the content PDF
            if os.path.exists(content_pdf_path):
                import shutil
                shutil.move(content_pdf_path, pdf_path)
                print(f"DEBUG: Fallback - using content PDF as final output")
    else:
        print("DEBUG: No cover image to add, using content PDF as final output")
        # If no cover image, just rename the content PDF
        if os.path.exists(content_pdf_path):
            import shutil
            shutil.move(content_pdf_path, pdf_path)
    
    char='*'
    title='********** ' + filename + ' PDF REPORT SAVED **********'
    qty=len(title)
    print(f'\x1b[33m\n\n{char*qty}\n{title}\n{char*qty}\x1b[0m')

def top_level_menu():
    print("\n\n\n\n\n\n\n\n")
    banner_msg(" Análisis de Herramientas Gerenciales ", YELLOW, GREEN, char = '-', margin = 24)
    print('\n')
    banner_msg(" Menú Principal ", YELLOW, WHITE)
    options = {
        1: "Generar Informe Individual",
        2: "Comparar Herramienta de Gestión entre Fuentes de Datos",
        # Change option 3 text
        3: "Generar TODOS los Informes Individuales (Batch)",
        4: "Salir"
    }
    for index, option in enumerate(options.values(), 1):
        print(f"{index}. {option}")
    while True:
        selection = input("\nIngrese el número de la opción a seleccionar: ")
        try:
            index = int(selection)
            if 1 <= index <= len(options):
                return index
            else:
                print(f"{RED}Opción inválida.{RESET}")
        except ValueError:
            print(f"{YELLOW}Por favor, ingrese un número válido.{RESET}")

def generate_pdf_toc(input_pdf_path, output_pdf_path, has_cover=False):
    """Generate a table of contents for a PDF and add it to the beginning of the document.
    
    Args:
        input_pdf_path (str): Path to the input PDF file
        output_pdf_path (str): Path where the output PDF will be saved
        has_cover (bool): Whether the document has a cover page
    """
    try:
        print(f"Attempting to generate TOC for {input_pdf_path}")
        
        # Check if the input PDF exists
        if not os.path.exists(input_pdf_path):
            print(f"Error: Input PDF {input_pdf_path} does not exist")
            return False
            
        # Import PyPDF2 with compatibility for different versions
        try:
            from PyPDF2 import PdfReader, PdfWriter
        except ImportError:
            from PyPDF2 import PdfFileReader as PdfReader, PdfFileWriter as PdfWriter
            
        # Read the input PDF
        reader = PdfReader(input_pdf_path)
        writer = PdfWriter()
        
        # Extract text from each page to find headings
        headings = []
        
        # Define main section patterns with word boundaries to avoid partial matches
        main_sections = [
            (re.compile(r'(?:^|\n)(?:\s*)(Resumen Ejecutivo)(?:\s*$|\s+)', re.IGNORECASE), 1),
            (re.compile(r'(?:^|\n)(?:\s*)(Tendencias Temporales)(?:\s*$|\s+)', re.IGNORECASE), 1),
            (re.compile(r'(?:^|\n)(?:\s*)(Análisis Cruzado de Palabras Clave)(?:\s*$|\s+)', re.IGNORECASE), 1),
            (re.compile(r'(?:^|\n)(?:\s*)(Análisis Específico de la Industria)(?:\s*$|\s+)', re.IGNORECASE), 1),
            (re.compile(r'(?:^|\n)(?:\s*)(Análisis ARIMA)(?:\s*$|\s+)', re.IGNORECASE), 1),
            (re.compile(r'(?:^|\n)(?:\s*)(Análisis Estacional)(?:\s*$|\s+)', re.IGNORECASE), 1),
            (re.compile(r'(?:^|\n)(?:\s*)(Análisis de Fourier)(?:\s*$|\s+)', re.IGNORECASE), 1),
            (re.compile(r'(?:^|\n)(?:\s*)(Conclusiones)(?:\s*$|\s+)', re.IGNORECASE), 1),
            (re.compile(r'(?:^|\n)(?:\s*)(Gráficos)(?:\s*$|\s+)', re.IGNORECASE), 1),
            (re.compile(r'(?:^|\n)(?:\s*)(Datos)(?:\s*$|\s+)', re.IGNORECASE), 1)
        ]
        
        print(f"PDF has {len(reader.pages)} pages")
        
        # First pass: Find main sections only
        main_section_headings = []
        current_page = 0
        
        for i, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if not text:
                    continue
                    
                # Only check for main sections in this pass
                for pattern, level in main_sections:
                    matches = pattern.findall(text)
                    for match in matches:
                        # Clean up the heading text
                        heading_text = match.strip()
                        # Only add if it's a significant heading (not just a word)
                        if len(heading_text) > 3:
                            main_section_headings.append((level, heading_text, i + 1))
                            print(f"Found main section: '{heading_text}' on page {i + 1}")
                
            except Exception as e:
                print(f"Error extracting text from page {i+1}: {str(e)}")
        
        # Filter to keep only desired sections
        filtered_main_sections = []
        seen_sections = set()
        datos_sections = []
        conclusiones_sections = []

        # Process main sections to keep only first occurrence of each (except Datos and Conclusiones)
        for level, title, page_num in main_section_headings:
            normalized_title = ' '.join(word.capitalize() for word in title.split())
            
            # Handle "Datos" separately - collect all instances
            if normalized_title.lower() == "datos":
                datos_sections.append((level, normalized_title, page_num))
                continue
                
            # Handle "Conclusiones" separately - collect all instances
            if normalized_title.lower() == "conclusiones":
                conclusiones_sections.append((level, normalized_title, page_num))
                continue
                
            # For other sections, keep only first occurrence
            if normalized_title.lower() not in seen_sections:
                seen_sections.add(normalized_title.lower())
                filtered_main_sections.append((level, normalized_title, page_num))

        # Add only the last occurrence of "Conclusiones" if it exists
        if conclusiones_sections:
            # Sort by page number and take the last one
            conclusiones_sections.sort(key=lambda x: x[2])
            filtered_main_sections.append(conclusiones_sections[-1])

        # Add only the last occurrence of "Datos" if it exists
        if datos_sections:
            # Sort by page number and take the last one
            datos_sections.sort(key=lambda x: x[2])
            filtered_main_sections.append(datos_sections[-1])

        # Sort all sections by page number
        filtered_main_sections.sort(key=lambda x: x[2])

        # Replace main_section_headings with our filtered list
        main_section_headings = filtered_main_sections
        
        # Use only main sections for the final TOC (no subsections)
        final_headings = main_section_headings
        
        print(f"Found {len(main_section_headings)} main sections (no subsections included)")
        
        # If no headings found, create default TOC entries
        if not final_headings:
            print("Warning: No headings found in the document. Creating default TOC entries.")
            final_headings = [
                (1, "Resumen Ejecutivo", 33),  # Start at page 33
                (1, "Tendencias Temporales", 35),
                (1, "Análisis Cruzado", 40),
                (1, "Análisis ARIMA", 45),
                (1, "Análisis Estacional", 50),
                (1, "Análisis de Fourier", 55),
                (1, "Conclusiones", 60),
                (1, "Gráficos", 65),
                (1, "Datos", 70)
            ]
        else:
            # Adjust all page numbers to start at 40
            adjusted_headings = []
            for level, title, page_num in final_headings:
                adjusted_headings.append((level, title, page_num + 39))  # Add 39 to start at 40
            final_headings = adjusted_headings

        # Create a TOC page with text in left column and page numbers in right column
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_LEFT, TA_RIGHT
        from reportlab.lib import colors
        from io import BytesIO

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=72, rightMargin=72, topMargin=72, bottomMargin=72)
        styles = getSampleStyleSheet()

        # Create custom styles for TOC
        title_style = ParagraphStyle(
            'TOCTitle',
            parent=styles['Heading1'],
            fontName='Times-Roman',
            fontSize=16,
            leading=20,
            alignment=TA_LEFT,
            spaceAfter=20
        )

        # Style for the TOC entry text
        entry_text_style = ParagraphStyle(
            'TOCEntryText',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=12,
            leading=16,
            alignment=TA_LEFT
        )

        # Style for the page numbers (right-aligned)
        page_num_style = ParagraphStyle(
            'TOCPageNum',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=12,
            leading=16,
            alignment=TA_RIGHT
        )

        # Create flowables for the TOC
        flowables = []

        # Add TOC title
        flowables.append(Paragraph("Tabla de Contenido", title_style))
        flowables.append(Spacer(1, 20))

        # Create table data for two-column layout (text and page number)
        table_data = []
        
        # Add the new items at the beginning of the TOC only if there is a cover
        if has_cover:
            table_data.extend([
                [Paragraph("Marco conceptual y metodológico", entry_text_style),
                 Paragraph("7", page_num_style)],
                [Paragraph("Alcances metodológicos del análisis", entry_text_style),
                 Paragraph("16", page_num_style)],
                [Paragraph("Base de datos analizada en el informe técnico", entry_text_style),
                 Paragraph("31", page_num_style)],
                [Paragraph("Grupo de herramientas analizadas: informe técnico", entry_text_style),
                 Paragraph("34", page_num_style)],
                [Paragraph("Parametrización para el análisis y extracción de datos", entry_text_style),
                 Paragraph("37", page_num_style)]
            ])

        # Add each TOC entry as a row in the table
        for level, title, page_num in final_headings:
            # No indentation needed since we only have main sections
            table_data.append([
                Paragraph(f"{title}", entry_text_style),
                Paragraph(f"{page_num}", page_num_style)
            ])

        # Create the table with appropriate column widths
        col_widths = ['85%', '15%']  # Adjust as needed
        toc_table = Table(table_data, colWidths=col_widths)

        # Add table style with dotted leader between text and page number
        table_style = TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            # Optional: Add dotted leader line
            ('LINEBELOW', (0, 0), (0, -1), 0.5, colors.gray, 1, (1, 2))
        ])

        toc_table.setStyle(table_style)
        flowables.append(toc_table)

        # Build the TOC PDF
        doc.build(flowables)
        
        # Get the PDF content from the buffer
        buffer.seek(0)
        toc_pdf = PdfReader(buffer)
        
        # Add TOC to the beginning of the document
        for i in range(len(toc_pdf.pages)):
            writer.add_page(toc_pdf.pages[i])
        
        # Add the original content
        for i in range(len(reader.pages)):
            writer.add_page(reader.pages[i])
        
        # Write the output PDF
        with open(output_pdf_path, 'wb') as output_file:
            writer.write(output_file)
            
        print(f"Successfully created TOC and saved to {output_pdf_path}")
        return True
        
    except Exception as e:
        print(f"Error generating TOC: {str(e)}")
        return False

def get_all_keywords():
    all_keywords = []
    for tool_list in tool_file_dic.values():
        for keyword in tool_list[1]:
            if keyword not in all_keywords:
                all_keywords.append(keyword)
    return all_keywords

def select_multiple_data_sources():
    global dbase_options
    
    banner_msg(" Fuentes de Datos Disponibles ", YELLOW, WHITE)
    for index, option in enumerate(dbase_options.values(), 1):
        print(f"{index}. {option}")
    
    selected_sources = []
    while True:
        selection = input("\nIngrese los números de las fuentes de datos a comparar (separados por comas), o ENTER para continuar: ")
        if selection.lower() == '':
            if not selected_sources:
                print(f"{YELLOW}Por favor, seleccione al menos una fuente de datos antes de terminar.{RESET}")
            else:
                break
        else:
            try:
                indices = [int(i.strip()) for i in selection.split(',')]
                valid_indices = []
                for index in indices:
                    if 1 <= index <= len(dbase_options):
                        if index not in selected_sources:
                            selected_sources.append(index)
                            valid_indices.append(index)
                        else:
                            print(f"{YELLOW}La fuente de datos {index} ya ha sido seleccionada.{RESET}")
                    else:
                        print(f"{RED}Selección inválida: {index}. Por favor, ingrese números entre 1 y {len(dbase_options)}.{RESET}")
                
                if valid_indices:
                    # Fixed f-string formatting
                    added_sources = [dbase_options[i] for i in valid_indices]
                    print("\nFuentes de datos añadidas:")
                    for source in added_sources:
                        print(f"- {source}")
                    print()
                
                # Show currently selected sources
                current_sources = [dbase_options[i] for i in selected_sources]
                print("Actualmente seleccionadas:")
                for source in current_sources:
                    print(f"- {source}")
                print()
            except ValueError:
                print(f"{RED}Entrada inválida. Por favor, ingrese números separados por comas o 'listo'.{RESET}")
    
    return selected_sources

def get_filenames_for_keyword(keyword, selected_sources):
    filenames = {}
    source_index_map = {1: 0, 2: 2, 3: 3, 4: 4, 5: 5}
    
    for source in selected_sources:
        index = source_index_map[source]
        for key, value in tool_file_dic.items():
            if keyword in value[1]:
                filenames[source] = value[index]
                break
    
    return filenames

def process_dataset(df, source, all_datasets, selected_sources):
    """
    Process dataset based on source type and selected sources.
    When GB is selected, converts monthly data to annual format.
    For Bain data, preserves annual values when GB is selected.
    
    Args:
        df (pd.DataFrame): Input dataset
        source (int): Source identifier
        all_datasets (dict): Dictionary of all datasets
        selected_sources (list): List of selected source identifiers
    
    Returns:
        pd.DataFrame: Processed dataset
    """
    global earliest_date
    global latest_date
    
    print(f"\nProcessing dataset for source {source}")
    print(f"Input shape: {df.shape}")
    print(f"Input frequency: {df.index.freq}")
    
    # Ensure the index is datetime and timezone-naive
    df.index = pd.to_datetime(df.index).tz_localize(None)
    
    # Find the common date range across all datasets
    earliest_date = max(df.index.min() for df in all_datasets.values())
    latest_date = min(df.index.max() for df in all_datasets.values())
    print(f"Common date range: {earliest_date} to {latest_date}")

    # Check if Google Books is selected
    is_annual_mode = 2 in selected_sources
    
    if is_annual_mode:
        # Handle different sources in annual mode
        if source == 2:  # Google Books
            # GB data is already annual, just trim to common date range
            df_resampled = df.loc[earliest_date:latest_date]
            
        elif source in [3, 5]:  # Bain (Usability & Satisfaction)
            # For Bain data, keep only the first month of each year as it represents the annual value
            df['year'] = df.index.year
            df_resampled = df.groupby('year').first()
            df_resampled.index = pd.to_datetime(df_resampled.index, format='%Y')
            df_resampled = df_resampled.loc[earliest_date:latest_date]
            
        elif source == 4:  # Crossref
            # Convert Crossref data to annual by taking the mean
            df = df.apply(pd.to_numeric, errors='coerce')
            df_resampled = df.resample('Y').mean()
            df_resampled.index = pd.to_datetime(df_resampled.index.strftime('%Y-01-01'))
            df_resampled = df_resampled.loc[earliest_date:latest_date]
            
        elif source == 1:  # Google Trends
            # Convert GT data to annual by taking the mean
            df_resampled = df.resample('Y').mean()
            df_resampled.index = pd.to_datetime(df_resampled.index.strftime('%Y-01-01'))
            df_resampled = df_resampled.loc[earliest_date:latest_date]
            
        else:
            df_resampled = df.copy()
            
    else:
        # For monthly data, simply trim to the common date range
        df_resampled = df.loc[earliest_date:latest_date]
    
    df_resampled_monthly = df.loc[earliest_date:latest_date]
    
    print(f"Final dataframe shape: {df_resampled.shape}")
    print(f"Final dataframe head:\n{df_resampled.head()}")
    print(f"Final frequency: {df_resampled.index.freq}")
    
    return df_resampled, df_resampled_monthly

def process_dataset_full(df, source, selected_sources):
    """
    Process dataset without trimming to common date range.
    Similar to process_dataset but preserves all dates.
    
    Args:
        df (pd.DataFrame): Input dataset
        source (int): Source identifier
        selected_sources (list): List of selected source identifiers
    
    Returns:
        pd.DataFrame: Processed dataset with all original dates
    """
    print(f"\nProcessing full dataset for source {source}")
    print(f"Input shape: {df.shape}")
    print(f"Input frequency: {df.index.freq}")
    
    # Ensure the index is datetime and timezone-naive
    df.index = pd.to_datetime(df.index).tz_localize(None)
    
    # Check if Google Books is selected
    is_annual_mode = 2 in selected_sources
    
    if is_annual_mode:
        # Handle different sources in annual mode
        if source == 2:  # Google Books
            # GB data is already annual, no need to resample
            df_resampled = df.copy()
            
        elif source in [3, 5]:  # Bain (Usability & Satisfaction)
            # For Bain data, keep only the first month of each year as it represents the annual value
            df['year'] = df.index.year
            df_resampled = df.groupby('year').first()
            df_resampled.index = pd.to_datetime(df_resampled.index, format='%Y')
            
        elif source == 4:  # Crossref
            # Convert Crossref data to annual by taking the mean
            df = df.apply(pd.to_numeric, errors='coerce')
            df_resampled = df.resample('Y').mean()
            df_resampled.index = pd.to_datetime(df_resampled.index.strftime('%Y-01-01'))
            
        elif source == 1:  # Google Trends
            # Convert GT data to annual by taking the mean
            df_resampled = df.resample('Y').mean()
            df_resampled.index = pd.to_datetime(df_resampled.index.strftime('%Y-01-01'))
            
        else:
            df_resampled = df.copy()
            
    else:
        # For monthly data, keep as is
        df_resampled = df.copy()

    df_resampled_monthly = df.copy()
    
    print(f"Final full dataframe shape: {df_resampled.shape}")
    print(f"Final full dataframe head:\n{df_resampled.head()}")
    print(f"Final frequency: {df_resampled.index.freq}")
    
    return df_resampled, df_resampled_monthly

def normalize_dataset(df):
    """
    Normalize dataset values to a 0-100 scale.
    
    Args:
        df (pd.DataFrame): Input dataset
    
    Returns:
        pd.DataFrame: Normalized dataset
    """
    # Create a copy to avoid modifying the original
    df_norm = df.copy()
    
    # Normalize each column to 0-100 range
    for col in df_norm.columns:
        min_val = df_norm[col].min()
        max_val = df_norm[col].max()
        
        # Check if min and max are the same to avoid division by zero
        if max_val != min_val:
            df_norm[col] = 100 * (df_norm[col] - min_val) / (max_val - min_val)
        else:
            # If all values are the same, set to 50 (middle of range)
            df_norm[col] = 50
    
    return df_norm

def normalize_dataset_full(df):
    """
    Normalize a dataset without assuming common date ranges, scaling to 
    0-100 if the original minimum is 0, and 1-100 otherwise.
    
    Args:
        df (pd.DataFrame): The dataset to normalize
        
    Returns:
        pd.DataFrame: Normalized dataset
    """
    # Create a copy to avoid modifying the original
    df_norm = df.copy()
    
    # Normalize each column
    for col in df_norm.columns:
        min_val = df_norm[col].min()
        max_val = df_norm[col].max()
        
        # Check if min and max are the same to avoid division by zero
        if max_val != min_val:
            # Check if the original minimum value was zero
            if min_val == 0:
                # Scale to 0-100 range if original min was 0
                df_norm[col] = 100 * (df_norm[col] - min_val) / (max_val - min_val)
            else:
                # Scale to 1-100 range if original min was not 0
                df_norm[col] = 1 + 99 * (df_norm[col] - min_val) / (max_val - min_val)
        else:
            # If all values are the same, set based on original value
            # If original value was 0, set normalized to 0 (or 1 if using 1-100 scale implicitly)
            # If original value > 0, set normalized to 50 (mid-range for 1-100)
            # Let's simplify and just set to 50 for constant non-zero, 0 for constant zero.
            if min_val == 0:
                 df_norm[col] = 0 
            else:
                 df_norm[col] = 50 # Represents a constant non-zero value in the scaled range

    return df_norm

def process_and_normalize_datasets(allKeywords):
    global menu
    global all_keywords
    global selected_keyword
    global selected_sources
    
    banner_msg(" Herramientas de Gestión Disponibles ", YELLOW, WHITE)
    for i, keyword in enumerate(allKeywords, 1):
        print(f"{i}. {keyword}")
    
    while True:
        selection = input("\nIngrese el número de la herramienta de gestión a comparar: ")
        try:
            index = int(selection) - 1
            if 0 <= index < len(allKeywords):
                selected_keyword = allKeywords[index]
                break
            else:
                print(f"{RED}Opción inválida.{RESET}")
        except ValueError:
            print(f"{YELLOW}Por favor, ingrese un número válido.{RESET}")

    selected_sources = select_multiple_data_sources()
    all_keywords = [selected_keyword]
    
    datasets_norm, selected_sources = get_file_data2(selected_keyword, selected_sources)
    
    return datasets_norm, selected_sources

def process_and_normalize_datasets_full():
    """
    Process and normalize datasets without trimming to common date range.
    Similar to process_and_normalize_datasets but preserves all dates.
    
    Relies on global selected_keyword and selected_sources set previously.

    Returns:
        tuple: (datasets_norm_full, selected_sources) - Normalized datasets with all dates and selected sources
    """
    global datasets_norm_full
    global all_datasets_full
    global all_datasets_full_monthly
    global selected_keyword # Ensure globals are declared
    global selected_sources # Ensure globals are declared
    global menu             # Ensure global menu is declared
    global dbase_options    # Ensure dbase_options is accessible

    # Use the same keyword and sources as in the regular function
    # which are expected to be set globally before calling this.

    # Initialize dictionaries to store datasets
    all_datasets_full = {}
    datasets_norm_full = {}
    all_datasets_full_monthly = {}
    datasets_norm_full_monthly = {} 

    # Check if selected_keyword and selected_sources are set globally
    keyword_missing = "selected_keyword" not in globals() or not selected_keyword
    sources_missing = "selected_sources" not in globals() or not selected_sources
    dbase_options_missing = "dbase_options" not in globals() or not dbase_options

    # Combined check for clarity (Fixes SyntaxError)
    if keyword_missing or sources_missing:
        print(f"{RED}Error: Keyword and sources must be selected before processing full datasets.{RESET}")
        # Return empty dicts and an empty list or handle error appropriately
        return {}, []

    if dbase_options_missing:
         print(f"{RED}Error: dbase_options not available globally.{RESET}")
         return {}, [] # Return empty results


    # Get file data for each source
    filenames = get_filenames_for_keyword(selected_keyword, selected_sources)

    # Get raw data for each source
    for source in selected_sources:
        menu = source # Set the global menu variable for get_file_data compatibility
        file_path = filenames.get(source, None)
        if file_path is None:
             # Use dbase_options for clearer warning messages
             print(f"Warning: No file found for source {dbase_options.get(source, f'ID {source}')} and keyword {selected_keyword}.")
             continue

        # Use menu global set above for get_file_data
        df = get_file_data(file_path, menu)

        if df is None or df.empty or (df == 0).all().all():
            print(f"Warning: Full dataset for source {dbase_options.get(source, f'ID {source}')} is empty or contains only zeros.")
            continue
        all_datasets_full[source] = df

    # Process each dataset without trimming
    for source in selected_sources:
        if source in all_datasets_full:
            # Pass selected_sources to process_dataset_full
            # Check if process_dataset_full exists and expects these args, assume it does for now based on prior context
            processed_df, processed_df_monthly = process_dataset_full(all_datasets_full[source], source, selected_sources)
            all_datasets_full[source] = processed_df
            print(f"\nConjunto de datos completo procesado: {dbase_options.get(source, f'ID {source}')}")
            # print(all_datasets_full[source].head()) # Keep output concise unless debugging
            print(f"Dimensiones: {all_datasets_full[source].shape}\n")
            all_datasets_full_monthly[source] = processed_df_monthly
            print(f"\nConjunto de datos completo procesado: {dbase_options.get(source, f'ID {source}')}")
            # print(all_datasets_full[source].head()) # Keep output concise unless debugging
            print(f"Dimensiones: {all_datasets_full_monthly[source].shape}\n")

    # Normalize each dataset
    datasets_norm_full = {source: normalize_dataset_full(df) for source, df in all_datasets_full.items() if df is not None and not df.empty}
    datasets_norm_full_monthly = {source: normalize_dataset_full(df) for source, df in all_datasets_full_monthly.items() if df is not None and not df.empty}

    return datasets_norm_full, datasets_norm_full_monthly

def get_file_data2(selected_keyword, selected_sources):
    # Obtener los nombres de archivo para la palabra clave y fuentes seleccionadas
    global menu  # Declare menu as global
    filenames = get_filenames_for_keyword(selected_keyword, selected_sources)

    datasets = {}
    datasets_monthly = {}
    all_raw_datasets = {}

    for source in selected_sources:
        #print(f"- {dbase_options[source]}: {filenames.get(source, 'Archivo no encontrado')}")
        menu = source  # This now sets the global menu variable
        df = get_file_data(filenames.get(source, 'Archivo no encontrado'), menu)
        if df.empty or (df == 0).all().all():
            print(f"Warning: Dataset for source {source} is empty or contains only zeros.")
            continue
        all_raw_datasets[source] = df

    for source in selected_sources:
        if source in all_raw_datasets:
            datasets[source] = all_raw_datasets[source]
            print(f"\nConjunto de datos procesado: {source}")
            print(datasets[source].head())
            print(f"Dimensiones: {datasets[source].shape}\n\n")
            # print(f"\nConjunto de datos procesado (monthly): {source}")
            # print(datasets_monthly[source].head())
            # print(f"Dimensiones: {datasets_monthly[source].shape}\n\n")

    print(datasets)
    
    # Normalize each dataset in datasets
    # datasets_norm = {source: normalize_dataset(df) for source, df in datasets.items()}
    datasets_norm = {source: normalize_dataset_full(df) for source, df in datasets.items()}
    # Print the normalized datasets for verification
    # for source, df_norm in datasets_norm.items():
    #     print(f"Normalized dataset for source {source}:")
    #     print(df_norm)
    #     print("\n")
    
    # Return df instead of datasets_norm, since the normalization is done already in the data source.
    return datasets_norm, selected_sources

def create_combined_dataset(datasets_norm, selected_sources, dbase_options):
    """
    Combines normalized datasets into a single DataFrame with date as index and source names as columns.
    Args:
        datasets_norm (dict): A dictionary where keys are source identifiers and values are DataFrames.
        selected_sources (list): A list of selected source identifiers.
        dbase_options (dict): A dictionary mapping source identifiers to their names.
    Returns:
        pandas.DataFrame: A combined DataFrame with date as index and source names as columns.
    """
    combined_data = pd.DataFrame()

    for source in selected_sources:
        if source in datasets_norm:
            df = datasets_norm[source]
            # Assuming each dataset has only one column of interest
            column_name = dbase_options[source]
            combined_data[column_name] = df.iloc[:, 0]  # Use iloc to select the first column

    # Ensure the index is datetime and set it as the index for the combined DataFrame
    # if not combined_data.empty:
    #    combined_data.index = df.index

    return combined_data

def create_combined_dataset2(datasets_norm, selected_sources, dbase_options):
    """
    Creates a combined dataset that includes ALL date ranges from all selected sources,
    filling missing values with NaN.
    
    Unlike create_combined_dataset which only includes common date ranges, this function
    preserves all dates from all sources.
    
    Parameters:
    -----------
    datasets_norm : dict
        Dictionary containing normalized datasets for each source
    selected_sources : list
        List of selected data sources
    dbase_options : dict
        Dictionary mapping source codes to their full names
        
    Returns:
    --------
    pandas.DataFrame
        Combined dataset with all dates from all sources
    """
    global combined_dataset2
    
    # Initialize an empty DataFrame to store the combined dataset
    combined_dataset2 = pd.DataFrame()
    
    # Get all unique dates from all datasets
    all_dates = set()
    for source in selected_sources:
        if source in datasets_norm and not datasets_norm[source].empty:
            all_dates.update(datasets_norm[source].index)
    
    # Sort the dates
    all_dates = sorted(list(all_dates))
    
    # Create a DataFrame with all dates
    combined_dataset2 = pd.DataFrame(index=all_dates)
    
    # Add data from each source
    for source in selected_sources:
        if source in datasets_norm and not datasets_norm[source].empty:
            source_name = dbase_options.get(source, source)
            # Reindex the source dataset to include all dates, filling with NaN
            source_data = datasets_norm[source].reindex(all_dates)
            
            # Add columns from this source to the combined dataset
            for col in source_data.columns:
                combined_dataset2[f"{source_name}"] = source_data[col]
    
    # Sort by date
    combined_dataset2.sort_index(inplace=True)
    
    return combined_dataset2

def display_combined_datasets():
    """
    Displays both combined datasets (common date range and all dates) in full,
    with a pause at the end to allow for comparison.
    
    This function prints the entire datasets, not just head and tail portions,
    to allow for complete examination of the data differences.
    """
    global combined_dataset, combined_dataset2
    
    # Check if both datasets exist
    if 'combined_dataset' not in globals() or combined_dataset is None:
        print(f"{RED}Error: combined_dataset is not available.{RESET}")
        return
        
    if 'combined_dataset2' not in globals() or combined_dataset2 is None:
        print(f"{RED}Error: combined_dataset2 is not available.{RESET}")
        return
    
    # Display header for the first dataset
    print(f"\n{YELLOW}{'='*80}{RESET}")
    print(f"{YELLOW}COMBINED DATASET (COMMON DATE RANGE ONLY){RESET}")
    print(f"{YELLOW}{'='*80}{RESET}")
    
    # Display the entire first dataset
    pd.set_option('display.max_rows', None)  # Show all rows
    pd.set_option('display.max_columns', None)  # Show all columns
    pd.set_option('display.width', None)  # Auto-detect width
    
    print(combined_dataset)
    
    # Display header for the second dataset
    print(f"\n{GREEN}{'='*80}{RESET}")
    print(f"{GREEN}COMBINED DATASET 2 (ALL DATES FROM ALL SOURCES){RESET}")
    print(f"{GREEN}{'='*80}{RESET}")
    
    # Display the entire second dataset
    print(combined_dataset2)
    
    # Reset display options to default
    pd.reset_option('display.max_rows')
    pd.reset_option('display.max_columns')
    pd.reset_option('display.width')
    
    # Display summary statistics
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}DATASET COMPARISON SUMMARY{RESET}")
    print(f"{BLUE}{'='*80}{RESET}")
    print(f"Combined Dataset (common dates) shape: {combined_dataset.shape}")
    print(f"Combined Dataset 2 (all dates) shape: {combined_dataset2.shape}")
    print(f"Additional dates in Dataset 2: {combined_dataset2.shape[0] - combined_dataset.shape[0]}")
    
    # Pause at the end
    input(f"\n{YELLOW}Press Enter to continue...{RESET}")

def main():
    global combined_dataset2, trends_results, csv_combined_dataset, menu
    global all_keywords, selected_keyword, selected_sources
    global datasets_norm, datasets_norm_full, dbase_options
    global combined_dataset, filename, unique_folder, all_kw
    global wider, one_keyword, actual_menu, actual_opt, data_filename
    global csv_all_data, csv_last_20_data, csv_last_15_data, csv_last_10_data
    global csv_last_5_data, csv_last_year_data, top_choice

    
    # Redirigir stderr a /dev/null
    import os
    import sys
    stderr = sys.stderr
    null = open(os.devnull, 'w')    
    
    while True:
        # Redirigir stderr antes de cada iteración
        #sys.stderr = null
        
        top_choice = top_level_menu()
        
        if top_choice == 4:  # Exit option
            print("\nGracias por usar el programa.\nSuerte en tu investigación, ¡Hasta luego!\n")
            break
            
        elif top_choice == 1:
            # --- Analysis for ONE tool on ONE data source ---
            menu_options = ["Google Trends", "Google Book Ngrams", "Bain - Uso", "Crossref.org", "Bain - Satisfacción"]
            menu_opt = ["GT","GB","BR","CR","BS"]

            # --- General Initialization (Reset state) ---
            init_variables()
            # --------------------------------------------

            # --- User Selection for Option 1 ---
            menu = main_menu() # Get data source choice
            actual_menu = menu_options[menu-1]
            actual_opt = menu_opt[menu-1]
            data_filename, all_keywords = get_user_selections(tool_file_dic, menu) # Get tool choice(s)
            print(f'Comenzaremos el análisis de las siguiente(s) herramienta(s) gerencial(es): \n{GREEN}{all_keywords}{RESET}')
            print(f'Buscando la data en: {YELLOW}{data_filename}{RESET}')
            # -----------------------------------

            # --- Keyword-Dependent Setup (Moved from init_variables) ---
            if not all_keywords or not data_filename:
                print(f"{RED}Error: No se seleccionó ninguna herramienta o archivo de datos.{RESET}")
                continue # Go back to main menu if selection failed

            wider = True if len(all_keywords) <= 2 else False
            one_keyword = True if len(all_keywords) < 2 else False
            all_kw = ", ".join(all_keywords)

            filename = create_unique_filename(all_keywords, top_choice)
            unique_folder = os.path.join(data_folder, filename)
            if not os.path.exists(unique_folder):
                os.makedirs(unique_folder)
                os.chmod(unique_folder, 0o777)

            trends_results = process_file_data(all_keywords, data_filename)
            if trends_results:
                # Save CSV data only if processing was successful
                total_years = trends_results.get('total_years', 0) # Assuming process_file_data returns this
                if total_years > 20:
                    csv_all_data = trends_results['all_data'].to_csv(index_label='date', float_format='%.2f', na_rep='N/A')
                else:
                    csv_all_data = None
                csv_last_20_data = trends_results['last_20_years_data'].to_csv(index_label='date', float_format='%.2f', na_rep='N/A')
                csv_last_15_data = trends_results['last_15_years_data'].to_csv(index_label='date', float_format='%.2f', na_rep='N/A')
                csv_last_10_data = trends_results['last_10_years_data'].to_csv(index_label='date', float_format='%.2f', na_rep='N/A')
                csv_last_5_data = trends_results['last_5_years_data'].to_csv(index_label='date', float_format='%.2f', na_rep='N/A')
                csv_last_year_data = trends_results['last_year_data'].to_csv(index_label='date', float_format='%.2f', na_rep='N/A')
            else:
                print(f"{RED}[Error] process_file_data falló para {data_filename}. Saltando análisis.{RESET}")
                continue # Go back to main menu if data processing failed
            # ---------------------------------------------------------

            # --- Run Analysis for Option 1 ---
            results()
            ai_analysis()
            report_pdf()
            # ----------------------------------

        elif top_choice == 2:
            # --- Analysis for ONE tool across MULTIPLE data sources ---

            # --- General Initialization (Reset state) ---
            init_variables()
            # --------------------------------------------

            # 1. Get all available tools/keywords
            all_tool_keywords = get_all_keywords()
            if not all_tool_keywords:
                print(f"{RED}No se encontraron herramientas de gestión. Verifique los archivos de datos.{RESET}")
                continue # Go back to main menu

            # 2. Prompt user to select ONE tool and MULTIPLE sources
            #    This function handles user selection, fetches, processes, and normalizes
            #    data for the common date range. It also sets global variables:
            #    selected_keyword, selected_sources, all_keywords=[selected_keyword], dbase_options
            datasets_norm, selected_sources_list = process_and_normalize_datasets(all_tool_keywords)

            # Check if selection was successful (user didn't cancel, data was found)
            if not selected_sources_list or datasets_norm is None or not datasets_norm:
                 print(f"{YELLOW}No se seleccionaron fuentes válidas o no se encontraron datos para la herramienta seleccionada en el rango común.{RESET}")
                 continue # Go back to main menu

            # We now rely on the global 'selected_sources' and 'dbase_options' set by the function above.
            if "selected_sources" not in globals() or not selected_sources:
                 print(f"{RED}Error Fatal: selected_sources no fue establecido globalmente.{RESET}")
                 continue
            if "dbase_options" not in globals() or not dbase_options:
                 print(f"{RED}Error Fatal: dbase_options no fue establecido globalmente.{RESET}")
                 continue

            # --- Keyword-Dependent Setup (Moved from init_variables) ---
            # Note: process_and_normalize_datasets sets global all_keywords = [selected_keyword]
            if not all_keywords:
                 print(f"{RED}Error Fatal: all_keywords no fue establecido por process_and_normalize_datasets.{RESET}")
                 continue

            wider = True # Option 2 compares sources for ONE tool, so wider layout is suitable
            one_keyword = True # Option 2 focuses on one keyword
            all_kw = selected_keyword # Use the single selected keyword

            filename = create_unique_filename(all_keywords, top_choice) # Use the list with one keyword
            unique_folder = os.path.join(data_folder, filename)
            if not os.path.exists(unique_folder):
                os.makedirs(unique_folder)
                os.chmod(unique_folder, 0o777)
            # ---------------------------------------------------------

            # Confirm selection to the user
            print(f"\n{CYAN}Analizando '{selected_keyword}' usando fuentes: {', '.join([dbase_options.get(s, str(s)) for s in selected_sources])}{RESET}")

            # 3. Create the combined dataset for the common date range
            combined_dataset = create_combined_dataset2(datasets_norm, selected_sources, dbase_options)

            print (combined_dataset)
                 
            # --- Run Analysis for Option 2 ---
            results()
            ai_analysis()
            #report_pdf()
            # ----------------------------------

            
        elif top_choice == 3:
            # --- Call the new batch function --- 
            generate_all_reports() 
            # ------------------------------------
            
    # Cerrar el archivo null y restaurar stderr al finalizar
    null.close()
    sys.stderr = stderr

# <<< Add this function definition >>>
def update_readme(report_info):
    """
    Updates the Informes/README.md file with a new report entry, keeping the list sorted by Nro.

    Args:
        report_info (dict): A dictionary containing keys: 'nro', 'informe_code', 'titulo', 'pdf_filename'
    """
    readme_path = "Informes/README.md"
    # Corrected base URL - Use blob for viewing files directly on GitHub usually
    github_base_url = "https://github.com/Wise-Connex/Management-Tools-Analysis/blob/main/Informes/"
    header = "# Índice de Informes\n\n| Nro | Informe | Título | Enlace |\n|---|---|---|---|\n"
    # Regex to capture existing rows, ignoring header/separator, making groups non-greedy
    row_pattern = re.compile(r"^\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*\[([^]]+?)\]\(([^)]+?)\)\s*\|\s*$", re.MULTILINE)

    entries = []
    if os.path.exists(readme_path):
        try:
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Find all existing valid rows using regex
                matches = row_pattern.findall(content)
                for match in matches:
                    nro, informe, titulo, link_text, link_url = match
                    # Extract filename from URL for robustness
                    # Handle potential URL encoding in existing links if needed, but assume base for now
                    pdf_filename_from_link = os.path.basename(link_url) # Get just the filename part
                    try:
                         entries.append({
                             'nro': int(nro.strip()), # Convert Nro to int for sorting
                             'informe_code': informe.strip(),
                             'titulo': titulo.strip(),
                             'pdf_filename': pdf_filename_from_link # Store decoded filename
                         })
                    except ValueError:
                         print(f"  {YELLOW}[Warning README] Skipping invalid row in README: Nro='{nro}' is not an integer.{RESET}")
        except Exception as e:
            print(f"  {YELLOW}[Warning README] Error al leer {readme_path}: {e}. Se creará uno nuevo.{RESET}")
            entries = [] # Start fresh if read error

    # --- Add or Update the new entry ---
    new_nro_str = report_info['nro']
    try:
        new_nro = int(new_nro_str) # Convert incoming Nro to int
    except ValueError:
         print(f"  {RED}[Error README] Invalid Nro received: '{new_nro_str}'. Cannot update README entry.{RESET}")
         return # Stop if Nro isn't a valid integer

    new_informe_code = report_info['informe_code']
    new_pdf_filename = report_info['pdf_filename']
    new_titulo = report_info['titulo']
    updated = False
    for entry in entries:
        # Update if Nro and Informe code match (using int for Nro comparison)
        if entry['nro'] == new_nro and entry['informe_code'] == new_informe_code:
            entry['titulo'] = new_titulo
            entry['pdf_filename'] = new_pdf_filename # Ensure filename is updated
            updated = True
            print(f"    [Info README] Entrada actualizada: Nro={new_nro}, Informe={new_informe_code}")
            break

    if not updated:
        # Check for duplicate Nro before adding (optional but good practice)
        if any(entry['nro'] == new_nro for entry in entries):
             print(f"  {YELLOW}[Warning README] Duplicate Nro {new_nro} found. Adding entry anyway, but consider checking metadata.{RESET}")

        entries.append({
            'nro': new_nro,
            'informe_code': new_informe_code,
            'titulo': new_titulo,
            'pdf_filename': new_pdf_filename
        })
        print(f"    [Info README] Nueva entrada añadida: Nro={new_nro}, Informe={new_informe_code}")

    # --- Sort entries numerically by 'nro' ---
    entries.sort(key=lambda x: x['nro'])

    # --- Generate new Markdown content ---
    markdown_content = header
    for entry in entries:
        # URL encode the filename for the link
        encoded_filename = quote(entry['pdf_filename'])
        link_url = f"{github_base_url}{encoded_filename}"
        # Display the decoded filename as the link text for readability
        link_text = entry['pdf_filename']
        markdown_content += f"| {entry['nro']} | {entry['informe_code']} | {entry['titulo']} | [{link_text}]({link_url}) |\n"

    # --- Write back to README.md ---
    try:
        # Ensure the Informes directory exists before writing
        informes_dir = os.path.dirname(readme_path)
        if not os.path.exists(informes_dir):
             os.makedirs(informes_dir)
             print(f"  [Info README] Directory created: {informes_dir}")

        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"    [Info README] {readme_path} actualizado correctamente.")
    except Exception as e:
        print(f"  {RED}[Error README] No se pudo escribir en {readme_path}: {e}{RESET}")

def generate_all_reports():
    """
    Generates individual reports for all tools across all data sources.
    Iterates TOOL first, then SOURCE.
    Saves a copy of each report to the 'Informes' folder with Nro-Cod-DataSource naming.
    """
    global menu, actual_menu, actual_opt, all_keywords, filename, unique_folder, top_choice
    global tool_file_dic, trends_results, data_filename # Ensure required globals are declared

    # Colors (ensure these are defined globally elsewhere or define them here)
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    
    print("\n" + "="*60)
    print(" Iniciando Generación de Todos los Informes Individuales (Batch)")
    print(" (Iterando por Herramienta -> Fuente de Datos)")
    print("="*60 + "\n")

    # Define data source mapping (menu index to details)
    data_sources = {
        1: {"name": "Google Trends", "code": "GT", "opt": "GT"},
        2: {"name": "Google Books Ngrams", "code": "GB", "opt": "GB"},
        3: {"name": "Bain - Usability", "code": "BU", "opt": "BR"},
        4: {"name": "Crossref.org", "code": "CR", "opt": "CR"},
        5: {"name": "Bain - Satisfaction", "code": "BS", "opt": "BS"}
    }

    # Create the 'Informes' directory if it doesn't exist
    informes_folder = "Informes"
    if not os.path.exists(informes_folder):
        os.makedirs(informes_folder)
        os.chmod(informes_folder, 0o777)
        print(f"[Info] Carpeta '{informes_folder}' creada.")

    # --- OUTER LOOP: Iterate through Tools --- 
    for tool_code, tool_data in tool_file_dic.items():
        current_tool_keywords = tool_data[1] # Keywords for the tool being processed
        print(f"\n{YELLOW}>>> Procesando Informes para Herramienta(s): {', '.join(current_tool_keywords)} <<< {RESET}")
        print("="*60)
        processed_sources_for_tool = 0

        # --- INNER LOOP: Iterate through Data Sources for the current tool --- 
        for source_menu_index, source_info in data_sources.items():
            print(f"\n  -- Intentando Fuente: {source_info['name']} --")

            # --- Load Metadata for THIS data source ---
            portada_csv_path = f"pub-assets/{source_info['code']}-Portada.csv"
            portada_df = None
            if os.path.exists(portada_csv_path):
                try:
                    portada_df = pd.read_csv(portada_csv_path, sep=';', quotechar='"', skipinitialspace=True)
                    portada_df.columns = portada_df.columns.str.strip()
                    # print(f"    [Info] Metadata cargada desde {portada_csv_path}") # Less verbose
                    if 'Nro.' in portada_df.columns:
                         portada_df['Nro.'] = portada_df['Nro.'].astype(str)
                    if 'Cód' in portada_df.columns:
                         portada_df['Cód'] = portada_df['Cód'].astype(str)
                except Exception as e:
                    print(f"    {YELLOW}[Warning] No se pudo cargar {portada_csv_path}: {e}. Se continuará sin metadatos.{RESET}")
                    portada_df = None
            else:
                print(f"    {YELLOW}[Warning] No se encontró {portada_csv_path}. Se continuará sin metadatos.{RESET}")
                portada_df = None
            # ------------------------------------------

            # --- Set variables for this specific Tool/Source combo --- 
            menu = source_menu_index
            actual_menu = source_info['name']
            actual_opt = source_info['opt']
            all_keywords = current_tool_keywords # Use tool keywords from outer loop
            top_choice = 1 # Simulate selecting option 1

            # --- Determine correct data_filename --- 
            data_file_index = 0 
            if menu == 1: data_file_index = 0
            elif menu == 2: data_file_index = 2
            elif menu == 3: data_file_index = 3
            elif menu == 4: data_file_index = 4
            elif menu == 5: data_file_index = 5
            current_data_filename = tool_data[data_file_index] # Local name for clarity

            # --- Check if data file exists --- 
            full_data_path = os.path.join("dbase", current_data_filename)
            if not os.path.exists(full_data_path):
                 print(f"    {YELLOW}[Skipping] Archivo de datos no encontrado: {current_data_filename}{RESET}")
                 continue 
            
            # --- Assign to GLOBAL data_filename REQUIRED by init_variables --- 
            data_filename = current_data_filename
            # ------------------------------------------------------------------
            
            print(f"    Procesando con archivo: {data_filename}")

            # --- Generate Report for this Tool/Source --- 
            try:
                # 1. Initialize variables 
                init_variables()

                # 2. Check data availability after init
                trends_data_available = False
                if 'trends_results' in globals() and trends_results is not None:
                     if 'all_data' in trends_results and not trends_results['all_data'].empty and all_keywords[0] in trends_results['all_data'].columns:
                         trends_data_available = True
                     elif 'last_20_years_data' in trends_results and not trends_results['last_20_years_data'].empty and all_keywords[0] in trends_results['last_20_years_data'].columns:
                          trends_data_available = True
                if not trends_data_available:
                     print(f"      {YELLOW}[Skipping] No se encontraron datos válidos post-inicialización.{RESET}")
                     continue

                # 3. Run Results Generation
                print(f"      Generando resultados y gráficos ({unique_folder})...")
                results()

                # 4. Run AI Analysis
                print("      Generando análisis AI...")
                ai_analysis()

                # 5. Generate PDF Report
                print("      Generando reporte PDF...")
                report_pdf()

                # 6. Copy and Rename PDF
                original_pdf_path = os.path.join(unique_folder, f'{filename}.pdf')
                if os.path.exists(original_pdf_path):
                    nro_val = "XXX"
                    cod_val = "XX"
                    tool_name_for_lookup = all_keywords[0]

                    if portada_df is not None:
                         match = portada_df[portada_df['Herramienta'] == tool_name_for_lookup]
                         if not match.empty:
                              nro_val = match.iloc[0].get('Nro.', nro_val)
                              cod_val = match.iloc[0].get('Cód', cod_val)
                         else:
                              print(f"      {YELLOW}[Warning] Metadatos no encontrados para '{tool_name_for_lookup}' en {portada_csv_path}{RESET}")
                    else:
                         print(f"      {YELLOW}[Warning] Saltando búsqueda de metadatos (archivo no cargado).{RESET}")

                    new_filename = f"Informe_{str(cod_val).strip()}.pdf"
                    new_pdf_path = os.path.join(informes_folder, new_filename)
                    
                    # Copy the PDF
                    try:
                        shutil.copy2(original_pdf_path, new_pdf_path) # copy2 preserves metadata
                        print(f"      {GREEN}Reporte copiado y renombrado a: {new_pdf_path}{RESET}")
                        processed_sources_for_tool += 1

                        # --- Call README Update --- 
                        if portada_df is not None and not match.empty:
                             # Construct the full title (use .get with default values)
                             titulo_prefix = match.iloc[0].get('Título', 'Título No Encontrado')
                             herramienta_name = match.iloc[0].get('Herramienta', tool_name_for_lookup) 
                             full_titulo = f"{str(titulo_prefix).strip()} {str(herramienta_name).strip()}"
                             
                             # Ensure Nro and Informe Code are strings for dictionary key safety if needed later
                             report_readme_info = {
                                 'nro': str(nro_val).strip(), 
                                 'informe_code': str(cod_val).strip(), 
                                 'titulo': full_titulo,
                                 'pdf_filename': new_filename # The actual filename used
                             }
                             update_readme(report_readme_info)
                        else:
                             print(f"      {YELLOW}[Warning README] No se actualizará README.MD porque faltan metadatos para '{tool_name_for_lookup}'.{RESET}")
                        # ------------------------

                    except Exception as copy_e:
                        print(f"      {RED}[Error] No se pudo copiar el reporte a '{new_pdf_path}': {copy_e}{RESET}")
                else:
                    print(f"      {RED}[Error] Reporte PDF no encontrado en: {original_pdf_path}{RESET}")

            except Exception as e:
                print(f"    {RED}[Error General] Procesando {source_info['name']}: {e}{RESET}")
                traceback.print_exc()
            # --- End Report Generation Try/Except ---
            
        # --- End Inner Loop (Sources) ---
        print("="*60)
        print(f"<<< Herramienta(s) {', '.join(current_tool_keywords)} completada. {processed_sources_for_tool} informes generados. >>>")
        
    # --- End Outer Loop (Tools) ---
    print("\n" + "="*60)
    print(" Generación de Todos los Informes (Batch) Completada")
    print("="*60 + "\n")
    
# <<< End of generate_all_reports function >>>

if __name__ == "__main__":
    main()