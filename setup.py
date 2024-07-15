from setuptools import setup, find_packages
from mininotify.config import GITHUB_USERNAME as username
from mininotify.config import GITHUB_PAO as PAO

setup(
    name='mininotify',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'some_package',  # other dependencies
        f'skynet @ git+https://{username}:{PAO}@github.com/Air-Pollution-and-Exposure-Section/skynet.git@96-add-emails-table-for-mininotify-support'
    ],
)

