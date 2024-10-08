#AI Prompts

system_prompt = """You are a highly experienced statistical analyst with a deep understanding of management tools and their trends.

**Contextualization:** My research focuses on the phenomenon of management tools, understood as the rapid adoption and diffusion of management tools, philosophies, or techniques that become popular in the business environment but are eventually abandoned. These tools often exhibit a life cycle that can be represented statistically, for example, through normal or skewed distributions. Using monthly data collected from {dbs}, my goal is to statistically analyze these tools to determine if they follow predictable patterns or if, instead, they reveal the existence of more complex cyclical or stationary phenomena.

You will receive a dataset of keywords and their corresponding {dbs} data, representing public interest over time. Your task is to analyze this data and provide insightful, concise, and structured responses to specific questions, considering this contextualization. Consider the following in your analysis:

- **Temporal trends:** Identify and interpret changes in search interest over time for individual keywords, considering their potential lifecycle as management tools.
- **Relationships between keywords:** Explore correlations and potential co-occurrences between different management fad keywords, investigating potential relationships in their adoption and decline.
- **External influences:** Consider how external factors (e.g., economic events, technological advancements) might impact search trends and contribute to the rise or fall of management tools.
- **Statistical rigor:** Employ appropriate statistical methods (e.g., time series analysis, regression, correlation) and clearly report results, including significance levels and effect sizes, to identify patterns and support conclusions about the nature of these tools.
- **Language:** Use clear and informative visualizations to support your findings and illustrate the lifecycle of the identified management tools.

IMPORTANT:
Avoid do general comments no specifics to the topic. Every analysis must be based on data and facts from the datasets.
Since Charts, and Visualizations will be include at the very end of the report, please don't mention nothing about it here.
"""

prompt_1 = """### **Analyze Temporal Trends**

**Objective:** To analyze the evolution of search interest for each keyword in {} over time and identify significant patterns.

**Tasks:**

1. **Identify peak periods:** Determine the dates when search interest for each keyword reached its highest point.
2. **Analyze decline periods:** Identify periods when search interest for a keyword significantly decreased.
3. **Evaluate resurgence:** Determine if there were any instances where search interest for a keyword rebounded after a decline.
4. **Analyze overall trends:** Assess the general direction of search interest for each keyword over the entire time period.

**Data Required:** The results of your calculations related to temporal trends.

**Data Requirements:**

1. **Keyword Data:** A dataset containing:
- for the last 20 years:
{}
- for the last 15 years:
{}
- for the last 10 years:
{}
- for the last 5 years:
{}
- for the last year:
{}
    - **Date:** The date for which the data was collected, is in the datasets. (Specify the frequency: monthly, except for the last year weekly)
    - **Keyword:** The specific keyword representing a management fad, each column of dataset (from the following list: {}).
    - **Search Interest:** A numerical value representing the relative search volume (RSV) with a scale of 0-100, indicating the relative search interest for the keyword at that date. This value is in the dataset for each period.
- Trends and means for keywords on last 20 years:
    {}


IMPORTANT:
Since Charts, and Visualizations will be include at the very end of the report, please don't mention nothing about it here.
    """

prompt_2 = """### **Explore Cross Relationships**

**Objective:** To analyze the relationships between different datasets in {} and identify any co-occurrence patterns.

**Tasks:**

1. **Identify correlated keywords:** Determine which keywords exhibit strong positive or negative correlations with each other.
2. **Analyze co-occurrence patterns:** Identify if there are any groups of keywords that tend to be searched together more frequently than expected.
3. **Evaluate potential synergies or conflicts:** Discuss the potential implications of the identified relationships for management practices.

**Data Required:** The results of your calculations related to cross-keyword relationships.

- Correlation analysis results:
{}
- Regression analysis results:
{}

IMPORTANT:
Since Charts, and Visualizations will be include at the very end of the report, please don't mention nothing about it here.
"""

prompt_3 = """### **Investigate Industry-Specific Trends**

**Objective:** To compare trends in the dataset with trends in other industries and identify any unique characteristics or patterns specific to the enterprises and finance sectors.

**Tasks:**

1. **Compare with other industries:** If available, compare the trends in your dataset with trends in other industries (e.g., technology, healthcare).
2. **Identify industry-specific patterns:** Determine if there are any unique trends or patterns that are more prevalent in the enterprises and finance sectors.
3. **Discuss potential factors:** Analyze potential factors that may be driving these industry-specific trends.

**Data Required:** The results of your calculations related to temporal trends and cross-keyword relationships, as well as any relevant data on trends in other industries.

- Trends and means for keywords for the last 20 years:
    {}
    - Correlation analysis results:
    {}
    - Regression analysis results:
    {}

IMPORTANT:
Since Charts, and Visualizations will be include at the very end of the report, please don't mention nothing about it here.
"""

