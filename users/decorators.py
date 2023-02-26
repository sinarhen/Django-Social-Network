from django.core.exceptions import PermissionDenied
from functools import wraps

def profile_required(view): 
    """Checks if request user has the Profile"""
    @wraps(view)
    def _view(request, *args, **kwargs):
        if not request.user.profile:    
            raise PermissionDenied("ACCESS DENIED")
        return view(request, *args, **kwargs)
    return _view
