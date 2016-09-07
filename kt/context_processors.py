def get_design_version(request):
    design_version = 'v1'
    if request.user.is_authenticated:
        design_version = 'v%d' % request.user.design_version
    if design_version == 'v1':
        design_version_postfix = ''
    else:
        design_version_postfix = '-%s' % design_version
    return {
        'design_version': design_version,
        'design_version_postfix': design_version_postfix,
    }
