class LogMethodCalls:
  def __init__(self, cls):
    self.cls = cls

  def __call__(self, *args, **kwargs):
    obj = self.cls(*args, **kwargs)
    methods = self.cls.__dict__
    for name in methods:
      if name.startswith("__") and name.endswith("__"):
        continue
      setattr(obj, name, self._wrap(name, getattr(obj, name)))
    return obj

  def _wrap(self, name, method):
    def wrapped(*args, **kwargs):
      print(f"Chiamata funzione {name}")
      calls = method(*args, **kwargs)
      calls = calls if calls else []
      for call in calls:
        print(f"Chiamata funzione {call} all'interno di {name}")
      return calls

    return wrapped

