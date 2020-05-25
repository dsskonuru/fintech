import io
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from .forms import DataForm
from .models import AMFIdata
from fintech_website.logic import get_results
from django.contrib import messages


@login_required
def home(request):
    if request.method == 'POST':
        form = DataForm(request.POST, request.FILES)
        if form.is_valid():
            code = form.cleaned_data['code']
            name = get_object_or_404(AMFIdata, pk=code)
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            rfr = float(form.cleaned_data['risk_free_rate'])
            n = form.cleaned_data['time_period']

            file = request.FILES['benchmark']
            if not file.name.endswith('.csv'):
                messages.error((request, 'This is not a CSV file'))

            bm = pd.read_csv(io.StringIO(file.read().decode('utf-8')), delimiter=',')
            results = get_results(code, bm, rfr, from_date, to_date, n=n)

            context = {'period': n, 'results': results, 'name': name}
            return render(request, 'results.html', context)
    else:
        form = DataForm()
        return render(request, 'home.html', {'form': form})