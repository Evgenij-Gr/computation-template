import sys
import workers_sl as wrk
from engine import compute, getConfiguration, parseArguments

ENGINE_REGISTRY = {'approachTime': 'mp',
                   'poincareMap': 'mp'}

if __name__ == "__main__":
    parseArguments(sys.argv)
    configDict = getConfiguration(sys.argv[1])
    compute(configDict, wrk.registry, ENGINE_REGISTRY)

