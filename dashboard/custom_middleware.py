from django.utils.deprecation import MiddlewareMixin
from . import views

class CustomMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path!='/request-count/reset':
            request.session['count']=request.session.get('count',0)+1
        elif request.path=='/request-count/reset' and request.method=='POST':
            request.session['count']=0
        
        
