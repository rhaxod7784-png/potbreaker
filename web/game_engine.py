"""Parameter-driven Pyodide engine with legacy modes and component instances."""
try:
    from .game import PotBreaker
    from .game_components import ComponentAssemblyMode
    from .ginkgo_modules import GinkgoMode
except ImportError:
    # The Worker builder concatenates these sources into the browser namespace.
    if "PotBreaker" not in globals() or "ComponentAssemblyMode" not in globals() or "GinkgoMode" not in globals():
        raise


class GameEngine:
    """Stable game facade; modes can be selected or assembled from feature instances.

    Examples:
        GameEngine("potbreaker", seed=7)
        GameEngine("ginkgo", difficulty="hard")
        GameEngine("composed", components=[timer, board, scoring, rules])
    """

    MODES = {"potbreaker", "ginkgo", "composed"}

    def __init__(self, mode="potbreaker", seed=None, difficulty="normal", components=None):
        if mode not in self.MODES:
            raise ValueError("unknown game mode")
        if mode == "composed":
            if components is None:
                raise ValueError("composed mode requires component instances")
            self.mode = ComponentAssemblyMode(components)
        else:
            if mode == "ginkgo" and components is not None:
                raise ValueError("Ginkgo features are assembled with composed mode")
            self.mode = (GinkgoMode(seed=seed, difficulty=difficulty) if mode == "ginkgo"
                         else PotBreaker(seed=seed, difficulty=difficulty, components=components))
        self.mode_name = mode

    @classmethod
    def compose(cls, *components):
        """Create an engine from feature objects instead of a whole game mode."""
        return cls(mode="composed", components=components)

    def reset(self):
        return self.mode.reset()

    def step(self, dt, mx=0, my=0, jump=False, fire=False, aimx=0, aimy=0):
        return self.mode.step(dt, mx, my, jump, fire, aimx, aimy)

    def tap(self, index):
        if not hasattr(self.mode, "tap"):
            raise ValueError("tap input is not supported by this engine composition")
        return self.mode.tap(index)

    def sync(self, payload):
        if not hasattr(self.mode, "sync"):
            raise ValueError("sync input is not supported by this engine composition")
        return self.mode.sync(payload)

    def state(self):
        return self.mode.state()

    def destroy(self):
        return None
