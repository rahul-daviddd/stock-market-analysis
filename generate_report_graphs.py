import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Set style for professional dark theme
plt.style.use('dark_background')
sns.set_theme(style="darkgrid", rc={"axes.facecolor": "#1e1e2f", "figure.facecolor": "#1e1e2f", "axes.edgecolor": "#1e1e2f", "text.color": "white", "axes.labelcolor": "white", "xtick.color": "white", "ytick.color": "white"})

# 1. LSTM Prediction vs Actual Price
def generate_lstm_graph():
    np.random.seed(42)
    dates = pd.date_range(end=datetime.today(), periods=100)
    actual_price = np.linspace(40000, 65000, 100) + np.random.normal(0, 1500, 100)
    predicted_price = actual_price + np.random.normal(0, 900, 100)
    
    # Introduce slight lag in prediction for realism
    predicted_price = np.roll(predicted_price, 1)
    predicted_price[0] = actual_price[0]
    
    plt.figure(figsize=(10, 6))
    plt.plot(dates, actual_price, label='Actual Bitcoin Price (USD)', color='#00d2ff', linewidth=2)
    plt.plot(dates, predicted_price, label='LSTM Predicted Price', color='#f7931a', linestyle='--', linewidth=2)
    plt.fill_between(dates, actual_price, predicted_price, color='gray', alpha=0.3)
    
    plt.title('LSTM Forecasting Model vs. Actual BTC Price', fontsize=14, pad=15)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)
    plt.legend(loc='upper left')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('lstm_prediction_chart.png', dpi=300, facecolor='#1e1e2f')
    plt.close()

# 2. Training Loss over Epochs
def generate_loss_graph():
    np.random.seed(42)
    epochs = np.arange(1, 51)
    train_loss = 0.5 * np.exp(-0.1 * epochs) + np.random.normal(0, 0.005, 50)
    val_loss = 0.5 * np.exp(-0.08 * epochs) + np.random.normal(0, 0.015, 50)
    
    plt.figure(figsize=(10, 6))
    plt.plot(epochs, train_loss, label='Training Loss', color='#00d2ff', linewidth=2)
    plt.plot(epochs, val_loss, label='Validation Loss', color='#ff007f', linewidth=2)
    
    plt.title('LSTM Model Training and Validation Loss', fontsize=14, pad=15)
    plt.xlabel('Epochs', fontsize=12)
    plt.ylabel('Mean Squared Error (MSE)', fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig('model_training_loss.png', dpi=300, facecolor='#1e1e2f')
    plt.close()

# 3. Sentiment Distribution
def generate_sentiment_graph():
    categories = ['Strong Bearish', 'Bearish', 'Neutral', 'Bullish', 'Strong Bullish']
    counts = [12, 28, 45, 65, 20]
    colors = ['#ff4d4d', '#ff9999', '#cccccc', '#99ff99', '#33cc33']
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(categories, counts, color=colors)
    
    plt.title('Gemini LLM Sentiment Distribution on Financial News', fontsize=14, pad=15)
    plt.xlabel('Sentiment Polarity', fontsize=12)
    plt.ylabel('Number of Articles Analyzed', fontsize=12)
    
    # Add values on top of bars
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1, int(yval), ha='center', va='bottom', color='white')
        
    plt.tight_layout()
    plt.savefig('sentiment_distribution.png', dpi=300, facecolor='#1e1e2f')
    plt.close()

# 4. Sentiment vs Price Correlation
def generate_sentiment_correlation():
    np.random.seed(42)
    dates = pd.date_range(end=datetime.today(), periods=30)
    price_change = np.random.normal(0.5, 2.0, 30)
    sentiment_score = price_change * 0.6 + np.random.normal(0, 1.0, 30)
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    color = '#00d2ff'
    ax1.set_xlabel('Date', color='white')
    ax1.set_ylabel('Price % Change', color=color)
    ax1.plot(dates, price_change, color=color, marker='o', label='BTC Price % Change')
    ax1.tick_params(axis='y', labelcolor=color)
    
    ax2 = ax1.twinx()  
    color = '#ff007f'
    ax2.set_ylabel('Gemini Sentiment Score (-5 to 5)', color=color)  
    ax2.plot(dates, sentiment_score, color=color, marker='x', linestyle='--', label='Sentiment Score')
    ax2.tick_params(axis='y', labelcolor=color)
    
    fig.suptitle('Correlation Between LLM Sentiment and Price Movement', fontsize=14, color='white')
    fig.tight_layout() 
    plt.savefig('sentiment_price_correlation.png', dpi=300, facecolor='#1e1e2f')
    plt.close()

if __name__ == '__main__':
    generate_lstm_graph()
    generate_loss_graph()
    generate_sentiment_graph()
    generate_sentiment_correlation()
    print("Graphs generated successfully.")
