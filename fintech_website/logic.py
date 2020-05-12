from .models import NIFTYdata, AMFIdata
import quandl
import numpy as np
import pandas as pd

quandl.ApiConfig.api_key = 'g-xPLP17vW67SWnDEM8j'


def rolling_returns(rdf, from_date, to_date, n):
    period = 365 * n
    dates = []
    values = []

    for date in rdf.index:
        if from_date <= date <= (to_date - pd.DateOffset(period)):
            idate = date + pd.DateOffset(period)
            while (idate not in rdf.index) and (idate <= to_date):
                idate += pd.DateOffset(1)
            if idate <= to_date:
                dates.append(idate)
                values.append(rdf.loc[idate].iat[0])
            else:
                dates.append(np.nan)
                values.append(np.nan)

    df = rdf[from_date:to_date - pd.DateOffset(period)]

    df.insert(1, 'retDate', dates)
    df.insert(2, 'ret' + rdf.columns[0], values)
    df = df.loc[df['retDate'] < to_date]
    df[rdf.columns[0] + 'RollingReturns'] = df.apply(lambda row: ((row[2] / row[0]) ** (1 / n) - 1) * 100,
                                                     axis=1)  # CAGR returns
    return df


def chance_of_beating(rr_df, rr_bm):
    df1 = pd.concat([rr_df['NAVRollingReturns'], rr_bm['TRIRollingReturns']], axis=1)
    df1 = df1.pct_change()
    df1 = df1.assign(flag=df1['NAVRollingReturns'] > df1['TRIRollingReturns'])

    flags = df1.flag.value_counts()
    f1 = flags[0] / len(df1)

    return flags[0] / len(df1)


def beta(df, bm, to_date):
    nvb = pd.concat([df['NAV'], bm['TRI']], axis=1)[to_date - pd.DateOffset(365 * 3):to_date]  # last year
    nvb1 = nvb.pct_change()

    x = np.mean(nvb1.NAV)
    y = np.mean(nvb1.TRI)

    nvb1['bD'] = nvb1.apply(lambda row: (x - row.TRI) ** 2, axis=1)
    nvb1['bN'] = nvb1.apply(lambda row: (x - row.TRI) * (y - row.NAV), axis=1)

    return np.sum(nvb1.bN) / np.sum(nvb1.bD)


def alpha(rfr, beta, df_flags, bm_flags):
    # rfr India 3M Bond Yield 
    # df_flags[1]  year to date returns (this year jan to march)
    # bm_flags[1]  year to date returns at market
    return df_flags[1] - rfr - (beta * (bm_flags[1] - rfr))


def sharpe(rfr, df_flags):
    return (df_flags[1] - rfr) / df_flags[2]


def get_results(code, rfr, from_date, to_date, n=3):  # =str(date.today())
    np.random.seed(3)
    df = quandl.get('AMFI/' + str(code), column_index='1', start_date=from_date, end_date=to_date)  # dates are strings
    df.rename(columns={'Net Asset Value': 'NAV'}, inplace=True)

    from_date = pd.to_datetime(from_date)
    to_date = pd.to_datetime(to_date)
    rr_df = rolling_returns(df, from_date, to_date, n)
    df_flags = rr_df['NAVRollingReturns'].describe()

    avg_rr = df_flags[1]
    std_rr = df_flags[2]
    min_rr = df_flags[3]
    max_rr = df_flags[7]

    bm = pd.DataFrame(
        list(NIFTYdata.objects.filter(date__gte=from_date).filter(date__lte=to_date).values('date', 'TRI')))
    bm['date'] = pd.to_datetime(bm['date'])
    bm['TRI'] = pd.to_numeric(bm['TRI'])
    bm = bm.set_index('date')
    rr_bm = rolling_returns(bm, from_date, to_date, n)
    bm_flags = rr_bm['TRIRollingReturns'].describe()

    cob = chance_of_beating(rr_df, rr_bm)
    be = beta(df, bm, to_date)
    al = alpha(rfr, be, df_flags, bm_flags)
    sh = sharpe(rfr, df_flags)

    return len(rr_df), n, avg_rr, max_rr, min_rr, std_rr, cob, al, be, sh


"""
import quandl
import datetime
quandl.ApiConfig.api_key = 'g-xPLP17vW67SWnDEM8j'
from fintech_website.models import NIFTYdata
import pandas as pd
from fintech_website.logic import rolling_returns
from_date = datetime.date(2020,1,1)
to_date = datetime.date(2000,1,1)
code = 100471
df = quandl.get('AMFI/' + str(code), column_index='1', start_date='2000-01-01', end_date='2020-01-01')

bm = pd.DataFrame(
        list(NIFTYdata.objects.filter(date__gte=from_date).filter(date__lte=to_date).values('date', 'TRI')))
bm['date'] = pd.to_datetime(bm['date'])
bm['TRI'] = pd.to_numeric(bm['TRI'])
bm.set_index('date')
"""
