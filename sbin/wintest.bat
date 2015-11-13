set PYTHON_MAJOR=2
set INTERP=py27
set PYVER=2.7

set PYTHONCMD=python
set PIPCMD=pip
set REPO_DIR=%CD%
set RESULTS_DIR=%REPO_DIR%\results
set PKG_NAME=putil
set PYTHON_SITE_PACKAGES=C:\Anaconda\envs\%INTERP%\lib\site-packages
set BIN_DIR=C:\Anaconda\envs\%INTERP%\Scripts
set SOURCE_DIR=%PYTHON_SITE_PACKAGES%\%PKG_NAME%
set VIRTUALENV_DIR=C:\Anaconda\envs\%INTERP%
set EXTRA_DIR=%VIRTUALENV_DIR%\share\%PKG_NAME%
set PYTHONPATH=%PYTHON_SITE_PACKAGES%;%EXTRA_DIR%;%EXTRA_DIR%\tests;%EXTRA_DIR%\docs;%EXTRA_DIR%\docs\support
set TRACER_DIR=%EXTRA_DIR%\docs\support
set PYTESTCMD=py.test
set COV_FILE=%SOURCE_DIR%\.coveragerc_ci_%INTERP%
set MAIN_REQUIREMENTS_FILE=%REPO_DIR%\requirements\main_%INTERP%.pip
set TESTS_REQUIREMENTS_FILE=%REPO_DIR%\requirements\tests_%INTERP%.pip
set CITMP=%REPO_DIR%\CITMP
mkdir %CITMP%

python %EXTRA_DIR%\sbin\coveragerc_manager.py 'ci' 1 %INTERP% %PYTHON_SITE_PACKAGES%
type %COV_FILE%
if "%INTERP%" == "py26" python %EXTRA_DIR%\sbin\patch_pylint.py %PYTHON_SITE_PACKAGES%

cd %EXTRA_DIR%\tests

python %EXTRA_DIR%\sbin\check_files_compliance.py -tps -d %SOURCE_DIR% -m %EXTRA_DIR%
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %SOURCE_DIR%
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %EXTRA_DIR%\sbin
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %EXTRA_DIR%\tests
pylint --rcfile=%EXTRA_DIR%\.pylintrc -f colorized -r no %EXTRA_DIR%\docs\support
py.test --doctest-glob='*.rst' %EXTRA_DIR%\docs
py.test --doctest-modules %SOURCE_DIR%
py.test -s -vv --junitxml=%RESULTS_DIR%\testresults\pytest.xml
py.test --cov-config %COV_FILE% --cov %SOURCE_DIR% --cov-report term
