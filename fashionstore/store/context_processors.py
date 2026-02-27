from .models import Cart

def cart_count(request):
    session_key = request.session.session_key
    count = 0
    if session_key:
        count = Cart.objects.filter(session_key=session_key).count()
    return {'cart_count': count}
