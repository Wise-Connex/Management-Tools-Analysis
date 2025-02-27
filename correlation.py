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
#import altair as alt
import scipy.fftpack as fftpack
import markdown
import weasyprint
import os
import csv
import io
import sys
import math
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
#from sklearn.preprocessing import StandardScaler
#from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from statsmodels.tsa.seasonal import seasonal_decompose
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import google.api_core.exceptions


# AI Prompts imports 
from prompts import system_prompt_1, system_prompt_2, temporal_analysis_prompt_1, temporal_analysis_prompt_2, \
    cross_relationship_prompt_1, cross_relationship_prompt_2, trend_analysis_prompt_1, trend_analysis_prompt_2, \
    arima_analysis_prompt_1, arima_analysis_prompt_2, seasonal_analysis_prompt_1, seasonal_analysis_prompt_2, \
    prompt_6_single_analysis, prompt_6_correlation, prompt_conclusions_standalone, prompt_conclusions_comparative, prompt_sp
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

global gem_temporal_trends_sp
global gem_cross_keyword_sp
global gem_industry_specific_sp
global gem_arima_sp
global gem_seasonal_sp
global gem_fourier_sp
global gem_conclusions_sp
global csv_fourier
global csv_fourierA
global csv_means_trends
global csv_means_trendsA
global csv_correlation
global csv_regression
global csv_arima
global csv_arimaA
global csv_arimaB
global csv_seasonal
global csv_seasonalA
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
global keycharts
global csv_combined_dataset
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

def gemini_prompt(system_prompt, prompt, m='flash', max_retries=5, initial_backoff=1):
  """
  Send a prompt to the Gemini API with retry logic for handling timeouts and service issues.
  
  Args:
      system_prompt: The system instructions for the model
      prompt: The user prompt to send to the model
      m: Model type ('pro' or 'flash')
      max_retries: Maximum number of retry attempts
      initial_backoff: Initial backoff time in seconds (will increase exponentially)
      
  Returns:
      The text response from the model
  """
  system_instructions = system_prompt

  #print('\n**************************** INPUT ********************************\n')
  #print(f'System Instruction: \n{system_instructions} \nPrompt: \n{prompt}')

  if m == 'pro':
    model = 'gemini-2.0-flash-thinking-exp-01-21' # @#param {type: "string"} ["gemini-1.0-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
  else:
    model = 'gemini-2.0-pro-exp-02-05' # @#param {type: "string"} ["gemini-1.0-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
  temperature = 0.31 # @#param {type: "slider", min: 0, max: 2, step: 0.05}
  stop_sequence = '*** END ANALYSIS ***'

  if model == 'gemini-1.0-pro' and system_instructions is not None:
    system_instructions = None
    print('\x1b[31m(WARNING: System instructions ignored, gemini-1.0-pro does not support system instructions)\x1b[0m')
  if model == 'gemini-1.0-pro' and temperature > 1:
    temperature = 1
    print('\x1b[34m(INFO: Temperature set to 1, gemini-1.0-pro does not support temperature > 1)\x1b[0m')

  if system_instructions == '':
    system_instructions = None

  # Load environment variables from a .env file (if using one)
  load_dotenv()

  # Retrieve the API key
  api_key = os.getenv('GOOGLE_API_KEY')

  if api_key is None:
      raise ValueError("GOOGLE_API_KEY environment variable is not set")
  
  genai.configure(api_key=api_key)
  model_instance = genai.GenerativeModel(model, system_instruction=system_instructions)
  config = genai.GenerationConfig(temperature=temperature, stop_sequences=[stop_sequence])
  
  # Implement retry logic with exponential backoff
  retry_count = 0
  backoff_time = initial_backoff
  
  while retry_count < max_retries:
    try:
      # If this isn't the first attempt, log that we're retrying
      if retry_count > 0:
        print(f"\x1b[33m(Retry attempt {retry_count}/{max_retries} after waiting {backoff_time}s)\x1b[0m")
      
      # Try to generate content
      response = model_instance.generate_content(contents=[prompt], generation_config=config)
      return response.text
      
    except google.api_core.exceptions.DeadlineExceeded as e:
      # Handle timeout errors specifically
      retry_count += 1
      
      if retry_count >= max_retries:
        print(f"\x1b[31mFailed after {max_retries} retries. Last error: {str(e)}\x1b[0m")
        # Return a fallback message instead of raising an exception
        return f"[API TIMEOUT ERROR: The request to the Gemini API timed out after {max_retries} attempts. The prompt may be too complex or the service may be experiencing issues.]"
      
      # Calculate exponential backoff with jitter
      jitter = random.uniform(0, 0.1 * backoff_time)  # Add up to 10% jitter
      wait_time = backoff_time + jitter
      print(f"\x1b[33mAPI timeout occurred. Retrying in {wait_time:.2f} seconds...\x1b[0m")
      time.sleep(wait_time)
      backoff_time *= 2  # Exponential backoff
      
    except Exception as e:
      # Handle other exceptions
      print(f"\x1b[31mError calling Gemini API: {str(e)}\x1b[0m")
      return f"[API ERROR: {str(e)}]"

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

# Create a cubic interpolation function
def cubic_interpolation(df, kw):
    # Extract actual data points (non-NaN values)
    actual_data = df[~df[kw].isna()]
    
    if actual_data.empty or len(actual_data) < 4:  # Cubic spline requires at least 4 points
        return linear_interpolation(df, kw)  # Fall back to linear interpolation if not enough points
    
    x = actual_data.index
    y = actual_data[kw].values

    # Create a Cubic Spline interpolator
    spline = CubicSpline(x, y)
    
    # Generate interpolated values only between first and last actual data points
    start_date = actual_data.index.min().date()
    end_date = actual_data.index.max().date()
    x_interp = pd.date_range(start_date, end_date, freq='MS')
    
    # Evaluate the spline at the interpolated points
    y_interp = spline(x_interp)

    # Create a new DataFrame with the interpolated values
    df_interpolated = pd.DataFrame(y_interp, index=x_interp, columns=[kw])
    
    # Preserve original values at actual data points to ensure accuracy
    for idx in actual_data.index:
        if idx in df_interpolated.index:
            df_interpolated.loc[idx, kw] = actual_data.loc[idx, kw]

    #PPRINT(f'DF INTERPOLATED:\n{df_interpolated}')
    return df_interpolated

