import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(

    author="",
    author_email="",
    url="https://github.com/nikltk/nikol",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    entry_points = {
        'console_scripts': ['nikol=nikol.main.cli:main'],
        
    }
)

