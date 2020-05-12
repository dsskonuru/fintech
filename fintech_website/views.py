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
            # name = form.cleaned_data['name']

            code = form.cleaned_data['code']
            name = get_object_or_404(AMFIdata, pk=code)
            from_date = form.cleaned_data['from_date']
            to_date = form.cleaned_data['to_date']
            rfr = form.cleaned_data['risk_free_rate']
            n = form.cleaned_data['time_period']
            len_rr, n, avg_rr, max_rr, min_rr, std_rr, cob, al, be, sh = get_results(code, rfr, from_date, to_date, n=n)

            context = {
                'len_rr': len_rr,
                'n': n,
                'avg_rr': round(avg_rr, 3),
                'max_rr': round(max_rr, 3),
                'min_rr': round(min_rr, 3),
                'std_rr': round(std_rr, 3),
                'cob': round(cob, 3),
                'al': round(al, 3),
                'be': round(be, 3),
                'sh': round(sh, 3),
                'name': name
            }
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
            nifty = get_object_or_404(NIFTYdata, pk=date)
            value = form.cleaned_data['value']
            print(value, date, nifty)

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
