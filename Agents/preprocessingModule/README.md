# Preprocessing Module

This module provides a comprehensive set of tools for data preprocessing using LangGraph and Streamlit. It follows the same architecture as other modules in the project, with a focus on data preprocessing tasks.

## Features

- Interactive Streamlit interface for data preprocessing
- Support for various preprocessing operations:
  - Handling missing values
  - Normalization
  - Categorical encoding
  - Outlier removal
  - Discretization
  - Interaction term creation
  - Log transformation
  - Polynomial feature creation
- LangGraph-based workflow management
- Modular and extensible architecture

## Architecture

The module consists of the following components:

1. **Planner**: Decides which agent to call next (caller or coder)
2. **Caller**: Handles preprocessing steps using predefined tools
3. **Coder**: Generates preprocessing code
   - Generator: Creates the preprocessing code
   - Checker: Validates the generated code
   - Reflector: Analyzes and suggests improvements
4. **Pipeline**: Orchestrates the preprocessing workflow

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Upload your dataset (CSV or Excel)

3. Select preprocessing steps:
   - Choose the column to process
   - Select the preprocessing type
   - Configure parameters
   - Add the step to the pipeline

4. Apply the preprocessing:
   - Review the preprocessing steps
   - Click "Apply Preprocessing"
   - Download the processed dataset

## Development

To add new preprocessing tools:

1. Add the tool function to `mainTools.py`
2. Decorate it with `@tool`
3. Update the Streamlit interface in `app.py`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 