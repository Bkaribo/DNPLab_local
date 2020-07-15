from . import dnpData as _dnpData
import numpy as _np

from scipy.optimize import least_squares


def t1Res(x,data,t):
    T1 = x[0]
    M_0 = x[1]
    M_inf = x[2]
    return data - t1Function(t,x)

def t1Function(t,x):
    T1 = x[0]
    M_0 = x[1]
    M_inf = x[2]
    M = M_0 - M_inf * _np.exp(-1.*t/T1)
    return M

def t1Fit(dataDict):
    '''
    '''
    isDict = False
    if isinstance(dataDict,dict):
        data = dataDict['proc'].copy()
        isDict = True
    elif isinstance(dataDict,_dnpData):
        data = dataDict.copy()
    else:
        print('Incompatible data type:')
        print(type(dataDict))
        return

    t1_axes = data.getAxes('t1')

    inputData = _np.real(data.data)

    x0 = [1.,inputData[-1],inputData[-1]]

    out = least_squares(t1Res,x0,verbose = 2,args = (inputData,t1_axes))

    new_axes = _np.r_[_np.min(t1_axes):_np.max(t1_axes):100j]
    fit = t1Function(new_axes,out['x'])

    fitData = _dnpData(fit,[new_axes],['t1'])
    fitData.params['t1'] = out['x'][0]
    fitData.params['M_0'] = out['x'][1]
    fitData.params['M_inf'] = out['x'][2]

    if isDict:
        dataDict['fit'] = fitData
        return dataDict
    else:
        return fitData

def enhancementRes(x,data,powerArray):
    '''
    '''
    E_max = x[0]
    power_half = x[1]

    return data - enhancementFunction(powerArray,x)

def enhancementFunction(powerArray,x):
    E_max = x[0]
    power_half = x[1]

    E = E_max * powerArray / (power_half + powerArray)
    return E


def enhancementFit(dataDict):
    '''
    '''
    isDict = False
    if isinstance(dataDict,dict):
        data = dataDict['proc'].copy()
        isDict = True
    elif isinstance(dataDict,_dnpData):
        data = dataDict.copy()
    else:
        print('Incompatible data type:')
        print(type(dataDict))
        return

    power_axes = data.getAxes('power')

    inputData = _np.real(data.data)

    x0 = [inputData[-1],0.1]

    out = least_squares(enhancementRes,x0,verbose = 2,args = (inputData,power_axes))

    new_axes = _np.r_[_np.min(power_axes):_np.max(power_axes):100j]
    fit = enhancementFunction(new_axes,out['x'])

    fitData = _dnpData(fit,[new_axes],['power'])
    fitData.params['E_max'] = out['x'][0]
    fitData.params['power_half'] = out['x'][1]

    if isDict:
        dataDict['fit'] = fitData
        return dataDict
    else:
        return fitData

