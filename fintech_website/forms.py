from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML
from django import forms
from dal import autocomplete


class DateInput(forms.DateInput):
    input_type = 'date'


class DataForm(forms.Form):
    code = forms.IntegerField(max_value=148366, min_value=100027)
    name = forms.CharField(max_length=150)
    from_date = forms.DateField(widget=DateInput)
    to_date = forms.DateField(widget=DateInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'code', 'name', 'from_date', 'to_date',
            HTML("<br></br>"),
            Submit('submit', 'Get Results', css_class='btn_success')
        )


class NiftyForm(forms.Form):
    value = forms.DecimalField()
    date = forms.DateField(widget=DateInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'value', 'date',
            HTML("<br></br>"),
            Submit('submit', 'Update', css_class='btn_success')
        )
