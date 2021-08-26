from MyWx.wx import *


class MyWxException:
    class SizerNotBuild(Exception):
        def __init__(self, message="Sizer must be build"):
            super().__init__(message)

    class MissingContent(Exception):
        def __init__(self, message="Content must be set before building"):
            super().__init__(message)

    class AlreadyExists(Exception):
        def __init__(self, message="Object already exists"):
            super().__init__(message)

    class NotExistent(Exception):
        def __init__(self, message="Object does not exist"):
            super().__init__(message)

    class InvalidArgument(Exception):
        def __init__(self, message="Invalid argument"):
            super().__init__(message)