# Create a BSpline interpolation function
def bspline_interpolation(df, column):
    # Extract actual data points (non-NaN values)
    actual_data = df[~df[column].isna()]
    
    if actual_data.empty or len(actual_data) < 4:  # B-spline typically requires at least 4 points
        # Fall back to simpler interpolation if not enough points
        if len(actual_data) >= 2:
            # Create a simple linear interpolation
            x = actual_data.index.astype(int) / 10**9
            y = actual_data[column].values
            
            # Generate interpolated values only between first and last actual data points
            start_date = actual_data.index.min()
            end_date = actual_data.index.max()
            x_interp = pd.date_range(start_date, end_date, freq='MS')
            x_interp_unix = x_interp.astype(int) / 10**9
            
            # Linear interpolation
            y_interp = np.interp(x_interp_unix, x, y)
            
            # Create result dataframe
            df_interpolated = pd.DataFrame(index=x_interp)
            df_interpolated[column] = y_interp
            
            # Preserve original values at actual data points
            for idx in actual_data.index:
                if idx in df_interpolated.index:
                    df_interpolated.loc[idx, column] = actual_data.loc[idx, column]
                    
            return df_interpolated
        else:
            return df.copy()  # Return original if not enough points
    
    x = actual_data.index.astype(int) / 10**9  # Convert to Unix timestamp
    y = actual_data[column].values

    # Create a B-spline interpolator
    tck = interp.splrep(x, y, k=3)  # k=3 for a cubic B-spline

    # Generate interpolated values only between first and last actual data points
    start_date = actual_data.index.min()
    end_date = actual_data.index.max()
    
    # Create a list to store interpolated data
    interpolated_data = []
    
    # Generate monthly points only between first and last actual data points
    x_interp = pd.date_range(start=start_date, end=end_date, freq='MS')
    x_interp_unix = x_interp.astype(int) / 10**9
    y_interp = interp.splev(x_interp_unix, tck)
    
    # Add the interpolated data
    for date, value in zip(x_interp, y_interp):
        interpolated_data.append((date, value))

    # Create a new DataFrame with the interpolated values
    df_interpolated = pd.DataFrame(interpolated_data, columns=['date', column])
    df_interpolated.set_index('date', inplace=True)

    # Preserve all original data points from the original dataset
    for idx in actual_data.index:
        if idx in df_interpolated.index:
            df_interpolated.loc[idx, column] = actual_data.loc[idx, column]

    return df_interpolated

#*** END GNNgram

# Displays the main menu and prompts the user to select an option.
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
    x = df.index.astype(int) / 10**9  # Convert to Unix timestamp
    y = df[column].values

    # Create a B-spline interpolator
    tck = interp.splrep(x, y, k=3)  # k=3 for a cubic B-spline

    # Generate interpolated values for all months within the original year range
    start_year = df.index.min().year
    end_year = df.index.max().year
    
    # Create a list to store interpolated data
    interpolated_data = []
    
    for year in range(start_year, end_year + 1):
        # Generate 12 monthly points for each year
        x_interp = pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31", freq='MS')
        x_interp_unix = x_interp.astype(int) / 10**9
        y_interp = interp.splev(x_interp_unix, tck)
        
        # Add the interpolated data for this year
        for date, value in zip(x_interp, y_interp):
            interpolated_data.append((date, value))

    # Create a new DataFrame with the interpolated values
    df_interpolated = pd.DataFrame(interpolated_data, columns=['date', column])
    df_interpolated.set_index('date', inplace=True)

    # Preserve the first and last data points from the original dataset
    df_interpolated.loc[df.index[0], column] = df.loc[df.index[0], column]
    df_interpolated.loc[df.index[-1], column] = df.loc[df.index[-1], column]

    return df_interpolated

def get_file_data(filename, menu):
    # Path to the local 'dbase' folder
    local_path = "./dbase/"
    
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
        # For Google Books Ngrams, assume the index is just the year
        df.index = pd.to_datetime(df.index.str.split('-').str[0], format='%Y')
    else:
        # For other data sources, assume 'Year-Month' format
        df.index = pd.to_datetime(df.index + '-01', format='%Y-%m-%d')
    
    if menu == 3 or menu == 5:
        # Apply bspline interpolation for menus 3 and 5
        interpolated_data = pd.DataFrame()
        for column in df.columns:
            interpolated = bspline_interpolation(df, column)
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
        image_markdown += f"## {title}\n\n"
        image_markdown += f"<img src='data:image/png;base64,{encoded_string}' style='max-width: 100%; height: auto;'>\n\n"
    else:
        print(f"Image file does not exist: {full_path}")

# Fourier Analisys
def fourier_analisys(period='last_year_data'):
  global charts
  global image_markdown
  char='*'
  title=' Análisis de Fourier '
  qty=len(title)
  print(f'\x1b[33m\n\n{char*qty}\n{title}\n{char*qty}\x1b[0m')
  banner_msg("Análisis de Fourier",margin=1,color1=YELLOW,color2=WHITE)
  csv_fourier="\nAnálisis de Fourier,Frequency,Magnitude\n"
  for keyword in all_keywords:
      # Extract data for the current keyword
      data = trends_results[period][keyword]
      print(f"\nPalabra clave: {keyword} ({actual_menu})\n")
      csv_fourier += f"\nPalabra clave: {keyword}\n\n"
      # Create time vector
      time_vector = np.arange(len(data))
      #csv_fourier += f"Vector de tiempo: \n{time_vector}\n"
      # Ensure data is a properly aligned NumPy array
      data = np.asarray(data, dtype=float).copy()
      # Perform Fourier transform
      fourier_transform = fftpack.fft(data)
      # Calculate frequency axis
      freq = fftpack.fftfreq(len(data))
      # Create DataFrame with time_vector as index and both magnitude and frequency as columns
      fourierT = pd.DataFrame({
          'frequency': freq,
          'magnitude': np.abs(fourier_transform)
      }, index=time_vector)
      print(fourierT)      
      csv_fourier += fourierT.to_csv(index=True)
      # Plot the magnitude of the Fourier transform
      plt.figure(figsize=(12, 10))  # Create a new figure for each keyword
      plt.plot(freq, np.abs(fourier_transform), color='#66B2FF')
      plt.xlabel('Frecuencia (ciclos/año)')
      #plt.yscale('log')
      plt.ylabel('Magnitud')  # Update label to reflect 1/2 log scale
      plt.title(f'Transformada de Fourier para {keyword} ({actual_menu})', pad=20)
      if top_choice == 2:
          plt.title(f'Transformada de Fourier para {actual_menu} ({keyword})', pad=20)
      # Save the plot to the unique folder
      base_filename = f'{filename}_fourier_{keyword[:3]}.png'
      image_filename=get_unique_filename(base_filename, unique_folder)
      plt.savefig(os.path.join(unique_folder, image_filename), bbox_inches='tight')
      add_image_to_report(f'Transformada de Fourier para {keyword}', image_filename)
      charts += f'Transformada de Fourier para {keyword} ({image_filename})\n\n'
      # Remove plt.show() to prevent graph windows from appearing
      plt.close()
  csv_fourier="".join(csv_fourier)
  return csv_fourier

