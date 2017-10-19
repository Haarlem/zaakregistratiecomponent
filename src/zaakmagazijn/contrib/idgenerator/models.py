from django.db import models
from django.db.models import Max
from django.utils import timezone


class IncrementalYearIdManager(models.Manager):
    def create_unique(self):
        year = timezone.now().strftime('%Y')

        max_number = self.model.objects.filter(year=year).aggregate(max_number=Max('number'))['max_number']
        if max_number is None:
            max_number = 0

        return self.create(year=year, number=max_number + 1)


class IncrementalYearId(models.Model):
    year = models.IntegerField()
    number = models.PositiveIntegerField()
    value = models.CharField(max_length=40, unique=True)

    objects = IncrementalYearIdManager()

    def save(self, *args, **kwargs):
        self.value = '{}-{:07d}'.format(self.year, self.number)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (
            ('year', 'number'),
        )
