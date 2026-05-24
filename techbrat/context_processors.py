from techbrat.models import SavedItem


def saved_items_summary(request):
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {'saved_items_count': 0}

    return {
        'saved_items_count': SavedItem.objects.filter(user=request.user).count(),
    }
