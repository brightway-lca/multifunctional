from setuptools import setup

v_temp = {}
with open("multifunctional/version.py") as fp:
    exec(fp.read(), v_temp)
version = ".".join((str(x) for x in v_temp["version"]))


setup(
    name='multifunctional',
    version=version,
    packages=["multifunctional"],
    author="Chris Mutel",
    author_email="cmutel@gmail.com",
    license="BSD-3-Clause",
    install_requires=[
        "brightway2"
    ],
    url="https://github.com/brightway-lca/multifunctional",
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    description='your_name_here',
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
)
