#import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
#import matplotlib.ticker as ticker
#import matplotlib.patches as mpatches
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
import numpy as np
import pandas as pd
import time  # Import the time module
import datetime
#import warnings
#import pdb
import re
import hashlib
import seaborn as sns
import itertools
import google.generativeai as genai
import statsmodels.api as sm
import altair as alt
import scipy.fftpack as fftpack
import markdown
import weasyprint
import os
#import platform
import csv
import io
import sys
#import ipdb
import math
import paramiko
from io import StringIO
#from google.colab import auth
from googleapiclient.discovery import build
from dotenv import load_dotenv
#from google.colab import drive
from PIL import Image
from statsmodels.tsa.arima.model import ARIMA
from pmdarima.arima import auto_arima
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller
from statsmodels.formula.api import ols
from IPython.display import display, Markdown
#from google.colab import userdata
from matplotlib.ticker import MultipleLocator, FuncFormatter, AutoMinorLocator
from scipy.stats import pearsonr
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.metrics import mean_squared_error, mean_absolute_error
from itertools import combinations
from sklearn.metrics import r2_score  # Import r2_score function
from enum import auto
#%matplotlib inline
#*** Google Books Nviewer
import requests
import scipy.interpolate as interp
from scipy.interpolate import CubicSpline
from mpl_toolkits.axes_grid1 import make_axes_locatable

# AI Prompts imports 
from prompts import system_prompt, prompt_1, prompt_2, prompt_3, prompt_4, prompt_5, prompt_6, prompt_conclusions
# Tools Dictionary
from tools import tool_file_dic

plt.ion()

#Mount MyDrive
# drive.mount('/content/drive')
# gtrends_folder = '/content/drive/MyDrive/GTrends'
# if not os.path.exists(gtrends_folder):
#      os.makedirs(gtrends_folder)

# Create a 'data' folder in the current directory
data_folder = 'data'
if not os.path.exists(data_folder):
    os.makedirs(data_folder)
    # Make the folder writable (0o777 is octal for rwxrwxrwx)
    os.chmod(data_folder, 0o777)
    
    
# *************************************************************************************
#   FUNCTIONS
# *************************************************************************************

# @title All Functions

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

def banner_msg (title="", color1=WHITE, color2=WHITE, margin=12, char='*'):
  qty=len(title)+margin*2
  print(f'{color2}\n\n{char*qty}\n{char*margin}{color1}{title}{color2}{char*margin}\n{char*qty}{RESET}')

# return a number in engineering notation
def eng_notation(number):
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

#*** GBNgram

def linear_interpolation(df, kw):
    x = df.index  # Keep index as DatetimeIndex
    y = df[kw].values

    # Use numpy.interp for linear interpolation
    x_interp = pd.date_range(df.index.min().date(), df.index.max().date(), freq='MS')
    y_interp = np.interp(x_interp, x, y)

    # Create a new DataFrame with the interpolated values
    df_interpolated = pd.DataFrame(y_interp, index=x_interp, columns=[kw])

    #PPRINT(f'DF INTERPOLATED:\n{df_interpolated}')
    return df_interpolated

# Create a cubic interpolation function
def cubic_interpolation(df, kw):
    x = df.index
    y = df[kw].values

    # Create a Cubic Spline interpolator
    spline = CubicSpline(x, y)
    # Generate interpolated values for all months within the original year range
    start_year_tm = df.index.min()
    start_year = start_year_tm.date()
    end_year_tm = df.index.max()
    end_year = end_year_tm.date()
    x_interp = pd.date_range(start_year, end_year, freq='MS')
    # Evaluate the spline at the interpolated points
    y_interp = spline(x_interp)

    # Create a new DataFrame with the interpolated values and set 'Month' as index
    df_interpolated = pd.DataFrame(y_interp, index=x_interp, columns=[kw])

    #PPRINT(f'DF INTERPOLATED:\n{df_interpolated}')
    return df_interpolated

