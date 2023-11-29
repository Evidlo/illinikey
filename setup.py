from setuptools import setup

setup(
    name='illinikey',
    version='0.2.1',
    packages=['illinikey'],
    author="Evan Widloski",
    author_email="evan@evanw.org",
    description="generate offline one-time passwords for Duo two-factor login",
    long_description=open('README.md').read(),
    license="WTFPL",
    keywords="two-factor two factor duo illinois",
    url="https://github.com/evidlo/illinikey",
    entry_points={
        'console_scripts': [
            'illinikey = illinikey.illinikey:main',
        ]
    },
    install_requires=[
        'pyotp',
        'requests',
        'pycryptodome'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
    ]
)
