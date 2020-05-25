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


def returns(df, bm, rfr, to_date, n, monthly=True):
    df_flags, results1 = return_flags(df)
    bm_flags, results2 = return_flags(bm)

    pidx = results2.index[results2 >= 0].tolist()
    nidx = results2.index[results2 < 0].tolist()

    avg_r = ((df.iloc[-1][0] / df.iloc[0][0]) ** (1 / n) - 1) * 100
    std_r = np.sqrt(12 * (df_flags[2] ** 2))
    min_r = df_flags[3]
    max_r = df_flags[7]
    r_square = r_2(df, bm, n)
    be = beta(df, bm, to_date)
    al = alpha(rfr, be, df_flags, bm_flags)

    results = {'average': round(avg_r, 3), 'std': round(std_r, 3),
               'minimum': round(min_r, 3), 'maximum': round(max_r, 3),
               'alpha': round(al, 3), 'beta': round(be, 3), 'r_2': round(r_square, 3)}

    if monthly:
        ucr = capture_ratio(pidx, results1, results2)
        dcr = capture_ratio(nidx, results1, results2)
        res = {'ucr': round(ucr, 3), 'dcr': round(dcr, 3)}
        results = {**results, **res}

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


def rolling_returns(df, bm, to_date, n, rfr):
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
    r_square = r_2(df, bm, n)

    results = {'average': round(avg_rr, 3),
               'std': round(std_rr, 3),
               'minimum': round(min_rr, 3),
               'maximum': round(max_rr, 3),
               'alpha': round(al, 3), 'beta': round(be, 3),
               'sharpe': round(sh, 3), 'cob': round(cob, 3),
               'length': len(rr_df), 'r_2': round(r_square, 3)}

    return results


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
    # df_flags[1]  year to date returns
    # bm_flags[1]  year to date returns at market
    return df_flags[1] - rfr - (bet * (bm_flags[1] - rfr))


def sharpe(rfr, df_flags):
    return (df_flags[1] - rfr) / df_flags[2]


def r_2(df, bm, n):
    x = np.array(df.iloc[:, 0])
    y = np.array(bm.iloc[:, 0])

    sig_x = sum(x)
    sig_y = sum(y)
    sig_x_2 = sig_x ** 2
    sig_y_2 = sig_y ** 2

    xy = np.array([i * j for i, j in zip(x, y)])
    sig_xy = sum(xy)

    x2 = x ** 2
    y2 = y ** 2
    sig_x2 = sum(x2)
    sig_y2 = sum(y2)

    r2 = (n * sig_xy - sig_x * sig_y) / np.sqrt((n * sig_x2 - sig_x_2) * (n * sig_y2 - sig_y_2))

    return r2


def create_data_frames(df, ind, td, n):
    df = df.reindex(ind, method='ffill')
    df = df.dropna()
    dfn = df[td - timedelta(days=365 * n):]
    dfm = dfn.resample('M').apply(lambda x: x.iloc[-1])
    dfy = dfn.resample('Y').apply(lambda x: x.iloc[-1])

    return df, dfn, dfm, dfy


def get_results(code, bm, rfr, from_date, to_date, n=3):
    df = quandl.get('AMFI/' + str(code), column_index='1', start_date=from_date, end_date=to_date)
    df.rename(columns={'Net Asset Value': 'NAV'}, inplace=True)

    bm.rename(columns={'Total Returns Index': 'TRI'}, inplace=True)
    bm['Date'] = pd.to_datetime(bm['Date'])
    bm['TRI'] = pd.to_numeric(bm['TRI'])
    bm = bm.set_index('Date')
    bm = bm.iloc[::-1]

    td = min(bm.index[-1], df.index[-1], to_date)
    ind = pd.date_range(from_date, td)

    df, dfn, dfm, dfy = create_data_frames(df, ind, td, n)
    bm, bmn, bmm, bmy = create_data_frames(bm, ind, td, n)

    yearly_returns = returns(dfy, bmy, rfr, td, n, monthly=False)
    monthly_returns = returns(dfm, bmm, rfr, td, n)
    r_returns = rolling_returns(df, bm, td, n, rfr)
    rn_returns = rolling_returns(dfn, bmn, td, 1, rfr)

    return {'year': yearly_returns, 'month': monthly_returns,
            'rolling': r_returns, 'n_rolling': rn_returns}
