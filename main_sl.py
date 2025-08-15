import datetime
import multiprocessing as mp
import os
import sys
import time
from functools import partial
from itertools import product

import yaml

import grid
import workers as wrk

if __name__ == "__main__":
    if '-h' in sys.argv or '--help' in sys.argv or len(sys.argv) != 2:
        if len(sys.argv) != 2:
            print(f"Wrong number of arguments, {len(sys.argv)-1} were given!")
        print(f"Script usage: python {os.path.basename(sys.argv[0])} <pathToConfig>"
              "\n    pathToConfig: full path to configuration file (e.g., \"./cfg.yaml\")")
        sys.exit()

    configName = sys.argv[1]
    assert os.path.isfile(configName), f"Configuration file {os.path.abspath(configName)} does not exist!"

    with open(configName, 'r') as f:
        configDict = yaml.load(f, Loader=yaml.loader.SafeLoader)

    startTime = datetime.datetime.today().strftime('%Y-%m-%d_%H-%M-%S')
    taskName = configDict['task']
    initFunc = wrk.registry['init'][taskName]
    initResult = initFunc(configDict, startTime)

    grid = grid.getGrid(configDict)
    worker = wrk.registry['worker'][taskName]

    pool = mp.Pool(mp.cpu_count())
    start = time.time()
    workerResult = pool.map(partial(worker, config=configDict, timeStamp=startTime, initResult=initResult), product(*grid))
    end = time.time()
    pool.close()
    print(f"Took {end-start}s ({datetime.timedelta(seconds=end-start)})")

    # define the post processing
    postProcess = wrk.registry['post'][taskName]
    postProcess(configDict, initResult, workerResult, grid, startTime)

