import os, timeit

# A bunch of useful functions

def multiplesInInterval(base, interval):
    multiples = set()
    intervalStart, intervalEnd = interval[0], interval[-1]
    rest = intervalStart % base
    if int(rest) == 0:
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
    def inner(object, stopTime = True, **kwargs):
        if stopTime:
            start = timeit.default_timer()
            return method(object, **kwargs), timeit.default_timer() - start
        else:
            return method(object, **kwargs), None
    return inner

def enumerateStep(iterable, stepSize, stepStart = 0):
    i = iterable.__iter__()
    while 1:
        try:
            yield stepStart, next(i)
            stepStart += stepSize
        except StopIteration:
            break

# A decorator for methods which allows to calculate the normal index of a negative index if the name
# of the indexedIterable is given.