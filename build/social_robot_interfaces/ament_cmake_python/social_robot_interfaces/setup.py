from setuptools import find_packages
from setuptools import setup

setup(
    name='social_robot_interfaces',
    version='0.1.0',
    packages=find_packages(
        include=('social_robot_interfaces', 'social_robot_interfaces.*')),
)
