class InvalidPipelineError(Exception):
    """
    Exception raised when a pipeline is invalid or a pipeline step fails execution.
    Provides a message indicating the cause of the error.
    """
    pass