# Create a BSpline interpolation function
def bspline_interpolation(df, kw):
    # Assuming your data is in a DataFrame called 'df' with columns 'year' and 'value'
    x = df.index
    y = df[kw].values

    # Create a B-spline interpolator
    tck = interp.splrep(x, y, k=3)  # k=3 for a cubic B-spline
    # Generate interpolated values for all months within the original year range
    start_year_tm = df.index.min()
    start_year = start_year_tm.date()
    end_year_tm = df.index.max()
    end_year = end_year_tm.date()
    x_interp = pd.date_range(start_year, end_year, freq='MS')  # Monthly intervals
    # x_interp = pd.date_range(start_year, end_year + pd.DateOffset(years=1), freq='MS')  # Monthly intervals
    y_interp = interp.splev(x_interp, tck)

    # Create a new DataFrame with the interpolated values and set 'Month' as index
    df_interpolated = pd.DataFrame(y_interp, index=x_interp, columns=[kw])

    #PPRINT(f'DF INTERPOLATED:\n{df_interpolated}')
    return df_interpolated

#*** END GNNgram

# Displays the main menu and prompts the user to select an option.
def main_menu():
    banner_msg(" Menú principal ", YELLOW, WHITE)
    options = {
        1: "Google Trends",
        2: "Google Books ngrams",
        3: "Bain Research",
        4: "Crossref",
        5: "All"
    }
    for index, option in enumerate(options.values(), 1):
        print(f"{index}. {option}")
    while True:
        selection = input("\nIngrese el número de la opción a seleccionar: ")
        try:
            index = int(selection) - 1  # Subtract 1 as indices start from 0
            if 0 <= index < len(options):
                selected_option = list(options.keys())[index]
                if index == 4:
                  print("Trabajando en esta opción... vuelva luego.")
                  sys.exit()
                return selected_option
            else:
                print(f"{RED}Opción no válida.{RESET}")
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
            print("Trabajando en esta opción... vuelva luego.")
            sys.exit()
        return selected_data_file_name, selected_strings
      else:
        print(f"{RED}Indice no válido.{RESET}")
    except ValueError:
      print(f"{YELLOW}Por favor, ingrese un número válido.{RESET}")
  return selected_data_file_name, selected_strings

def get_file_data(filename):
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
        if heading_level < level:
            # Handle nested headings by closing previous sections
            for _ in range(level - heading_level):
                toc_items.append("  ")  # Indent for nested levels
            toc_items.append("  ")  # Add an extra space for clarity
        toc_items.append(f"- {heading_text}")
        level = heading_level
    return "</br>".join(toc_items)

global image_markdown
image_markdown = "\n\n# Gráficos\n\n"

def add_image_to_report(title, filename):
    global image_markdown
    full_path = os.path.abspath(os.path.join('./', unique_folder, filename))
    print(f"Adding image to report: {full_path}")
    if os.path.exists(full_path):
        print(f"Image file exists: {full_path}")
    else:
        print(f"Image file does not exist: {full_path}")
    image_markdown += f"## {title}\n\n"
    image_markdown += f"<img src='{filename}' style='max-width: 100%; height: auto;'>\n\n"

