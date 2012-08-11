===
nap
===

api access models and tools
===========================

Accessing APIs open-endily is an easy affair. pip install requests, pass in your data get data back. But the slight differences and demands of different API creating code that’s structured, re-usable and simple proves difficult.

nap hopes to help.

..  code-block:: python

    # note/client.py
    from nap.resources import ResourceModel, Field


    class Note(ResourceModel):

        pk = Field(api_name='id', resource_id=True)
        title = Field()
        content = Field()

        class Meta:
            root_url = 'http://127.0.0.1:8000/api/'
            resource_name = 'note'

    n = Note(title='Some Title', content="some content")

    # POST http://127.0.0.1:8000/api/note/
    n.save()

    n = Note.get('note/1/')
    # Some Title
    n.title

    # GET http://127.0.0.1:8000/api/note/1/
    n = Note.lookup(pk=1)
    n.title = "New Title"
    n.content = "I sure do love naps!"

    # PUT http://127.0.0.1:8000/api/note/1/
    n.save()

    n = Note.get('note/1/')
    # "New Title"
    n.title


nap aims to:

* Support Read (GET) and Write (POST/PUT/PATCH)
* Required little to no configuration needed for to-spec REST APIs
* Be easily configurable to fit any REST-like API
* Be customizable to fit even edgier use cases


Docs
====
https://nap.readthedocs.org


Installation
============

``% pip install https://github.com/jacobb/nap/``