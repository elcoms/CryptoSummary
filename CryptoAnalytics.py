import pandas as pd
import pathlib
import matplotlib
import datetime
import os


os.system("reset")
currentFilePath = pathlib.Path(__file__).parent.absolute()

def ReadCSV(filename, parse_date=False):
    path = currentFilePath / "data" / filename
    if pathlib.Path(path).is_file():
        if parse_date:
            return pd.read_csv(path, header=0, parse_dates=[0], infer_datetime_format=True, keep_date_col=True)
        else:
            return pd.read_csv(path, header=0)
    else:
        raise Exception(f"[CryptoAnalytics] File ({path}) not found.")

def DollarToFloat(dollar):
    if type(dollar) is str:
        dollar = dollar.replace('$', '')
        dollar = dollar.replace(',', '')
        return float(dollar)
    elif type(dollar) is pd.DataFrame or type(dollar) is pd.Series:
        dollar = dollar.str.replace('$', '', regex=False)
        dollar = dollar.str.replace(',', '', regex=False)
        return dollar.astype('float')

def AvgDiff(high, low):
    diff = high - low
    return diff.mean(axis=0)

def LinearPrediction(filename, high=True):
    df = ReadCSV(filename, parse_date=True)
    data = df['High'] if high else df['Low']
    data = DollarToFloat(data)

    # Find Regression Line
    points = GetPeakValues(data, high)
    xMean = points['x'].mean(axis=0)
    yMean = points['y'].mean(axis=0)
    xyMean = (points['x'] * points['y']).mean(axis=0)
    xSqrMean = (points['x'] * points['x']).mean(axis=0)
    m = (xMean * yMean - xyMean) / (xMean * xMean - xSqrMean)
    b = yMean - m * xMean
    
    # Find the most common num of days for it to spike
    diff = {'i': []}
    for i in range(1, len(points['x'])):
        diff['i'].append(points['x'].iat[i] - points['x'].iat[i-1])

    diff = pd.DataFrame(data=diff)
    mode = diff.mode()
    mode = mode.iat[0, 0].item()

    # Find the rise/fall line
    # Find the interc ept between the 2 lines

    # Find the rough probability by correlation
    yLine = {'y': []}
    for i in range(0, len(points['x'])):
        yLine['y'].append(m * points['x'].iat[i] + b)

    def sqrError(errorList):
        return (errorList.apply(lambda x: x**2)).sum(axis=0)

    yLine = pd.DataFrame(data=yLine)
    errorSqr = sqrError(yLine['y'] - points['y'])
    errorSqrMean = sqrError((points['y']).apply(lambda x: yMean - x))
    lineProb = errorSqr / errorSqrMean
    
    # mode amt compared to total
    totalCount=0
    for i in diff.items():
        if i == mode:
            totalCount += 1
    modeProb = totalCount / len(diff['i'])

    finalProb = (lineProb + modeProb) / 2 * 100
    finalProb = round(finalProb, 2)

    # Find the next spike value
    y = m * (len(points['x']) + mode) + b
    y = round(y, 2)

    # Date
    date = df['Date'].iat[0] + datetime.timedelta(days=mode)
    date = date.strftime("%d %B")

    # Output
    print(f"The next spike will be ${y} on {date} with a probability of {finalProb}%")


def GetPeakValues(data, high=True):
    values = {'x': [], 'y': []}

    peak = False
    prev = data.iat[len(data)-1]
    index=0
    for i in range(len(data)-1, -1, -1):
        # if current value higher than previous 
        # and we want the highest, continue until
        # current value lower than prev
        # then we save the value and mark as peaked
        # so that we don't save extra values until 
        # we are climbing up again
        if data.iat[i] > prev and peak:
            peak = False
            if not high:
                values['x'].append(index)
                values['y'].append(prev)
        elif not peak:
            peak = True
            if high:
                values['x'].append(index)
                values['y'].append(prev)

        prev = data.iat[i]
        index+=1

    return pd.DataFrame(data=values)

# Dataframe: How to get
# Column
# print(df.iloc[:, 0])
# df[df.columns[0]
# Row
# print(df.iloc[0, :])
# Row Iteration
# df.itertuples(index=False)
# Value from a Column
# df.iloc[:, 0].iat[0]
# Column Length
# print(len(df.iloc[:, 0]))