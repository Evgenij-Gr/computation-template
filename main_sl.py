import sys
import engine
import workers_sl as wrk
from engine import workflow, getConfiguration, parseArguments

ENGINE_REGISTRY = {'approachTime': engine.multiprocessing_engine,
                   'poincareMap': engine.multiprocessing_engine}

if __name__ == "__main__":
    parseArguments(sys.argv)
    configDict = getConfiguration(sys.argv[1])
    taskName = configDict['task']
    initFunc = wrk.registry['init'][taskName]
    worker = wrk.registry['worker'][taskName]
    engine = ENGINE_REGISTRY[taskName]
    postProcess = wrk.registry['post'][taskName]
    workflow(configDict, initFunc, worker, engine, postProcess)

