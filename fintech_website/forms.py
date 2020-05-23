from django import forms


class DateInput(forms.DateInput):
    input_type = 'date'


class DataForm(forms.Form):
    code = forms.IntegerField(max_value=148366, min_value=100027)
    # name = forms.CharField(max_length=150)
    time_period = forms.IntegerField(required=False, initial=3)
    from_date = forms.DateField(widget=DateInput)
    to_date = forms.DateField(widget=DateInput)
    risk_free_rate = forms.DecimalField()


class NiftyForm(forms.Form):
    value = forms.DecimalField()
    date = forms.DateField(widget=DateInput)