def report_pdf():
    global data_txt
    global charts
    global report
    global csv_means_trends
    global image_markdown
    data_txt = ''
    data_txt += "\n\n\n"
    data_txt += "#Datos\n"
    data_txt += "## Herramientas Gerenciales:\n"
    data_txt += ", ".join(all_keywords) + "\n"
    data_txt += "\n\n\n"
    data_txt += f"## Datos de {actual_menu}\n"
    year_adjust = 0
    if menu == 2:
        year_adjust = 2
        data_txt += f"### 72 años (Mensual) ({current_year-70+year_adjust} - {current_year-year_adjust})\n"
        data_txt += csv_all_data + "\n"
    elif menu == 4:
        year_adjust = 2
        data_txt += f"### 74 años (Mensual) ({current_year-74} - {current_year})\n"
        data_txt += csv_all_data + "\n"
    data_txt += f"### 20 años (Mensual) ({current_year-20} - {current_year})\n"
    data_txt += csv_last_20_data + "\n"
    data_txt += f"### 15 años (Mensual) ({current_year-15} - {current_year})\n"
    data_txt += csv_last_15_data + "\n"
    data_txt += f"### 10 años (Mensual) ({current_year-10} - {current_year})\n"
    data_txt += csv_last_10_data + "\n"
    data_txt += f"### 5 años (Mensual) ({current_year-5} - {current_year})\n"
    data_txt += csv_last_5_data + "\n"
    data_txt += f"### 1 año (Mensual) ({current_year-1} - {current_year})\n"
    data_txt += csv_last_year_data + "\n"
    data_txt += "\n\n\n"
    data_txt += "## Datos Medias y Tendencias\n"
    data_txt += f"### Medias y Tendencias ({current_year-20} - {current_year})\n"
    data_txt += csv_means_trends.replace("\n", "</br>") + "\n"
    if not one_keyword:
        data_txt += f"### Correlacion\n"
        data_txt += str(csv_correlation) + "\n"
        data_txt += f"### Regresion\n"
        data_txt += str (csv_regression) + "\n"
    data_txt += f"## ARIMA\n"
    data_txt += "<blockquote>\n" + str(csv_arima) + "\n</blockquote>\n"
    data_txt += f"## Estacional\n"
    data_txt += str(csv_seasonal) + "\n"
    data_txt += f"## Fourier\n"
    data_txt += str(csv_fourier) + "\n"
    report = "\n"
    report += gem_temporal_trends_sp
    if not one_keyword:
        report += gem_cross_keyword_sp
    report += gem_industry_specific_sp
    report += gem_arima_sp
    report += gem_seasonal_sp
    report += gem_fourier_sp
    report += gem_conclusions_sp

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
    report = f"#Análisis de {', '.join(all_keywords)} ({actual_menu}) ({str(start_year)} - {str(end_year)})\n\n</br></br> *Tabla de Contenido*\n</br></br>{toc}\n\n</br></br> {report}"
    report += data_txt
    report += "\n---</br></br></br><small>\n"
    report += "\n**************************************************\n"
    report += f"(c) 2024 - {current_year} Diomar Anez & Dimar Anez\n</br>"
    report += f'Contacto: https://www.wiseconnex.com \n'
    report += "**************************************************\n"
    report += "</br></br>Todas las librerías utilizadas están bajo la debida licencia de sus autores y dueños de los derechos de autor. "
    report += "Algunas secciones de este reporte fueron generadas con la asistencia de Gemini AI. "
    report += "Este reporte está licenciado bajo la Licencia MIT. Para obtener más información, consulta https://opensource.org/licenses/MIT/ "
    now = datetime.datetime.now()
    date_time_string = now.strftime("%Y-%m-%d %H:%M:%S")
    report += "</br></br>Reporte generado el " + date_time_string + "\n"
    report += "</small>"
    html_content = markdown.markdown(report, extensions=["tables"])

    # Convert image references to base64
    def img_to_base64(img_path):
        with open(img_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()

    # Replace image src with base64 encoded images
    for img_tag in re.findall(r'<img.*?src="(.*?)".*?>', html_content):
        img_path = os.path.join(unique_folder, img_tag)
        if os.path.exists(img_path):
            b64_img = img_to_base64(img_path)
            html_content = html_content.replace(img_tag, f"data:image/png;base64,{b64_img}")
        else:
            print(f"Image not found: {img_path}")

    pdf_path = os.path.join(unique_folder, f'{filename}.pdf')
    print(f"Saving PDF to: {pdf_path}")
    print(f"Number of images in report: {html_content.count('<img')}")
    weasyprint.HTML(string=html_content).write_pdf(pdf_path)
    char='*'
    title='********** ' + filename + ' PDF REPORT SAVED **********'
    qty=len(title)
    print(f'\x1b[33m\n\n{char*qty}\n{title}\n{char*qty}\x1b[0m')

# Fourier Analisys
def fourier_analisys(period='last_year_data'):
  global charts
  global image_markdown
  char='*'
  title=' Análisis de Fourier '
  qty=len(title)
  print(f'\x1b[33m\n\n{char*qty}\n{title}\n{char*qty}\x1b[0m')
  banner_msg("Análisis de Fourier",margin=1,color1=YELLOW,color2=WHITE)
  csv_fourier="\nAnálisis de Fourier\n"
  for keyword in all_keywords:
      # Extract data for the current keyword
      data = trends_results[period][keyword]
      print(f"\nPalabra clave: {keyword} ({actual_menu})\n")
      csv_fourier += f"Palabra clave: {keyword}\n"
      # Create time vector
      time_vector = np.arange(len(data))
      csv_fourier += f"Vector de tiempo: \n{time_vector}\n"
      # Ensure data is a properly aligned NumPy array
      data = np.asarray(data, dtype=float).copy()
      # Perform Fourier transform
      fourier_transform = fftpack.fft(data)
      print(fourier_transform)
      csv_fourier += f"Transformada de Fourier: \n{fourier_transform}\n"
      # Calculate frequency axis
      freq = fftpack.fftfreq(len(data))
      csv_fourier += f"Eje de frecuencia: \n{freq}\n"
      # Plot the magnitude of the Fourier transform
      plt.figure(figsize=(12, 10))  # Create a new figure for each keyword
      plt.plot(freq, np.abs(fourier_transform), color='#66B2FF')
      plt.xlabel('Frecuencia (ciclos/año)')
      #plt.yscale('log')
      plt.ylabel('Magnitud')  # Update label to reflect 1/2 log scale
      plt.title(f'Transformada de Fourier para {keyword} ({actual_menu})')
      # Save the plot to the unique folder
      image_filename = f'{filename}_fourier_{keyword[:3]}.png'
      plt.savefig(os.path.join(unique_folder, image_filename), bbox_inches='tight')
      add_image_to_report(f'Transformada de Fourier para {keyword}', image_filename)
      charts += f'Transformada de Fourier para {keyword} ({image_filename})\n\n'
      plt.show()
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
    csv_seasonal = '\n****** ANÁLISIS ESTACIONAL ********\n'
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
    # Analyze each keyword
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
        csv_seasonal += f"\nAnalyzing {keyword} ({actual_menu}):\n"
        # Extract the series for the keyword
        series = data[keyword]
        # Decompose the time series
        seasonal = decompose_series(series)
        
        if seasonal is None:
            continue  # Skip to the next keyword if decomposition is not possible

        seasonal_index = seasonal / series.mean()
        print(seasonal_index)
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            csv_seasonal+=seasonal_index.to_csv(index=False)
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
        plt.xlabel('Aos')
        plt.ylabel('Indice')
        plt.grid(True)
        # Save the plot to the unique folder
        image_filename = f'{filename}_season_{keyword[:3]}.png'
        plt.savefig(os.path.join(unique_folder, image_filename), bbox_inches='tight')
        add_image_to_report(f'Indice de Temporada para {keyword}', image_filename)
        charts += f'Indice de Temporada para {keyword} ({image_filename})\n\n'
        plt.show()
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
  for col in numeric_columns:
      banner_msg(f'Modelo ARIMA para: {col} {actual_menu}',margin=1,color1=YELLOW,color2=WHITE)
      csv_arima += f"\n\nFitting ARIMA model for {col} ({actual_menu})\n"
      
      # Check if the column has enough non-zero values
      if (train[col] != 0).sum() <= 10:  # Adjust this threshold as needed
          print(f"Skipping {col} due to insufficient non-zero values")
          csv_arima += f"Skipping {col} due to insufficient non-zero values\n"
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
          csv_arima += f'\n{results.summary()}'

          # Prepare data for plotting (last 24 months)
          last_months = train[col].iloc[-mb:]
          # Make predictions (adjust steps as needed)
          predictions, conf_int = best_model.predict(n_periods=mf, return_conf_int=True)
          predictions = results.forecast(steps=mf)
          # Calculate RMSE and MAE
          actual = test[col]
          predicted = predictions
          if len(predictions) > len(test[col]):
            predicted = predictions[:len(test[col])]
          rmse = mean_squared_error(actual, predicted, squared=False)
          mae = mean_absolute_error(actual, predicted)
          print(f"Predicciones para {col} ({actual_menu}):\n{predictions}")
          csv_arima += f"\nPredictions for {col} ({actual_menu}):\n{predictions}"
          print(f"\nError Cuadrático Medio Raíz (ECM Raíz) RMSE: {rmse}\nError Absoluto Medio (EAM) MAE: {mae}\n")
          csv_arima += f"\nRMSE: {rmse}, MAE: {mae}"
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
          ci_fill = ax.fill_between(predictions.index, conf_int[:, 0], conf_int[:, 1], alpha=0.1, color='b', label='Intervalo de Confidencia')
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
          train_min = train[col].min()
          train_max = train[col].max()
          buffer = (train_max - train_min) * 0.1  # Add a 10% buffer
          ax.set_ylim(train_min - buffer, train_max + buffer)
          #plt.autoscale(ax=ax)  # Fine-tune based on actual data
          # Adjust layout to prevent cutoff of tick labels
          fig.tight_layout()
          # Save the plot
          image_filename = f'{filename}_arima_{col[:3]}.png'
          plt.savefig(os.path.join(unique_folder, image_filename), bbox_inches='tight')
          add_image_to_report(f'Modelo ARIMA para {col}', image_filename)
          charts += f'Modelo ARIMA para {col} ({image_filename})\n\n'
          plt.show()
      except Exception as e:
          print(f"Error fitting ARIMA model for {col}: {str(e)}")
          csv_arima += f"Error fitting ARIMA model for {col}: {str(e)}\n"
          continue

  csv_arima="".join(csv_arima)
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
  if menu == 2:
    mean = data.mean()
  else:
    mean = round(data.mean(), 2)
  return mean

#  Fetches and processes Google Trends data for different time periods.
def process_file_data(all_kw, d_filename):
  # Group data and calculate means
  all_data = get_file_data(d_filename)
  #PPRINT(f"\n{all_data}")

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
    
    print(f"\nCreando gráficos de comparación relativa...")

    fig = plt.figure(figsize=(24, 35))  # Increased width from 22 to 24

    x_pos = np.arange(len(all_keywords))

    # Define colors here
    colors = plt.cm.rainbow(np.linspace(0, 1, len(all_keywords)))

    window_size = 10

    # Calculate the maximum y-value across all datasets
    all_means = [
        trends_results['mean_all'] if menu == 2 or menu == 4 else None,
        trends_results['mean_last_20'],
        trends_results['mean_last_15'],
        trends_results['mean_last_10'],
        trends_results['mean_last_5'],
        trends_results['mean_last_year']
    ]
    max_y_value = max(mean.max() for mean in all_means if mean is not None)

    # Determine the number of rows in the gridspec
    total_rows = 7 if menu == 2 or menu == 4 else 6

    # Create grid spec with 9 columns and the determined number of rows
    gs = fig.add_gridspec(total_rows, 9, height_ratios=[0.2] + [1] * (total_rows - 1))

    # Define slices for odd and even subplots
    axODD = slice(0, 7)  # Line graph takes 7 columns
    axEVEN = slice(8, 10)  # Bar graph takes 2 columns, leaving one column (7) blank

    i = 1
    # all data
    if menu == 2 or menu == 4:
        ax1 = fig.add_subplot(gs[i, axODD])
        ax2 = fig.add_subplot(gs[i, axEVEN])
        setup_subplot(ax1, trends_results['all_data'], trends_results['mean_all'], title_odd_charts, f'Período de {72 if menu == 2 else 74} años\n({current_year - (72 if menu == 2 else 74)}-{current_year})', window_size, colors)
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
    i += 1

    # Last 1-year
    ax11 = fig.add_subplot(gs[i, axODD])
    ax12 = fig.add_subplot(gs[i, axEVEN])
    setup_subplot(ax11, trends_results['last_year_data'], trends_results['mean_last_year'], '', f'Período de 1 año\n({current_year - 1}-{current_year})', window_size, colors, is_last_year=True)
    setup_bar_subplot(ax12, trends_results['mean_last_year'], '', max_y_value, x_pos, colors)

    # Add legend at the bottom, outside of the plots
    handles, labels = ax3.get_legend_handles_labels()
    labels = [f"{label} ({actual_menu})" for label in labels]
    fig.legend(handles, labels, loc='lower right', bbox_to_anchor=(0.55, 0.05),
                ncol=len(all_keywords), fontsize=12)

    # Adjust the layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.95, bottom=0.1, hspace=0.3, wspace=0.4)  # Reduced wspace from 0.5 to 0.4

    # Save the plot to the unique folder
    image_filename = f'{filename}_overtime.png'
    plt.savefig(os.path.join(unique_folder, image_filename), bbox_inches='tight')
    add_image_to_report('Interés por período', image_filename)
    charts += f'Interés por período ({image_filename})\n\n'
    plt.show()

    print(f"\nGráficos de comparación relativa creados.")

def setup_subplot(ax, data, mean, title, ylabel, window_size=10, colors=None, is_last_year=False):
    if colors is None:
        colors = plt.cm.rainbow(np.linspace(0, 1, len(all_keywords)))
    
    # Plot data
    for i, kw in enumerate(all_keywords):
        if menu == 2:
            ax.plot(data[kw].index, data[kw], label=kw, color=colors[i])
        else:
            smoothed_data = smooth_data(data[kw], window_size)
            ax.plot(data[kw].index, smoothed_data, label=kw, color=colors[i])
            
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
    ax.grid(True, which='major', linestyle='--', linewidth=0.5, color='grey', alpha=0.1)  # Reduced grid line opacity to 0.1

    # Create bar plot with corresponding value labels
    bar_container = ax.bar(x_pos, mean[:len(all_keywords)], align='center', color='blue')  # Changed bar color to blue

    # Add value labels using `bar_label`
    ax.bar_label(bar_container, fmt=eng_format)  # Format values (optional)

    ax.set_title(title, fontsize=16)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(replace_spaces_with_newlines(all_keywords), rotation=0, ha='center', fontsize=8)
    ax.tick_params(axis='y', which='major', labelsize=8)

    # Set y-axis limit to the maximum value
    ax.set_ylim(0, y_max)

    # Adjust y-axis limits to avoid clipping labels (if needed)
    plt.setp(ax.get_yticklabels(), rotation=45, ha='right')  # Rotate y-axis labels if crowded
    plt.tight_layout()  # Adjust spacing to avoid clipping labels

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
    data = trends_results['last_20_years_data']
    mean = trends_results['mean_last_20']
    banner_msg(title=' Herramienta: ' + kw.upper() + ' (' + actual_menu + ') ', margin=1,color1=YELLOW, color2=WHITE)

    # Set years2 based on menu
    years2 = 2 if menu == 4 else 0

    # Calculate averages
    if menu == 2 or menu == 4:
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

    # Calculate relative widths
    if menu == 2 or menu == 4:
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

    # Create the bar graph
    fig, ax = plt.subplots(figsize=(10,6))

    # Create bars
    if menu == 2 or menu == 4:
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
    ax.set_title(f'Media a lo largo del tiempo de:\n{kw} según {actual_menu}')

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
    image_filename = f'{filename}_means_{kw[:3]}.png'
    plt.savefig(os.path.join(unique_folder, image_filename), bbox_inches='tight')
    add_image_to_report(f'Medias de {kw}', image_filename)
    charts += f'Medias de {kw} ({image_filename})\n\n'

    # Show the plot
    if menu == 2:
        plt.yscale('log')
    plt.show()

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
    if menu == 2 or menu == 4:
        interest_var = "las publicaciones"
    elif menu == 3:
        interest_var = "la utilización"
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
        char='*'
        title=' Correlación - Mapa de Calor '
        qty=len(title)
        print(f'\x1b[33m\n\n{char*qty}\n{title}\n{char*qty}\x1b[0m')
        # Save the plot to the unique folder
        image_filename = f'{filename}_heatmap.png'
        plt.savefig(os.path.join(unique_folder, image_filename), bbox_inches='tight')
        add_image_to_report('Mapa de Calor de Correlación', image_filename)
        charts += f'Mapa de Calor ({image_filename})\n\n'
        plt.show()

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
        all_combinations = []
        for r in range(2, len(keywords) + 1):
            all_combinations.extend(combinations(keywords, r))
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
            csv_output += f"\nRegression for keywords: {combo}\n"
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
          for i in range(2, max_keywords + 1):
            combinations = itertools.combinations(columns, i)
            for combo in combinations:
              if len(combo) == 2:
                # Single scatter plot for two keywords
                fig, ax = plt.subplots(figsize=(7, 7))
                ax.scatter(df[combo[0]], df[combo[1]])
                ax.set_xlabel(combo[0])
                ax.set_ylabel(combo[1])
              plt.tight_layout()
              image_filename = f'{filename}_scatter_{combo[0][:3]}{combo[1][:3]}.png'
              plt.savefig(os.path.join(unique_folder, image_filename), bbox_inches='tight')
              add_image_to_report(f'Gráfico de Dispersión para {", ".join(combo)}', image_filename)
              charts += f'Gráfico de Dispersión para {", ".join(combo)} ({image_filename})\n\n'
              plt.show()

        # Scatter plot
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
      'regression': csv_regression
    }
    
