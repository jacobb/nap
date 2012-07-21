==========
Quickstart
==========


Step One: Declare your resource
===============================


..  code-block:: python

    # note/client.py
    from nap.resources import RemoteModel, Field


    class Note(RemoteModel):

        pk = Field(api_name='id')
        title = Field()
        content = Field()

        class Meta:
            root_url = 'http://127.0.0.1:8000/api/'


Step Two: Access your data
==========================

.. code-block:: python

    from note.client import Note

    n = Note.objects.get('resource/1/')
    n.title
    # Some Title


Boring, right? Let's add some more stuff...

Step Three: Add a lookup url

..  code-block:: python
    :emphasize-lines: 13

    # note/client.py
    from nap.resources import RemoteModel, Field


    class Note(RemoteModel):

        pk = Field(api_name='id')
        title = Field()
        content = Field()

        class Meta:
            root_url = 'http://127.0.0.1:8000/api/'

    Note.add_lookup_url(r'note/(?P<pk>\d*)/')

    n = Note.lookup(pk=1)
    n.title = "New Title"
    n.save()

    n = Note.objects.get('resource/1/')
    n.title
    # "New Title"

