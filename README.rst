django-anss-archive
===================

A Django application to archive real-time earthquake notifications from the `U.S. Geological Survey's Advanced National Seismic System <https://earthquake.usgs.gov/earthquakes/feed/>`_


Requirements
------------

* The Django web framework
* A geospatial database backend like PostGIS


Getting started
---------------

Install the Python package.

::

    $ pipenv install django-anss-archive

Add to Django's INSTALLED_APPS.::

    INSTALLED_APPS = (
        ...
        "anss",
    )

Run migrations to create database tables.::

    $ python manage.py migrate

Run the archive command to save all earthquakes in the latest hour greater than 1.0 magnitude.::

    $ python manage.py getlatestearthquakes

Start your test server and visit the admin to see the results.::

    $ python manage.py runserver


Contributing
------------

Install dependencies for development ::

    $ pipenv install --dev

Run tests ::

    $ make test

Ship new version to PyPI ::

    $ make ship
