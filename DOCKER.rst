============
Installation
============

Getting started
===============

Quick start using Docker
------------------------

The easiest way to get started is by using
`Docker Compose <https://docs.docker.com/compose/install/>`_.

1. Clone or download the code from
   `Github <https://github.com/Haarlem/zaakregistratiecomponent>`_ in a
   folder like ``zaakmagazijn``:

   .. code-block:: bash

       $ git clone git@github.com:Haarlem/zaakregistratiecomponent.git zakenmagazijn
       Cloning into 'zakenmagazijn'...
       ...

       $ cd zakenmagazijn

2. Start the database and Zakenmagazijn services:

   .. code-block:: bash

       $ docker-compose up -d
       Starting zakenmagazijn_db_1 ... done
       Starting zakenmagazijn_web_1 ... done

3. Create an admin user for our Zakenmagazijn and load initial data. If
   different container names are shown above, use the container name ending
   with ``_web_1``:

   .. code-block:: bash

       $ docker exec -it zakenmagazijn_web_1 /app/src/manage.py createsuperuser
       Username: admin
       ...
       Superuser created successfully.

       $ docker exec -it zakenmagazijn_web_1 /app/src/manage.py loaddata admin_index groups
       Installed 5 object(s) from 2 fixture(s)

4. Point your browser to ``http://localhost:8000/`` to access the
   Zaaktypecatalogus with the credentials used in step 3.

   If you are using ``Docker Machine``, you need to point your browser to the
   Docker VM IP address. You can get the IP address by doing
   ``docker-machine ls`` and point your browser to
   ``http://<ip>:8000/`` instead (where the IP is shown below the URL column):

   .. code-block:: bash

       $ docker-machine ls
       NAME      ACTIVE   DRIVER       STATE     URL
       default   *        virtualbox   Running   tcp://<ip>:<port>

5. To shutdown the services, use ``docker-compose down``.

More Docker
-----------

If you just want to run the Zaaktypecatalogus as a Docker container and
connect to an external database, you can build and run the ``Dockerfile`` and
pass several environment variables. See ``src/zaakmagazijn/conf/docker.py`` for all
settings.

.. code-block:: bash

    $ docker build . && docker run \
        -p 8000:8000 \
        -e DJANGO_SETTINGS_MODULE=zaakmagazijn.conf.docker \
        -e DATABASE_USERNAME=... \
        -e DATABASE_PASSWORD=... \
        -e DATABASE_HOST=... \
        --name zakenmagazijn

    $ docker exec -it zakenmagazijn /app/src/manage.py createsuperuser