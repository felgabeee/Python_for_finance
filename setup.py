from setuptools import setup
import setuptools
setup(
    name="Python_for_finance",
    version="0.0.1",
    description="Usefull finance related functions",
    long_description_content_type="",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/felgabeee",
    author="felgabe",
    author_email="felix.gabet@edhec.com",
    keywords=["Options", "black and scholes", "Python for finance", "Bloomberg", "Implied volatility"],
    license="MIT",
    packages=setuptools.find_packages(),
    include_package_data=True,
)