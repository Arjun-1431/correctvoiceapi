from django.urls import path
from .views import *

urlpatterns = [
    path('make_call/', make_outbound_call, name='make_outbound_call'),
    path('handle_call/', handle_call, name='handle_call'),
    path('', call_page, name='call_page'),
    path('get_twilio_token/', get_twilio_token, name='get_twilio_token'), 
    path('save_call_details/', save_call_details, name='save_call_details'),
    path('get_call_history/', get_call_history, name='get_call_history'),
    path('call_history/', call_history_page, name='call_history_page'),
    path('get_balance/', get_balance, name='get_balance'),



]

