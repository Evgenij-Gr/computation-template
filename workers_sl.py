import pandas as pd

import dyn_tools as dynt
from grid import gridNodeToUpdate, gridNodeToDict, GridPoint
from stuart_landau import StuartLandau
from workers_utils import getTaskParams, register, fullInit, makeFinalOutname, idlePost

registry = {
    "worker": {},
    "init": {},
    "post": {}
}

registry['init']['approachTime'] = fullInit
registry['init']['poincareMap'] = fullInit

registry['post']['poincareMap'] = idlePost


def makeSystem(gridNode, config):
    # extract default parameters
    defParDict = config['defaultSystem']
    r = defParDict['r']
    s = defParDict['s']
    om = defParDict['omega']
    # and make default system
    dsys = StuartLandau(r, om, s)
    # update it with values from gridNode
    upd = gridNodeToUpdate(gridNode)
    dsys.setParams(upd)
    return dsys


@register(registry, 'worker', 'poincareMap')
def workerPoincareMap(gridNode: tuple[GridPoint], config, timeStamp, initResult):
    dsys = makeSystem(gridNode, config)
    # get solver data
    slvPars = dynt.SolverParams(**config['solver'])
    # get task parameters
    taskParams = getTaskParams(config)
    minX = taskParams['minX']
    maxX = taskParams['maxX']
    steps = taskParams['steps']
    # adjust outName
    ext = config['output']['imageExtension']
    outName = makeFinalOutname(config, initResult, ext, timeStamp, gridNode)
    pltDict = config['misc']['plotParams']
    # do the task
    dynt.plotPoincareMap(dsys, slvPars, outName, minX, maxX, steps, pltDict)


@register(registry, 'worker', 'approachTime')
def workerApproachTime(gridNode, config, timeStamp, initResult):
    dsys = makeSystem(gridNode, config)
    # get solver data
    slvPars = dynt.SolverParams(**config['solver'])
    # get task parameters
    taskParams = getTaskParams(config)
    startPt = taskParams['startPtX'], taskParams['startPtY']
    delta = taskParams['delta']
    # do the task
    appTime = dynt.calcApproachTime(dsys, slvPars, startPt, delta)
    gDict = gridNodeToDict(gridNode)
    return {**gDict, 'approachTime': appTime}


@register(registry, 'post', 'approachTime')
def postApproachTime(config, initResult, workerResult, grid: list[list[GridPoint]], timeStamp):
    # adjust outName
    outTxtName = makeFinalOutname(config, initResult, 'txt', None)
    df = pd.DataFrame(workerResult)
    gridParamNames = [g[0].name for g in grid]
    indexColumns = [ind for ind, _ in zip(['i', 'j'], gridParamNames)]
    df.sort_values(by=indexColumns)
    df[indexColumns + gridParamNames + ['approachTime']].to_csv(outTxtName, sep=' ', index=False)

    ext = config['output']['imageExtension']
    outImgName = makeFinalOutname(config, initResult, ext, None)
    pltDict = config['misc']['plotParams']
    if len(grid) == 1:
        param = grid[0]
        paramName = config['grid']['first']['caption']
        paramVals = [gn.val for gn in param]
        appTimes = df['approachTime'].values.tolist()
        dynt.plotApproachTimeGraph(paramName, "Some title", outImgName, paramVals, appTimes, pltDict)
    elif len(grid) == 2:
        paramXs = grid[0]
        paramYs = grid[1]
        paramXName = config['grid']['first']['caption']
        paramYName = config['grid']['second']['caption']
        paramXVals = [gn.val for gn in paramXs]
        paramYVals = [gn.val for gn in paramYs]
        apTData = df[['i', 'j', 'approachTime']].values.tolist()
        dynt.plotApproachTimeMap(apTData, paramXVals, paramXName, paramYVals, paramYName, outImgName, "Some title",
                                 pltDict)
    else:
        raise Exception("There is no method for such grid!")