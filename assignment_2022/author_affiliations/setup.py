from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    author="Kalle Mäkelä",
    author_email='kallemakela@example.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description="author_affiliations",
    entry_points={
        'console_scripts': [
            'author_affiliations=author_affiliations.cli:main',
            'authors_by_country=author_affiliations.authors_by_country:main',
            'co_author_graph=author_affiliations.co_author_graph:main',
            'country_network=author_affiliations.country_network:main',
        ],
    },
    install_requires=['networkx'],
    long_description=readme,
    include_package_data=True,
    name='author_affiliations',
    packages=find_packages(include=['author_affiliations', 'author_affiliations.*']),
    test_suite='tests',
    tests_require=['pytest>=3'],
    url='https://github.com/Kallemakela/author_affiliations',
    version='0.1.0',
    zip_safe=False,
)
