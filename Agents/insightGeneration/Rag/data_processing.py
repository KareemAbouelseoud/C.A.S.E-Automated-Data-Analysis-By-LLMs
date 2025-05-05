import os
import pandas as pd
import numpy as np
import pickle
from langchain_core.documents import Document
from langchain.chains.query_constructor.base import AttributeInfo
from typing import List, Tuple, Dict, Any


from config import ENCODINGS_TO_TRY, MAX_PAGE_CONTENT_LENGTH

def load_csv_robustly(file_path: str) -> pd.DataFrame:
   
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found at: {file_path}")

    df = None
    last_exception = None
    print(f"Attempting to load CSV: {file_path}")
    for enc in ENCODINGS_TO_TRY:
        try:

            df = pd.read_csv(file_path, encoding=enc, low_memory=False)

            df = df.convert_dtypes(infer_objects=True, convert_string=True,
                                   convert_integer=True, convert_boolean=True, convert_floating=True)
            print(f"Successfully read CSV with encoding: {enc}")
            break # Exit loop on success
        except UnicodeDecodeError:
            print(f"Failed to read with encoding: {enc}")
            last_exception = UnicodeDecodeError(f"Failed encoding {enc}", b'', 0, 0, "N/A") # Provide dummy args
        except FileNotFoundError: 
            
             raise
        except Exception as e:
            print(f"An error occurred while reading CSV with encoding {enc}: {e}")
            last_exception = e 

    if df is None:

        if last_exception:
            raise ValueError(f"Could not read CSV file '{file_path}' with any attempted encoding. Last error: {last_exception}")
        else:
            raise ValueError(f"Could not read CSV file '{file_path}' with any attempted encoding.")

    if df.empty:
        raise ValueError(f"CSV file '{file_path}' is empty.")

    print(f"CSV loaded successfully with {len(df)} rows and {len(df.columns)} columns.")
    return df


def get_attribute_type(dtype: np.dtype) -> str:
    """
    Infers attribute type (int, float, bool, string) from pandas/numpy dtype
    for SelfQueryRetriever compatibility.
    """
    if hasattr(dtype, 'numpy_dtype'):
         dtype = dtype.numpy_dtype # E.g., Int64Dtype -> np.int64

    if pd.api.types.is_integer_dtype(dtype):
        return "int"
    elif pd.api.types.is_float_dtype(dtype):
        return "float"
    elif pd.api.types.is_bool_dtype(dtype):
        return "bool"

    else:
        # Default to string for Chroma metadata compatibility if not clearly numeric/bool
        return "string"


