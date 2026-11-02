import React, { useEffect, useRef, useState } from 'react';
import { createChart, CrosshairMode, CandlestickSeries, LineSeries } from 'lightweight-charts';
import { Activity, TrendingUp, TrendingDown, DollarSign, Newspaper } from 'lucide-react';
import './App.css';

function App() {
  const chartContainerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);
  const [data, setData] = useState([]);
  const [technicals, setTechnicals] = useState(null);
  const fibLinesRef = useRef([]);
  const zigzagSeriesRef = useRef(null);
  const [sentiment, setSentiment] = useState(null);
  const [symbol, setSymbol] = useState('BTC');
  const [error, setError] = useState(null);

  useEffect(() => {
    setError(null);
    setTechnicals(null);
    setData([]);
    // 1. Fetch Price Action & LSTM / Indicators
    fetch(`http://127.0.0.1:8000/api/history/${symbol}`)
      .then((res) => {
        if (!res.ok) throw new Error("Connection Refused");
        return res.json();
      })
      .then((payload) => {
        if (payload.history && Array.isArray(payload.history)) {
          const formatted = payload.history.map(d => ({
            time: d.time.split(' ')[0],
            open: d.open,
            high: d.high,
            low: d.low,
            close: d.close
          }));
          setData(formatted);
          setTechnicals(payload.technicals);
        }
      })
      .catch((err) => {
        console.error("Failed to fetch history", err);
        setError("Backend Server Offline. Please start Uvicorn.");
      });

    // 2. Fetch FinBERT News Sentiment (Runs in parallel)
    setSentiment(null); // Reset while loading
    fetch(`http://127.0.0.1:8000/api/sentiment/${symbol}`)
      .then((res) => {
        if (!res.ok) throw new Error("Connection Refused");
        return res.json();
      })
      .then((payload) => {
        setSentiment(payload);
      })
      .catch((err) => {
        console.error("Failed to fetch sentiment", err);
        setError("Backend Server Offline. Please start Uvicorn.");
      });
      
  }, [symbol]);

  // Mock Real-Time Updates (Every 30 seconds)
  useEffect(() => {
    if (data.length === 0) return;

    const intervalId = setInterval(() => {
      setData(prevData => {
        const newData = [...prevData];
        const lastCandle = { ...newData[newData.length - 1] };
        
        // Simulate a small random price movement (-0.2% to +0.2%)
        const volatility = lastCandle.close * 0.004; 
        const change = (Math.random() - 0.5) * volatility;
        
        lastCandle.close = lastCandle.close + change;
        
        // Update high/low if the new close exceeds them
        if (lastCandle.close > lastCandle.high) lastCandle.high = lastCandle.close;
        if (lastCandle.close < lastCandle.low) lastCandle.low = lastCandle.close;

        newData[newData.length - 1] = lastCandle;
        
        // Update the chart series directly to show the animation
        if (seriesRef.current) {
          seriesRef.current.update(lastCandle);
        }
        
        return newData;
      });
    }, 5000);

    return () => clearInterval(intervalId);
  }, [data.length]);

  useEffect(() => {
    if (chartContainerRef.current && data.length > 0) {
      if (!chartRef.current) {
        chartRef.current = createChart(chartContainerRef.current, {
          width: chartContainerRef.current.clientWidth || 800,
          height: 400,
          layout: {
            background: { type: 'solid', color: 'transparent' },
            textColor: '#d1d4dc',
          },
          grid: {
            vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
            horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
          },
          crosshair: {
            mode: CrosshairMode.Normal,
          },
          rightPriceScale: {
            borderColor: 'rgba(197, 203, 206, 0.8)',
          },
          timeScale: {
            borderColor: 'rgba(197, 203, 206, 0.8)',
          },
        });

        const candlestickSeries = chartRef.current.addSeries(CandlestickSeries, {
          upColor: '#00f5d4',
          downColor: '#ff3366',
          borderDownColor: '#ff3366',
          borderUpColor: '#00f5d4',
          wickDownColor: '#ff3366',
          wickUpColor: '#00f5d4',
        });

        candlestickSeries.setData(data);
        seriesRef.current = candlestickSeries;
        
        zigzagSeriesRef.current = chartRef.current.addSeries(LineSeries, {
            color: 'rgba(252, 163, 17, 0.8)',
            lineWidth: 2,
            lineStyle: 0,
            crosshairMarkerVisible: false,
            lastValueVisible: false,
            priceLineVisible: false
        });

        const handleResize = () => {
          chartRef.current.applyOptions({
            width: chartContainerRef.current.clientWidth
          });
        };
        window.addEventListener('resize', handleResize);
        
        return () => {
          window.removeEventListener('resize', handleResize);
          chartRef.current.remove();
          chartRef.current = null;
          seriesRef.current = null;
          zigzagSeriesRef.current = null;
          fibLinesRef.current = [];
        };
      } else {
        if (seriesRef.current) {
          seriesRef.current.setData(data);
        }
      }
      
      // Update Technicals Overlays (Runs gracefully on mount and updates)
      if (seriesRef.current && technicals) {
          if (technicals.zigzag && zigzagSeriesRef.current) {
              zigzagSeriesRef.current.setData(technicals.zigzag);
          }
          
          if (fibLinesRef.current.length > 0) {
              fibLinesRef.current.forEach(line => seriesRef.current.removePriceLine(line));
              fibLinesRef.current = [];
          }
          
          if (technicals.fibonacci) {
              Object.entries(technicals.fibonacci).forEach(([lvl, price]) => {
                  const line = seriesRef.current.createPriceLine({
                      price: price,
                      color: lvl === "0" || lvl === "1" ? 'rgba(255, 51, 102, 0.6)' : 'rgba(0, 245, 212, 0.3)',
                      lineWidth: 1,
                      lineStyle: 2,
                      axisLabelVisible: true,
                      title: `Fib ${lvl}`
                  });
                  fibLinesRef.current.push(line);
              });
          }
      }
    }
  }, [data, technicals]);

  return (
    <div className="dashboard-container">
      <header className="header glass-panel">
        <h1 className="text-gradient">NexTrade Crypto Analytics</h1>
        <div className="ticker-selector">
          <select value={symbol} onChange={(e) => setSymbol(e.target.value)}>
            <option value="BTC">Bitcoin (BTC)</option>
            <option value="ETH">Ethereum (ETH)</option>
            <option value="SOL">Solana (SOL)</option>
            <option value="ADA">Cardano (ADA)</option>
          </select>
        </div>
      </header>

      <main className="main-content">
        <div className="stats-row">
          <div className="stat-card glass-panel">
            <DollarSign className="stat-icon" style={{color: 'var(--accent-green)'}}/>
            <div>
              <h3>Latest Price</h3>
              <p className="stat-value text-gradient">
                ${data.length > 0 && typeof data[data.length-1]?.close === 'number' ? (data[data.length-1].close).toFixed(2) : '---'}
              </p>
              {technicals?.lstm_forecast?.length > 0 && (
                <p style={{fontSize: '0.8rem', color: '#9d50bb', margin: '4px 0 0 0', fontWeight: 'bold'}}>
                   LSTM 5-Day Target: ${technicals.lstm_forecast[4]}
                </p>
              )}
            </div>
          </div>
          
          <div className="stat-card glass-panel">
            <Activity className="stat-icon" style={{color: error ? 'var(--accent-red)' : 'var(--accent-purple)'}}/>
            <div>
              <h3>Basic Signal (RSI & MACD)</h3>
              <p className="stat-value" style={{color: error ? 'var(--accent-red)' : technicals?.signal?.includes('Buy') ? 'var(--accent-green)' : technicals?.signal?.includes('Sell') ? 'var(--accent-red)' : 'white'}}>
                {error ? 'Offline' : technicals ? technicals.signal : 'Evaluating...'}
              </p>
            </div>
          </div>
          
          {technicals && (
             <div className="stat-card glass-panel">
               <TrendingDown className="stat-icon" style={{color: '#8c8d9e'}}/>
               <div>
                 <h3>Indicators</h3>
                 <p className="stat-value" style={{fontSize: '1.2rem', marginTop: '0.5rem'}}>
                   RSI: {technicals.rsi.toFixed(1)} 
                   <br/>
                   MACD: {technicals.macd.toFixed(2)}
                 </p>
               </div>
             </div>
          )}

          <div className="stat-card glass-panel">
             <Newspaper className="stat-icon" style={{color: error ? 'var(--accent-red)' : '#3498db'}}/>
             <div>
               <h3>AI News Sentiment</h3>
               <p className="stat-value" style={{
                 color: error ? 'var(--accent-red)' : sentiment?.narrative === 'Bullish' ? 'var(--accent-green)' : 
                        sentiment?.narrative === 'Bearish' ? 'var(--accent-red)' : '#8c8d9e'
               }}>
                 {error ? 'Offline' : sentiment ? sentiment.narrative : 'Loading AI...'}
               </p>
             </div>
          </div>

        </div>

        <div className="content-grid">
          <div className="chart-container glass-panel">
            <h2>{symbol} Price Action</h2>
            {error && <div style={{padding: '1rem', background: 'rgba(239, 68, 68, 0.1)', color: 'var(--accent-red)', borderRadius: '8px', marginBottom: '1rem', border: '1px solid var(--accent-red)', fontWeight: '500'}}>{error}</div>}
            <div ref={chartContainerRef} className="chart-wrapper"></div>
          </div>
          
          {sentiment?.articles && sentiment.articles.length > 0 && (
            <div className="news-container glass-panel">
              <h2>Latest Market Intelligence</h2>
              <div className="news-list">
                {sentiment.articles.map((article, i) => (
                  <div key={i} className="news-article" style={{ borderLeft: `4px solid ${article.sentiment === 'positive' ? 'var(--accent-green)' : article.sentiment === 'negative' ? 'var(--accent-red)' : 'var(--text-muted)'}` }}>
                    <a href={article.url} target="_blank" rel="noreferrer" className="news-link">
                      {article.title}
                    </a>
                    <span className="news-badge" style={{ color: article.sentiment === 'positive' ? 'var(--accent-green)' : article.sentiment === 'negative' ? 'var(--accent-red)' : '#8c8d9e' }}>
                      {article.sentiment.toUpperCase()} ({Math.round(article.confidence * 100)}%)
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

      </main>
    </div>
  );
}

export default App;
