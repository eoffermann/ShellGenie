@echo off
REM Export environment without build hashes
conda env export --no-builds | findstr /V "prefix:" > environment.yml

echo Universal environment file created.
