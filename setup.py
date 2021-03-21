from setuptools import find_packages, setup

setup(
    name='bvrnapi',
    version='0.0.1',
    python_requires='>=3.8',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)
