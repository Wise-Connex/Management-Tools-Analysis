# code snipets

This document have some important code snipets from correlation.py

init_variables is a very important function, don't delete nothing for it, if you need to do any changes let me know first

## init_variables

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

## check_trends2

```python
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
```
