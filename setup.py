from setuptools import setup, find_packages

setup(
    name="frontdesk",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Add dependencies here, e.g. "flask", "requests"
    ],
    entry_points={
        "console_scripts": [
            "frontdesk=your_module.main:main",  # adjust to your entry file
        ],
    },
)

