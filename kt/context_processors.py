def get_design_version(request):
    design_version = 'v1'
    design_version_postfix = ''
    if request.user.is_authenticated:
        if request.user.id == 1:
            design_version = 'v2'
            design_version_postfix = '-v2'
    return {
        'design_version': design_version,
        'design_version_postfix': design_version_postfix,
    }
