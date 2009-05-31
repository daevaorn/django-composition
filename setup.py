#!/usr/bin/env python

from distutils.core import setup

def get_description():
    import os
    return "".join(
        file(
            os.path.join(os.path.dirname(os.path.normpath(__file__)),
            'README'
        ), 'r').readlines()[1:] # strip markdown marker line
    )

setup(
    name="django-composition",
    version="0.2",

    license="New BSD License",

    author='Alex Koshelev',
    author_email="daevaorn@gmail.com",

    url="http://bitbucket.org/daevaorn/django-composition/",

    packages=[
        "composition",
        "composition.shortcuts",
        "composition.tests"
    ],

    description=get_description(),

    classifiers=[
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
    ]
)
