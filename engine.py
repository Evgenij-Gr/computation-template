import datetime
import grid
from functools import partial
import time
import multiprocessing as mp
from itertools import product
import yaml
import os
import sys

ENGINES = {}


def parseArguments(argv):
    if '-h' in argv or '--help' in argv or len(argv) != 2:
        if len(argv) != 2:
            print(f"Wrong number of arguments, {len(argv) - 1} were given!")

        print(f"Script usage: python {os.path.basename(argv[0])} <pathToConfig>"


              "\n    pathToConfig: full path to configuration file (e.g., \"./cfg.yaml\")")
        sys.exit()


def getConfiguration(configPath):
    assert os.path.isfile(configPath), f"Configuration file {os.path.abspath(configPath)} does not exist!"

    with open(configPath, 'r') as f:
        configDictionary = yaml.load(f, Loader=yaml.loader.SafeLoader)

    return configDictionary


def multiprocessing_engine(worker, configDict, startTime, initResult, dataGrid):
    pool = mp.Pool(mp.cpu_count())
    start = time.time()
    workerResult = pool.map(partial(worker, config=configDict,
                                    timeStamp=startTime,
                                    initResult=initResult),
                            product(*dataGrid))
    end = time.time()
    pool.close()
    print(f"Took {end - start}s ({datetime.timedelta(seconds=end - start)})")
    return workerResult


ENGINES['mp'] = multiprocessing_engine


def simple_loop_iter_engine(worker, configDict, startTime, initResult, dataGrid):
    start = time.time()
    workerResult = list(map(partial(worker, config=configDict,
                                    timeStamp=startTime,
                                    initResult=initResult),
                            product(*dataGrid)))
    end = time.time()
    print(f"Took {end - start}s ({datetime.timedelta(seconds=end - start)})")
    return workerResult


ENGINES['iter'] = simple_loop_iter_engine


def compute(configDict, workersRegistry, engineRegistry):
    startTime = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
    print(f"\nStarted at {startTime}")
    taskName = configDict['task']
    print(f"Task name: {taskName}")
    initFunc = workersRegistry['init'][taskName]
    print("INIT STAGE")
    initResult = initFunc(configDict, startTime)

    dataGrid = grid.getGrid(configDict)
    worker = workersRegistry['worker'][taskName]
    engine = ENGINES[engineRegistry[taskName]]
    print("COMPUTE STAGE")
    workerResult = engine(worker, configDict, startTime, initResult, dataGrid)

    # define the post processing
    postProcess = workersRegistry['post'][taskName]
    print("POSTPROCESSING STAGE")
    postProcess(configDict, initResult, workerResult, dataGrid, startTime)
