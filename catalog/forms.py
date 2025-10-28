from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import datetime
from django import forms

class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
        help_text="Введите дату между сегодняшним днем и 4 неделями вперед (по умолчанию 3 недели).",
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'style': 'max-width: 300px;'
        }),
        label="Новая дата возврата"
    )

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']
        if data < datetime.date.today():
            raise ValidationError(_('Неверная дата - продление в прошлом'))
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(
                _('Неверная дата - продление более чем на 4 недели вперед'))

        return data