# Seasonal Analysis
def seasonal_analysis(period='last_20_years_data'):
    global charts
    global csv_seasonal
    global image_markdown
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
    csv_seasonal = ""# Analyze each keyword
    for keyword in all_keywords:
        def decompose_series(series):
            if menu == 2:
                # For annual data, we can't perform seasonal decomposition
                print(f"Seasonal decomposition not applicable for annual data ({keyword})")
                return None
            else:
                if len(series) < 24:
                    print(f"Not enough data points for seasonal decomposition ({keyword})")
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
  global menu
  
  # Ensure menu has a default value if not set
  if 'menu' not in globals() or menu is None:
    menu = 1  # Default value, adjust as needed
    
  menu2 = menu
  if top_choice == 1:
    # Group data and calculate means
    all_data = get_file_data(d_filename, menu2)
  if top_choice == 2:
    all_data = combined_dataset#PPRINT(f"\n{all_data}")

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

  # Return results as a dictionary
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

# Create Charts
def relative_comparison():
    global charts
    global title_odd_charts
    global title_even_charts
    global image_markdown
    global keycharts
    global current_year
    
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
        trends_results['mean_all'] if menu == 2 or menu == 4 else None,
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
        
    # Create grid spec with 9 columns and the determined number of rows
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
        i = 1
        # all data
        if menu == 2 or menu == 4 or menu == 3 or menu == 5:
            ax1 = fig.add_subplot(gs[i, axODD])
            ax2 = fig.add_subplot(gs[i, axEVEN])
            setup_subplot(ax1, trends_results['all_data'], trends_results['mean_all'], title_odd_charts, f'Período de {72 if menu == 2 else 74 if menu == 4 else 42} años\n({current_year - (72 if menu == 2 else 74 if menu == 4 else 30)}-{current_year})', window_size, colors)
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
    handles, labels = ax3.get_legend_handles_labels()
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
    
    if colors is None:
        colors = plt.cm.rainbow(np.linspace(0, 1, len(all_keywords)))
    
    # Plot data
    if top_choice == 2:
        menu = 1
        
    for i, kw in enumerate(all_keywords):
        if menu == 2:
            ax.plot(data[kw].index, data[kw], label=kw, color=colors[i])
        else:
            smoothed_data = smooth_data(data[kw], window_size)
            ax.plot(data[kw].index, smoothed_data, label=kw, color=colors[i])
            
            # Only show yearly calculations if top_choice != 2
            if top_choice != 2:
                if menu == 4:
                    # Calculate yearly sum of previous 12 months
                    yearly_sums = []
                    years = data.index.year.unique()
                    for year in years[1:]:  # Start from the second year
                        end_date = f"{year}-01-01"
                        start_date = f"{year-1}-01-01"
                        yearly_sum = data[kw].loc[start_date:end_date].sum()
                        yearly_sums.append((pd.Timestamp(year, 1, 1), yearly_sum))
                    
                    # Create secondary y-axis for yearly sums
                    ax2 = ax.twinx()
                    
                    # Create bar plot for yearly sums on secondary y-axis
                    bar_positions, bar_heights = zip(*yearly_sums)
                    ax2.bar(bar_positions, bar_heights, width=365, alpha=0.1, color='red', align='center')
                    
                    # Set label for secondary y-axis
                    ax2.set_ylabel('Suma anual', color='red', fontsize=12)
                    ax2.tick_params(axis='y', labelcolor='red')
                else:
                    # Original yearly mean calculation
                    yearly_means = []
                    years = data.index.year.unique()
                    for idx, year in enumerate(years):
                        if idx == 0:  # First year
                            start_date = f"{year}-01-01"
                            end_date = f"{year}-06-30"
                        elif idx == len(years) - 1:  # Last year
                            start_date = f"{year}-07-01"
                            end_date = f"{year}-12-31"
                        else:  # All other years
                            start_date = f"{year-1}-07-01"
                            end_date = f"{year}-06-30"
                        
                        yearly_mean = data[kw].loc[start_date:end_date].mean()
                        yearly_means.append((pd.Timestamp(year, 1, 1), yearly_mean))
                    
                    # Create bar plot for yearly means
                    bar_positions, bar_heights = zip(*yearly_means)
                    ax.bar(bar_positions, bar_heights, width=365, alpha=0.1, color='red', align='center')

    # Grid lines for major ticks only
    ax.grid(True, which='major', linestyle='--', linewidth=0.3, color='grey', alpha=0.1)

    # Set y-axis to start at 0
    y_min, y_max = ax.get_ylim()
    ax.set_ylim(bottom=0, top=y_max)

    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_title(title, fontsize=16)

    def format_month(x, pos):
      if mdates.num2date(x).month == 7:
          ax.axvline(x, color='lightgrey',linestyle ='--', linewidth=0.3)
          return '|'
      else:
          return ''

    def format_month2(x, pos):
      if mdates.num2date(x).month != 1:
          ax.axvline(x, color='lightgrey',linestyle ='dotted', linewidth=0.3)
          return str(mdates.num2date(x).month)
      else:
          return ''

    # X-axis formatting based on time period
    if is_last_year:
        year_locator = mdates.YearLocator()
        ax.xaxis.set_major_locator(year_locator)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_minor_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_formatter(mdates.DateFormatter('%m'))
        ax.xaxis.set_minor_formatter(FuncFormatter(format_month2))
    else:
        # For other periods, years as major and months as minor
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax.xaxis.set_minor_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_formatter(FuncFormatter(format_month))

    ax.tick_params(axis='both', which='both', labelsize=8, labelrotation=45)

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

# Check Trends
def check_trends2(kw):
    global charts
    global image_markdown
    global current_year
    global actual_menu
    global menu
    global trends_results
    
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
    else:
        banner_msg(title=' Fuente de Datos: ' + kw.upper() + ' (' + actual_menu + ') ', margin=1,color1=YELLOW, color2=WHITE)

    # Set years2 based on menu
    if menu == 3 or menu == 5:
        years2 = -42
    elif menu == 4:
        years2 = 2 
    else:
        years2 = 0

