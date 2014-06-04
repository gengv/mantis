# coding: utf-8

class DataNotFoundException(Exception):
    def __init__(self, message, status_code=None):
        Exception.__init__(self, message)
        self.status_code = status_code
        
        
class DataMoreThanExpectedException(Exception):
    status_code = 400
    
    def __init__(self, message, status_code=None):
        Exception.__init__(self, message)
        self.status_code = status_code
        
        
class AuthorizationException(Exception):
    status_code = 400
    
    def __init__(self, message, status_code=None):
        Exception.__init__(self, message)
        self.status_code = status_code