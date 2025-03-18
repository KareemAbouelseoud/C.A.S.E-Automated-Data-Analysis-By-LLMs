import asyncio
from typing import Dict, List, Tuple
from collections import defaultdict
import pandas as pd
from .preprocessingtools import identify_tools
from .preprocessingtools import tool_node as execute_tool
from .coder.pipeline import coder_workflow as process_code_step
from .pipeline import PreprocessingState

def dependency_analyzer(steps: List[Dict]) -> Tuple[List, List]:
    column_operations = defaultdict(list)
    
    for step in steps:
        cols = get_affected_columns(step)
        for col in cols:
            column_operations[col].append(step)
    
    independent = []
    dependent = []
    seen = set()
    
    for step in steps:
        cols = get_affected_columns(step)
        step_deps = {dep for col in cols for dep in column_operations[col]}
        
        if not step_deps - {step}:
            independent.append(step)
            seen.add(step['name'])
        else:
            dependent.append(step)
    
    return independent, dependent

def get_affected_columns(step: Dict) -> List[str]:
    params = step.get('params', {})
    if 'columns' in params:
        return params['columns']
    if 'column' in params:
        return [params['column']]
    return []

async def execute_parallel_steps(state: PreprocessingState) -> PreprocessingState:
    independent, dependent = dependency_analyzer(state['preprocessing_steps'])
    
    parallel_results = await asyncio.gather(
        *[process_step(step, state) for step in independent]
    )
    
    return merge_parallel_results(state, parallel_results, dependent)

async def process_step(step: Dict, state: PreprocessingState) -> Dict:
    step_state = {
        **state,
        "current_step": step,
        "preprocessing_steps": [step]
    }
    
    if identify_tools(step):
        return await execute_tool(step_state)
    return await process_code_step(step_state)

def merge_parallel_results(original: PreprocessingState, results: List[Dict], remaining_steps: List[Dict]) -> PreprocessingState:
    merged = original.copy()
    for result in results:
        merged['dataset_state'] = {**merged['dataset_state'], **result.get('dataset_state', {})}
        merged['transformers'].update(result.get('transformers', {}))
        merged['logs'].extend(result.get('logs', []))
        merged['errors'].extend(result.get('errors', []))
    
    merged['preprocessing_steps'] = remaining_steps
    return merged