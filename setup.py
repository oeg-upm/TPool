import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
    # get rid of the first three lines in the readme
    long_description = "\n".join(long_description.split('\n')[3:])

setuptools.setup(
    name="TPool",
    version="1.3",
    author="Ahmad Alobaid",
    author_email="aalobaid@fi.upm.es",
    description="Thread Pool for Python 2 and 3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/oeg-upm/PPool",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: System :: Operating System"
    ],
)