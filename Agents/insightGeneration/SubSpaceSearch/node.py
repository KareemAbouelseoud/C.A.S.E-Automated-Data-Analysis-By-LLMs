from io import StringIO
import math
import time
import threading
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy.spatial import distance
from models import DataDescription, InsightCard
from .helperFunctions import *
from .agent import  run_pandas_Coder_agent_ad_card
from Filteration.scoringNode import *
from Filteration.scoringNode import Score_card
CONFIGURATIONS={
    'temperature':0.5,
    'model':"gemini-2.0-flash",
    'number of retries':3,
    "beam_width":100,
    "exp_factor":100,
    "max_depth":1,
    "w_llm":0.5,
}



async def SubspaceSearchNode(state: dict) -> str:
    """
    This function is responsible for generating advanced insights based on the original insight card.
    It uses the LangChain framework to interact with the LLM and generate new insights.
    """
    advanced_cards_dict={}
    print("Running Subspace Search Node...")
    
    df = pd.read_json(StringIO(state['df']))
    start = time.time()
    thread_function(df, state["insight_cards"], state["description"],advanced_cards_dict)
    print(f"Subspace Search Node took {time.time()-start} seconds")
    # Extracting the original insight card from the state
    
    return ({"advanced_insight_cards" : advanced_cards_dict})

def process_card(df: pd.DataFrame, card: InsightCard, DataDescription: DataDescription, advanced_cards_dict: Dict[str, List[Tuple[Dict[str,List],InsightCard]]]) -> None:
    """Processes a single InsightCard, including subspace search."""
    response = subspace_search(df, card, DataDescription, beam_width=10, max_depth=1, exp_factor=2) #remove await because it has no async

    advanced_cards_dict[card.id] = response

def thread_function(df, unique_cards, DataDescription,advanced_cards_dict):
    threads = []
    for card in unique_cards:
        thread = threading.Thread(target=process_card, args=(df, card, DataDescription,advanced_cards_dict))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
#TODO: WE NEED TO CONSIDER THE FILTERS WITH THE SAME SCORE AS ONE ENTRY IN THE BEAM
def subspace_search(df:pd.DataFrame,card:InsightCard,desc:DataDescription, beam_width=3, max_depth=2, exp_factor=2):
    """Beam Search, modified for scoring functions."""
    # Initialize
    So = {"filters": [], "used_cols": []}
    card=Score_card(card)
    original_card_df=pd.read_json(StringIO(card.resulted_df))
    beam = [(So, card)]  # Initialize beam with the original card
    for depth in range(1, max_depth + 1):
        # print("Original QUGEN CARD",card.question)
        for S, _card in beam:
            #TODO: Threading for the Expfactor Loop
            for i in range(exp_factor):
                Snew,Advanced_Card = EXPAND(S, df, _card,desc=desc)
                if Advanced_Card == None:
                    # print(f"Warning: Skipping current Advanced Card as - no suggested cards available.")
                    continue
                filtered_dfs,multiple_views = apply_filters(df, Snew["filters"])
                for df_index,_filtered_df in enumerate(filtered_dfs):
                    # Check if the filtered DataFrame is empty
                    if _filtered_df.empty:
                        # print(f"Warning: Dropping This view - filtered DataFrame is empty.")
                        continue
                    # print(f"Original Card id {card.id},{card.insight_type}\n")
                    # print("="*60)
                    Advanced_Card=run_pandas_Coder_agent_ad_card(filtered_df=_filtered_df,card=Advanced_Card)
                    
                    # print("="*60)
                    try:
                        if Advanced_Card.breakdown != _card.breakdown:
                            # print(f"Warning: Dropping This view - breakdown column mismatch.")
                            continue
                        if Advanced_Card.resulted_df==pd.DataFrame.empty or Advanced_Card.resulted_df=="":
                            # print(f"Warning: Skipping current Advance Card as - resulted_df is empty.")
                            if df_index == filtered_dfs.__len__()-1:
                                # If it's the last DataFrame in the list, remove the last filter and used column
                                # This ensures that the filter is not removed in the middle of the iterations of the muliple views
                                # and only removed when the last DataFrame is reached
                                # for example the max view
                                # print(f"Removing the last filter and used column from Snew")
                                Snew["filters"].pop()  # Remove the last filter added
                                Snew["used_cols"].pop()
                            else:
                                # If it's not the last DataFrame, continue to the next iteration and start the next Card in the multiple views
                                continue
                            
                            
                        # Select and score: try each scoring function and pick the highest score and pattern
                        # AS WE ALREADY MAKE THE LLM SUGGEST THE INSIGHT TYPE FROM THE BEGINNING
                        print(Advanced_Card.insight_type)
                        if Advanced_Card.insight_type == "Distribution Difference":
                            Advanced_Card_resulted_df =pd.read_json(StringIO(Advanced_Card.resulted_df))
                            if Advanced_Card_resulted_df.shape != original_card_df.shape:
                                print(f"Warning: Resulted_df shape mismatch. Fixing Card using validate_dfs")
                            # Advanced_Card.Score=score_distribution_difference(card.resulted_df,Advanced_Card.resulted_df)
                            original_card_df,Advanced_Card_resulted_df=validate_dfs(original_card_df,Advanced_Card_resulted_df,card)
                            # print(Advanced_Card.resulted_df)
                            # print(original_card_df)
                            _s=(distance.jensenshannon(original_card_df.iloc[:,1].values,Advanced_Card_resulted_df.iloc[:,1].values)**2)*2
                            if _s==np.nan:
                                # print(f"Warning: Skipping current Advanced Card as -Score is not available.")
                                continue
                            if _s == np.nan or _s == None or _s == np.inf or _s == -np.inf:
                                # print(f"Warning: Skipping current Advanced Card as -Score is not available.")
                                continue

                            Advanced_Card.Score=float(_s)
                            Advanced_Card.Considered=True
                            Advanced_Card.resulted_df=Advanced_Card_resulted_df.to_json()
                        else:
                            _s=Score_card(Advanced_Card)
                            Advanced_Card.Score=float(_s.Score)
                        
                        # WE CHANGED THE ALGORITHM AND THE WAY OF THINKING 
                        
                        # print(f"Advanced Insight Card: {Advanced_Card.insight_type}")
                        
                        print(f"Original Card id {card.id}\nSubspace: {Snew}, Score: {Advanced_Card.Score}")
                        print("-" * 40)
                        _new_subspace=copy.deepcopy(Snew)
                        # Advanced_Card.subSpace=_new_subspace["filters"]
                        beam.append((_new_subspace, Advanced_Card))  # Save the new beam with the best attributes
                    except:
                        # print(f"Warning: Skipping current Advanced Card as - no suggested cards available.")
                        continue
                # for _ss in beam:
                #     print("*" * 40)
                #     print("Printing the beam array After Expanding")
                #     print(f"Subspace: {_ss[0]}, Score: {_ss[1].Score}")
                    
        beam.sort(key=lambda x: x[1].Score, reverse=True)  # Truncate beam
        
    return beam[:beam_width]
