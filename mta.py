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

# AI Prompts imports 
from prompts import system_prompt, prompt_1, prompt_2, prompt_3, prompt_4, prompt_5, prompt_6, prompt_conclusions
# Tools Dictionary
from tools import tool_file_dic

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

    PPRINT(f'DF INTERPOLATED:\n{df_interpolated}')
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

    PPRINT(f'DF INTERPOLATED:\n{df_interpolated}')
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

    PPRINT(f'DF INTERPOLATED:\n{df_interpolated}')
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
    # Replace with your SFTP server's hostname, port, username, and private key path
    hostname = "129.146.107.0"
    port = 22
    username = "ubuntu"
    private_key_path = "./WC-VSCODE-Private.key"
    remotepath = "/home/ubuntu/GTrendsData/"
    # Create an SSH client object
    ssh = paramiko.SSHClient()
    # Allow SSH client to accept unknown hosts (adjust as needed for security)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Connect to the SFTP server using the private key
    ssh.connect(hostname, port=port, username=username, key_filename=private_key_path)
    # Open an SFTP client object
    sftp = ssh.open_sftp()
    # Download the CSV file
    remote_file = remotepath + filename
    local_file = filename
    sftp.get(remote_file, local_file)
    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(local_file, index_col=0)  # Set the first column as index
    df.index = df.index.str.strip()  # Remove leading/trailing whitespace from index values
    # Convert the 'Year-Month' column to 'Year-Month-Day' format (assuming the day is 1)
    match menu:
      case 1:
        df.index = pd.to_datetime(df.index + '-01', format='%Y-%m-%d')
        PPRINT(f'\n{df}')
      case 2:
        df.index = pd.to_datetime(df.index + '-01', format='%Y-%m-%d')
        PPRINT(f'df not interpolate:\n{df}')
        for kw in all_keywords:
          #df = bspline_interpolation(df, kw)
          #df = cubic_interpolation(df, kw)
          df = linear_interpolation(df, kw)
        PPRINT(f'{kw}\n{df}')

    # Close SFTP and SSH connections
    sftp.close()
    ssh.close()
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

def report_pdf():
  global data_txt
  global charts
  global report
  global csv_means_trends
  data_txt = ''
  data_txt += "\n\n\n"
  data_txt += "#Datos\n"
  data_txt += "## Herramientas Gerenciales:\n"
  data_txt += ", ".join(all_keywords) + "\n"
  data_txt += "\n\n\n"
  data_txt += "## Datos de Google Trends\n"
  data_txt += f"### 20 años (Mensual) ({current_year-20} - {current_year})\n"
  data_txt += csv_last_20_data + "\n"
  data_txt += f"### 15 años (Mensual) ({current_year-15} - {current_year})\n"
  data_txt += csv_last_15_data + "\n"
  data_txt += f"### 10 años (Mensual) ({current_year-10} - {current_year})\n"
  data_txt += csv_last_10_data + "\n"
  data_txt += f"### 5 años (Mensual) ({current_year-5} - {current_year})\n"
  data_txt += csv_last_5_data + "\n"
  data_txt += f"### 1 año (Semanal) ({current_year-1} - {current_year})\n"
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
  toc = generate_markdown_toc(report)
  report = f"#Análisis de {', '.join(all_keywords)} ({str(current_year-20)} - {str(current_year)})\n\n</br></br> *Tabla de Contenido*\n</br></br>{toc}\n\n</br></br> {report}"
  report += "#Indice de Gráficos\n"
  report += '\n' + charts + '\n</br>'
  report += data_txt
  report += "\n---</br></br></br><small>\n"
  report += "\n**************************************************\n"
  report += f"(c) 2024 - {current_year} Diomar Anez & Dimar Anez\n</br>"
  report += f'Contacto: https://www.wiseconnex.com \n'
  report += "**************************************************\n"
  report += "Librerías de python utilizadas:\n"
  report += "matplotlib, numpy, pandas, time, datetime, warnings, pdb, re, hashlib, seaborn, itertools, google.generativeai, statsmodels, altair, scipy, markdown, weasyprint, os, platform, csv, io, google.colab, googleapiclient.discovery, PIL, statsmodels.tsa.arima.model, statsmodels.graphics.tsaplots, statsmodels.tsa.stattools, pytrends.request, IPython.display, scipy.stats, sklearn.linear_model, sklearn.cluster, sklearn.metrics. "
  report += "</br></br>Todas las librerías utilizadas están bajo la debida licencia de sus autores y dueños de los derechos de autor. "
  report += "Algunas secciones de este reporte fueron generadas con la asistencia de Gemini AI. "
  report += "Este reporte está licenciado bajo la Licencia MIT. Para obtener más información, consulta https://opensource.org/licenses/MIT/ "
  now = datetime.datetime.now()
  date_time_string = now.strftime("%Y-%m-%d %H:%M:%S")
  report += "</br></br>Reporte generado el " + date_time_string + "\n"
  report += "</small>"
  #display(Markdown(report))
  html_content = markdown.markdown(report, extensions=["tables"])
  #path_img = os.path.join(unique_folder, f'{filename}_fourier_{keyword[:3]}.png')
  weasyprint.HTML(string=html_content).write_pdf(unique_folder + '/' + filename +'.pdf')
  char='*'
  title='********** ' + filename + ' PDF REPORT SAVED **********'
  qty=len(title)
  print(f'\x1b[33m\n\n{char*qty}\n{title}\n{char*qty}\x1b[0m')
  #print('\n\n\n\n****************************************************\n********* ' + filename + ' PDF REPORT SAVED ********\n****************************************************\n')


