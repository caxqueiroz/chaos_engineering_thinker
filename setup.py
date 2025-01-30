from setuptools import setup, find_packages

setup(
    name="chaos_engineering_thinker",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scikit-learn",
        "joblib",
        "pytest",
        "fastapi",
        "pydantic",
        "python-dotenv",
    ],
    python_requires=">=3.8",
)
