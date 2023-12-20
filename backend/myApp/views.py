from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from myApp.scripts import accompaniment
from myApp.scripts import separation
import zipfile
import tempfile
import os
from pydub import AudioSegment


def helloWorld(request):
    print("hello")
    return JsonResponse({'message': 'Hello, World!'})

@csrf_exempt
def accompanimentGenerate(request):
    if request.method == 'POST':
        # Access the array from the form data
        instruments = request.POST.get('instruments')
        print('Received instruments from frontend:', instruments)

        # Access the audio file from the form data
        audio_file = request.FILES.get('audioFile')
        if audio_file:
            output_audio_path = './myApp/inputs/' + str(audio_file)
            with open(output_audio_path, 'wb') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)

            print('Audio file received and saved')

            drums = None
            if 'drums' in instruments:
                drums = 'normal'
            elif 'double-time' in instruments:
                drums = 'double-time'
            elif 'half-time' in instruments:
                drums = 'half-time'
            piano = True if 'piano' in instruments else False

            accompaniment.main(str(audio_file), length=30, drums=drums, piano=piano)

            file_base_name = str(audio_file)[:-4]
            accom = AudioSegment.from_file('./myApp/outputs/' + str(audio_file))

            with tempfile.TemporaryDirectory() as temp_dir:
                accom_path = os.path.join(temp_dir, str(audio_file))

                accom.export(accom_path, format='wav')

                # Create a ZIP file containing the processed audio files
                zip_buffer = tempfile.TemporaryFile()
                with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                    zip_file.write(accom_path, 'accompaniment.wav')

                # Seek to the beginning of the buffer before sending the response
                zip_buffer.seek(0)

                # Return the ZIP file as a response
                response = HttpResponse(zip_buffer.read(), content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename="processed_audio.zip"'

                print('Returning')
                return response

        return JsonResponse({'error': 'Audio file not received'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
def sourceSeparate(request):
    if request.method == 'POST':
        # Access the audio file from the form data
        audio_file = request.FILES.get('audioFile')
        if audio_file:
            # Do something with the audio file, e.g., save it to disk
            output_audio_path = './myApp/inputs/' + str(audio_file)
            with open(output_audio_path, 'wb') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)

            print('Audio file received and saved')

            separation.main(str(audio_file), 'vocals')

            file_base_name = str(audio_file)[:-4]
            vocals = AudioSegment.from_file('./myApp/scripts/separated/htdemucs/' + file_base_name + '_vocals.wav')
            ins = AudioSegment.from_file('./myApp/scripts/separated/htdemucs/' + file_base_name + '_no_vocals.wav')

            with tempfile.TemporaryDirectory() as temp_dir:
                vocals_path = os.path.join(temp_dir, file_base_name + '_vocals.wav')
                instruments_path = os.path.join(temp_dir, file_base_name + '_no_vocals.wav')

                vocals.export(vocals_path, format='wav')
                ins.export(instruments_path, format='wav')

                # Create a ZIP file containing the processed audio files
                zip_buffer = tempfile.TemporaryFile()
                with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                    zip_file.write(vocals_path, 'vocals.wav')
                    zip_file.write(instruments_path, 'instruments.wav')

                # Seek to the beginning of the buffer before sending the response
                zip_buffer.seek(0)

                # Return the ZIP file as a response
                response = HttpResponse(zip_buffer.read(), content_type='application/zip')
                response['Content-Disposition'] = 'attachment; filename="processed_audio.zip"'

                print('Returning')
                return response

        return JsonResponse({'error': 'Audio file not received'}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)