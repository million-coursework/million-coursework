from django.db import models

# Create your models here.


class Feedback(models.Model):
    text = models.TextField()
    email = models.TextField()

    def __str__(self):
        return self.text[:20] + "..."
