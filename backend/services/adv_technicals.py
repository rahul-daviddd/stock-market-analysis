import pandas as pd

def calculate_fibonacci(data: pd.DataFrame):
    """
    Calculates Fibonacci Retracement levels from the global High and Low over the period.
    """
    if len(data) == 0:
        return {}
    
    max_price = float(data['high'].max())
    min_price = float(data['low'].min())
    diff = max_price - min_price
    
    levels = {
        "0": max_price,
        "0.236": max_price - 0.236 * diff,
        "0.382": max_price - 0.382 * diff,
        "0.5": max_price - 0.5 * diff,
        "0.618": max_price - 0.618 * diff,
        "0.786": max_price - 0.786 * diff,
        "1": min_price
    }
    
    return {k: round(v, 2) for k, v in levels.items()}

def calculate_zigzag(data: pd.DataFrame, deviation_perc: float = 5.0):
    """
    Simplified Elliott Wave / ZigZag algorithm.
    Finds swing highs and lows that deflect by at least deviation_perc.
    Returns struct of coordinates [ {time: 'YYYY-MM-DD', value: price}, ... ]
    """
    if len(data) == 0:
        return []
        
    deviation = deviation_perc / 100.0
    swings = []
    
    last_high = float(data['high'].iloc[0])
    last_low = float(data['low'].iloc[0])
    
    def get_date_str(idx):
        return str(idx.date()) if hasattr(idx, 'date') else str(idx).split(' ')[0]
        
    last_high_time = get_date_str(data.index[0])
    last_low_time = last_high_time
    
    if len(data) > 1:
        trend = 1 if data['close'].iloc[1] > data['close'].iloc[0] else -1
    else:
        trend = 1
    
    for idx, row in data.iterrows():
        date_str = get_date_str(idx)
        high = float(row['high'])
        low = float(row['low'])
        
        if trend == 1:
            if high > last_high:
                last_high = high
                last_high_time = date_str
            elif low < last_high * (1 - deviation):
                swings.append({"time": last_high_time, "value": round(last_high, 2)})
                trend = -1
                last_low = low
                last_low_time = date_str
        else:
            if low < last_low:
                last_low = low
                last_low_time = date_str
            elif high > last_low * (1 + deviation):
                swings.append({"time": last_low_time, "value": round(last_low, 2)})
                trend = 1
                last_high = high
                last_high_time = date_str
                
    # Close out the sequence
    if len(data) > 0:
        final_idx = data.index[-1]
        swings.append({"time": get_date_str(final_idx), "value": round(float(data['close'].iloc[-1]), 2)})
        
    return swings
