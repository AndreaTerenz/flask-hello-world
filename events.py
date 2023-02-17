import functools

class Event:
    def __init__(self, name):
        self.name = name
        self.functions = []
        self.main_func = None

    def append_func(self, func, main = False):
        if func in self.functions:
            raise FuncAlreadyConnected(self.name, func)

        idx = len(self.functions)
        if main:
            if self.main_func is not None:
                raise MainFuncAlreadySet(self.name, func)
            self.main_func = func
            idx = 0

        self.functions.insert(idx, func)

    def emit(self, data):
        res = None
        for f in self.functions:
            tmp = f(data)
            if f == self.main_func:
                res = tmp
        return res

connections = {
    "NEW_GAME": None,
    "JOIN_GAME": None,
}
for e in connections.keys():
    connections[e] = Event(e)

def on(_targets, make_main : bool = False):
    def _on_decorator(func):
        if type(_targets) is str:
            targets = [_targets]
        else:
            targets = _targets

        for t in targets:
            if connections.get(t) is None:
                raise EventNotFound(t)

            connections[t].append_func(func, make_main)

        @functools.wraps(func)
        def _on_wrapper(data):
            return func(data)

        return _on_wrapper

    return _on_decorator

def emit_event(event_name, data):
    ev = connections.get(event_name)
    if ev is not None:
        return ev.emit(data)
    else:
        raise EventNotFound(event_name)

class EventNotFound(Exception):
    """Raised when trying to access a non-existent event"""
    def __init__(self, event):
        self.event = event

class FuncAlreadyConnected(Exception):
    """Raised when connecting a function to an event it is already connected to"""
    def __init__(self, event, func):
        self.event = event
        self.func = func

class MainFuncAlreadySet(Exception):
    """Raised when trying to set a connecting function as main for an event when it is already set"""
    def __init__(self, event, func):
        self.event = event
        self.func = func

############### TEST CODE

if __name__ == "__main__":
    @on(["NEW_GAME", "JOIN_GAME"], make_main=True)
    def test(data):
        print(data)
        print("UGABUGA")
        return 69

    @on("NEW_GAME")
    def test2(data):
        print(data)
        print("AAAA")
        return 0

    r = emit_event("NEW_GAME", [1,2,3])
    print(r)
    r = emit_event("JOIN_GAME", [4,5,6])
    print(r)