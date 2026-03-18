from .models import MediaAsset


def site_logo(request):
    logo = MediaAsset.objects.filter(tag='logo', is_active=True).order_by('order').first()
    return {'site_logo': logo}