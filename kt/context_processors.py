from ktapp.utils import get_design_version


def get_design_version_context(request):
    design_version = 'v%d' % get_design_version(request)
    if design_version == 'v1':
        design_version_postfix = ''
    else:
        design_version_postfix = '-%s' % design_version
    return {
        'design_version': design_version,
        'design_version_postfix': design_version_postfix,
    }


def get_number_of_suggested_stuff_for_admins(request):
    from ktapp import models
    return {
        'number_of_suggested_films': models.SuggestedContent.objects.filter(domain=models.SuggestedContent.DOMAIN_FILM).count(),
        'number_of_suggested_links': models.SuggestedContent.objects.filter(domain=models.SuggestedContent.DOMAIN_LINK).count(),
        'number_of_suggested_reviews': models.Review.objects.filter(approved=False).count(),
        'number_of_suggested_bios': models.Biography.objects.filter(approved=False).count(),
    }
