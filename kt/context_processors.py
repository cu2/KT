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
