import logging
def setup_logging(log_file="logfile.log", log_level=logging.ERROR,module_name="main"):
    """
    Configures logging for the entire project.
    
    Args:
        log_file (str): Path to the log file.
        log_level (int): Logging level (e.g., logging.DEBUG, logging.INFO).
    """
    # Create a custom logger
    logger = logging.getLogger(module_name)
    logger.setLevel(log_level)  # Set the root logger level

    # Remove existing handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # Create handlers
    file_handler = logging.FileHandler(log_file)  # Log to a file
    console_handler = logging.StreamHandler()     # Log to the console

    # Set logging levels for handlers
    file_handler.setLevel(log_level)
    console_handler.setLevel(logging.INFO)  # Console gets INFO and above

    # Create formatters and add them to handlers
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger