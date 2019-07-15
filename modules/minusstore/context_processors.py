def pjax(request):
    """chech whether request is called from pjax js function"""
    if 'HTTP_X_PJAX' in request.META and request.META['HTTP_X_PJAX']:
        return {'pjax':True}
    else: return {'pjax':False} 
