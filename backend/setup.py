from setuptools import setup, find_packages

setup(
    name="workflow-forge",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.109.2",
        "uvicorn==0.27.1",
        "pydantic==2.6.1",
        "sqlalchemy==2.0.27",
        "aiosqlite==0.19.0",
        "langchain-core==0.1.18",
        "langgraph==0.0.19",
        "python-multipart==0.0.9",
        "python-dotenv==1.0.1",
        "httpx==0.26.0",
    ],
    extras_require={
        "dev": [
            "pytest==8.0.2",
            "pytest-asyncio==0.23.5",
            "black==24.2.0",
            "isort==5.13.2",
            "flake8==7.0.0",
        ]
    },
    python_requires=">=3.11",
)
