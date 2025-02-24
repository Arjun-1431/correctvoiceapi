# from django.conf import settings
# from django.http import JsonResponse, HttpResponse
# from django.views.decorators.csrf import csrf_exempt  # ✅ Disable CSRF for Twilio
# from twilio.rest import Client
# from twilio.twiml.voice_response import VoiceResponse
# import urllib.parse  # ✅ Import this to encode URLs properly

# def make_outbound_call(request):
#     """Initiates an outbound call using Twilio API to the requested number."""
#     client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

#     to_number = request.GET.get("to")  # The number to call
#     if not to_number:
#         return JsonResponse({"error": "Missing 'to' phone number"}, status=400)

#     try:
#         # ✅ Remove spaces & properly encode the URL
#         encoded_to_number = urllib.parse.quote(to_number)  # Encodes special characters
#         twiml_url = f"https://c02a-2405-201-3031-e87f-88da-faa8-73c7-a615.ngrok-free.app/calls/handle_call/?to={encoded_to_number}"

#         call = client.calls.create(
#             url=twiml_url,  # Twilio will request this URL for call instructions
#             to=to_number.strip(),  # ✅ Strip spaces from the phone number
#             from_=settings.TWILIO_PHONE_NUMBER
#         )
#         return JsonResponse({"message": "Call initiated", "call_sid": call.sid})
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# @csrf_exempt  # ✅ Disable CSRF for Twilio requests
# def handle_call(request):
#     """Directly connects the caller to the requested number."""
#     response = VoiceResponse()
    
#     # ✅ Get the number from request parameters (sent from make_outbound_call)
#     to_number = request.GET.get("to")  
#     if not to_number:
#         return HttpResponse("Missing 'to' phone number", status=400)

#     # ✅ Directly dial the requested number (no keypress required)
#     dial = response.dial(callerId=settings.TWILIO_PHONE_NUMBER)
#     dial.number(to_number.strip())  # ✅ Strip spaces from phone number
#     response.append(dial)

#     return HttpResponse(str(response), content_type="text/xml")



from django.conf import settings
from django.http import JsonResponse
from twilio.jwt.access_token import AccessToken  # ✅ Import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant  # ✅ Import VoiceGrant
from django.conf import settings

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Dial
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from twilio.rest import Client
import urllib.parse

from .models import *



def make_outbound_call(request):
    """Initiates an outbound call to a real phone number using Twilio API."""
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    to_number = request.GET.get("to")  # ✅ Get the number from the request
    if not to_number:
        return JsonResponse({"error": "Missing 'to' phone number"}, status=400)

    try:
        # ✅ Make sure Twilio sends the call to the correct endpoint
        twiml_url = f"https://728e-2405-201-3031-e87f-e40c-1a87-d9ff-79a8.ngrok-free.app/handle_call/?to={urllib.parse.quote(to_number)}"

        call = client.calls.create(
            url=twiml_url,  # ✅ Twilio will fetch call instructions from this URL
            to=to_number.strip(),
            from_=settings.TWILIO_PHONE_NUMBER
        )
        return JsonResponse({"message": "Call initiated!", "call_sid": call.sid})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)



from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse, Dial
@csrf_exempt  # ✅ Disable CSRF protection for Twilio Webhooks
def handle_call(request):
    """Handles Twilio incoming calls and connects to an outbound number."""
    
    # ✅ Check if request is POST (Twilio sends POST requests)
    if request.method != "POST":
        return HttpResponse("Invalid request method", status=400)
    
    response = VoiceResponse()
    
    # ✅ Twilio sends phone number in "to" parameter (GET or POST)
    to_number = request.GET.get("to") or request.POST.get("To")
    
    if not to_number:
        return HttpResponse("Missing 'to' phone number", status=400)

    # ✅ Connect the WebRTC caller to the entered phone number
    dial = Dial(callerId=settings.TWILIO_PHONE_NUMBER)
    dial.number(to_number)
    response.append(dial)

    return HttpResponse(str(response), content_type="text/xml")


def get_twilio_token(request):
    """Generates Twilio token for WebRTC calls in the browser."""
    account_sid = settings.TWILIO_ACCOUNT_SID
    api_key = settings.TWILIO_API_KEY
    api_secret = settings.TWILIO_API_SECRET
    twilio_app_sid = settings.TWILIO_TWIML_APP_SID

    identity = "browser_user"  # The identity used in Twilio Client

    token = AccessToken(account_sid, api_key, api_secret, identity=identity)
    voice_grant = VoiceGrant(outgoing_application_sid=twilio_app_sid)
    token.add_grant(voice_grant)

    return JsonResponse({"token": token.to_jwt()})

def call_page(request):
  return render(request, "call.html")





from .models import CallDetail
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from datetime import datetime


@csrf_exempt
def save_call_details(request):
    if request.method == 'POST':
        try:
            print(f"Request body: {request.body}")  # Debugging
            data = json.loads(request.body)
            print(f"Parsed data: {data}")

            number = data.get('number')
            status = data.get('status')
            timestamp = data.get('timestamp')

            if not number or not status or not timestamp:
                print("❌ Missing fields")
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            # Convert Unix timestamp (milliseconds) to datetime
            timestamp = datetime.fromtimestamp(timestamp / 1000.0)

            call_detail = CallDetail.objects.create(
                phone_number=number,
                call_status=status,
                timestamp=timestamp
            )
            print(f"✅ Call saved: {call_detail}")

            return JsonResponse({'message': 'Call details saved successfully'}, status=201)
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            print(f"❌ Unexpected server error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)



def call_history_page(request):
  return render(request, 'callhistory.html')

def get_call_history(request):
    calls = CallDetail.objects.all().order_by('phone_number', 'timestamp')
    call_durations = []

    call_map = {}

    for call in calls:
        if call.call_status == 'started':
            call_map[call.phone_number] = call.timestamp
        elif call.call_status == 'ended' and call.phone_number in call_map:
            start_time = call_map.pop(call.phone_number)
            duration = call.timestamp - start_time
            call_durations.append({
                'phone_number': call.phone_number,
                'duration': str(duration)
            })

    return JsonResponse(call_durations, safe=False)


def get_balance(request):
    try:
        balance = Balance.objects.first()
        if balance:
            return JsonResponse({'balance': f"{balance.amount:.2f}"})
        else:
            return JsonResponse({'balance': '0.00'})
    except Balance.DoesNotExist:
        return JsonResponse({'balance': '0.00'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)