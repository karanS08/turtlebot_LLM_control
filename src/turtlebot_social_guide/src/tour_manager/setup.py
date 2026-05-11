from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'tour_manager'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*')))
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='tom',
    maintainer_email='a.liver.f.let.cha@gmail.com',
    description='SQLite-backed tour recording, retrieval, and visualization tools.',
    license='Apache-2.0',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'tour_manager = tour_manager.tour_manager_service:main',
            'tour_saver = tour_manager.tour_saver:main',
            'waypoint_visualizer = tour_manager.waypoint_visualizer:main',
        ],
    },
)
