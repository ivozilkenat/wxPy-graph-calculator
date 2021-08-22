import wx
import random


def randomRGBTriple():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def adjustForNegIndex(indexedIterableObjectName):
    def callable(method):
        def inner(object, index, *args, **kwargs):
            def normNegIndex(idx, valueAmount):
                if idx >= 0:
                    raise ValueError
                else:
                    return valueAmount + idx

            if index >= 0:
                return method(object, index, *args, **kwargs)
            else:
                return method(object, normNegIndex(index, len(getattr(object, indexedIterableObjectName))), *args,
                              **kwargs)

        return inner

    return callable