# *************************************************************************************
# INIT VARIABLES
# *************************************************************************************

# Suppress the FutureWarning related to the pytrends library
# warnings.filterwarnings("ignore", category=FutureWarning, module="pytrends.request")
plt.style.use('ggplot')

# Get current year
current_year = datetime.datetime.now().year

# pytrends = TrendReq(hl='en-US')
all_keywords= []
keywords = []
csv_correlation = None
csv_regression = None
csv_arima = None

cat = '0'
geo = ''
gprop = ''
charts=""
data_txt=""
report=""
colors=None
one_keyword=False



# *************************************************************************************
# MAIN - KEYWORDS MENU
# *************************************************************************************

# ****** K E Y W O R D S *******************************************************************************************
all_keywords = []
menu_options = ["Google Trends", "Google Ngrams", "Bain Research", "Crossref.org", "All"]
menu_opt = ["GT","GB","BR","CR","AL"]

menu = main_menu()
actual_menu = menu_options[menu-1]
actual_opt = menu_opt[menu-1]

# *****************************************************************************************************************

data_filename, all_keywords = get_user_selections(tool_file_dic, menu)

print(f'Comenzaremos el análisis de las siguiente(s) herramienta(s) gerencial(es): \n{GREEN}{all_keywords}{RESET}')
print(f'Buscando la data en: {YELLOW}{data_filename}{RESET}')

