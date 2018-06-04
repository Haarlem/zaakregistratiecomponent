from django.db import models, transaction
from django.db.models import Max
from django.utils import timezone


class IncrementalYearIdManager(models.Manager):
    @transaction.atomic
    def create_unique(self, organisation=None):
        year = timezone.now().strftime('%Y')

        if organisation is None:
            organisation = ''

        max_number = self.model.objects.filter(
            year=year, organisation=organisation
        ).aggregate(
            max_number=Max('number')
        )['max_number']

        if max_number is None:
            max_number = 0

        return self.create(year=year, organisation=organisation, number=max_number + 1)


class IncrementalYearId(models.Model):
    year = models.IntegerField()
    number = models.PositiveIntegerField()
    organisation = models.CharField(max_length=4, blank=True, default='')
    value = models.CharField(max_length=40, unique=True)

    objects = IncrementalYearIdManager()

    def save(self, *args, **kwargs):
        self.value = '{}-{:07d}'.format(self.year, self.number)
        if self.organisation:
            self.value = '{}-{}'.format(self.organisation, self.value)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = (
            ('year', 'number', 'organisation'),
        )
