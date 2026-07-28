class ApplicationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ValidationError(ApplicationError):
    pass

class DocumentNotFoundError(ApplicationError):
    pass

class DocumentProcessingError(ApplicationError):
    pass

class RetrievalError(ApplicationError):
    pass

class LLMProviderError(ApplicationError):
    pass
