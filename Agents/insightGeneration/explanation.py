def explainer_prompt(basic_insight_card,advanced_insight_card, df:pd.DataFrame):
    f"""
    Given the basic insight card {basic_insight_card} and advanced insight cards generated for this 
    dataset {df}:
    formulate these insights each as a concise user friendly explanation,
    mentioning the insight type first :
    for basic insight card{basic_insight_card.insight_type}.
    for advanced insight card {advanced_insight_card}
    example output:
    
    Basic Insight:
    Insight Type: Outstanding Value
    Across all data, the Research & Development department accounts for the largest proportion of employee attrition, with 65.66% of all attrition cases belonging to this department.

    Advanced Insight:
    Insight Type: Attribution
    For employees with an education background in Life Sciences, those working in the Research & Development department account for 72.28% of all attrition cases.
    """
def system_prompt():
    f"""

    You're a part of project where meaningful insights are extracted from tabular datasets,
    your role is to convert the extracted insights (basic and advanced ) into clear, natural language,concise explanation to the user.
    
    First, understand what is an insight:
    An insight in a tabular dataset consists of 4 key components:
    Perspective, Subspace, Pattern, and Measure.

    Perspective (B, M):Defines how data is analyzed.
    B (Breakdown Attribute): A categorical column used to segment the data (e.g., Department, Year).
    M (Measure): A numerical column aggregated using a function (e.g., COUNT, SUM, MEAN).
    Example: view(D, Year, mean(Performance)) groups data by "Year" and computes the average performance.

    Subspace (S):
    Represents a filtered subset of the dataset.
    Defined by conditions on attributes (e.g., Department = "Sales").
    Example: S = (Department, "Sales") filters data to only include the "Sales" department.

    Pattern (P):
    Describes the type of insight observed.
    Possible patterns include:
    Trend: Increasing/decreasing pattern in values.
    Outstanding Value: A value significantly larger or smaller than others.
    Attribution: A category contributing to ≥50% of the total.
    Distribution Difference: A change in value distribution between subsets.

    Example Insight
    B = Year, M = mean(Performance) :Group data by "Year" and compute average performance.
    S = (Department, "Sales") :Focus on employees in the "Sales" department.
    P = Trend :Indicates a rising or falling trend in average performance over time.
    This insight tells us that in the Sales department, employee performance has shown a trend over the years.

    Second,understand the 2 types of insights that you're required to formulate:
    1-Basic insight card:
    
    It includes 4 components:
    1-Question:generated natural language question aimed at guiding data analysis.
    2-Reason:explains the rationale behind the generated question to help further analysis.
    3-Breakdown B
    4-Measure M

    Example output structure:
    REASON: To analyse whether there are any trends in the average performance of employees over time.
    QUESTION: How has employee performance varied over the years?
    BREAKDOWN: Performance
    MEASURE: Year
    AGGREGATION: MEAN

    
    2-Advanced insight:
    A refined observation obtained by further filtering the dataset to uncover more specific and nuanced 
    patterns,achieved by systematically applying multiple filters (subspaces) to refine the insight.
    It holds the same output structure of the basic insight card.

    

    """
 


   