# Fourier Analisys
def fourier_analisys(period='last_year_data'):
  global charts
  char='*'
  title=' Análisis de Fourier '
  qty=len(title)
  print(f'\x1b[33m\n\n{char*qty}\n{title}\n{char*qty}\x1b[0m')
  csv_fourier="\nFourier Analisys\n"
  for keyword in all_keywords:
      # Extract data for the current keyword
      data = trends_results[period][keyword]
      print(f"\nKeyword: {keyword}\n")
      csv_fourier += f"Keyword: {keyword}\n"
      # Create time vector
      time_vector = np.arange(len(data))
      csv_fourier += f"Time Vector: \n{time_vector}\n"
      # Ensure data is a properly aligned NumPy array
      data = np.asarray(data, dtype=float).copy()
      # Perform Fourier transform
      fourier_transform = fftpack.fft(data)
      print(fourier_transform)
      csv_fourier += f"Fourier Transform: \n{fourier_transform}\n"
      # Calculate frequency axis
      freq = fftpack.fftfreq(len(data))
      csv_fourier += f"Frequency Axis: \n{freq}\n"
      # Plot the magnitude of the Fourier transform
      plt.figure(figsize=(12, 10))  # Create a new figure for each keyword
      plt.plot(freq, np.abs(fourier_transform), color='#66B2FF')
      plt.xlabel('Frecuencia (ciclos/año)')
      #plt.yscale('log')
      plt.ylabel('Magnitud')  # Update label to reflect 1/2 log scale
      plt.title(f'Transformada de Fourier para {keyword}')
      # Save the plot to the unique folder
      plt.savefig(os.path.join(unique_folder, f'{filename}_fourier_{keyword[:3]}.png'), bbox_inches='tight')
      #path_img = os.path.join(unique_folder, f'{filename}_fourier_{keyword[:3]}.png')
      path_img = f'{filename}_fourier_{keyword[:3]}.png'
      # file_path = path_img
      # folder_name = filename
      # folder_id = get_folder_id(folder_name)
      # make_folder_public(folder_id)
      # path_image = get_file_url_from_path(file_path)
      charts+='Transformada de Fourier para ' + str(keyword) + ' (' + str(path_img) + ')\n\n'
      plt.show()
  csv_fourier="".join(csv_fourier)
  return csv_fourier

# Seasonal Analysis
def seasonal_analysis(period='last_20_years_data'):
  global charts
  global csv_seasonal
  # Assuming 'trends_results' is a dictionary
  data = pd.DataFrame(trends_results[period])
  char='*'
  title=' Análisis Estacional '
  qty=len(title)
  print(f'\x1b[33m\n\n{char*qty}\n{title}\n{char*qty}\x1b[0m')
  csv_seasonal = '\n****** SEASONAL ANALYSIS ********\n'
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
          decomposition = sm.tsa.seasonal_decompose(series, model='additive', period=12)
          seasonal = decomposition.seasonal
          return seasonal

      print(f"\nAnalizando {keyword}:")
      csv_seasonal += f"\nAnalyzing {keyword}:\n"
      #print(data[keyword])
      #analyze_keyword(data, keyword)
      # Extract the series for the keyword
      series = data[keyword]
      # Decompose the time series
      decomposition = sm.tsa.seasonal_decompose(series, model='additive', period=12)
      # Extract the seasonal index
      seasonal = decompose_series(series)
      seasonal_index = seasonal / series.mean()
      print(seasonal_index)
      with pd.option_context('display.max_rows', None, 'display.max_columns', None):
          csv_seasonal+=seasonal_index.to_csv(index=False)
      # Prepare for plot formatting
      plt.figure(figsize=(12, 2))
      plt.plot(seasonal_index, color='green')
      plt.title(f'Indice Estacional de {keyword}')
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
      plt.ylabel('Indice')
      plt.grid(True)
      # Save the plot to the unique folder
      plt.savefig(os.path.join(unique_folder, f'{filename}_season_{keyword[:3]}.png'), bbox_inches='tight')
      # path_image = os.path.join(unique_folder, f'{filename}_season_{keyword[:3]}.png')
      path_image = f'{filename}_season_{keyword[:3]}.png'
      # file_path = path_image
      # folder_name = filename
      # folder_id = get_folder_id(folder_name)
      # make_folder_public(folder_id)
      # path_image = get_file_url_from_path(file_path)
      charts+='Indice de Temporada para ' + str(keyword) + ' (' + str(path_image) + ')\n\n'
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
  # Check for stationarity using Dickey-Fuller test (optional)
  # You can uncomment the following lines to perform the test.
  from statsmodels.tsa.stattools import adfuller
  result = adfuller(data)
  if result[1] > 0.05:
    print("Data is not stationary. Consider differencing.")
    # You might need to difference the data before finding optimal parameters.
  # Use auto_arima from pmdarima if statsmodels version is not compatible
  stepwise_model = auto_arima(data, start_p=1, d=None, start_q=1, start_P=1, Start_Q=1,
                              max_p=5, max_d=5, max_q=5, max_P=5, max_Q=5, D=10, max_D=10,
                              m=1,  # Set m=1 for non-seasonal data
                              seasonal=False,  # Set seasonal=False for non-seasonal data
                              error_action='ignore',  # Ignore warnings
                              trace=True,  # Print details during search
                              suppress_warnings=True)  # Suppress warnings

  # Print the chosen model with information criterion
  # print("Chosen ARIMA Model (with AIC):", stepwise_model.summary())
  # Return the parameters, information criterion, and fitted model
  return stepwise_model.order, stepwise_model.aic, stepwise_model

