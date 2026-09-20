from django import forms
from .models import Property, PropertyImage, Inquiry


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
    'title', 'description', 'property_type',
    'address', 'city', 'area', 'landmark', 'latitude', 'longitude',
    'price', 'deposit', 'price_negotiable', 'location_unlock_fee',
    'bedrooms', 'bathrooms', 'area_sqft', 'floor', 'total_floors',
    'furnishing', 'gender_preference',
    'has_wifi', 'has_parking', 'has_kitchen', 'has_ac', 'has_water',
    'has_electricity', 'has_security', 'has_balcony', 'has_lift',
    'has_gym', 'pets_allowed', 'smoking_allowed',
    'status', 'contact_phone', 'contact_whatsapp',
]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Spacious Single Room near Campus'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your property...'}),
            'property_type': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kathmandu'}),
            'area': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Baneshwor'}),
            'landmark': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monthly rent'}),
            'deposit': forms.NumberInput(attrs={'class': 'form-control'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'area_sqft': forms.NumberInput(attrs={'class': 'form-control'}),
            'floor': forms.TextInput(attrs={'class': 'form-control'}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control'}),
            'furnishing': forms.Select(attrs={'class': 'form-control'}),
            'gender_preference': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_whatsapp': forms.TextInput(attrs={'class': 'form-control'}),
            'has_wifi': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_parking': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_kitchen': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_ac': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_water': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_electricity': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_security': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_balcony': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_lift': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_gym': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'pets_allowed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'smoking_allowed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'price_negotiable': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'location_unlock_fee': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Fee to unlock location'}),
        }


class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ['image', 'caption', 'is_primary']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['message', 'phone']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Hi, I am interested in this property. Is it still available?'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your phone number (optional)'
            }),
        }


class PropertySearchForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Search by location, title...'
    }))
    property_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Property.PROPERTY_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    city = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'City'
    }))
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Min Price'
    }))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Max Price'
    }))
    bedrooms = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={
        'class': 'form-control',
        'placeholder': 'Bedrooms',
        'min': 0
    }))
    furnishing = forms.ChoiceField(
        choices=[('', 'Any')] + list(Property.FURNISHING),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    gender_preference = forms.ChoiceField(
        choices=[('', 'Any')] + list(Property.GENDER_PREF),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    has_wifi = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    has_parking = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    has_kitchen = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    has_ac = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
