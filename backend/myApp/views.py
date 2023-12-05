from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from myApp.scripts import accompaniment
import os

def helloWorld(request):
    return JsonResponse({'message': 'Hello, World!'})

@csrf_exempt
def melodyGenerate(request):
    if request.method == 'POST':
        # Access the array from the form data
        instruments = request.POST.get('instruments')
        print('Received instruments from frontend:', instruments)

        # Access the audio file from the form data
        audio_file = request.FILES.get('audioFile')
        if audio_file:
            # Do something with the audio file, e.g., save it to disk
            filename = "melody.wav"
            output_audio_path = 'myApp/inputs/' + filename
            with open(output_audio_path, 'wb') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)

            print('Audio file received and saved')
            
            accompaniment.main(filename)
            # Process the audio file if needed (replace this with your processing logic)

            # Return the processed audio file as a response
            with open('scripts/generated/melody_generated.wav', 'rb') as audio_file:
                response = HttpResponse(audio_file.read(), content_type='audio/wav')
                response['Content-Disposition'] = 'attachment; filename="accompaintment.wav"'
                return response

        return JsonResponse({'error': 'Audio file not received'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)