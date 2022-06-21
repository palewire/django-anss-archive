import os
from distutils.core import Command

from setuptools import setup


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


def version_scheme(version):
    """
    Version scheme hack for setuptools_scm.
    Appears to be necessary to due to the bug documented here: https://github.com/pypa/setuptools_scm/issues/342
    If that issue is resolved, this method can be removed.
    """
    import time

    from setuptools_scm.version import guess_next_version

    if version.exact:
        return version.format_with("{tag}")
    else:
        _super_value = version.format_next_version(guess_next_version)
        now = int(time.time())
        return _super_value + str(now)


def local_version(version):
    """
    Local version scheme hack for setuptools_scm.
    Appears to be necessary to due to the bug documented here: https://github.com/pypa/setuptools_scm/issues/342
    If that issue is resolved, this method can be removed.
    """
    return ""


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
                    "HOST": "localhost",
                    "PORT": 5432,
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
    description=(
        "A Django application to archive real-time earthquake "
        "notifications from the USGS's Advanced National Seismic System"
    ),
    long_description=read("README.rst"),
    author="Ben Welsh",
    author_email="b@palewi.re",
    url="https://palewi.re/docs/django-anss-archive/",
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
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
    ],
    project_urls={
        "Maintainer": "https://github.com/palewire",
        "Source": "https://github.com/palewire/django-anss-archive",
        "Tracker": "https://github.com/palewire/django-anss-archive/issues",
    },
    setup_requires=["setuptools_scm"],
    use_scm_version={"version_scheme": version_scheme, "local_scheme": local_version},
)
