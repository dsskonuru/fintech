from .models import NIFTYdata
import quandl
import numpy as np
import pandas as pd
from datetime import timedelta

quandl.ApiConfig.api_key = 'g-xPLP17vW67SWnDEM8j'
np.random.seed(3)


def return_flags(df):
    df1 = df[:-1].iloc[:, 0].to_numpy()
    df2 = df[1:].iloc[:, 0].to_numpy()

    result = ((df2 / df1) - 1) * 100
    result = pd.Series(result)
    flags = result.describe()

    return flags, result


def capture_ratio(idx, results1, results2):
    df_result = []
    for i, result in enumerate(results1):
        if i in idx:
            df_result.append((result + 100) / 100)
        else:
            df_result.append(1)

    bm_result = []
    for i, result in enumerate(results2):
        if i in idx:
            bm_result.append((result + 100) / 100)
        else:
            bm_result.append(1)

    num_prod = np.prod(df_result)
    den_prod = np.prod(bm_result)

    n = len(idx)
    cr = (num_prod ** (12 / n) - 1) / (den_prod ** (12 / n) - 1)

    return cr


def returns(df, bm, rfr, to_date):
    df_flags, results1 = return_flags(df)
    bm_flags, results2 = return_flags(bm)

    pidx = results2.index[results2 >= 0].tolist()
    nidx = results2.index[results2 < 0].tolist()

    ucr = capture_ratio(pidx, results1, results2)
    dcr = capture_ratio(nidx, results1, results2)

    avg_r = df_flags[1]
    std_r = np.sqrt(12 * (df_flags[2] ** 2))
    min_r = df_flags[3]
    max_r = df_flags[7]

    be = beta(df, bm, to_date)
    al = alpha(rfr, be, df_flags, bm_flags)

    results = {'average': round(avg_r, 3), 'std': round(std_r, 3),
               'minimum': round(min_r, 3), 'maximum': round(max_r, 3),
               'alpha': round(al, 3), 'beta': round(be, 3),
               'ucr': round(ucr, 3), 'dcr': round(dcr, 3)}
    return results


def rolling(df, to_date, n):
    df1 = df[:to_date - pd.Timedelta(days=365 * n)]
    df2 = df[to_date - pd.Timedelta(days=len(df1) - 1):]

    df1.insert(1, 'retNAV', list(df2.iloc[:, 0]))
    string = str(df.columns[0] + 'RollingReturns')
    df1 = df1.assign(col=df1.apply(lambda row: ((row[1] / row[0]) ** (1 / n) - 1) * 100,
                                   axis=1))  # CAGR returns
    df1.rename(columns={'col': string}, inplace=True)
    return df1


def chance_of_beating(rr_df, rr_bm):
    df1 = pd.concat([rr_df['NAVRollingReturns'], rr_bm['TRIRollingReturns']], axis=1)
    df1 = df1.pct_change()
    df1 = df1.assign(flag=df1['NAVRollingReturns'] > df1['TRIRollingReturns'])

    flags = df1.flag.value_counts()

    return flags[0] / len(df1)


def beta(df, bm, to_date):
    nvb = pd.concat([df['NAV'], bm['TRI']], axis=1)[to_date - pd.DateOffset(365 * 3):to_date]  # last year
    nvb1 = nvb.pct_change()

    x = np.mean(nvb1.NAV)
    y = np.mean(nvb1.TRI)

    nvb1['bD'] = nvb1.apply(lambda row: (x - row.TRI) ** 2, axis=1)
    nvb1['bN'] = nvb1.apply(lambda row: (x - row.TRI) * (y - row.NAV), axis=1)

    return np.sum(nvb1.bN) / np.sum(nvb1.bD)


def alpha(rfr, bet, df_flags, bm_flags):
    # rfr India 3M Bond Yield 
    # df_flags[1]  year to date returns (this year jan to march)
    # bm_flags[1]  year to date returns at market
    return df_flags[1] - rfr - (bet * (bm_flags[1] - rfr))


def sharpe(rfr, df_flags):
    return (df_flags[1] - rfr) / df_flags[2]


# noinspection DuplicatedCode
def get_results(code, rfr, from_date, to_date, n=3):  # =str(date.today())
    df = quandl.get('AMFI/' + str(code), column_index='1', start_date=from_date, end_date=to_date)
    df.rename(columns={'Net Asset Value': 'NAV'}, inplace=True)

    ind = pd.date_range(from_date, to_date)

    df = df.reindex(ind, method='ffill')
    dfm = df[to_date - timedelta(days=365 * n):].resample('M').apply(lambda x: x.iloc[-1])
    dfy = df[to_date - timedelta(days=365 * n):].resample('Y').apply(lambda x: x.iloc[-1])

    bm = pd.DataFrame(
        list(NIFTYdata.objects.filter(date__gte=from_date).filter(date__lte=to_date).values('date', 'TRI')))
    bm['date'] = pd.to_datetime(bm['date'])
    bm['TRI'] = pd.to_numeric(bm['TRI'])
    bm = bm.set_index('date')

    bm = bm.reindex(ind, method='ffill')
    bmm = bm[to_date - timedelta(days=365 * n):].resample('M').apply(lambda x: x.iloc[-1])
    bmy = bm[to_date - timedelta(days=365 * n):].resample('Y').apply(lambda x: x.iloc[-1])

    yearly_returns = returns(dfy, bmy, rfr, to_date)
    monthly_returns = returns(dfm, bmm, rfr, to_date)

    rr_df = rolling(df, to_date, n)
    df_flags = rr_df['NAVRollingReturns'].describe()

    avg_rr = df_flags[1]
    std_rr = df_flags[2]
    min_rr = df_flags[3]
    max_rr = df_flags[7]

    rr_bm = rolling(bm, to_date, n)
    bm_flags = rr_bm['TRIRollingReturns'].describe()

    cob = chance_of_beating(rr_df, rr_bm)
    be = beta(df, bm, to_date)
    al = alpha(rfr, be, df_flags, bm_flags)
    sh = sharpe(rfr, df_flags)

    rolling_returns = {'average': round(avg_rr, 3),
                       'std': round(std_rr, 3),
                       'minimum': round(min_rr, 3),
                       'maximum': round(max_rr, 3),
                       'alpha': round(al, 3), 'beta': round(be, 3),
                       'sharpe': round(sh, 3), 'cob': round(cob, 3),
                       'length': len(rr_df)}

    return {'year': yearly_returns, 'month': monthly_returns,
            'rolling': rolling_returns}
