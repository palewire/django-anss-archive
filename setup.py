import os
from setuptools import setup
from distutils.core import Command


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
        from django.core.management import call_command
        from django.conf import settings
        settings.configure(
            DATABASES={
                'default': {
                    'NAME': 'test',
                    'USER': 'postgres',
                    'ENGINE': 'django.contrib.gis.db.backends.postgis'
                },
            },
            MEDIA_ROOT="media",
            INSTALLED_APPS=("anss",),
            LOGGING={
                'version': 1,
                'disable_existing_loggers': False,
                'handlers': {
                    'file': {
                        'level': 'DEBUG',
                        'class': 'logging.FileHandler',
                        'filename': os.path.join(os.path.dirname(__file__), 'tests.log'),
                    },
                },
                'formatters': {
                    'verbose': {
                        'format': '%(levelname)s|%(asctime)s|%(module)s|%(message)s',
                        'datefmt': "%d/%b/%Y %H:%M:%S"
                    }
                },
                'loggers': {
                    'anss': {
                        'handlers': ['file'],
                        'level': 'DEBUG',
                        'propagate': True,
                    },
                }
            }
        )
        django.setup()
        call_command('test', 'anss')


setup(
    name='django-anss-archive',
    version='0.0.1',
    description=(
        "A Django application to archive real-time earthquake "
        "notifications from the USGS's Advanced National Seismic System"
    ),
    long_description=read('README.rst'),
    author='Los Angeles Times Data Desk',
    author_email='datadesk@latimes.com',
    url='http://www.github.com/datadesk/django-anss-archive',
    license="MIT",
    packages=("anss",),
    cmdclass={'test': TestCommand},
    install_requires=(
        "requests",
    ),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
    ],
    project_urls={
        'Maintainer': 'https://github.com/datadesk',
        'Source': 'https://github.com/datadesk/django-anss-archive',
        'Tracker': 'https://github.com/datadesk/django-anss-archive/issues'
    },
)
