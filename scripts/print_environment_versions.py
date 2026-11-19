"""Print exact project-relevant versions for a reproducible lockfile.

Run in the same environment that produced the course project results.
"""
import platform
from importlib.metadata import PackageNotFoundError, version

print("python==" + platform.python_version())
for package in ("numpy", "pandas", "scikit-learn", "joblib", "matplotlib", "ipython", "jupyterlab", "ipykernel", "nbconvert"):
    try:
        print(f"{package}=={version(package)}")
    except PackageNotFoundError:
        print(f"# {package} not installed")
