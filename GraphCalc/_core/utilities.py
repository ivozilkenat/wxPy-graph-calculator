import os, timeit


# A bunch of useful functions

def multiplesInInterval(base, interval):
    multiples = set()
    intervalStart, intervalEnd = interval[0], interval[-1]
    rest = intervalStart % base
    if rest == 0:
        firstMultiple = intervalStart
    else:
        firstMultiple = (intervalStart // base + 1) * base
    while firstMultiple < intervalEnd:
        multiples.add(firstMultiple)
        firstMultiple += base
    return multiples


def absPathsFromDir(dirName):
    absPath = os.path.abspath(dirName)
    for _, _, fileNames in os.walk(dirName):
        for f in fileNames:
            yield os.path.join(absPath, f)


def timeMethod(method):
    def inner(object, *args, stopTime=True, **kwargs):
        if stopTime:
            start = timeit.default_timer()
            return method(object, *args, **kwargs), timeit.default_timer() - start
        else:
            return method(object, *args, **kwargs), None

    return inner


def enumerateStep(iterable, stepSize, stepStart=0):
    i = iterable.__iter__()
    while 1:
        try:
            yield stepStart, next(i)
            stepStart += stepSize
        except StopIteration:
            break


def convertToScientificStr(number):
    return f"{number:.2e}"


def notScientificStrRange(number, powerOfTen=3):
    if 10 ** -powerOfTen < abs(number) < 10 ** powerOfTen or number == 0:
        return f"{number:.{powerOfTen}f}"
    else:
        return convertToScientificStr(number)
