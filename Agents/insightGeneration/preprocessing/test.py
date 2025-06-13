import sys
import os
from dotenv import load_dotenv
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.getcwd())
load_dotenv()
from dotenv import load_dotenv
from preprocessing.pipeline import preprocess_data
import pandas as pd

if __name__ == "__main__":
    import asyncio
    import sys
    
    async def main():
        project_id = "1"
        preprocessing_tasks =[{'args': {'preprocessing_steps': [
        {'explanation': 'Specialization entries contain combined specializations, which might need to be parsed '
        'for more granular analysis. This will allow for more specific insights related to individual'
        ' specializations rather than combined ones.', 
        'column_name': 'Specialization',
        'preprocessing_step': 'Parse combined specializations'}, 
        
        {'explanation': "Some 'Hospital Address' "
        "entries are missing or listed as 'No Address Available'. These should be handled by either imputing"
        " the addresses or marking them as missing so that they don't skew location-based analysis. "
        "Imputation can be done based on doctor's city if the hospital is known in that city.", 
        'column_name': 'Hospital Address', 
        'preprocessing_step': 'Handle missing addresses'},

        {'explanation': "Some 'Doctors Link' entries are missing or listed as 'No Link Available'. "
        "These should be handled by marking them as missing so that they don't cause errors during analysis"
        " or skew results related to online presence.",
        'column_name': 'Doctors Link',
        'preprocessing_step': 'Handle missing links'}]}, 'type': 'preprocessing_recommender'}]

        dataframe = pd.read_csv(r"C:\Users\DEll\Downloads\DoctorFeePrediction.csv")
       
        try:
            result = await preprocess_data(project_id, dataframe, preprocessing_tasks)
            
        except Exception as e:
            print(f"Error during preprocessing: {f'{type(e).__name__}: {str(e)}'}")
            sys.exit(1)

    asyncio.run(main())