#         1: "Google Trends",
#         2: "Google Books Ngrams",
#         3: "Bain - Usabilidad",
#         4: "Crossref.org",
#         5: "Bain - Satisfacción"
    
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
        if menu == 2 or menu == 4 or menu == 3 or menu == 5:
            avg_all_width = base_width * (72 + years2) / 20 * 2
            avg_20_width = base_width * 20 / 20 * 2
            avg_15_width = base_width * 15 / 20 * 2
            avg_10_width = base_width * 10 / 20 * 2
            avg_5_width = base_width * 5 / 20 * 2
            avg_1_width = base_width * 1 / 20 * 2.5

            bar_positions = [0, avg_all_width/1.55, avg_all_width/1.62 + avg_20_width, avg_all_width/1.71 + avg_20_width + avg_15_width,
                            avg_all_width/1.81 + avg_20_width + avg_15_width + avg_10_width,
                            avg_all_width/1.89 + avg_20_width + avg_15_width + avg_10_width + avg_5_width]
            bar_widths = [avg_all_width, avg_20_width, avg_15_width, avg_10_width, avg_5_width, avg_1_width]
            years_list = [72 + years2, 20, 15, 10, 5, 1]
            if top_choice == 2:
                years_list = [years_range, years2, 15, 10, 5, 1]
        else:
            avg_20_width = base_width * 20 / 20 * 2
            avg_15_width = base_width * 15 / 20 * 2
            avg_10_width = base_width * 10 / 20 * 2
            avg_5_width = base_width * 5 / 20 * 2
            avg_1_width = base_width * 1 / 20 * 2.5

            bar_positions = [0, avg_20_width, avg_20_width + avg_15_width,
                            avg_20_width + avg_15_width + avg_10_width,
                            avg_20_width + avg_15_width + avg_10_width + avg_5_width]
            bar_widths = [avg_20_width, avg_15_width, avg_10_width, avg_5_width, avg_1_width]
            years_list = [20, 15, 10, 5, 1]
            if top_choice == 2:
                years_list = [years2, 15, 10, 5, 1]
    else:
        if years_range > 20:
            avg_all_width = base_width * (years_range) / 20 * 2
            avg_20_width = base_width * 20 / 20 * 2
            avg_15_width = base_width * 15 / 20 * 2
            avg_10_width = base_width * 10 / 20 * 2
            avg_5_width = base_width * 5 / 20 * 2
            avg_1_width = base_width * 1 / 20 * 2.5

            bar_positions = [0, avg_all_width/1.55, avg_all_width/1.62 + avg_20_width, avg_all_width/1.71 + avg_20_width + avg_15_width,
                            avg_all_width/1.81 + avg_20_width + avg_15_width + avg_10_width,
                            avg_all_width/1.89 + avg_20_width + avg_15_width + avg_10_width + avg_5_width]
            bar_widths = [avg_all_width, avg_20_width, avg_15_width, avg_10_width, avg_5_width, avg_1_width]
            years_list = [years_range, years2, 15, 10, 5, 1]
        else:
            avg_20_width = base_width * years2 / 20 * 2
            avg_15_width = base_width * 15 / 20 * 2
            avg_10_width = base_width * 10 / 20 * 2
            avg_5_width = base_width * 5 / 20 * 2
            avg_1_width = base_width * 1 / 20 * 2.5

            bar_positions = [0, avg_20_width, avg_20_width + avg_15_width,
                            avg_20_width + avg_15_width + avg_10_width,
                            avg_20_width + avg_15_width + avg_10_width + avg_5_width]
            bar_widths = [avg_20_width, avg_15_width, avg_10_width, avg_5_width, avg_1_width]
            years_list = [years2, 15, 10, 5, 1]
                
    # Create the bar graph
    fig, ax = plt.subplots(figsize=(10,6))

    # Create bars
    if top_choice == 1:
        if menu == 2 or menu == 4:
            # Filter out None values and create bars only for valid data
            rects = [ax.bar(pos, avg, width, label=f'Media {years} Años ({current_year-years} - {current_year}): {eng_notation(avg)}', color=color)
                    for pos, width, avg, years, color in zip(bar_positions, bar_widths, 
                                                            [avg_all, avg_20, avg_15, avg_10, avg_5, avg_1],
                                                            years_list,
                                                            ['lightgrey', 'lightsteelblue', 'steelblue', 'dodgerblue', 'darkblue', 'midnightblue'])
                    if avg is not None]  # Add this condition
        else:
            rects = [ax.bar(pos, avg, width, label=f'Media {years} Años ({current_year-years} - {current_year}): {eng_notation(avg)}', color=color)
                    for pos, width, avg, years, color in zip(bar_positions, bar_widths, 
                                                            [avg_20, avg_15, avg_10, avg_5, avg_1],
                                                            years_list,
                                                            ['lightsteelblue', 'steelblue', 'dodgerblue', 'darkblue', 'midnightblue'])
                    if avg is not None]  # Add this condition
    else:
        if years_range > 20:
            rects = [ax.bar(pos, avg, width, label=f'Media {years} Años ({current_year-years} - {current_year}): {eng_notation(avg)}', color=color)
                    for pos, width, avg, years, color in zip(bar_positions, bar_widths, 
                                                            [avg_all, avg_20, avg_15, avg_10, avg_5, avg_1],
                                                            years_list,
                                                            ['lightgrey', 'lightsteelblue', 'steelblue', 'dodgerblue', 'darkblue', 'midnightblue'])]
        else:
            rects = [ax.bar(pos, avg, width, label=f'Media {years} Años ({current_year-years} - {current_year}): {eng_notation(avg)}', color=color)
                    for pos, width, avg, years, color in zip(bar_positions, bar_widths, 
                                                            [avg_20, avg_15, avg_10, avg_5, avg_1],
                                                            years_list,
                                                            ['lightsteelblue', 'steelblue', 'dodgerblue', 'darkblue', 'midnightblue'])]
    # Set the x-axis labels and title
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
    print('')
    print(f'Tendencia Normalizada de Desviación Anual (20 años): {trend_20}')

    # Calculate the moving average for the last 5 years (adjust as needed)
    last_20_years_data = trends_results['last_20_years_data'][kw]
    moving_avg = last_20_years_data.rolling(window=12).mean()  # 12-month moving average

    # Compare the last value of the moving average to the 20-year average
    trend2_20 = round(((moving_avg.iloc[-1] - avg_20) / avg_20) * 100, 2)
    print(f'Tendencia Suavizada por Media Móvil (20 años): {trend2_20}')
    print('')

    trends = {}
    trends[kw] = [trend_20, trend2_20]

    # Define the variable based on the menu selection
    if menu == 2 or menu == 4 :
        interest_var = "las publicaciones"
    elif menu == 3:
        interest_var = "la utilización"
    elif menu == 5:
        interest_var = "la satisfacción"
    else:
        interest_var = "el interés"

    print(f'{interest_var.capitalize()} promedio de los últimos 20 años para "{kw.upper()}" fue {eng_notation(trends_results["mean_last_20"][kw])}.')
    print(f'{interest_var.capitalize()} del último año para "{kw.upper()}" comparado con los últimos 20 años resulta con una tendencia de {trend_20}%.')

    trend = trend_20
    yearsago = 20
    mean_value = mean[kw]

    # Adjusted logic based on 1-100 index range
    if mean_value > 75:
        if abs(trend) <= 5:
            print(f'{interest_var.capitalize()} por "{kw.upper()}" es muy alto y estable durante los últimos {yearsago} años.')
        elif trend > 5:
            print(f'{interest_var.capitalize()} por "{kw.upper()}" es muy alto y está aumentando durante los últimos {yearsago} años.')
        else:
            print(f'{interest_var.capitalize()} por "{kw.upper()}" es muy alto pero está disminuyendo durante los últimos {yearsago} años.')
    elif mean_value > 50:
        if abs(trend) <= 10:
            print(f'{interest_var.capitalize()} por "{kw.upper()}" es alto y relativamente estable durante los últimos {yearsago} años.')
        elif trend > 10:
            print(f'{interest_var.capitalize()} por "{kw.upper()}" es alto y está aumentando significativamente durante los últimos {yearsago} años.')
        else:
            print(f'{interest_var.capitalize()} por "{kw.upper()}" es alto pero está disminuyendo significativamente durante los últimos {yearsago} años.')
    elif mean_value > 25:
        if abs(trend) <= 15:
            print(f'{interest_var.capitalize()} por "{kw.upper()}" es moderado y muestra algunas fluctuaciones durante los últimos {yearsago} años.')
        elif trend > 15:
            print(f'{interest_var.capitalize()} por "{kw.upper()}" es moderado pero está en tendencia creciente durante los últimos {yearsago} años.')
        else:
            print(f'{interest_var.capitalize()} por "{kw.upper()}" es moderado pero muestra una tendencia decreciente durante los últimos {yearsago} años.')
    else:
        if trend > 50:
            print(f'{interest_var.capitalize()} por "{kw.upper()}" es bajo pero está creciendo rápidamente durante los últimos {yearsago} años.')
        elif trend > 0:
            print(f'{interest_var.capitalize()} por "{kw.upper()}" es bajo pero muestra un ligero crecimiento durante los últimos {yearsago} años.')
        elif trend < -50:
            print(f'{interest_var.capitalize()} por "{kw.upper()}" es bajo y está disminuyendo rápidamente durante los últimos {yearsago} años.')
        else:
            print(f'{interest_var.capitalize()} por "{kw.upper()}" es bajo y muestra una ligera disminución durante los últimos {yearsago} años.')

    # Comparison last year vs. 20 years ago
    if avg_20 == 0:
        print(f'No había {interest_var} medible por "{kw.upper()}" hace {yearsago} años.')
    elif trend2_20 > 50:
        print(f'{interest_var.capitalize()} del último año es mucho más alto en comparación con hace {yearsago} años. Ha aumentado en un {trend2_20}%.')
    elif trend2_20 > 15:
        print(f'{interest_var.capitalize()} del último año es considerablemente más alto en comparación con hace {yearsago} años. Ha aumentado en un {trend2_20}%.')
    elif trend2_20 < -50:
        print(f'{interest_var.capitalize()} del último año es mucho más bajo en comparación con hace {yearsago} años. Ha disminuido en un {abs(trend2_20)}%.')
    elif trend2_20 < -15:
        print(f'{interest_var.capitalize()} del último año es considerablemente más bajo en comparación con hace {yearsago} años. Ha disminuido en un {abs(trend2_20)}%.')
    else:
        print(f'{interest_var.capitalize()} del último año es comparable al de hace {yearsago} años. Ha cambiado en un {trend2_20}%.')
    print('')

    return {
        'means': means[kw],
        'trends': trends[kw]
    }

