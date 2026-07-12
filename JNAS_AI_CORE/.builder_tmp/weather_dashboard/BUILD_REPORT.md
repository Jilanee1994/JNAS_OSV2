# BUILD REPORT: WEATHER_DASHBOARD

- Provider: `ollama`
- Milestone: `1`
- Project root: `JNAS_AI_CORE/weather_dashboard`
- Final status: FAILED
- Debug directory: `JNAS_AI_CORE/debug/failed_builds/20260711_204546_weather_dashboard`
- Execution time: 246.89s

## Generated Files
- `/home/ubuntu/JNAS-os/JNAS_AI_CORE/weather_dashboard/README.md`
- `/home/ubuntu/JNAS-os/JNAS_AI_CORE/weather_dashboard/requirements.txt`
- `/home/ubuntu/JNAS-os/JNAS_AI_CORE/weather_dashboard/src/main.py`
- `/home/ubuntu/JNAS-os/JNAS_AI_CORE/weather_dashboard/tests/test_main.py`
- `/home/ubuntu/JNAS-os/JNAS_AI_CORE/weather_dashboard/src/__init__.py`

## Compile Result
PASS

```text
Listing 'JNAS_AI_CORE/.builder_tmp/weather_dashboard'...
Listing 'JNAS_AI_CORE/.builder_tmp/weather_dashboard/src'...
Listing 'JNAS_AI_CORE/.builder_tmp/weather_dashboard/tests'...
Compiling 'JNAS_AI_CORE/.builder_tmp/weather_dashboard/tests/test_main.py'...
```

## Test Result
FAIL

```text
==================================== ERRORS ====================================
_ ERROR collecting JNAS_AI_CORE/.builder_tmp/weather_dashboard/tests/test_main.py _
ImportError while importing test module '/home/ubuntu/JNAS-os/JNAS_AI_CORE/.builder_tmp/weather_dashboard/tests/test_main.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3.12/importlib/__init__.py:90: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
tests/test_main.py:1: in <module>
    from main import get_weather, main
E   ModuleNotFoundError: No module named 'main'
=========================== short test summary info ============================
ERROR tests/test_main.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.12s
```

## Runtime Result
NOT RUN

## Retry Result
failed

## Errors
- src/main.py imports undeclared third-party dependency: requests
- Debug artifacts available at: JNAS_AI_CORE/debug/failed_builds/20260711_204546_weather_dashboard
