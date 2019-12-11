Let’s assume you need a model called: `Page`. Create a file under `YOUR_APP/models/page.py`:

```python
# example for Django’s default model
# YOUR_APP/models/page.py

from django.db import models

__all__ = ['Page',]

class Page(models.Model):
    # define your fields here...
    pass

# YOUR_APP/models/__init__.py
# append:
from .page import *
```

or, you can use `CustomBaseModel` or `CustomBaseModelWithSoftDelete`:

```bash
from django.db import models

from vb_baseapp.models import CustomBaseModelWithSoftDelete

__all__ = ['Page']

class Page(CustomBaseModelWithSoftDelete):
    # define your fields here...
    pass
```

Now make migrations etc... Use it as `from YOUR_APP.models import Page` :)
