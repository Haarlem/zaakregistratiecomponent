===================
Alfresco on Vagrant
===================

Creates a linux VM with vagrant, downloads, installs and runs Alfresco
Community.

Usage
=====

To use this with your project you need to follow these steps:

#. Start the virtual machine::

    $ vagrant up

#. If this is the first time, it will take a while for Alfresco to be
   downloaded, installed and configured.

#. Navigate to ``http://localhost:8080/share/page/context/mine/myfiles``.

#. In the UI, navigate to: Data ``Dictionary`` > ``Models``

#. Locate the ``alfresco-zsdms-model.xml`` in this folder and upload it.

#. After upload, hover over the file and on the right side click
   "Eigenschappen bewerken"

#. Find "Model Active" and make sure the checkbox is checked.

#. Click "Opslaan".

====

#. You can find the Alfresco installation at::

    http://localhost:8080/

The default username/password are: Admin/admin


Background
==========

Virtual machine
---------------

- Uses Vagrant Virtualbox provider
- Creates a VM based on Ubuntu Xenial 64bit
- VM with 4 CPUs, 4GB of memory
- Downloads Alfresco from Sourceforge
- Alfresco is exposed to **local port 8080**

Alfresco Setup
--------------

- Standard Alfresco installation with PostgreSQL
- Admin login defaults to admin:admin
- Install location: /opt/alfresco
