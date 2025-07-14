from setuptools import setup, find_packages

setup(
    name='xfox',
    version='0.1.0',
    description='Linux joystick remapper using evdev + uinput',
    author='pxlman',
    author_email='agxgv7573@gmail.com',
    packages=find_packages(),  # auto-discovers the remaper/ package
    install_requires=[
        'evdev-binary',
    ],
    entry_points={
        'console_scripts': [
            'xfox = xfox.cli:main'  # cmd name = package.module:function
        ]
    },
    python_requires='>=3.7',
    include_package_data=True,
    zip_safe=False,
)