def create_unique_filename(keywords, max_length=20):
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

# *************************************************************************************
# INIT VARIABLES
# *************************************************************************************
def init_variables():
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
    global csv_means_trends
    global trends_results
    global all_kw
    global current_year
    global charts
    global image_markdown
    global one_keyword
    global menu
    global current_year
    
    image_markdown = "\n\n# Gráficos\n\n"
    
    plt.style.use('ggplot')
    # Get current year
    current_year = datetime.now().year
    # pytrends = TrendReq(hl='en-US')
    wider = True
    one_keyword = False
    all_keywords= []
    charts=""
    
    if top_choice == 1:
        one_keyword=False
        # MAIN - KEYWORDS MENU
        all_keywords = []
        menu_options = ["Google Trends", "Google Book Ngrams", "Bain - Uso", "Crossref.org", "Bain - Satisfacción"]
        menu_opt = ["GT","GB","BR","CR","BS"]
        menu = main_menu()
        actual_menu = menu_options[menu-1]
        actual_opt = menu_opt[menu-1]
        # *****************************************************************************************************************
        data_filename, all_keywords = get_user_selections(tool_file_dic, menu)
        print(f'Comenzaremos el análisis de las siguiente(s) herramienta(s) gerencial(es): \n{GREEN}{all_keywords}{RESET}')
        print(f'Buscando la data en: {YELLOW}{data_filename}{RESET}')

        # Set the flag based on the count of keywords
        wider = True if len(all_keywords) <= 2 else False
        if len(all_keywords) < 2:
            one_keyword = True # Set one keyword
        trends_results = process_file_data(all_keywords, data_filename)
        print(all_keywords)
        if menu==2 or menu==4:
          csv_all_data = trends_results['all_data'].to_csv(index_label='date', float_format='%.2f', na_rep='N/A')
        csv_last_20_data = trends_results['last_20_years_data'].to_csv(index_label='date', float_format='%.2f', na_rep='N/A')
        csv_last_15_data = trends_results['last_15_years_data'].to_csv(index_label='date', float_format='%.2f', na_rep='N/A')
        csv_last_10_data = trends_results['last_10_years_data'].to_csv(index_label='date', float_format='%.2f', na_rep='N/A')
        csv_last_5_data = trends_results['last_5_years_data'].to_csv(index_label='date', float_format='%.2f', na_rep='N/A')
        csv_last_year_data = trends_results['last_year_data'].to_csv(index_label='date', float_format='%.2f', na_rep='N/A')
        all_kw = ", ".join(all_keywords)    
    else:
        all_keywords = get_all_keywords()
        
    filename = create_unique_filename(all_keywords)
    # unique_folder = os.path.join(gtrends_folder, filename)
    unique_folder = os.path.join(data_folder, filename)
    if not os.path.exists(unique_folder):
        os.makedirs(unique_folder)
        # Make the unique folder writable
        os.chmod(unique_folder, 0o777)

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
    global all_keywords
    global csv_means_trendsA
    
    # *************************************************************************************
    # Part 1 - Tendencias y Medias
    # *************************************************************************************

    banner_msg(' Part 1 - Tendencias y Medias ', color2=GREEN)
    csv_string = io.StringIO()
    csv_writer = csv.writer(csv_string)
    csv_writer.writerow(['Keyword', '20 Years Average', '15 Years Average', '10 Years Average', '5 Years Average', '1 Year Average', 'Trend NADT', 'Trend MAST'])
    
    if top_choice == 2:
        all_keywords = combined_dataset.columns.tolist()
    for kw in all_keywords:
        results = check_trends2(kw)
        csv_writer.writerow([kw] + results['means'] + results['trends'])

    csv_data = csv_string.getvalue()
    csv_means_trendsA = "Means and Trends\n</br> Trend NADT: Normalized Annual Desviation\n</br> Trend MAST: Moving Average Smoothed Trend\n\n"
    csv_means_trends = csv_data

    # *************************************************************************************
    # Part 2 - Comparación a lo largo del tiempo
    # *************************************************************************************

    banner_msg(' Part 2 - Comparación a lo largo del tiempo ', color2=GREEN)
    relative_comparison()

    # *************************************************************************************
    # Part 3 - Correlación - Regresión
    # *************************************************************************************

    banner_msg(' Part 3 - Correlación - Regresión ', color2=GREEN)
    analysis = analyze_trends(trends_results)
    if one_keyword:
      csv_correlation = None
      csv_regression = None
      print('Se requieren al menos dos variables para realizar los cálculos de correlación y regresión')
    else:
      csv_correlation = analysis['correlation']
      csv_regression = analysis['regression']
      
    # *************************************************************************************
    # Part 4 - Modelo ARIMA
    # *************************************************************************************

    banner_msg(' Part 4 - Modelo ARIMA ', color2=GREEN)
    # Call the arima_model function with the best parameters
    # mb: months back. Past
    # mf: months foward. future
    # ts: test size. Size of test in months
    # p, d, q: ARIMA parameters
    # auto = True: Calculate p,d,q. False: use given p, d, q values.
    csv_arima=arima_model(mb=120, mf=36, ts=18, p=2, d=1, q=0)

    # *************************************************************************************
    # Part 5 - Análisis Estacional
    # *************************************************************************************

    banner_msg(' Part 5 - Análisis estacional ', color2=GREEN)
    seasonal_analysis('last_10_years_data')

    # *************************************************************************************
    # Part 6 - Fourier Analisys
    # *************************************************************************************

    banner_msg(' Part 6 - Análisis de Fourier ', color2=GREEN)
    csv_fourier=fourier_analisys('last_20_years_data') #'last_20_years_data','last_15_years_data', ... , 'last_year_data'
    # to chage Y axis to log fo to line 131 in all functions

    
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

    banner_msg(' Part 7 - Análisis con IA ', color2=GREEN)

    if top_choice == 1:
        f_system_prompt = system_prompt_1.format(dbs=actual_menu)
    else:
        sel_sources = ", ".join(dbase_options[source] for source in selected_sources)
        f_system_prompt = system_prompt_2.format(selected_sources=sel_sources)
        csv_combined_data = combined_dataset.to_csv(index=True)

    # Add the selected_sources parameter to the format call
    if top_choice == 1:
        p_sp = prompt_sp.format(all_kws=all_keywords, selected_sources="")
    else:
        p_sp = prompt_sp.format(all_kws=actual_menu, selected_sources=sel_sources)

    if top_choice == 1:
        p_1 = temporal_analysis_prompt_1.format(dbs=actual_menu, all_kw=all_kw, \
                          csv_last_20_data=csv_last_20_data, csv_last_15_data=csv_last_15_data, csv_last_10_data=csv_last_10_data, \
                          csv_last_5_data=csv_last_5_data, csv_last_year_data=csv_last_year_data, \
                          csv_means_trends=csv_means_trends)        
    else:
        p_1 = temporal_analysis_prompt_2.format(selected_sources=sel_sources, all_kw=actual_menu, \
                          csv_combined_data=csv_combined_data, csv_means_trends=csv_means_trends, \
                          csv_corr_matrix=csv_correlation)
    
    n=0
    n+=1
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

    if not one_keyword:
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
            
        p_2 = cross_relationship_prompt_2.format(dbs=sel_sources, all_kw=actual_menu, 
                                               csv_corr_matrix=csv_corr_for_prompt, 
                                               csv_combined_data=csv_data_for_prompt)        
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
    if top_choice == 1:
      p_3 = trend_analysis_prompt_1.format(all_kw=all_keywords, dbs=actual_menu, csv_means_trends=csv_means_trends, csv_corr_matrix=csv_correlation, csv_regression=csv_regression)
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
      p_3 = trend_analysis_prompt_2.format(all_kw=actual_menu, selected_sources=sel_sources, 
                                          csv_corr_matrix=csv_correlation, 
                                          csv_combined_data=csv_for_prompt)
      print(f'\n\n\n{n}. Investigando patrones de tendencias entre las fuentes de datos...')  
    
    # Use the optimized gemini_prompt function with retry logic
    print("Enviando solicitud a la API de Gemini (esto puede tardar un momento)...")
    gem_industry_specific=gemini_prompt(f_system_prompt, p_3)
    
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

    n+=1
    if top_choice == 1:
      p_4 = arima_analysis_prompt_1.format(all_kw=all_keywords, dbs=actual_menu, arima_results=csv_arima)
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

    n+=1
    if top_choice == 1:
      p_5 = seasonal_analysis_prompt_1.format(all_kw=all_keywords, dbs=actual_menu, csv_seasonal=csv_seasonal)
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
          
      p_5 = seasonal_analysis_prompt_2.format(selected_keyword=actual_menu, selected_sources=sel_sources, 
                                            csv_seasonal=csv_seasonal_for_prompt, 
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
      p_6 = prompt_6_single_analysis.format(all_kw=all_keywords, dbs=actual_menu, csv_fourier=csv_fourier)
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
      
      p_6 = prompt_6_correlation.format(selected_keyword=actual_menu, 
                                      selected_sources=sel_sources, 
                                      csv_fourier=csv_fourier_for_prompt, 
                                      csv_combined_data=csv_data_for_prompt)        
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
    if top_choice == 1:
      p_conclusions = prompt_conclusions_standalone.format(all_kw=all_keywords, dbs=actual_menu, \
          temporal_trends=gem_temporal_trends, tool_relationships=gem_cross_keyword, industry_patterns=gem_industry_specific, \
          arima_predictions=gem_arima, seasonal_analysis=gem_seasonal, cyclical_patterns=gem_fourier)
    else:
      p_conclusions = prompt_conclusions_comparative.format(all_kw=actual_menu, selected_sources=sel_sources, \
          temporal_trends=gem_temporal_trends, tool_relationships=gem_cross_keyword, industry_patterns=gem_industry_specific, \
          arima_predictions=gem_arima, seasonal_analysis=gem_seasonal, cyclical_patterns=gem_fourier)          
    
    print(f'\n\n\n{n}. Sintetizando hallazgos y sacando conclusiones...\n')
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

def csv2table(csv_data, header_line=0):
        csv_lines= csv_data.strip().split('\n')
        headers = csv_lines[header_line].split(',')
        # Create markdown table header with smaller font and rotated text
        table = "<div class='table-wrapper'>\n<table class='data-table'>\n"
        table += "<tr>" + "".join([f"<th>{h}</th>" for h in headers]) + "</tr>\n"
        # Add data rows
        for line in csv_lines[1:]:
            values = line.split(',')
            table += "<tr>" + "".join([f"<td>{v}</td>" for v in values]) + "</tr>\n"
        table += "</table>\n</div>\n\n"
        return table
    
def report_pdf():
    global data_txt
    global charts
    global report
    global csv_means_trends
    global image_markdown
    
    data_txt = ''
    data_txt += "<div class='page-break'></div>\n"
    data_txt += "# Datos\n"
    if top_choice == 1:
        data_txt += "## Herramientas Gerenciales:\n"
        data_txt += ", ".join(all_keywords) + "\n"
    else:
        data_txt += "## Herramientas Gerenciales:\n"
        data_txt += actual_menu + "\n"
        data_txt += "### Fuentes de Datos:\n"
        data_txt += ", ".join(all_keywords) + "\n"
    data_txt += "\n\n\n"
    data_txt += f"## Datos de {actual_menu}\n"
    
    if top_choice == 1:
        year_adjust = 0
        if menu == 2:
            year_adjust = 2
            data_txt += f"### 72 años (Mensual) ({current_year-70+year_adjust} - {current_year-year_adjust})\n"
            #data_txt += csv_all_data.replace(',', ' | ').replace('\n', ' |\n| ') + "\n"
            data_txt += csv2table(csv_all_data)
        elif menu == 4:
            year_adjust = 2
            data_txt += f"### 74 años (Mensual) ({current_year-74} - {current_year})\n"
            #data_txt += csv_all_data.replace(',', ' | ').replace('\n', ' |\n| ') + "\n"
            data_txt += csv2table(csv_all_data)
        data_txt += f"### 20 años (Mensual) ({current_year-20} - {current_year})\n"
        #data_txt += csv_last_20_data.replace(',', ' | ').replace('\n', ' |\n| ') + "\n"
        data_txt += csv2table(csv_last_20_data)
        data_txt += f"### 15 años (Mensual) ({current_year-15} - {current_year})\n"
        #data_txt += csv_last_15_data.replace(',', ' | ').replace('\n', ' |\n| ') + "\n"
        data_txt += csv2table(csv_last_15_data)
        data_txt += f"### 10 años (Mensual) ({current_year-10} - {current_year})\n"
        #data_txt += csv_last_10_data.replace(',', ' | ').replace('\n', ' |\n| ') + "\n"
        data_txt += csv2table(csv_last_10_data)
        data_txt += f"### 5 años (Mensual) ({current_year-5} - {current_year})\n"
        #data_txt += csv_last_5_data.replace(',', ' | ').replace('\n', ' |\n| ') + "\n"
        data_txt += csv2table(csv_last_5_data)
    else:
        data_txt += csv2table(csv_combined_data)     
    data_txt += "\n\n\n"
    data_txt += "<div class='page-break'></div>\n"  # Add page break here
    data_txt += "## Datos Medias y Tendencias\n"
    data_txt += f"### Medias y Tendencias ({current_year-20} - {current_year})\n"
    data_txt += csv_means_trendsA
    data_txt += csv2table(csv_means_trends)
    if not one_keyword:
        data_txt += f"### Correlación\n"
        data_txt += csv2table(csv_correlation)        
        data_txt += f"### Regresión\n"
        data_txt += csv2table(csv_regression)
    data_txt += f"## ARIMA\n"
    for n in range(len(csv_arimaA)):
        data_txt += csv_arimaA[n]
        data_txt += csv2table(csv_arimaB[n])
    data_txt += f"## Estacional\n"
    data_txt += csv2table(csv_seasonal)
    data_txt += f"## Fourier\n"
    data_txt += csv2table(csv_fourier)
    data_txt += "<div class='page-break'></div>\n"  # Add another page break here
    report = "\n"
    report += "<div class='page-break'></div>\n"
    report += gem_temporal_trends_sp
    report += "<div class='page-break'></div>\n"
    if not one_keyword:
        report += gem_cross_keyword_sp
        report += "<div class='page-break'></div>\n"
    report += gem_industry_specific_sp
    report += "<div class='page-break'></div>\n"
    report += gem_arima_sp
    report += "<div class='page-break'></div>\n"
    report += gem_seasonal_sp
    report += "<div class='page-break'></div>\n"
    report += gem_fourier_sp
    report += "<div class='page-break'></div>\n"
    report += gem_conclusions_sp
    report += "<div class='page-break'></div>\n"

    # Add the image markdown to the report
    report += image_markdown

    toc = generate_markdown_toc(report)
    if menu == 2:
        start_year = current_year-70+year_adjust
        end_year = current_year-year_adjust
    elif menu == 4:
        start_year = current_year-74
        end_year = current_year
    else:
        start_year = current_year-20
        end_year = current_year
    report = f"<div style='text-align: center;'><h1>Análisis de {', '.join(all_keywords)} \n</h1></div><div style='text-align: center;'>({actual_menu}) ({str(start_year)} - {str(end_year)})</div>\n\n</br></br></br></br>**Tabla de Contenido**\n</br></br>{toc}\n\n</br></br>\n {report}"
    report += data_txt
    report += "\n---</br></br></br><small>\n"
    report += "\n**************************************************\n"
    report += f"(c) 2024 - {current_year} Diomar Anez & Dimar Anez\n</br>"
    report += f'Contacto: https://www.wiseconnex.com \n'
    report += "**************************************************\n"
    report += "</br></br>Todas las librerías utilizadas están bajo la debida licencia de sus autores y dueños de los derechos de autor. "
    report += "Algunas secciones de este reporte fueron generadas con la asistencia de Gemini AI. "
    report += "Este reporte está licenciado bajo la Licencia MIT. Para obtener más información, consulta https://opensource.org/licenses/MIT/ "
    now = datetime.now()
    date_time_string = now.strftime("%Y-%m-%d %H:%M:%S")
    report += "</br></br>Reporte generado el " + date_time_string + "\n"
    report += "</small>"

    html_content = f"""
    <html>
    <head>
        <style>
            @page {{
                @bottom-right {{
                    content: counter(page);
                }}
            }}
            body {{
                counter-reset: page;
            }}
            .page-break {{
                page-break-after: always;
                counter-increment: page;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
            }}
            th, td {{
                border: 1px solid black;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .table-wrapper {{
                width: 100%;
                overflow-x: auto;
                margin-bottom: 1em;
            }}
            .data-table {{
                font-size: 8pt;
                width: 100%;
                border-collapse: collapse;
                table-layout: fixed;
            }}
            .data-table th {{
                padding: 5px 2px;
                vertical-align: bottom;
                text-align: left;
                font-size: 8pt;
                /* Change white-space to normal to allow wrapping */
                white-space: normal;
                /* Add word-wrap for better control */
                word-wrap: break-word;
                /* Optional: add a max height if needed */
                max-height: 50px;
            }}
            .data-table td {{
                padding: 5px 2px;
                font-size: 7pt;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            @media print {{
                .table-wrapper {{
                    overflow-x: visible;
                }}
                
                .data-table {{
                    font-size: 7pt;
                    page-break-inside: avoid;
                }}
            }}            
        </style>
    </head>
    <body>
        {markdown.markdown(report, extensions=["tables"])}
    </body>
    </html>
    """

    # Replace existing page break divs with the new class
    html_content = html_content.replace('<div style="page-break-after: always;"></div>', '<div class="page-break"></div>')

    # Add page breaks after each graph
    html_content = html_content.replace('</img>', '</img><div class="page-break"></div>')

    pdf_path = os.path.join(unique_folder, f'{filename}.pdf')
    print(f"Saving PDF to: {pdf_path}")
    print(f"Number of images in report: {html_content.count('<img')}")
    weasyprint.HTML(string=html_content).write_pdf(pdf_path)
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
        3: "Reservado para función futura",
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
    dbase_options = {
        1: "Google Trends",
        2: "Google Books Ngrams",
        3: "Bain - Usabilidad",
        4: "Crossref.org",
        5: "Bain - Satisfacción"
    }
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
    global earliest_date
    global latest_date
    
    print(f"Processing dataset for source {source}")
    print(f"Original dataframe shape: {df.shape}")
    print(f"Original dataframe head:\n{df.head()}")
    print(f"Original dataframe dtypes:\n{df.dtypes}")

    # Ensure the index is datetime and timezone-naive
    df.index = pd.to_datetime(df.index).tz_localize(None)
    
    # Find the common date range across all datasets
    earliest_date = max(df.index.min() for df in all_datasets.values())
    latest_date = min(df.index.max() for df in all_datasets.values())
    print(f"Common date range: {earliest_date} to {latest_date}")

    # Handle Crossref data when combined with Bain or Google Books
    has_bain = any(src in selected_sources for src in [3, 5])
    has_crossref = 4 in selected_sources
    has_google_books = 2 in selected_sources

    if has_crossref and (has_bain or has_google_books):
        # If Crossref is combined with Bain or Google Books, 
        # adjust the date range to start from the earliest Bain/Google Books data
        bain_or_books_datasets = {
            src: data for src, data in all_datasets.items() 
            if src in ([2] if has_google_books else []) + ([3, 5] if has_bain else [])
        }
        earliest_other = max(df.index.min() for df in bain_or_books_datasets.values())
        earliest_date = max(earliest_date, earliest_other)
        print(f"Adjusted date range to match Bain/Google Books: {earliest_date} to {latest_date}")

    if 2 in selected_sources:
        # Resample data based on source
        if source == 2:
            df_resampled = df.loc[earliest_date:latest_date]
        elif source == 4:
            df = df.apply(pd.to_numeric, errors='coerce')
            df_resampled = df.resample('YE').sum()
            df_resampled.index = pd.to_datetime(df_resampled.index.strftime('%Y-01-01'))
            # Trim to common date range after resampling
            df_resampled = df_resampled.loc[earliest_date:latest_date]
        elif source in [1, 3, 5]:
            df_resampled = []
            years = range(earliest_date.year, latest_date.year + 1)
            
            for year in years:
                if year == earliest_date.year:
                    # First year: January to June only
                    period_data = df[
                        (df.index.year == year) & 
                        (df.index.month <= 6)
                    ]
                    if not period_data.empty:
                        mean_value = period_data.iloc[:, 0].mean()
                        df_resampled.append((f"{year}-01-01", mean_value))
                elif year == latest_date.year:
                    # Last year: July to December only
                    period_data = df[
                        (df.index.year == year) & 
                        (df.index.month >= 7)
                    ]
                    if not period_data.empty:
                        mean_value = period_data.iloc[:, 0].mean()
                        df_resampled.append((f"{year}-01-01", mean_value))
                else:
                    # Calculate mean from July of previous year to June of current year
                    period_data = df[
                        ((df.index.year == year - 1) & (df.index.month >= 7)) |
                        ((df.index.year == year) & (df.index.month <= 6))
                    ]
                    if len(period_data) == 12:  # Only calculate if we have full 12 months
                        mean_value = period_data.iloc[:, 0].mean()
                        df_resampled.append((f"{year}-01-01", mean_value))
            
            df_resampled = pd.DataFrame(df_resampled, columns=['Date', 'Value'])
            df_resampled.set_index('Date', inplace=True)
            df_resampled.index = pd.to_datetime(df_resampled.index)
        else:
            df_resampled = df.copy()

    else:
        # For monthly data, simply trim to the common date range
        df_resampled = df.loc[earliest_date:latest_date]

    print(f"Final dataframe shape: {df_resampled.shape}")
    print(f"Final dataframe head:\n{df_resampled.head()}")

    return df_resampled

def normalize_dataset(df):
    """
    Normalizes the dataset to a scale from 0 to 100.
    Args:
        df (pandas.DataFrame): The dataset to normalize.
    Returns:
        pandas.DataFrame: The normalized dataset.
    """
    min_val = df.min().min()
    max_val = df.max().max()
    normalized_df = (df - min_val) / (max_val - min_val) * 100
    return normalized_df

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


def get_file_data2(selected_keyword, selected_sources):
    # Obtener los nombres de archivo para la palabra clave y fuentes seleccionadas
    global menu  # Declare menu as global
    filenames = get_filenames_for_keyword(selected_keyword, selected_sources)

    datasets = {}
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
            datasets[source] = process_dataset(all_raw_datasets[source], source, all_raw_datasets, selected_sources)
            print(f"\nConjunto de datos procesado: {source}")
            print(datasets[source].head())
            print(f"Dimensiones: {datasets[source].shape}\n\n")

    print(datasets)
    
    # Normalize each dataset in datasets
    datasets_norm = {source: normalize_dataset(df) for source, df in datasets.items()}

    # Print the normalized datasets for verification
    for source, df_norm in datasets_norm.items():
        print(f"Normalized dataset for source {source}:")
        print(df_norm)
        print("\n")
    
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

def main():
    global top_choice
    global combined_dataset
    global trends_results
    global csv_combined_dataset
    global menu  # Ensure menu is declared as global here
    
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
            # Flujo existente para informe individual
            init_variables()
            results()
            ai_analysis()
            report_pdf()
            
        elif top_choice == 2:
            # Nuevo flujo para comparación entre fuentes de datos
            init_variables()
            datasets_norm, selected_sources = process_and_normalize_datasets(all_keywords)
            combined_dataset = create_combined_dataset(datasets_norm, selected_sources, dbase_options)
            csv_combined_dataset = combined_dataset.to_csv(index=True)  
            print(combined_dataset)
            print(csv_combined_dataset)
            # Set menu to a default value if it's not already set
            if 'menu' not in globals() or menu is None:
                menu = 1  # Default value, adjust as needed based on your application logic
            trends_results = process_file_data(all_keywords, "")
            results()
            ai_analysis()
            report_pdf()
            
        elif top_choice == 3:
            print(f"{YELLOW}Esta función estará disponible próximamente.{RESET}")
    # Cerrar el archivo null y restaurar stderr al finalizar
    null.close()
    sys.stderr = stderr

    
if __name__ == "__main__":
    main()