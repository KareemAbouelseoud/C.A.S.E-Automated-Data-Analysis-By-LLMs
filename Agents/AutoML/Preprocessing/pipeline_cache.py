import asyncio
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from API.Requests import projectRequests  # Ensure proper import for projectRequests
from multiprocessing import Manager

# Create a Manager and a shared dictionary for pipeline caching
manager = Manager()
pipeline_cache = manager.dict()

async def get_cached_pipeline(project_id, mode, state=None):
    """
    Retrieves a cached pipeline for a given project and mode.
    If not available, fetches from the backend or creates a new one.
    """
    # For debugging, cast the manager dict to a normal dict for a snapshot view.
    print("Fetching Pipeline from Cache", dict(pipeline_cache), flush=True)
    key = f"{project_id}_{mode}"
    
    # Check if the pipeline is already in the shared cache
    if key in pipeline_cache:
        return pipeline_cache[key]

    # Pipeline not in cache: fetch or create a new one.
    pipeline = await projectRequests.get_preprocessing_pipeline(project_id, mode)
    if not pipeline and state:
        if mode == 'X':
            # Create a new pipeline for mode X using state info
            droper = ('Drop', Pipeline(steps=[]), state["X_columns"])
            pipeline = ColumnTransformer([droper], remainder='passthrough', sparse_threshold=0)
        else:
            # Create a new pipeline for mode Y
            droper = ('Drop', Pipeline(steps=[]), state['y_column'])
            pipeline = ColumnTransformer([droper], remainder='passthrough', sparse_threshold=0)
        print("New pipeline created", flush=True)
    else:
        # If no pipeline was fetched and state is not provided, return None.
        return None

    # Save the new pipeline in the shared cache.
    pipeline_cache[key] = pipeline
    return pipeline

async def update_cached_pipeline(project_id, mode, pipeline):
    """
    Updates the cached pipeline.
    """
    key = f"{project_id}_{mode}"
    pipeline_cache[key] = pipeline
    print("Pipeline updated in cache", dict(pipeline_cache), flush=True)

async def remove_project_pipelines(project_id):
    """
    Removes all pipeline entries for a specific project from the cache.
    
    Args:
        project_id: ID of the project whose pipelines should be removed
    
    Returns:
        bool: True if any pipelines were removed, False otherwise
    """
    keys_to_remove = []
    removed = False

    # Identify keys to remove from the shared cache.
    for key in list(pipeline_cache.keys()):
        if key.startswith(f"{project_id}_"):
            keys_to_remove.append(key)
    
    # Remove the identified keys.
    for key in keys_to_remove:
        del pipeline_cache[key]
        removed = True

    if removed:
        print(f"Removed {len(keys_to_remove)} pipelines for project {project_id}", flush=True)
    
    return removed

# Dictionary to store models in memory
model_cache = manager.dict()

async def save_model(project_id, model, model_type="default"):
    """
    Saves a model to the cache.
    
    Args:
        project_id: ID of the project
        model: The model object to cache
        model_type: Type/identifier for the model (default: "default")
        
    Returns:
        bool: True if model was saved successfully
    """
    key = f"{project_id}_model_{model_type}"
    model_cache[key] = model
    print(f"Model {model_type} saved in cache for project {project_id}", flush=True)
    return True

async def fetch_model(project_id, model_type="default"):
    """
    Retrieves a cached model for a given project.
    
    Args:
        project_id: ID of the project
        model_type: Type/identifier of the model to fetch
        
    Returns:
        The cached model if available, None otherwise
    """
    key = f"{project_id}_model_{model_type}"
    if key in model_cache:
        print(f"Model {model_type} fetched from cache for project {project_id}", flush=True)
        return model_cache[key]
    
    print(f"Model {model_type} not found in cache for project {project_id}", flush=True)
    return None

async def remove_project_models(project_id):
    """
    Removes all model entries for a specific project from the cache.
    
    Args:
        project_id: ID of the project whose models should be removed
    
    Returns:
        bool: True if any models were removed, False otherwise
    """
    keys_to_remove = []
    removed = False

    # Identify keys to remove from the model cache
    for key in list(model_cache.keys()):
        if key.startswith(f"{project_id}_model_"):
            keys_to_remove.append(key)
    
    # Remove the identified keys
    for key in keys_to_remove:
        del model_cache[key]
        removed = True

    if removed:
        print(f"Removed {len(keys_to_remove)} models for project {project_id}", flush=True)
    
    return removed