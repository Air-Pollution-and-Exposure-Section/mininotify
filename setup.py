from setuptools import setup, find_packages

setup(
    name='mininotify',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'some_package',  # other dependencies
        'skynet @ git+https://github.com/Air-Pollution-and-Exposure-Section/skynet.git@96-add-emails-table-for-mininotify-support'
    ],
)

