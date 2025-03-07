#!/bin/bash
# Export Conda environment without build hashes and exclude prefix
conda env export --no-builds | grep -v '^prefix:' > environment.yml

echo "Universal environment file created."