# Fit ARIMA model
def arima_model(mb=24, mf=60, ts=18, p=0, d=1, q=2, auto=True):
  global charts
  print('\n\n--------------------- ARIMA MODEL ---------------------\n')
  csv_arima = "\nARIMA MODEL\n"
  # Assuming 'trends_results' is a dictionary
  data = pd.DataFrame(trends_results['last_20_years_data'])
  # Handle 'isPartial' column (if present)
  if 'isPartial' in data.columns:
      data = data.drop('isPartial', axis=1)
  #split data
  train = data[:-ts]
  test = data[-ts:]
  # Set frequency information (optional)
  try:
      # Attempt to infer datetime format
      #data.index = pd.to_datetime(data.index, infer_datetime_format=True)
      train.index = pd.to_datetime(train.index, format="%Y-%m-%d")  # Assuming daily frequency
      train = train.resample('M').mean()  # Resample to monthly frequency
  except pd.errors.ParserError:
      # Provide a more specific format string if known
      print("Couldn't infer datetime format. Please provide a format string (e.g., '%Y-%m-%d')")
  # Fit ARIMA models to each numeric column
  numeric_columns = train.select_dtypes(include=['int64', 'float64'])
  for col in numeric_columns:
      qty=len(f'Modelo ARIMA para: {col}')+2
      char='*'
      print(f"\n\n{char*qty}\n Modelo ARIMA para: \x1b[33m{col}\x1b[0m\n{char*qty}\n")
      csv_arima += f"\n\nFitting ARIMA model for {col}\n"
      # Example ARIMA parameters (adjust p, d, q based on data analysis)
      #p, d, q = 2, 1, 1
      best_params, best_aic, best_model = find_best_arima_params(train[col])
      if auto:
          p, d, q = best_params  # Unpack the tuple
          print(f"Los mejores parámetros de ARIMA encontrados: p={p}, d={d}, q={q}")
      #try:
      # Fit ARIMA model using try-except for potential non-stationarity
      model = ARIMA(train[col], order=(p, d, q))  # Pass individual values
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
      print(f"Predicciones para {col}:\n{predictions}")
      csv_arima += f"\nPredictions for {col}:\n{predictions}"
      print(f"\nError Cuadrático Medio Raiz (ECM Raíz) RMSE: {rmse}\nError Absoluto Medio (EAM) MAE: {mae}\n")
      csv_arima += f"\nRMSE: {rmse}, MAE: {mae}"
      # Combine actual data and predictions for plotting
      data_to_plot = pd.concat([last_months, predictions])
      # Create the plot
      fig, ax = plt.subplots(figsize=(12, 8))  # Adjust figure size as needed
      # Plot data actual
      data_actual_line, = ax.plot(data_to_plot.index, smooth_data(data_to_plot, window_size=9), label='Data Actual')
      # Plot predictions with dashed line and blue color
      predictions_line, = ax.plot(predictions.index, predictions, label='Predicciones', linestyle='--', color='blue')
      # Plot test data with scatter and alpha
      test_scatter = ax.scatter(test.index, test[col], label='Data Test', alpha=0.4, marker='*')
      # Fill between for confidence interval
      ci_fill = ax.fill_between(predictions.index, conf_int[:, 0], conf_int[:, 1], alpha=0.1, color='b', label='Intervalo de Confidencia')
      # Add labels and title
      ax.set_title(f"Modelo ARIMA para {col}")
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
      plt.savefig(os.path.join(unique_folder, f'{filename}_arima_{col[:3]}.png'), bbox_inches='tight')
      path_image = f'{filename}_arima_{col[:3]}.png'
      charts += 'Modelo ARIMA para ' + str(col) + ' (' + str(path_image) + ')\n\n'
      plt.show()
      # except Exception as e:
      #     print(f"Error fitting ARIMA for {col}: {e}")
      #     print("Consider checking stationarity and adjusting parameters.")
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
  match menu:
    case 2:
      mean = data.mean()
    case 1:
      mean = round(data.mean(),2)
  return mean

