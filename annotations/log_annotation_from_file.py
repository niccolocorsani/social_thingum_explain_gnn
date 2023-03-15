import ast
import importlib
import inspect
def log_function_calls(func):
  def wrapper(*args, **kwargs):
    print(f"Chiamata la funzione {func.__name__}")
    return func(*args, **kwargs)

  return wrapper



def log_all_function_calls(module_name):

    # Importa il modulo dato il nome del modulo
    module = importlib.import_module(module_name)

    print(module)

    # Ottieni il nome di tutte le funzioni definite nel modulo
    function_names = [node.name for node in ast.walk(ast.parse(inspect.getsource(module))) if isinstance(node, ast.FunctionDef)]

    # Per ogni nome di funzione
    for name in function_names:
        print(name)
        function = getattr(module, name)

        # Sostituisci la funzione originale con una nuova funzione che logga il nome della funzione e poi chiama la funzione originale
        setattr(module, name, log_function_calls(function))

        # Analizza il codice sorgente della funzione per individuare tutte le chiamate di funzione al suo interno
        function_tree = ast.parse(inspect.getsource(function))
        call_names = [node.func.id for node in ast.walk(function_tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)]

        # Per ogni nome di funzione chiamata all'interno della funzione
        for call_name in call_names:
            if call_name in function_names:
                # Sostituisci la funzione chiamata con una nuova funzione che logga il nome della funzione e poi chiama la funzione originale
                setattr(function, call_name, log_function_calls(getattr(function, call_name)))
