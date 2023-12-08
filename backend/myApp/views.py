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
            output_audio_path = 'myApp/inputs/' + str(audio_file)
            with open(output_audio_path, 'wb') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)

            print('Audio file received and saved')
            
            # Process the audio file if needed (replace this with your processing logic)
            accompaniment.main(str(audio_file), length=30, drums='half-time')

            # Return the processed audio file as a response
            with open('myApp/outputs/' + str(audio_file), 'rb') as audio_file:
                response = HttpResponse(audio_file.read(), content_type='audio/wav')
                response['Content-Disposition'] = 'attachment; filename="accompaintment.wav"'
                return response

        return JsonResponse({'error': 'Audio file not received'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)