#  Fetches and processes Google Trends data for different time periods.
def process_file_data(all_kw, d_filename):
  # Group data and calculate means
  all_data = get_file_data(d_filename)
  PPRINT(f"\n{all_data}")

  last_20_years = all_data[-20*12:]
  PPRINT(f"\n{last_20_years}")

  last_15_years = last_20_years[-15*12:]
  PPRINT(f"\n{last_15_years}")

  last_10_years = last_20_years[-10*12:]
  PPRINT(f"\n{last_10_years}")

  last_5_years = last_20_years[-5*12:]
  PPRINT(f"\n{last_5_years}")

  last_year = last_20_years[-1*12:]
  PPRINT(f"\n{last_year}")

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

    PPRINT(f"original data\n{data}")
    PPRINT(f"smothed data\n{smoothed_data}")
    return smoothed_data

# Create Charts
def relative_comparison():
    global charts
    global title_odd_charts
    global title_even_charts

    fig = plt.figure(figsize=(20, 35))  # Increased figure height

    x_pos = np.arange(len(all_keywords))

    color_map = plt.colormaps['tab10']
    colors = [color_map(i) for i in range(len(all_keywords))]

    window_size = 10

    def setup_subplot(ax, data, mean, title, ylabel, is_last_year=False):
        for i, kw in enumerate(all_keywords):
            smoothed_data = smooth_data(data[kw], window_size)
            # Assuming `data[kw]` has the original x-axis dates as its index
            ax.plot(data[kw].index, smoothed_data, label=kw, color=colors[i])

        # Set major and minor ticks for the y-axis
        # ax.yaxis.set_major_locator(MultipleLocator(10))
        # ax.yaxis.set_minor_locator(MultipleLocator(5))

        # Grid lines for major ticks only
        ax.grid(True, which='major', linestyle='--', linewidth=0.5, color='grey')

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

    def setup_bar_subplot(ax, mean, title):
        mean, ispartial = remove_ispartial(mean)  # Assuming this handles partial data

        # Set major and minor ticks for the y-axis
        # ax.yaxis.set_major_locator(plt.MultipleLocator(10))
        # ax.yaxis.set_minor_locator(plt.MultipleLocator(5))

        # Grid lines for major ticks only
        ax.grid(True, which='major', linestyle='--', linewidth=0.5, color='grey')

        # Create bar plot with corresponding value labels
        bar_container = ax.bar(x_pos, mean[:len(all_keywords)], align='center', color=colors)

        # Add value labels using `bar_label` (if Matplotlib >= 3.8)
        #ax.bar_label(bar_container, fmt="{:.1E}".format)  # Format values (optional)
        ax.bar_label(bar_container, fmt=eng_format)  # Format values (optional)

        ax.set_title(title, fontsize=16)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(replace_spaces_with_newlines(all_keywords), rotation=0, ha='center', fontsize=8)
        ax.tick_params(axis='y', which='major', labelsize=8)

        # Adjust y-axis limits to avoid clipping labels (if needed)
        plt.setp(ax.get_yticklabels(), rotation=45, ha='right')  # Rotate y-axis labels if crowded
        plt.tight_layout()  # Adjust spacing to avoid clipping labels

    # Create grid spec to allow uneven column widths and space for legend
    total_graphs = 6
    h_r = [0.2, 1, 1, 1, 1, 1]
    if menu == 2:
      period = 72
      total_graphs = 7
      h_r = [0.2, 1, 1, 1, 1, 1, 1]

    if wider:
      gs = fig.add_gridspec(total_graphs, 6, height_ratios=h_r)
      axODD = slice(0,5)
      axEVEN = 5
    else:
      gs = fig.add_gridspec(total_graphs, 4, height_ratios=h_r)
      axODD = slice(0,3)
      axEVEN = 3

    i = 1
    # all data
    if menu == 2:
      ax1 = fig.add_subplot(gs[i, axODD])
      ax2 = fig.add_subplot(gs[i, axEVEN])
      setup_subplot(ax1, trends_results['all_data'], trends_results['mean_all'], title_odd_charts, 'Período de ' + str(period) + ' años\n(' + str(current_year - period) + '-' + str(current_year) + ')')
      setup_bar_subplot(ax2, trends_results['mean_all'], title_even_charts)
      i+=1
      title_odd_charts = ''
      title_even_charts = ''

    # Last 20-years
    ax3 = fig.add_subplot(gs[i, axODD])
    ax4 = fig.add_subplot(gs[i, axEVEN])
    setup_subplot(ax3, trends_results['last_20_years_data'], trends_results['mean_last_20'], title_odd_charts, 'Período de 20 años\n(' + str(current_year - 20) + '-' + str(current_year) + ')')
    setup_bar_subplot(ax4, trends_results['mean_last_20'], title_even_charts)
    i+=1

    # Last 15-years
    ax5 = fig.add_subplot(gs[i, axODD])
    ax6 = fig.add_subplot(gs[i, axEVEN])
    setup_subplot(ax5, trends_results['last_15_years_data'], trends_results['mean_last_15'], '', 'Período de 15 años\n(' + str(current_year - 15) + '-' + str(current_year) + ')')
    setup_bar_subplot(ax6, trends_results['mean_last_15'], '')
    i+=1

    # Last 10-years
    ax7 = fig.add_subplot(gs[i, axODD])
    ax8 = fig.add_subplot(gs[i, axEVEN])
    setup_subplot(ax7, trends_results['last_10_years_data'], trends_results['mean_last_10'], '', 'Período de 10 años\n(' + str(current_year - 10) + '-' + str(current_year) + ')')
    setup_bar_subplot(ax8, trends_results['mean_last_10'], '')
    i+=1

    # Last 5-years
    ax9 = fig.add_subplot(gs[i, axODD])
    ax10 = fig.add_subplot(gs[i, axEVEN])
    setup_subplot(ax9, trends_results['last_5_years_data'], trends_results['mean_last_5'], '', 'Período de 5 años\n(' + str(current_year - 5) + '-' + str(current_year) + ')')
    setup_bar_subplot(ax10, trends_results['mean_last_5'], '')
    i+=1

    # Last 1-year
    ax11 = fig.add_subplot(gs[i, axODD])
    ax12 = fig.add_subplot(gs[i, axEVEN])
    setup_subplot(ax11, trends_results['last_year_data'], trends_results['mean_last_year'], '', 'Período de 1 año\n(' + str(current_year - 1) + '-' + str(current_year) + ')', is_last_year=True)
    setup_bar_subplot(ax12, trends_results['mean_last_year'], '')

    # Add legend at the bottom, outside of the plots
    if menu == 2:
      handles, labels = ax1.get_legend_handles_labels()
    else:
      handles, labels = ax3.get_legend_handles_labels()
    
    fig.legend(handles, labels, loc='lower right', bbox_to_anchor=(0.55, 0.05),
                 ncol=len(all_keywords), fontsize=12)

    # Adjust the layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.95, bottom=0.1, hspace=0.3, wspace=0.3)  # Increased bottom margin and wspace

    # Save the plot to the unique folder
    plt.savefig(os.path.join(unique_folder, f'{filename}_overtime.png'), bbox_inches='tight')
    path_image = f'{filename}_overtime.png'
    charts+='Interés por período (' + str(path_image) + ')\n\n'
    plt.show()

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

  match menu:
    case 2:
      overall_average = np.mean(np.float64(yearly_averages))
    case 1:
      overall_average = round(np.mean(yearly_averages), 2)
  return overall_average

