import os
from distutils.core import Command

from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import django
        from django.conf import settings
        from django.core.management import call_command

        settings.configure(
            DATABASES={
                "default": {
                    "NAME": "test",
                    "USER": "postgres",
                    "ENGINE": "django.contrib.gis.db.backends.postgis",
                },
            },
            MEDIA_ROOT="media",
            INSTALLED_APPS=("anss",),
        )
        django.setup()
        call_command("test", "anss")


setup(
    name="django-anss-archive",
    version="0.0.4",
    description=(
        "A Django application to archive real-time earthquake "
        "notifications from the USGS's Advanced National Seismic System"
    ),
    long_description=read("README.rst"),
    author="Los Angeles Times Data Desk",
    author_email="datadesk@latimes.com",
    url="http://www.github.com/datadesk/django-anss-archive",
    license="MIT",
    packages=(
        "anss",
        "anss.migrations",
        "anss.management",
        "anss.management.commands",
    ),
    cmdclass={"test": TestCommand},
    install_requires=("requests",),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
    ],
    project_urls={
        "Maintainer": "https://github.com/datadesk",
        "Source": "https://github.com/datadesk/django-anss-archive",
        "Tracker": "https://github.com/datadesk/django-anss-archive/issues",
    },
)
