class DateOverFlowError( Exception ):
    def __init__(self , value ):
        self.value = value
    def __str__(self):
        return repr(self.value)

class TaskAlreadyExistsError( Exception ):
    def __init__(self , value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class DateOutOfRangeError( Exception ):
    def __init__(self , value):
        self.value = value
    def __str__(self):
        return repr(self.value)