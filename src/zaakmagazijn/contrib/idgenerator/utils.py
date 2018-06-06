

def create_incremental_year_id(data=None):
    from .models import IncrementalYearId
    obj = IncrementalYearId.objects.create_unique()
    return obj.value


def create_incremental_year_with_org_id(data=None):
    try:
        organisation = data.stuurgegevens.ontvanger.organisatie
    except AttributeError as e:
        raise ValueError('Ontvangende organisatie is verplicht in de stuurgegevens voor het genereren van identificaties.')

    from .models import IncrementalYearId
    obj = IncrementalYearId.objects.create_unique(organisation=organisation)
    return obj.value
