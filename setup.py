from setuptools import setup, find_packages

setup(
    name="fasjson",
    author="Christian Heimes",
    version="0.0.1",
    author_email="cheimes@redhat.com",
    description="Read-only REST-like API for Fedora Account System",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "Flask==1.1.1",
        "python-ldap==3.2.0",
        "dnspython==1.16.0",
        "gssapi==1.6.2",
        "typing==3.7.4.1"
    ],
    tests_requires=[
        'pytest==5.3.5',
        'pytest-sugar==0.9.2',
        'pytest-mock==2.0.0',
        'mypy==0.761',
        'mypy-extensions==0.4.3'
    ],
    python_requires=">=3.6",
)
