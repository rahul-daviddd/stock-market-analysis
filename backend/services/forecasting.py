import torch
import torch.nn as nn
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pandas as pd

class LightweightLSTM(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2, output_size=1):
        super(LightweightLSTM, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        # Initialize hidden state with zeros
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).requires_grad_()
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size).requires_grad_()

        # We need to detach as we are doing truncated backpropagation through time (BPTT)
        out, _ = self.lstm(x, (h0.detach(), c0.detach()))

        # Index hidden state of last time step
        out = self.fc(out[:, -1, :]) 
        return out

def train_and_predict(df_history, forecast_days=5):
    """
    Trains a micro-LSTM on the fly to predict `forecast_days` out.
    Takes historically verified close prices.
    Returns array of forecasted close prices.
    """
    try:
        # 1. Prepare Data
        data = df_history[['close']].values.astype(float)
        scaler = MinMaxScaler(feature_range=(-1, 1))
        data_normalized = scaler.fit_transform(data)
        
        # Hyperparameters
        seq_length = 21  # 3 weeks lookback
        
        X, y = [], []
        for i in range(len(data_normalized) - seq_length):
            X.append(data_normalized[i:i+seq_length])
            y.append(data_normalized[i+seq_length])
            
        X = torch.tensor(np.array(X)).float()
        y = torch.tensor(np.array(y)).float()
        
        # 2. Build and Train Model
        model = LightweightLSTM()
        criterion = torch.nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
        
        epochs = 150 # Fast micro-training
        for _ in range(epochs):
            optimizer.zero_grad()
            outputs = model(X)
            loss = criterion(outputs, y)
            loss.backward()
            optimizer.step()
            
        # 3. Forecast future predictions
        predictions = []
        # Start with the last known sequence
        current_seq = X[-1].unsqueeze(0) 
        
        model.eval()
        for _ in range(forecast_days):
            with torch.no_grad():
                pred = model(current_seq)
                predictions.append(pred.item())
                # Append the new prediction and shift the sequence window
                # Ensure the pred tensor has matching dimensions to append
                pred_expanded = pred.unsqueeze(1) 
                current_seq = torch.cat((current_seq[:, 1:, :], pred_expanded), dim=1)
                
        # Inverse transform
        predicted_prices = scaler.inverse_transform(np.array(predictions).reshape(-1, 1))
        return [round(float(p[0]), 2) for p in predicted_prices]
        
    except Exception as e:
        print("LSTM Forecasting Failed:", e)
        return []