# Check Trends
def check_trends2(kw):
    global charts
    data = trends_results['last_20_years_data']
    mean = trends_results['mean_last_20']
    char='*'
    rep=len('Herramientas: ' + kw) + 3
    print('\n\n'+ char*rep + '\n Herramienta: \x1b[33m"' + kw.upper() + '"\x1b[0m\n' + char*rep)

    # Calculate averages
    avg_all = calculate_yearly_average(trends_results['all_data'][kw])
    avg_20 = calculate_yearly_average(trends_results['all_data'][-20*12:][kw])
    avg_15 = calculate_yearly_average(trends_results['all_data'][-15*12:][kw])
    avg_10 = calculate_yearly_average(trends_results['all_data'][-10*12:][kw])
    avg_5 = calculate_yearly_average(trends_results['all_data'][-5*12:][kw])
    avg_1 = calculate_yearly_average(trends_results['all_data'][-12:][kw])

    means = {}
    means[kw] = [avg_all, avg_20, avg_15, avg_10, avg_5, avg_1]

    # Base width
    base_width = 0.35

    # Calculate relative widths
    avg_all_width = base_width * 72 / 20 * 2
    avg_20_width = base_width * 20 / 20 * 2
    avg_15_width = base_width * 15 / 20 * 2
    avg_10_width = base_width * 10 / 20 * 2
    avg_5_width = base_width * 5 / 20 * 2
    avg_1_width = base_width * 1 / 20 * 2.5

    # Create the bar graph
    fig, ax = plt.subplots(figsize=(10,6))

    # Define bar positions and widths
    bar_positions = [0, avg_all_width/1.55, avg_all_width/1.62 + avg_20_width, avg_all_width/1.71 + avg_20_width + avg_15_width,
                    avg_all_width/1.81 + avg_20_width + avg_15_width + avg_10_width,
                    avg_all_width/1.89 + avg_20_width + avg_15_width + avg_10_width + avg_5_width]
    bar_widths = [avg_all_width, avg_20_width, avg_15_width, avg_10_width, avg_5_width, avg_1_width]

    # Create bars
    rects = [ax.bar(pos, avg, width, label=f'Media {years} Años ({current_year-years} - {current_year}): {eng_notation(avg)}', color=color)
            for pos, width, avg, years, color in zip(bar_positions, bar_widths, [avg_all, avg_20, avg_15, avg_10, avg_5, avg_1],
                                                    [72, 20, 15, 10, 5, 1],
                                                    ['lightgrey', 'lightsteelblue', 'steelblue', 'dodgerblue', 'darkblue', 'midnightblue'])]

        # Set the x-axis labels and title
    x_positions = [0, avg_all_width/1.55, avg_all_width/1.62 + avg_20_width, avg_all_width/1.71 + avg_20_width + avg_15_width,
                    avg_all_width/1.81 + avg_20_width + avg_15_width + avg_10_width,
                    avg_all_width/1.89 + avg_20_width + avg_15_width + avg_10_width + avg_5_width]
    ax.set_xticks(x_positions)
    ax.set_xticklabels(keywords)
    ax.set_ylabel('Media de Interés de Búsqueda')
    ax.set_title(f'Media de Interés de Búsqueda a lo largo del tiempo de:\n{kw}')
    # Add labels over each bar
    def add_labels(rects, avg, position):
        for rect in rects:
            height = rect.get_height()
            plt.text(rect.get_x() + rect.get_width() / 2, height, eng_notation(height), # f"{height:.2e}",
                    ha='center', va='bottom', fontsize=8, color='black')
    add_labels(rects[0], avg_all, 1)
    add_labels(rects[1], avg_20, 2)
    add_labels(rects[2], avg_15, 3)
    add_labels(rects[3], avg_10, 4)
    add_labels(rects[4], avg_5, 5)
    add_labels(rects[5], avg_1, 6)
    # Move the legend outside the plot
    legend = ax.legend(loc='upper center', fontsize=9, bbox_to_anchor=(0.5, -0.15), ncol=2)
    # Save the plot to the unique folder
    plt.savefig(os.path.join(unique_folder, f'{filename}_means_{kw[:3]}.png'), bbox_inches='tight')
    # path_image = os.path.join(unique_folder, f'{filename}_season_{keyword[:3]}.png')
    path_image = f'{filename}_means_{kw[:3]}.png'
    charts+='Medias de ' + str(kw) + ' (' + str(path_image) + ')\n\n'
    # Show the plot
    if menu == 2:
      plt.yscale('log')
    plt.show()

    # Calculate trends
    trend_20 = round(((avg_1/trends_results['mean_last_20'][kw])-1)*100,2)
    print('')
    print(f'Tendencia Normalizada de Desviación Anual: {trend_20}')
    trend2_20 = round(((avg_1/avg_20)-1)*100,2)
    print(f'Tendencia Suavizada por Media Móvil: {trend2_20}')
    print('')

    trends = {}
    trends[kw] = [trend_20, trend2_20]

    print(f'El interés promedio de los últimos 20 años para "{kw.upper()}" fue {eng_notation(trends_results["mean_last_20"][kw])}.')
    print(f'El interés del último año para "{kw.upper()}" comparado con los últimos 20 años resulta con una tendencia de {trend_20}%.')

    trend = trend_20
    yearsago = 20
    mean_value = mean[kw]

    # Adjusted logic based on 1-100 index range
    if mean_value > 75:
        if abs(trend) <= 5:
            print(f'El interés por "{kw.upper()}" es muy alto y estable durante los últimos {yearsago} años.')
        elif trend > 5:
            print(f'El interés por "{kw.upper()}" es muy alto y está aumentando durante los últimos {yearsago} años.')
        else:
            print(f'El interés por "{kw.upper()}" es muy alto pero está disminuyendo durante los últimos {yearsago} años.')
    elif mean_value > 50:
        if abs(trend) <= 10:
            print(f'El interés por "{kw.upper()}" es alto y relativamente estable durante los últimos {yearsago} años.')
        elif trend > 10:
            print(f'El interés por "{kw.upper()}" es alto y está aumentando significativamente durante los últimos {yearsago} años.')
        else:
            print(f'El interés por "{kw.upper()}" es alto pero está disminuyendo significativamente durante los últimos {yearsago} años.')
    elif mean_value > 25:
        if abs(trend) <= 15:
            print(f'El interés por "{kw.upper()}" es moderado y muestra algunas fluctuaciones durante los últimos {yearsago} años.')
        elif trend > 15:
            print(f'El interés por "{kw.upper()}" es moderado pero está en tendencia creciente durante los últimos {yearsago} años.')
        else:
            print(f'El interés por "{kw.upper()}" es moderado pero muestra una tendencia decreciente durante los últimos {yearsago} años.')
    else:
        if trend > 50:
            print(f'El interés por "{kw.upper()}" es bajo pero está creciendo rápidamente durante los últimos {yearsago} años.')
        elif trend > 0:
            print(f'El interés por "{kw.upper()}" es bajo pero muestra un ligero crecimiento durante los últimos {yearsago} años.')
        elif trend < -50:
            print(f'El interés por "{kw.upper()}" es bajo y está disminuyendo rápidamente durante los últimos {yearsago} años.')
        else:
            print(f'El interés por "{kw.upper()}" es bajo y muestra una ligera disminución durante los últimos {yearsago} años.')

    # Comparison last year vs. 20 years ago
    if avg_20 == 0:
        print(f'No había interés medible por "{kw.upper()}" hace {yearsago} años.')
    elif trend2_20 > 50:
        print(f'El interés del último año es mucho más alto en comparación con hace {yearsago} años. Ha aumentado en un {trend2_20}%.')
    elif trend2_20 > 15:
        print(f'El interés del último año es considerablemente más alto en comparación con hace {yearsago} años. Ha aumentado en un {trend2_20}%.')
    elif trend2_20 < -50:
        print(f'El interés del último año es mucho más bajo en comparación con hace {yearsago} años. Ha disminuido en un {abs(trend2_20)}%.')
    elif trend2_20 < -15:
        print(f'El interés del último año es considerablemente más bajo en comparación con hace {yearsago} años. Ha disminuido en un {abs(trend2_20)}%.')
    else:
        print(f'El interés del último año es comparable al de hace {yearsago} años. Ha cambiado en un {trend2_20}%.')
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