prompt_4 = """### **Analyze ARIMA Model Performance**

**Objective:** To evaluate the effectiveness of the ARIMA model in forecasting search interest.

**Tasks:**

1. **Assess accuracy:** Evaluate the model's accuracy using appropriate metrics (e.g., RMSE, MAE).
2. **Analyze parameter significance:** Determine the significance of the ARIMA model's parameters.
3. **Identify potential improvements:** Suggest potential improvements to the model, such as incorporating additional variables or adjusting parameters.

**Data Required:** The results of your ARIMA model calculations and the actual search interest data.

- ARIMA Model:
{}

IMPORTANT:
Since Charts, and Visualizations will be include at the very end of the report, please don't mention nothing about it here.
"""

prompt_5 = """### **Interpret Seasonal Patterns**

**Objective:** To analyze the significance of identified seasonal patterns in search interest.

**Tasks:**

1. **Evaluate seasonal strength:** Determine the strength of the seasonal patterns.
2. **Analyze potential causes:** Discuss potential factors driving these seasonal fluctuations.
3. **Evaluate impact on forecasting:** Assess the impact of seasonality on forecasting accuracy.

**Data Required:** The results of your seasonal analysis and the actual search interest data.

- Seasonal Analysis:
{}

IMPORTANT:
Since Charts, and Visualizations will be include at the very end of the report, please don't mention nothing about it here.
"""

prompt_6 = """### **Interpret Cyclical Patterns**

**Objective:** To analyze the significance of identified cyclical patterns in search interest.

**Tasks:**

1. **Evaluate cycle strength:** Determine the strength of the cyclical patterns.
2. **Analyze potential causes:** Discuss potential factors driving these cyclical fluctuations.
3. **Evaluate impact on forecasting:** Assess the impact of cyclical patterns on forecasting accuracy.

**Data Required:** The results of your Fourier analysis and the actual search interest data.

- Fourier Analysis:
{}

IMPORTANT:
Since Charts, and Visualizations will be include at the very end of the report, please don't mention nothing about it here.
"""

prompt_conclusions = """## Synthesize Findings and Draw Conclusions

**Objective:** To synthesize the findings from the previous prompts and draw comprehensive conclusions about the dynamics of management tools in the enterprises and finance sectors.

**Tasks:**

1. **Summarize Key Findings:**
    - **Concisely** summarize the most important insights from each of the previous prompts.
    - **Highlight** any significant trends, patterns, or relationships identified.
2. **Draw Overall Conclusions:**
    - **Based on the synthesized findings**, draw broader conclusions about the dynamics of management tools in the enterprises and finance sectors.
    - **Discuss** the implications of these findings for researchers and practitioners.
3. **Identify Key Aspects:**
    - **Pinpoint** the most significant trends, strongest relationships between keywords, or most influential factors driving search interest.
    - **Provide evidence** to support your claims.
4. **Offer Recommendations:**
    - **Suggest** potential areas for future research or practical applications based on the findings.
    - **Propose** specific recommendations for researchers, practitioners, or policy-makers.

**Data Required:** The outputs from the previous six prompts.

- Temporal Trends:
{}
- Cross-Keyword Relationships:
{}
- Industry Specific Trends:
{}
- ARIMA Model performance:
{}
- Seasonal Patters:
{}
- Cyclical Patterns
{}

**Additional Considerations:**

- **Clarity and Conciseness:** Ensure that your responses are clear, concise, and easy to understand.
- **Relevance:** Ensure that your conclusions and recommendations are directly related to the research question and findings.
- **Depth:** Provide sufficient detail to support your claims, but avoid unnecessary information.
- **Critical Thinking:** Demonstrate your ability to analyze and interpret the data in a thoughtful and critical manner.

**Specific Questions to Consider:**

- How do management tools evolve over time?
- What are the key factors driving the popularity of management tools?
- Are there any industry-specific trends or differences in the adoption of management tools?
- What are the potential risks and benefits of adopting management tools?
- How can organizations effectively evaluate and respond to management tools?

IMPORTANT:
Since Charts, and Visualizations will be include at the very end of the report, please don't mention nothing about it here.
"""