def prepare_documents_and_metadata(df: pd.DataFrame) -> Tuple[List[Document], List[AttributeInfo]]:
    """
    Converts DataFrame rows into LangChain Documents and generates metadata info
    for the SelfQueryRetriever. Cleans column names and handles type conversions.

    Args:
        df: The input pandas DataFrame (should have types converted by load_csv_robustly).

    Returns:
        A tuple containing:
            - A list of LangChain Document objects (one per row).
            - A list of AttributeInfo objects for the SelfQueryRetriever.
    """
    documents = []
    metadata_field_info = []

    original_columns = df.columns.tolist()
    # 1. Replace whitespace with underscores
    df.columns = df.columns.str.replace(r'\s+', '_', regex=True)
    # 2. Remove any characters not alphanumeric or underscore
    df.columns = df.columns.str.replace(r'[^A-Za-z0-9_]+', '', regex=True)
    # 3. Prepend 'col_' if name starts with a digit
    df.columns = ['col_' + col if col and col[0].isdigit() else col for col in df.columns]
    # 4. Handle potential empty column names after cleaning
    df.columns = [f'column_{i}' if not col else col for i, col in enumerate(df.columns)]
    # 5. Handle potential duplicate column names after cleaning
    if df.columns.duplicated().any():
        print("Warning: Duplicate column names detected after cleaning. Appending suffixes.")
        df.columns = pd.io.parsers.base_parser.maybe_convert_usecols(df.columns)

    cleaned_columns = df.columns.tolist()
    column_mapping = dict(zip(original_columns, cleaned_columns))
    print("Column name cleaning applied:")
    for orig, clean in column_mapping.items():
        if orig != clean:
            print(f"  '{orig}' -> '{clean}'")


    print("\nGenerating metadata info for columns:")
    valid_columns_for_metadata = []
    df_copy = df.copy() # Work on a copy for type coercion checks/attempts

    for col in df_copy.columns:
        col_type = get_attribute_type(df_copy[col].dtype)
        # Use original column name for description if available and different
        orig_col_name = next((k for k, v in column_mapping.items() if v == col), col)
        col_desc = f"The '{orig_col_name.replace('_', ' ').title()}' column (as '{col}'), type: {col_type}"

        # Attempt type coercion again specifically for metadata compatibility if needed
        # This section tries to ensure the data *can* be represented as the target type
        try:
            if col_type == 'int':
                # Convert to float first, then nullable Int64 for robust handling
                coerced_series = pd.to_numeric(df_copy[col], errors='coerce').astype(float).astype('Int64')
            elif col_type == 'float':
                coerced_series = pd.to_numeric(df_copy[col], errors='coerce').astype(float)
            elif col_type == 'bool':
                 # Convert common string bools, keep others as NA, then convert to BooleanDtype
                 bool_map = {'true': True, '1': True, 'yes': True, 't': True,
                             'false': False, '0': False, 'no': False, 'f': False}
                 temp_series = df_copy[col]
                 if temp_series.dtype == 'object' or pd.api.types.is_string_dtype(temp_series.dtype):
                     temp_series = temp_series.str.lower().map(bool_map)
                 coerced_series = temp_series.astype('boolean') # Nullable boolean
            else: 
                 coerced_series = df_copy[col].astype(str)

            metadata_field_info.append(AttributeInfo(name=col, description=col_desc, type=col_type))
            valid_columns_for_metadata.append(col)
           
            
            print(f"- Column: '{col}', Target Type: {col_type}, Description: {col_desc}")

        except (ValueError, TypeError, pd.errors.IntCastingNaNError) as e:
             print(f"- WARNING: Column '{col}' (originally '{orig_col_name}') could not be consistently typed as {col_type} for metadata due to errors: {e}. Treating as 'string'.")
             col_type = "string"
             col_desc = f"The '{orig_col_name.replace('_', ' ').title()}' column (as '{col}'), type: {col_type} (fallback)"
             existing_info = next((info for info in metadata_field_info if info.name == col), None)
             if existing_info:
                 existing_info.type = col_type
                 existing_info.description = col_desc
             else:
                 metadata_field_info.append(AttributeInfo(name=col, description=col_desc, type=col_type))

             if col not in valid_columns_for_metadata:
                 valid_columns_for_metadata.append(col)
             df[col] = df[col].astype(str)
             print(f"- Column: '{col}', Target Type: {col_type} (Fallback), Description: {col_desc}")


    # --- Create Langchain Documents ---
    print(f"\nCreating Langchain documents for {len(df)} rows...")
    for i, row in enumerate(df.itertuples(index=False)):
        metadata: Dict[str, Any] = {}
        row_dict = row._asdict() # Convert named tuple row to dict

        for col in valid_columns_for_metadata:
            value = row_dict.get(col)
            col_info = next((info for info in metadata_field_info if info.name == col), None)
            target_type = col_info.type if col_info else "string"

            if pd.isna(value):
                metadata[col] = "N/A" 
                continue

            try:
                if target_type == 'int':
                    metadata[col] = int(float(value))
                elif target_type == 'float':
                    metadata[col] = float(value)
                elif target_type == 'bool':

                    if isinstance(value, str):
                         if value.lower() in ['true', '1', 'yes', 't']: metadata[col] = True
                         elif value.lower() in ['false', '0', 'no', 'f']: metadata[col] = False
                         else: metadata[col] = "N/A" 
                    else:
                         metadata[col] = bool(value) 
                else: # String
                    metadata[col] = str(value)
            except (ValueError, TypeError) as e:
                 print(f"Warning: Final conversion error for column '{col}', value '{value}' in row {i}. Storing as string. Error: {e}")
                 metadata[col] = str(value) 


        content_parts = [f"{col}: {metadata.get(col, 'N/A')}" for col in valid_columns_for_metadata]
        page_content = f"Row {i}: " + "; ".join(content_parts)

        # Truncate if too long
        if len(page_content) > MAX_PAGE_CONTENT_LENGTH:
             page_content = page_content[:MAX_PAGE_CONTENT_LENGTH] + "..."

        documents.append(Document(
            page_content=page_content, 
            metadata=metadata       
        ))

    if i % 100 == 0 and i > 0:
        print(f"  Processed {i+1}/{len(df)} rows...")

    print(f"Document creation complete. Generated {len(documents)} documents.")

    if not documents:
         raise ValueError("No documents were generated. Check CSV content and processing steps.")
    if not metadata_field_info:
         raise ValueError("Metadata field info is empty. Check column processing and data types.")

    return documents, metadata_field_info


def save_metadata(metadata_info: List[AttributeInfo], doc_description: str, file_path: str):
    """Saves metadata field info and document description to a pickle file."""
    print(f"Saving metadata info to: {file_path}")
    try:
        with open(file_path, 'wb') as f:
            pickle.dump({
                'metadata_field_info': metadata_info,
                'document_content_description': doc_description
            }, f)
        print("Metadata saved successfully.")
    except Exception as e:
        print(f"Error saving metadata file '{file_path}': {e}")
        raise


def load_metadata(file_path: str) -> Tuple[List[AttributeInfo], str]:
    """Loads metadata field info and document description from a pickle file."""
    print(f"Loading metadata info from: {file_path}")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Metadata file not found: {file_path}")
    try:
        with open(file_path, 'rb') as f:
            saved_data = pickle.load(f)
            if 'metadata_field_info' in saved_data and 'document_content_description' in saved_data:
                print("Metadata loaded successfully.")
                return saved_data['metadata_field_info'], saved_data['document_content_description']
            else:
                raise ValueError("Loaded metadata file is missing required keys ('metadata_field_info', 'document_content_description').")
    except Exception as e:
        print(f"Error loading metadata file '{file_path}': {e}")
