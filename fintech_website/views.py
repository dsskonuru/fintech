from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from .forms import DataForm, NiftyForm
from .models import AMFIdata, NIFTYdata
from fintech_website.logic import get_results


@login_required
def home(request):
    if request.method == 'POST':
        form = DataForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            name = get_object_or_404(AMFIdata, pk=code)
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            rfr = float(form.cleaned_data['risk_free_rate'])
            n = form.cleaned_data['time_period']
            results = get_results(code, rfr, from_date, to_date, n=n)

            context = {'period': n, 'results': results, 'name': name}
            return render(request, 'results.html', context)
    else:
        form = DataForm()
        return render(request, 'home.html', {'form': form})


@login_required  # update the database!
def nifty_update(request):
    if request.method == 'POST':
        form = NiftyForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            value = form.cleaned_data['value']

            d = NIFTYdata(date, value)
            d.save()

            context = {
                'form': NiftyForm(),
                'message': 'The value has been updated',
                'table': get_nifty_top(),
            }

    else:
        context = {
            'form': NiftyForm(),
            'message': '',
            'table': get_nifty_top(),
        }
    return render(request, 'nifty_update.html', context)


def get_nifty_top():
    qs = NIFTYdata.objects.all()[:5]
    tab = []
    for q in qs:
        r = ' '.join([str(q.get_date()), str(q.get_tri())])
        tab.append(r)
    return tab
