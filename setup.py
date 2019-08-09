from setuptools import setup, find_packages

import versioneer


setup(
    name="pinnwand",
    version=versioneer.get_version(),  # type: ignore
    cmdclass=versioneer.get_cmdclass(),  # type: ignore
    description="Straightforward pastebin software.",
    url="https://github.com/supakeen/pinnwand",
    author="supakeen",
    author_email="cmdr@supakeen.com",
    packages=find_packages(),
    setup_requires=["pytest-runner", "pytest-cov"],
    install_requires=["click", "tornado", "pygments", "sqlalchemy"],
    tests_require=["pytest", "pytest-cov"],
    entry_points={"console_scripts": ["pinnwand=pinnwand.command:main"]},
    extras_require={
        "dev": ["pre-commit", "flake8", "black", "pytest", "pytest-cov", "mypy"]
    },
    package_data={"pinnwand": ["pinnwand/static", "pinnwand/template"]},
    include_package_data=True,
)
