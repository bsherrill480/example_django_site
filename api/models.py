from django.db import models
from safedelete.models import SafeDeleteModel, SOFT_DELETE


# Create your models here.
class Master(SafeDeleteModel):
    class Meta:
        abstract = True
    create_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    _safedelete_policy = SOFT_DELETE
