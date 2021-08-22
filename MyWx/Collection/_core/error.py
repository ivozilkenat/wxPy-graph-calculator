from MyWx.wx import *


class MyWxException:
    class SizerNotBuild(Exception):
        def __init__(self, message="Sizer must be build"):
            super().__init__(message)

    class MissingContent(Exception):
        def __init__(self, message="Content must be set before building"):
            super().__init__(message)