#    print(result_df)

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
        plt.savefig(os.path.join(unique_folder, f'{filename}_heatmap.png'), bbox_inches='tight')
        path_image = f'{filename}_heatmap.png'
        charts+='Mapa de Calor (' + str(path_image) + ')\n\n'
        plt.show()

        # Regression analysis
        # Extract the last 20 years data
        char='*'
        title=' Análisis de Regresión '
        qty=len(title)
        print(f'\x1b[33m\n\n{char*qty}\n{title}\n{char*qty}\x1b[0m')
        print('\nNota: La primera variable es la variable dependiente\n      y el rersto son las variables independientes para cada combinación\n      ej: (dependiente, independiente1, independiente2...)\n')
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
            r_squared = r2_score(y, model.predict(X))  # Use r2_score to calculate R-squared
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
              plt.savefig(os.path.join(unique_folder, f'{filename}_scatter_{combo[0][:3]}{combo[1][:3]}.png'), bbox_inches='tight')
              # path_image = os.path.join(unique_folder, f'{filename}_scatter_{combo[0][:3]}{combo[1][:3]}.png')
              path_image = f'{filename}_scatter_{combo[0][:3]}{combo[1][:3]}.png'
              # file_path = path_image
              # folder_name = filename
              # folder_id = get_folder_id(folder_name)
              # make_folder_public(folder_id)
              # path_image = get_file_url_from_path(file_path)
              charts+='Gráfico de Dispersión para ' + str(", ".join(combo)) + ' (' + str(path_image) +')\n\n'
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

