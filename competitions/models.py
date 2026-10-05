import uuid
import re
from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify

from clubs.models import Club


class Competitions(models.Model):
    title = models.CharField(
        max_length=100,
    )
    date = models.DateField()
    context = models.TextField()

    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        editable=False,
    )

    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="competitions"
    )

    participants = models.ManyToManyField(
        User,
        related_name='joined_participants',
        blank=True,
    )

    def _generate_slug(self):
        """Генерира валиден slug с поддръжка на кирилица"""
        base_slug = slugify(self.title)

        if not base_slug:
            cyrillic_to_latin = {
                'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
                'е': 'e', 'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y',
                'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
                'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
                'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh',
                'щ': 'sht', 'ъ': 'a', 'ь': 'y', 'ю': 'yu', 'я': 'ya',
                'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D',
                'Е': 'E', 'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y',
                'К': 'K', 'Л': 'L', 'М': 'M', 'Н': 'N', 'О': 'O',
                'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
                'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh',
                'Щ': 'Sht', 'Ъ': 'A', 'Ь': 'Y', 'Ю': 'Yu', 'Я': 'Ya'
            }

            transliterated = ''
            for char in self.title:
                if char in cyrillic_to_latin:
                    transliterated += cyrillic_to_latin[char]
                elif char.isalnum():
                    transliterated += char
                elif char == ' ':
                    transliterated += '-'
                else:
                    transliterated += '-'

            base_slug = re.sub(r'-+', '-', transliterated).strip('-')
            base_slug = base_slug.lower()

        if not base_slug:
            base_slug = str(uuid.uuid4())[:8]

        return base_slug

    def save(self, *args, **kwargs):
        """Генерира уникален slug при запазване"""
        if not self.slug:
            base_slug = self._generate_slug()
            slug = base_slug
            counter = 1

            while True:
                existing = Competitions.objects.filter(slug=slug)
                if self.pk:
                    existing = existing.exclude(pk=self.pk)

                if not existing.exists():
                    break

                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - Hosted by {self.club.title} on {self.date}"