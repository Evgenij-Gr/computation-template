class StuartLandau:
    """ Stuart-Landau system """

    def __init__(self, r, omega, s):
        self.r = r
        assert omega > 0., "omega must be greater than zero!"
        self.omega = omega
        assert s > 0, "alpha must be greater than zero!"
        self.s = s

    def setParams(self, paramDict):
        for key in paramDict:
            if hasattr(self, key):
                setattr(self, key, paramDict[key])
            else:
                raise KeyError(f"System has no parameter '{key}'")

    def getSystem(self, t, X):
        x, y = X
        om, s, r = self.omega, self.s, self.r
        dx = +om * y + s * x * (r * r - x * x - y * y)
        dy = -om * x + s * y * (r * r - x * x - y * y)
        return [dx, dy]
