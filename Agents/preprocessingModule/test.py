from pipeline import preprocess_data
import pandas as pd
if __name__ == "__main__":
    import asyncio
    import sys
    
    async def main():
        project_id = "1"
        preprocessing_tasks = [
            {
                "task": "remove_outliers",
                "column": "Fare",
                "strategy": "zscore"
            },
            {
                "task": "handle_missing_values",
                "column": "Age",
                "strategy": "mean"
            },
            {
                "task": "handle_missing_values",
                "column": "Cabin",
                "strategy": "drop"
            }
        ]
        dataframe = pd.read_csv(r"C:\Users\mshir\OneDrive\Desktop\Private\Python_projects\Graduation Project\datasets\titanic\Titanic-Dataset.csv")
        try:
            result = await preprocess_data(project_id, dataframe, preprocessing_tasks)
            
        except Exception as e:
            print(f"Error during preprocessing: {f'{type(e).__name__}: {str(e)}'}")
            sys.exit(1)

    asyncio.run(main())
