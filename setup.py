from setuptools import setup, find_packages

setup(
    name="pinnwand",
    version="0.0.1",
    description="Straightforward pastebin software.",
    url="https://github.com/supakeen/pinnwand",
    author="supakeen",
    author_email="cmdr@supakeen.com",
    packages=find_packages(),
    setup_requires=["pytest-runner", "pytest-cov"],
    install_requires=[
        "flask",
        "pygments",
        "sqlalchemy",
    ],
    tests_require=["pytest", "pytest-cov"],
    entry_points={"console_scripts": ["unchaind=unchaind.command:main"]},
    extras_require={
        "dev": ["pre-commit", "flake8", "black", "pytest", "pytest-cov", "mypy"]
    },
    package_data={"pinnwand": ["pinnwand/static", "pinnwand/templates"]},
    include_package_data=True,
)
