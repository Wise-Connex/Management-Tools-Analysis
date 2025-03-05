# code snipets

This document have some important code snipets from correlation.py

init_variables is a very important function, don't delete nothing for it, if you need to do any changes let me know first

```python
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
```
