from os import mkdir
from os.path import join, isdir, abspath
import subprocess
import yaml
import sys

from grid import gridNodeToIndexes


def register(registry, jobType, *names):
    def decoratorRegisterJob(func):
        if jobType in ['worker', 'init', 'post']:
            for name in names:
                registry[jobType][name] = func
        else:
            raise KeyError("type must be either 'worker', 'init' or 'post'")
        return func

    return decoratorRegisterJob


# worker always generates data or does some stuff
# mostly we generate data and gather it in the end
# postprocessing manages that data and does final step
def idleWorker(gridNode, config, timeStamp, initResult: dict):
    return None


def watchWorker(gridNode, config, timeStamp, initResult):
    return gridNode, timeStamp, config['task']


# init functions are used to load stuff
# that would be used by all workers: for example,
# a file with starting points should be loaded only once;
# or creates a directory that every worker would use
def idleInit(config, timeStamp):
    return None


# usually it saves generated data and plots something
# basing on it
def idlePost(config, initResult, workerResult, grid, timeStamp):
    return None


def prepareOutputDirInit(config, timeStamp):
    outputDict = config['output']
    targetDir = outputDict['directory']
    assert isdir(targetDir), f"Directory {targetDir} does not exist!"

    stampMode = outputDict['useTimestamp']
    if stampMode in ['folder', 'both']:
        newTargetDir = join(targetDir, timeStamp)
        mkdir(newTargetDir)
        return {'targetDir': newTargetDir}
    elif stampMode in ['file', 'ignore']:
        # we'll add mask later
        return {'targetDir': targetDir}
    else:
        raise KeyError(f"Unknown 'useTimeStamp' key ({stampMode})")


def saveReproducibilityInfo(config, timeStamp, initResult):
    reproSteps = [('REPO BRANCH', 'git branch --show-current'),
                  ('REPO COMMIT', 'git --no-pager log -n 1 --oneline'),
                  ('REPO REMOTE', 'git remote -v'),
                  ('REPO STATUS', 'git status --short --branch'),
                  ('PYTHON PACKAGES', 'pip list --format=freeze')]
    reproData = f'SCRIPT PATH:\n{abspath(sys.argv[0])}\n\nCONFIG PATH:\n{abspath(sys.argv[1])}\n\n'
    for entry, cmd in reproSteps:
        rst = subprocess.run(cmd, capture_output=True)
        txtVal = rst.stdout.decode('utf-8').replace('\r', '')
        reproData += f"{entry}:\n{txtVal}\n"

    reproData += f"CONFIG CONTENT:\n{yaml.dump(config)}"

    gitOutName = f"{config['output']['mask']}_{timeStamp}_repro.txt"
    outFName = join(initResult['targetDir'], gitOutName)
    with open(outFName, 'w') as f:
        f.write(reproData)

    return initResult


def fullInit(config, timeStamp):
    initRst = prepareOutputDirInit(config, timeStamp)
    initRst = saveReproducibilityInfo(config, timeStamp, initRst)
    return initRst


def getTaskParams(config):
    """
        Better make it a separate function
        to never handle that manually
    """
    return config[config['task']]


def makeFinalOutname(config, initResult, outFileExtension, timeStamp, gridNode=None):
    newDir = initResult['targetDir']
    newMask = config['output']['mask']
    if gridNode:
        inds = gridNodeToIndexes(gridNode)
        formatIndStrs = [f"{ind:0>{len(str(config['grid'][parName]['steps'] - 1))}}"
                         for ind, parName in zip(inds, ['first', 'second'])]
        indStr = '_' + '_'.join(formatIndStrs)
    else:
        indStr = ''
    tStampMode = config['output']['useTimestamp']
    tStampStr = ''
    if tStampMode in ['file', 'both']:
        tStampStr = f"_{timeStamp}"

    outName = join(newDir, f"{newMask}{indStr}{tStampStr}.{outFileExtension}")
    return outName