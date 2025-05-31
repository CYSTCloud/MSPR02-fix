#!/bin/bash

echo "Starting dependency installation..."

# Install Python dependencies from requirements.txt
pip install -r requirements.txt

# Explicitly install TensorFlow (as a fallback or to ensure it's there)
pip install tensorflow

echo "Python dependencies installation complete."

# Verify installations
echo "Verifying key package installations..."
python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')"
python -c "import pandas; print(f'Pandas version: {pandas.__version__}')"
python -c "import numpy; print(f'NumPy version: {numpy.__version__}')"
python -c "import sklearn; print(f'Scikit-learn version: {sklearn.__version__}')"
python -c "import xgboost; print(f'XGBoost version: {xgboost.__version__}')"
python -c "import tensorflow; print(f'TensorFlow version: {tensorflow.__version__}')"

echo "Dependency verification complete."
