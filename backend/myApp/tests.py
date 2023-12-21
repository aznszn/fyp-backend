from django.test import TestCase
from scripts import accompaniment
import demucs.separate

accompaniment.main("atifcropped.wav", length=30, drums='half-time')