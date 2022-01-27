import numpy as np
from scipy.io import loadmat


def import_power(path, filename=""):
    """
    import powers file
    """
    fullPath = path + filename

    if fullPath[-4:] == ".mat":
        rawDict = loadmat(fullPath)
        t = rawDict["timelist"].reshape(-1)
        p = rawDict["powerlist"].reshape(-1)

    elif fullPath[-4:] == ".csv":
        raw = np.loadtxt(fullPath, delimiter=",", skiprows=1)
        t = raw[:, 0].reshape(-1)
        p = raw[:, 1].reshape(-1)

    else:
        print("Could not identify power data type")
        return

    return t, p


def chop_power(t, p, threshold=0.1):
    """
    Use Derivative to chop Powers
    """

    diffPower = np.diff(p)

    step = [abs(x) > threshold for x in diffPower]

    correctedStep = []
    for ix in range(len(step) - 1):
        if step[ix] and step[ix + 1]:
            correctedStep.append(False)
        elif step[ix] and not step[ix + 1]:
            correctedStep.append(True)
        else:
            correctedStep.append(False)

    stepIndex = [0]
    for ix in range(len(correctedStep)):
        if correctedStep[ix]:
            stepIndex.append(ix)

    stepTupleList = []
    for ix in range(len(stepIndex) - 1):
        stepTupleList.append((stepIndex[ix], stepIndex[ix + 1]))

    averagePowerList = []
    averageTimeList = []
    for stepTuple in stepTupleList:
        averagePower = p[stepTuple[0] + 1 : stepTuple[1]]
        averagePower = np.mean(averagePower)
        averagePowerList.append(averagePower)
        averageTime = (t[stepTuple[0] + 1] + t[stepTuple[1]]) / 2.0
        averageTimeList.append(averageTime)

    averagePowerArray = np.array(averagePowerList)
    averageTimeArray = np.array(averageTimeList)
    return averageTimeArray, averagePowerArray


def assign_power(dataDict, expNumList, powersList):
    """
    Given a dictionary of dnpData objects with key being folder string,
    return the data with power values assigned to a new axis dimension
    """

    doInitialize = True
    for ix, expNum in enumerate(expNumList):
        if str(expNum) in dataDict:
            if doInitialize:
                data = dataDict[str(expNum)]
                data.addAxes("power", powersList[ix])
                doInitialize = False
            else:
                tempData = dataDict[str(expNum)].copy()
                tempData.addAxes("power", powersList[ix])
                data.concatenateAlong(tempData, "power")

    return data
