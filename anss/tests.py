from django.core.management import call_command
from django.test import TestCase


class USGSTest(TestCase):
    def test_command(self):
        call_command("getlatestanssfeed")
