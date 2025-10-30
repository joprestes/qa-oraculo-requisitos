from setuptools import setup, find_packages

setup(
    name="qa-oraculo",
    version="1.0.0",
    packages=find_packages(exclude=["tests*", "venv*", "htmlcov*"]),
    python_requires=">=3.11",
    install_requires=[
        "streamlit>=1.39.0",
        "pandas>=2.2.2",
        "openpyxl>=3.1.2",
        "fpdf2>=2.7.9",
        "google-generativeai>=0.5.4",
        "langchain>=0.3.0",
        "langchain-google-genai>=1.0.7",
        "langgraph>=0.0.65",
        "python-dotenv>=1.0.1",
        "matplotlib>=3.9.0",
    ],
)