#proxies={'https': 'https://' + get_proxies()}

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
title_odd_charts = 'Interés relativo\na lo largo del tiempo'
title_even_charts = 'Interés relativo\npara el período'
# ********************************************

# Set the flag based on the count of keywords
wider = True if len(all_keywords) <= 2 else False

if len(all_keywords) < 2:
    one_keyword = True # Set one keyword
trends_results = process_file_data(all_keywords, data_filename)
print(all_keywords)
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
# Part 1 - Trends and Means
# *************************************************************************************

csv_string = io.StringIO()
csv_writer = csv.writer(csv_string)
csv_writer.writerow(['Keyword', '20 Years Average', '15 Years Average', '10 Years Average', '5 Years Average', '1 Year Average', 'Trend NADT', 'Trend MAST'])

for kw in all_keywords:
    results = check_trends2(kw)
    csv_writer.writerow([kw] + results['means'] + results['trends'])

csv_data = csv_string.getvalue()
csv_means_trends = "Means and Trends\n</br> Trend NADT: Normalized Annual Desviation\n</br> Trend MAST: Moving Average Smoothed Trend\n\n" + csv_data

# *************************************************************************************
# Part 2 - Comparison along time
# *************************************************************************************

relative_comparison()


# *************************************************************************************
# Part 3 - Correlation - Regression
# *************************************************************************************

