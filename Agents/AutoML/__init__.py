import logging
import warnings

# Configure logging to suppress specific warnings
logging.getLogger('langsmith._internal._serde').setLevel(logging.CRITICAL)
warnings.filterwarnings('ignore', category=UserWarning, module='langsmith')
warnings.filterwarnings('ignore', message='.*Unable to serialize unknown type: <class.*')

# Suppress other potentially noisy loggers
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger('httpcore').setLevel(logging.WARNING) 