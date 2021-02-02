from setuptools import setup, find_packages
from os.path import join, dirname
import Server

setup(
    name='ServerTechData',
    version=Server.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    entry_points={
        'console_scripts': [
            "server = Server.ServerSocketApp:main"
        ]
    },
    include_package_data=True,
    stest_suite='test'
)