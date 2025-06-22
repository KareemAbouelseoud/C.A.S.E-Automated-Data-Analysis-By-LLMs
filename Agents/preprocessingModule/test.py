from io import StringIO
from pipeline import preprocess_data
import pandas as pd
if __name__ == "__main__":
    import asyncio
    import sys
    
    async def main():
        project_id = "1"
        preprocessing_tasks = [
            {'task': 'Imputation', 
            'column': 'Age', 
            'strategy': 'Missing values in Age column can be imputed using mean or median to avoid data loss and improve the accuracy of insights.'}, 
            {'task': 'Handle Missing Values', 
            'column': 'Cabin', 
            'strategy': "Since Cabin has a high percentage of missing values, consider imputing with a new category like 'Unknown' or dropping the column if it's not relevant. This prevents biased insights."}, 
            {'task': 'Transformation', 
            'column': 'SibSp', 
            'strategy': 'SibSp is skewed, applying log transformation can reduce the skewness and improve the performance of some machine learning algorithms, leading to more reliable insights.'}, 
            {'task': 'Transformation', 
            'column': 'Parch', 
            'strategy': 'Parch is skewed, applying log transformation can reduce the skewness and improve the performance of some machine learning algorithms, leading to more reliable insights.'}, 
            {'task': 'Transformation', 
            'column': 'Fare', 
            'strategy': 'Fare is skewed, applying log transformation can reduce the skewness and improve the performance of some machine learning algorithms, leading to more reliable insights.'}, 
            {'task': 'Feature Extraction', 
            'column': 'Name', 
            'strategy': 'Extract titles (Mr, Mrs, Miss, etc.) from the Name column to create new categorical features. This can help in identifying patterns related to social status and survival rates.'}, 
            {'task': 'Feature Engineering', 
            'column': 'Ticket', 
            'strategy': 'The Ticket column has high cardinality and may not be directly useful. Consider extracting meaningful patterns or grouping similar tickets to reduce dimensionality and improve insight generation.'}, 
            {'task': 'Imputation', 
            'column': 'Embarked', 
            'strategy': 'Impute missing values in Embarked with the mode or a new category. This ensures that the Embarked column can be used effectively in downstream analysis without introducing bias.'}]
        # preprocessing_tasks = [
        #     {
        #         "task": "remove_outliers",
        #         "column": "Fare",
        #         "strategy": "zscore"
        #     },
        #     {
        #         "task": "handle_missing_values",
        #         "column": "Age",
        #         "strategy": "mean"
        #     },
        #     {
        #         "task": "handle_missing_values",
        #         "column": "Cabin",
        #         "strategy": "drop"
        #     }
        # ]
        dataframe = pd.read_csv(r"F:\00000000 GP\0 MY PACE\MY Playground\Statistics\Titanic_uncleaned.csv").to_json()
        try:
            result = await preprocess_data(project_id, dataframe, preprocessing_tasks)
            
            print(type(result["preprocessed_dataframe"]))
            pd.read_json(StringIO(result["preprocessed_dataframe"])).to_csv(r"F:\00000000 GP\C.A.S.E-Automated-Data-Analysis-By-LLMs\Agents\preprocessingModule\Preprocess_test.csv",index=False)
        except Exception as e:
            print(f"Error during preprocessing: {f'{type(e).__name__}: {str(e)}'}")
            sys.exit(1)

    asyncio.run(main())
