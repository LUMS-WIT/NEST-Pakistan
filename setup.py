from setuptools import setup, find_packages
#from Cython.Build import cythonize

setup(
    name='messageix_pakistan',
    version='0.1.0',
    description='An Open Source Integrated Assessment Model for Pakistan',
    author='Your Name',
    author_email='your.email@example.com',
    packages=find_packages(include=['MESSAGE_PK', 'MESSAGE_PK.*']),  # Adjust if needed
    install_requires=[
        'setuptools >= 64', # Address deprecation warning from pip
        'pandas',
        'numpy',
        'plotly',
        'pycountry',
        'ixmp',
        'message_ix >= 3.4.0',
        'pyam-iamc >= 0.6',
        'scipy',
        'toml',
        'ipykernel',
        'pytest',
        'click',
        'message-ix-models[report]',
    ],
    entry_points={
        'console_scripts': [
            'message-pakistan=MESSAGE_PK:messagerun',  
        ],
    },
    extras_require={
        'extras': ['geotext', 'message-ix-models'],  # Optional dependencies
    },
    #ext_modules = cythonize("MESSAGE_PK.py"),
)
