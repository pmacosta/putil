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
set EXTRA_DIR=%VIRTUALENV_DIR%\usr\share\%PKG_NAME%
set PYTHONPATH=%PYTHONPATH%;%PYTHON_SITE_PACKAGES%;%EXTRA_DIR%;%EXTRA_DIR%\tests;%EXTRA_DIR%\docs;%EXTRA_DIR%\docs\support
set PYTESTCMD=py.test
set COV_FILE=%SOURCE_DIR%\.coveragerc_ci_%INTERP%
set MAIN_REQUIREMENTS_FILE=%REPO_DIR%\requirements\main_%INTERP%.pip
set TESTS_REQUIREMENTS_FILE=%REPO_DIR%\requirements\tests_%INTERP%.pip

conda update -y conda
conda env remove -y --name %INTERP%
conda create -y --name %INTERP% python=%PYVER% numpy scipy matplotlib
activate %INTERP%
