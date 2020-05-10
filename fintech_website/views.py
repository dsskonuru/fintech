from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import AMFIdata

from .forms import DataForm, NiftyForm
from dal import autocomplete


@login_required
def home(request):
    if request.method == 'POST':
        form = DataForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            data = get_object_or_404(AMFIdata, pk=code)
            name = form.cleaned_data['name']
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            print(code, name, from_date, to_date, data)
            return render(request, 'results.html')
    else:
        form = DataForm()
        return render(request, 'home.html', {'form': form})


@login_required
def nifty_update(request):
    if request.method == 'POST':
        form = NiftyForm(request.POST)
        if form.is_valid():
            value = form.cleaned_data['value']
            date = form.cleaned_data['date']
            print(value, date)
    else:
        form = NiftyForm()
    return render(request, 'nifty_update.html', {'form': form})
