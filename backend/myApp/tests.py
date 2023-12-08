from django.test import TestCase
from scripts import accompaniment

accompaniment.main("sunshine30s.wav", length=30, drums='half-time')