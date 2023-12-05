from django.test import TestCase
from scripts import accompaniment

accompaniment.main("../inputs/melody.wav", length=10)