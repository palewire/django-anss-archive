from django.test import TestCase
from django.core.management import call_command


class USGSTest(TestCase):

    def test_command(self):
        call_command("getlatestanssfeed")
