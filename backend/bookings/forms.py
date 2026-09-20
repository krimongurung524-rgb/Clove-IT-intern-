from django import forms
from .models import VisitBooking


class VisitBookingForm(forms.ModelForm):
    class Meta:
        model = VisitBooking
        fields = ['preferred_date', 'preferred_time', 'message']
        widgets = {
            'preferred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'preferred_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requests or questions?'
            }),
        }
    
    def clean_preferred_date(self):
        date = self.cleaned_data['preferred_date']
        from django.utils import timezone
        if date < timezone.now().date():
            raise forms.ValidationError("Visit date cannot be in the past.")
        return date
