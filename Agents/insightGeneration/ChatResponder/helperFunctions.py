from .config import *
def extract_dataframe_from_output(output_str: str) -> pd.DataFrame:
        """
        Converts a string representation of pandas Series or DataFrame output into a proper DataFrame.
        This function parses a string that represents the output of a pandas Series or DataFrame 
        display (typically seen in console/notebook output) and converts it into an actual pandas DataFrame
        with two columns.
        Parameters
        ----------
        output_str : str
            A string representing pandas Series/DataFrame output.
            Expected format example:
            'HasCabin
            False    0.333333
            True     1.000000
            Name: Survived, dtype: float64'
        Returns
        -------
        pd.DataFrame
            A pandas DataFrame with two columns where:
            - First column contains the index/categories from the input
            - Second column contains the corresponding values
        Example
        -------
        >>> input_str = 'HasCabin\\nFalse    0.333333\\nTrue     1.000000\\nName: Survived, dtype: float64\\n'
        >>> result = extract_dataframe_from_output(input_str)
        >>> # Returns DataFrame:
        >>> #   HasCabin  Survived
        >>> # 0   False    0.333333
        >>> # 1   True     1.000000
        Notes
        -----
        - Function assumes the input string follows a specific format with newlines separating rows
        - The second column name is extracted from 'Name:' if present, otherwise defaults to 'Value'
        - Handles variable whitespace between index and value in each row
        """
        
        lines = output_str.strip().split('\n')
        # Step 2: Extract column names
        first_col_name = lines[0].strip()
        second_col_match = re.search(r'Name:\s*(\w+)', output_str)
        second_col_name = second_col_match.group(1) if second_col_match else 'Value'

        # Step 3: Parse the data lines
        data_lines = lines[1:-1]  # skip first (header) and last (dtype)

        csv_lines = [f"{first_col_name},{second_col_name}"]
        for line in data_lines:
            # robust splitting: assume last token is the value
            parts = line.strip().rsplit(maxsplit=1)
            if len(parts) == 2:
                key, value = parts
                csv_lines.append(f"{key},{value}")

        # Step 4: Convert to DataFrame
        csv_str = "\n".join(csv_lines)
        df_from_output = pd.read_csv(StringIO(csv_str))
        return df_from_output