# *****************************************************************************************************************

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


 
# ********************************************

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
csv_seasonal_index = None
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


# *************************************************************************************
# Part 1 - Tendencias y Medias
# *************************************************************************************

banner_msg(' Part 1 - Tendencias y Medias ', color2=GREEN)
csv_string = io.StringIO()
csv_writer = csv.writer(csv_string)
csv_writer.writerow(['Keyword', '20 Years Average', '15 Years Average', '10 Years Average', '5 Years Average', '1 Year Average', 'Trend NADT', 'Trend MAST'])

for kw in all_keywords:
    results = check_trends2(kw)
    csv_writer.writerow([kw] + results['means'] + results['trends'])

csv_data = csv_string.getvalue()
csv_means_trends = "Means and Trends\n</br> Trend NADT: Normalized Annual Desviation\n</br> Trend MAST: Moving Average Smoothed Trend\n\n" + csv_data

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

banner_msg(' Part 7 - Análisis con IA ', color2=GREEN)
api_key_name = 'GOOGLE_API_KEY'

def gemini_prompt(system_prompt,prompt,m='flash'):
  system_instructions = system_prompt

  #print('\n**************************** INPUT ********************************\n')
  #print(f'System Instruction: \n{system_instructions} \nPrompt: \n{prompt}')

  if m == 'pro':
    model = 'gemini-1.5-pro' # @#param {type: "string"} ["gemini-1.0-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
  else:
    model = 'gemini-1.5-flash' # @#param {type: "string"} ["gemini-1.0-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
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
  #api_key = userdata.get(api_key_name)
  genai.configure(api_key=api_key)
  model = genai.GenerativeModel(model, system_instruction=system_instructions)
  config = genai.GenerationConfig(temperature=temperature, stop_sequences=[stop_sequence])
  response = model.generate_content(contents=[prompt], generation_config=config)
  return response.text

