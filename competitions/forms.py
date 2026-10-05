from django import forms
from django.utils import timezone

from SoftUniFinalExam.mixins import ReadOnlyMixin, PlaceholderMixin
from competitions.models import Competitions


class CompetitionBaseForm(forms.ModelForm):
    class Meta:
        model = Competitions
        exclude = ('slug', 'participants')
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'date-picker'
                },
                format='%Y-%m-%d'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = timezone.now().date()
        self.fields['date'].widget.attrs['min'] = today.isoformat()

        self.fields['date'].widget.attrs['placeholder'] = 'Select a date'


class CompetitionCreateForm(CompetitionBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] += ' create-date-field'


class CompetitionEditForm(PlaceholderMixin, CompetitionBaseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.date:
            self.initial['date'] = self.instance.date.strftime('%Y-%m-%d')


class CompetitionDeleteForm(ReadOnlyMixin, CompetitionBaseForm):
    readonly_fields = ['title', 'club', 'context', 'date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.readonly_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['disabled'] = True
                self.fields[field_name].widget.attrs['readonly'] = True

        if 'date' in self.fields:
            self.fields['date'].widget = forms.DateInput(
                attrs={
                    'type': 'date',
                    'disabled': True,
                    'readonly': True,
                    'class': 'readonly-date'
                },
                format='%Y-%m-%d'
            )

    def clean(self):
        cleaned_data = super().clean()
        for field_name in self.readonly_fields:
            if field_name in cleaned_data and self.instance:
                cleaned_data[field_name] = getattr(self.instance, field_name)
        return cleaned_data