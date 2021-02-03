from setuptools import setup, find_packages
from os.path import join, dirname
import Server
import Client

setup(
    name='ServerTechData',
    version=Server.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    entry_points={
        'console_scripts': [
            "serverTech = Server.ServerSocketApp:main",
            "beremiz = Client.SocketClientApp:beremiz_simulation",
            'test_node = Client.SocketClientApp:test_node'
        ]
    },
    include_package_data=True,
    test_suite='TestServer'
)