analysis = analyze_trends(trends_results)
if one_keyword:
  csv_correlation = None
  csv_regression = None
  print('Se requieren al menos dos variables para realizar los cálculos de correlación y regresión')
else:
  csv_correlation = analysis['correlation']
  csv_regression = analysis['regression']
  

# *************************************************************************************
# Part 4 - ARIMA
# *************************************************************************************

# Call the arima_model function with the best parameters
# mb: months back. Past
# mf: months foward. future
# ts: test size. Size of test in months
# p, d, q: ARIMA parameters
# auto = True: Calculate p,d,q. False: use given p, d, q values.
csv_arima=arima_model(mb=120, mf=36, ts=18, p=2, d=1, q=0)


# *************************************************************************************
# Part 5 - Seasonal Analisys
# *************************************************************************************

seasonal_analysis('last_10_years_data')

# *************************************************************************************
# Part 6 - Fourier Analisys
# *************************************************************************************

csv_fourier=fourier_analisys('last_20_years_data') #'last_20_years_data','last_15_years_data', ... , 'last_year_data'
# to chage Y axis to log fo to line 131 in all functions


# *************************************************************************************
# AI Analysis
# *************************************************************************************

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

p_1 = prompt_1.format(all_kw, \
                      csv_last_20_data, csv_last_15_data, csv_last_10_data, csv_last_5_data, csv_last_year_data, \
                      all_kw, csv_means_trends)
n=0
n+=1
print(f'\n\n\n{n}. Analizing Temporal Trends...')
gem_temporal_trends=gemini_prompt(system_prompt,p_1)
prompt_spanish=f'{prompt_sp} {gem_temporal_trends}'
gem_temporal_trends_sp=gemini_prompt(system_prompt,prompt_spanish)
display(Markdown(gem_temporal_trends_sp))

if not one_keyword:
  n+=1
  p_2 = prompt_2.format(all_kw, csv_correlation, csv_regression)
  print(f'\n\n\n{n}. Analizing Cross-Keyword Relationships...')
  gem_cross_keyword=gemini_prompt(system_prompt,p_2)
  prompt_spanish=f'{prompt_sp} {gem_cross_keyword}'
  gem_cross_keyword_sp=gemini_prompt(system_prompt,prompt_spanish)
  display(Markdown(gem_cross_keyword_sp))
else:
  gem_cross_keyword=""
  csv_correlation=""
  csv_regression=""

n+=1
p_3 = prompt_3.format(csv_means_trends, csv_correlation, csv_regression)
print(f'\n\n\n{n}. Analizing Industry-Specific Trends...')
gem_industry_specific=gemini_prompt(system_prompt,p_3)
prompt_spanish=f'{prompt_sp} {gem_industry_specific}'
gem_industry_specific_sp=gemini_prompt(system_prompt,prompt_spanish)
display(Markdown(gem_industry_specific_sp))

n+=1
p_4 = prompt_4.format(csv_arima)
print(f'\n\n\n{n}. Analizing ARIMA Model Performance...')
gem_arima=gemini_prompt(system_prompt,p_4)
prompt_spanish=f'{prompt_sp} {gem_arima}'
gem_arima_sp=gemini_prompt(system_prompt,prompt_spanish)
display(Markdown(gem_arima_sp))

n+=1
p_5 = prompt_5.format(csv_seasonal)
print(f'\n\n\n{n}. Analizing Seasonal Patterns...\n')
gem_seasonal=gemini_prompt(system_prompt,p_5)
prompt_spanish=f'{prompt_sp} {gem_seasonal}'
gem_seasonal_sp=gemini_prompt(system_prompt,prompt_spanish)
display(Markdown(gem_seasonal_sp))

n+=1
p_6 = prompt_6.format(csv_fourier)
print(f'\n\n\n{n}. Analizing Cyclical Patterns...\n')
gem_fourier=gemini_prompt(system_prompt,p_6)
prompt_spanish=f'{prompt_sp} {gem_fourier}'
gem_fourier_sp=gemini_prompt(system_prompt,prompt_spanish)
display(Markdown(gem_fourier_sp))

n+=1
p_conclusions = prompt_conclusions.format(gem_temporal_trends, gem_cross_keyword, gem_industry_specific, gem_arima, gem_seasonal, gem_fourier)
print(f'\n\n\n{n}. Synthesize Findings and Draw Conclusions...\n')
gem_conclusions=gemini_prompt(system_prompt,p_conclusions)
prompt_spanish=f'{prompt_sp} {gem_conclusions}'
gem_conclusions_sp=gemini_prompt(system_prompt,prompt_spanish)
display(Markdown(gem_conclusions_sp))

report_pdf()