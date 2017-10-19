

def create_incremental_year_id():
    from .models import IncrementalYearId
    obj = IncrementalYearId.objects.create_unique()
    return obj.value
