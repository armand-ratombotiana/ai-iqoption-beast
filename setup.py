#!/usr/bin/env python3
"""Setup script for IQOption AI Trading Bot"""

from setuptools import setup, find_packages
import os


def read_file(filename):
    """Read file contents"""
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()


# Read README if it exists
long_description = ''
if os.path.exists('README.md'):
    long_description = read_file('README.md')

setup(
    name='iqoption-ai-trading-bot',
    version='1.0.0',
    description='AI-powered binary options trading bot with advanced risk management',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='KAEL Trading Bot',
    python_requires='>=3.8',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'flask>=3.0.0',
        'requests>=2.31.0',
        'python-dateutil>=2.8.2',
        'python-dotenv>=1.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.4.3',
            'pytest-cov>=4.1.0',
            'pytest-flask>=1.3.0',
            'black>=23.12.1',
            'flake8>=7.0.0',
            'mypy>=1.8.0',
        ],
        'prod': [
            'gunicorn>=21.2.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'trading-bot=src.api.app:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Office/Business :: Financial :: Investment',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)
