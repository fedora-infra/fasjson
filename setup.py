from setuptools import setup, find_packages

setup(
    name="fasjson",
    author="Christian Heimes",
    version="0.0.1",
    author_email="cheimes@redhat.com",
    description="Read-only REST-like API for Fedora Account System",
    #package_dir={"": "src"},
    #packages=find_packages(where="src"),
    packages=find_packages(exclude=('test,')),
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
        "Flask",
        "python-ldap",
        "dnspython",
        "gssapi",
        "typing"
    ],
    tests_requires=[
        'pytest',
        'pytest-sugar',
        'pytest-mock',
        'mypy',
        'mypy-extensions'
    ],
    python_requires=">=3.6",
)
