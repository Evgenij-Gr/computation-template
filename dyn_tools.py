import numpy as np
from scipy.integrate import solve_ivp
from stuart_landau import StuartLandau
import matplotlib
from matplotlib import pyplot as plt

matplotlib.use('cairo')


class SolverParams:
    def __init__(self, **kwargs):
        self.rtol = kwargs['rtol']
        self.atol = kwargs['atol']
        self.maxT = kwargs['maxT']
        self.method = kwargs['method']


def poincareMapSL(x, dsys: StuartLandau, slvPars: SolverParams):
    def poincareSection(t, pt):
        ptX, ptY = pt
        return ptY

    startPt = np.array([x, 0])
    evt = poincareSection
    evt.direction = 1.
    evt.terminal = True
    rhs = dsys.getSystem

    # going a bit from Poincare section
    sol = solve_ivp(rhs, [0, 1], startPt, method=slvPars.method,
                    rtol=slvPars.rtol, atol=slvPars.atol, )
    newPt = sol.y[:, -1]
    # and then integrating with event
    sol = solve_ivp(rhs, [0, slvPars.maxT], newPt, method=slvPars.method,
                    rtol=slvPars.rtol, atol=slvPars.atol, events=evt)
    lastPtX, _ = sol.y_events[0][-1, :]

    return lastPtX


def plotPoincareMap(dsys: StuartLandau, solverParams: SolverParams, outName, minX, maxX, steps, plotDict):
    pd = {'labelFontsize': 15,
          'titleFontsize': 20}
    assert set(plotDict.keys()) <= set(pd.keys()), \
        f"plotDict has wrong keys!\n{list(plotDict.keys()) = }\nvs\n{list(pd.keys()) = }"
    pd.update(plotDict)

    xs = np.linspace(minX, maxX, steps)
    poinc = lambda x: poincareMapSL(x, dsys, solverParams)
    ys = list(map(poinc, xs))
    plt.plot(xs, ys, 'k', label=r'$x_{n+1} = f(x_n)$')
    plt.gca().set_aspect('equal', adjustable='box')
    plt.plot([minX, maxX], [minX, maxX], 'b--', label=r'$x_{n+1} = x_n$')
    plt.xlabel(r'$x_n$', fontsize=pd['labelFontsize'])
    plt.ylabel(r'$x_{n+1}$', fontsize=pd['labelFontsize'])
    plt.title("Отображение Пуанкаре", fontsize=pd['titleFontsize'])
    plt.legend()
    plt.tight_layout()
    plt.savefig(outName, facecolor='white')
    plt.close()


def calcApproachTime(dsys: StuartLandau, slvPars: SolverParams, startPt, delta):
    def evtApproachCircle(radius):
        def evt(t, X):
            x, y = X
            return x * x + y * y - radius ** 2
        evt.terminal = True
        evt.direction = 0
        return evt

    # we know that the limit cycles is at x^2 + y^2 = dsys.r ^ 2
    # let's figure out how fast we approach circle R = dsys.r with precision delta
    # this is a lazy version, just a proof of concept
    r = dsys.r
    rads = [r - delta, r + delta]
    evts = [evtApproachCircle(r) for r in rads]
    rhs = dsys.getSystem
    sol = solve_ivp(rhs, [0, slvPars.maxT], startPt, method=slvPars.method,
                    rtol=slvPars.rtol, atol=slvPars.atol, events=evts)

    retTime = sol.t[-1]
    return retTime


def plotApproachTimeGraph(paramName, titleString, outName, paramVals, appTimes, plotDict):
    pd = {'labelFontsize': 15,
          'titleFontsize': 20}
    assert set(plotDict.keys()) <= set(pd.keys()), \
        f"plotDict has wrong keys!\n{list(plotDict.keys()) = }\nvs\n{list(pd.keys()) = }"
    pd.update(plotDict)

    plt.plot(paramVals, appTimes)
    plt.xlabel(f"${paramName}$", fontsize=pd['labelFontsize'])
    plt.ylabel("Approach time", fontsize=pd['labelFontsize'])
    plt.title(titleString)
    plt.tight_layout()
    plt.savefig(outName, facecolor='white')
    plt.close()


def plotApproachTimeMap(approachData, xPars, xParName, yPars, yParName, outFileName, titleStr, plotDict):
    """
        approachData is expected to be a list of (i, j, approachData(i, j))
    """
    pd = {'labelFontsize': 15,
          'colorScheme': 'jet'}
    assert set(plotDict.keys()) <= set(pd.keys()), \
        f"plotDict has wrong keys!\n{list(plotDict.keys()) = }\nvs\n{list(pd.keys()) = }"
    pd.update(plotDict)
    N = len(xPars)
    M = len(yPars)
    timeGrid = np.zeros((M, N))
    for data in approachData:
        i = int(data[0])
        j = int(data[1])
        timeGrid[j][i] = data[2]

    plt.pcolormesh(xPars, yPars, timeGrid, cmap=plt.cm.get_cmap(pd['colorScheme']))
    plt.colorbar()
    plt.xlabel(f'${xParName}$', fontsize=pd['labelFontsize'])
    plt.ylabel(f'${yParName}$', fontsize=pd['labelFontsize'])
    plt.title(titleStr)
    plt.tight_layout()
    plt.savefig(outFileName, facecolor='white')
    plt.close()
