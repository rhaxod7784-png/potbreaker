"""Small, instance-based components for assembling browser game modes."""
import json


class GameComponent:
    """A stateful feature instance with shared assembly context and lifecycle hooks."""

    def __init__(self, name):
        self.name = name

    def reset(self, context):
        return None

    def step(self, context, dt, **inputs):
        return None

    def tap(self, context, index):
        return None

    def sync(self, context, payload):
        return None

    def state(self):
        return {}


class ComponentAssemblyMode:
    """Runs supplied component *instances* in order and merges their state."""

    def __init__(self, components, mode_name="composed"):
        self.components = tuple(components or ())
        if not self.components:
            raise ValueError("at least one component instance is required")
        names = [getattr(component, "name", None) for component in self.components]
        if any(not name for name in names) or len(names) != len(set(names)):
            raise ValueError("components need unique, non-empty names")
        if any(not isinstance(component, GameComponent) for component in self.components):
            raise TypeError("components must be GameComponent instances")
        self.mode_name = mode_name
        self.context = {component.name: component for component in self.components}
        self.reset()

    def reset(self):
        for component in self.components:
            component.reset(self.context)
        return self.state()

    def step(self, dt, mx=0, my=0, jump=False, fire=False, aimx=0, aimy=0, **inputs):
        inputs.update(mx=mx, my=my, jump=jump, fire=fire, aimx=aimx, aimy=aimy)
        for component in self.components:
            component.step(self.context, dt, **inputs)
        return self.state()

    def tap(self, index):
        result = None
        for component in self.components:
            handled = component.tap(self.context, index)
            if handled is not None:
                result = handled
        return result if result is not None else False

    def sync(self, payload):
        data = json.loads(payload) if isinstance(payload, str) else payload
        for component in self.components:
            component.sync(self.context, data)
        return self.state()

    def state(self):
        merged = {"mode": self.mode_name}
        for component in self.components:
            values = component.state()
            overlap = merged.keys() & values.keys()
            if overlap:
                raise ValueError(f"duplicate state fields: {sorted(overlap)}")
            merged.update(values)
        return json.dumps(merged, ensure_ascii=False)
