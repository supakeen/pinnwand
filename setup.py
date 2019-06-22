from setuptools import setup, find_packages

setup(
    name="pinnwand",
    version="0.0.2",
    description="Straightforward pastebin software.",
    url="https://github.com/supakeen/pinnwand",
    author="supakeen",
    author_email="cmdr@supakeen.com",
    packages=find_packages(),
    setup_requires=["pytest-runner", "pytest-cov"],
    install_requires=[
        "click",
        "tornado",
        "pytoml",
        "pygments",
        "sqlalchemy",
        "tornado-sqlalchemy",
    ],
    tests_require=["pytest", "pytest-cov"],
    entry_points={"console_scripts": ["pinnwand=pinnwand.command:main"]},
    extras_require={
        "dev": ["pre-commit", "flake8", "black", "pytest", "pytest-cov", "mypy"]
    },
    package_data={"pinnwand": ["pinnwand/static", "pinnwand/template"]},
    include_package_data=True,
)
