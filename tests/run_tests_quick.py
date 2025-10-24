import importlib.util
import sys
from pathlib import Path

# Simple loader to run our test file functions without pytest
spec = importlib.util.spec_from_file_location('test_get_ai_signal', Path(__file__).parent / 'test_get_ai_signal.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

print('Running lightweight tests...')

# run each test function defined in the module
for name in dir(mod):
    if name.startswith('test_'):
        print(f' - {name}... ', end='')
        try:
            getattr(mod, name)()
            print('OK')
        except AssertionError as e:
            print('FAIL')
            print(e)
        except Exception as e:
            print('ERROR')
            print(e)

print('Done')
