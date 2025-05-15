from setuptools import setup, Extension
import pybind11

# Define the extension module
ext_modules = [
    Extension(
        'knapsack_optimizer_cpp',  # Name of the module to import in Python
        ['knapsack.cpp'],        # List of C++ source files
        include_dirs=[
            pybind11.get_include(), # Include directory for pybind11 headers
            # Add any other include directories your C++ code might need here
        ],
        language='c++',
        extra_compile_args=['/std:c++17'] # For MSVC, use '-std=c++17' for GCC/Clang
    ),
]

setup(
    name='knapsack_optimizer_cpp',
    version='0.1.0',
    author='Your Name', # Replace with your name
    author_email='your.email@example.com', # Replace with your email
    description='C++ extension for knapsack-like optimization',
    ext_modules=ext_modules,
    # You might need to specify the pybind11 version if you install it via setup_requires
    # setup_requires=['pybind11>=2.6'], # Example
    zip_safe=False, # Recommended for C++ extensions
) 