prompt_sp=f'Translate this Markdown text to spanish, using an academic language, and an enterprise approach. \
If you found any of this words: {",".join(all_keywords)}, please do not translate it. This is the text: '

f_system_prompt = system_prompt.format(dbs=actual_menu)

p_1 = prompt_1.format(all_kw, \
                      csv_last_20_data, csv_last_15_data, csv_last_10_data, csv_last_5_data, csv_last_year_data, \
                      all_kw, csv_means_trends)
n=0
n+=1
print(f'\n\n\n{n}. Analizando tendencias temporales...')
gem_temporal_trends=gemini_prompt(f_system_prompt,p_1)
prompt_spanish=f'{prompt_sp} {gem_temporal_trends}'
gem_temporal_trends_sp=gemini_prompt(f_system_prompt,prompt_spanish)
#display(Markdown(gem_temporal_trends_sp))
print(gem_temporal_trends_sp)

if not one_keyword:
  n+=1
  p_2 = prompt_2.format(all_kw, csv_correlation, csv_regression)
  print(f'\n\n\n{n}. Analizando relaciones entre palabras clave...')
  gem_cross_keyword=gemini_prompt(f_system_prompt,p_2)
  prompt_spanish=f'{prompt_sp} {gem_cross_keyword}'
  gem_cross_keyword_sp=gemini_prompt(f_system_prompt,prompt_spanish)
  #display(Markdown(gem_cross_keyword_sp))
  print(gem_cross_keyword_sp)
