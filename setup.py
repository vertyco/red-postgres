import re
from pathlib import Path

from setuptools import find_packages, setup

version_raw = (Path(__file__).parent / "red_postgres" / "version.py").read_text()
version = re.compile(r'__version__\s=\s"(\d+\.\d+.\d)').search(version_raw).group(1)


setup(
    name="red-postgres",
    version=version,
    author="Vertyco",
    url="https://github.com/vertyco/red-postgres",
    author_email="alex.c.goble@gmail.com",
    long_description=Path("README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    description="Piccolo Postgres integration for Red",
    packages=find_packages(),
    keywords=[
        "piccolo",
        "postgres",
        "red",
        "discord",
        "bot",
        "database",
        "async",
        "asyncpg",
        "orm",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Framework :: Pydantic :: 2",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
    install_requires=["piccolo[postgres]>=1.0.0", "discord.py"],
    python_requires=">=3.10",
    project_urls={
        "Homepage": "https://github.com/vertyco/red-postgres",
        "Bug Tracker": "https://github.com/vertyco/red-postgres/issues",
        "Changelog": "https://github.com/vertyco/red-postgres/blob/main/CHANGELOG.md",
    },
)
