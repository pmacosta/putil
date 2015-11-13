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
set VIRTUALENV_DIR=\Anaconda\envs\%INTERP%
set EXTRA_DIR=%VIRTUALENV_DIR%\share\%PKG_NAME%
set PYTHONPATH=%PYTHONPATH%;%PYTHON_SITE_PACKAGES%;%EXTRA_DIR%;%EXTRA_DIR%\tests;%EXTRA_DIR%\docs;%EXTRA_DIR%\docs\support
set PYTESTCMD=py.test
set COV_FILE=%SOURCE_DIR%\.coveragerc_ci_%INTERP%
set MAIN_REQUIREMENTS_FILE=%REPO_DIR%\requirements\main_%INTERP%.pip
set TESTS_REQUIREMENTS_FILE=%REPO_DIR%\requirements\tests_%INTERP%.pip

pip install --disable-pip-version-check --user --upgrade pip setuptools wheel

set TMPPYTHONPATH=%PYTHONPATH%
set PYTHONPATH=%REPO_DIR%;%PYTHONPATH%
python %REPO_DIR%\sbin\gen_req_files.py freeze
set PYTHONPATH=%TMPPYTHONPATH%
pip install --upgrade -r%MAIN_REQUIREMENTS_FILE%
pip install --upgrade -r%TESTS_REQUIREMENTS_FILE%
pip install --upgrade -r%REPO_DIR%\\requirements\docs.pip
pip freeze

if not exist "%RESULTS_DIR%\\testresults" mkdir %RESULTS_DIR%\testresults
if not exist "%RESULTS_DIR%\\codecoverage" mkdir %RESULTS_DIR%\codecoverage
if not exist "%RESULTS_DIR%\\images" mkdir %RESULTS_DIR%\images

type %REPO_DIR%\MANIFEST.in
python .\sbin\fix_windows_symlinks.py
python setup.py sdist
cd %REPO_DIR%
python -c "import sys; sys.path.append(['./putil']);import putil.version; print(putil.version.__version__)" > version.txt
set /p PKG_VERSION=<version.txt
echo "PKG_VERSION=%PKG_VERSION%"
cd %PYTHON_SITE_PACKAGES%
pip install %REPO_DIR%\dist\%PKG_NAME%-%PKG_VERSION%.zip

cd C:\Users\%USERNAME%\Documents