else:
  gem_cross_keyword=""
  csv_correlation=""
  csv_regression=""

n+=1
p_3 = prompt_3.format(csv_means_trends, csv_correlation, csv_regression)
print(f'\n\n\n{n}. Analizando tendencias específicas de la industria...')
gem_industry_specific=gemini_prompt(f_system_prompt,p_3)
prompt_spanish=f'{prompt_sp} {gem_industry_specific}'
gem_industry_specific_sp=gemini_prompt(f_system_prompt,prompt_spanish)
#display(Markdown(gem_industry_specific_sp))
print(gem_industry_specific_sp)

n+=1
p_4 = prompt_4.format(csv_arima)
print(f'\n\n\n{n}. Analizando el rendimiento del modelo ARIMA...')
gem_arima=gemini_prompt(f_system_prompt,p_4)
prompt_spanish=f'{prompt_sp} {gem_arima}'
gem_arima_sp=gemini_prompt(f_system_prompt,prompt_spanish)
#display(Markdown(gem_arima_sp))
print(gem_arima_sp)

n+=1
p_5 = prompt_5.format(csv_seasonal)
print(f'\n\n\n{n}. Analizando patrones estacionales...\n')
gem_seasonal=gemini_prompt(f_system_prompt,p_5)
prompt_spanish=f'{prompt_sp} {gem_seasonal}'
gem_seasonal_sp=gemini_prompt(f_system_prompt,prompt_spanish)
#display(Markdown(gem_seasonal_sp))
print(gem_seasonal_sp)

n+=1
p_6 = prompt_6.format(csv_fourier)
print(f'\n\n\n{n}. Analizando patrones cíclicos...\n')
gem_fourier=gemini_prompt(f_system_prompt,p_6)
prompt_spanish=f'{prompt_sp} {gem_fourier}'
gem_fourier_sp=gemini_prompt(f_system_prompt,prompt_spanish)
#display(Markdown(gem_fourier_sp))
print(gem_fourier_sp)

n+=1
p_conclusions = prompt_conclusions.format(gem_temporal_trends, gem_cross_keyword, gem_industry_specific, gem_arima, gem_seasonal, gem_fourier)
print(f'\n\n\n{n}. Sintetizando hallazgos y sacando conclusiones...\n')
gem_conclusions=gemini_prompt(f_system_prompt,p_conclusions)
prompt_spanish=f'{prompt_sp} {gem_conclusions}'
gem_conclusions_sp=gemini_prompt(f_system_prompt,prompt_spanish)
#display(Markdown(gem_conclusions_sp))
print(gem_conclusions_sp)

report_pdf()