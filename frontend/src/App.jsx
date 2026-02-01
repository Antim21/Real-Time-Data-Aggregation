import { useState, useEffect, useCallback } from 'react'
import './App.css'
import RateGrid from './components/RateGrid'
import FreshnessIndicator from './components/FreshnessIndicator'
import ErrorState from './components/ErrorState'

const API_BASE_URL = 'http://localhost:8000'
const REFRESH_INTERVAL = 60000 // Auto-refresh every 60 seconds

function App() {
  const [rates, setRates] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastUpdated, setLastUpdated] = useState(null)
  const [freshness, setFreshness] = useState('fresh')
  const [sourcesUsed, setSourcesUsed] = useState(0)
  const [sourcesAvailable, setSourcesAvailable] = useState(3)
  const [isCached, setIsCached] = useState(false)
  const [message, setMessage] = useState(null)
  const [baseCurrency, setBaseCurrency] = useState('USD')

  // Fetch rates from backend API
  const fetchRates = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/rates?base=${baseCurrency}`)

      if (!response.ok) {
        throw new Error('Failed to fetch rates')
      }

      const data = await response.json()

      setRates(data.rates)
      setLastUpdated(new Date(data.last_updated))
      setFreshness(data.freshness)
      setSourcesUsed(data.sources_used)
      setSourcesAvailable(data.sources_available)
      setIsCached(data.is_cached)
      setMessage(data.message)
      setError(null)
    } catch (err) {
      console.error('Error fetching rates:', err)
      // Only show error if no cached data
      if (!rates) {
        setError('Unable to fetch exchange rates. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }, [baseCurrency, rates])

  // Set up auto-refresh interval
  useEffect(() => {
    fetchRates()
    const interval = setInterval(fetchRates, REFRESH_INTERVAL)
    return () => clearInterval(interval)  // Cleanup on unmount
  }, [fetchRates])

  const handleRetry = () => {
    setLoading(true)
    setError(null)
    fetchRates()
  }

  const handleBaseCurrencyChange = (newBase) => {
    setBaseCurrency(newBase)
    setLoading(true)
  }

  const currencyNames = {
    USD: 'US Dollar',
    EUR: 'Euro',
    GBP: 'British Pound',
    JPY: 'Japanese Yen',
    INR: 'Indian Rupee'
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <h1 className="title">
            <span className="logo">💱</span>
            Currency Exchange Rates
          </h1>
          <p className="subtitle">Live rates from multiple trusted sources • Auto-updates every 60 seconds</p>
        </div>
      </header>

      <main className="main">
        <div className="explanation-section">
          <p className="explanation-title">📊 What This Shows</p>
          <p className="explanation-text">
            Below you'll see how much <strong>1 {baseCurrency} ({currencyNames[baseCurrency]})</strong> is worth in other currencies.
            <br />
            For example, if EUR shows <strong>0.84</strong>, it means 1 {baseCurrency} = 0.84 EUR.
          </p>
        </div>

        <div className="controls">
          <div className="base-selector">
            <label htmlFor="base-currency">Convert From:</label>
            <select
              id="base-currency"
              value={baseCurrency}
              onChange={(e) => handleBaseCurrencyChange(e.target.value)}
              disabled={loading}
            >
              <option value="USD">🇺🇸 USD - US Dollar</option>
              <option value="EUR">🇪🇺 EUR - Euro</option>
              <option value="GBP">🇬🇧 GBP - British Pound</option>
              <option value="JPY">🇯🇵 JPY - Japanese Yen</option>
              <option value="INR">🇮🇳 INR - Indian Rupee</option>
            </select>
          </div>

          <FreshnessIndicator
            freshness={freshness}
            lastUpdated={lastUpdated}
            sourcesUsed={sourcesUsed}
            sourcesAvailable={sourcesAvailable}
            isCached={isCached}
          />
        </div>

        {message && (
          <div className={`message-banner ${freshness === 'stale' ? 'warning' : 'info'}`}>
            ℹ️ {message}
          </div>
        )}

        {loading && !rates ? (
          <div className="loading">
            <div className="spinner"></div>
            <p>Fetching latest exchange rates...</p>
          </div>
        ) : error && !rates ? (
          <ErrorState message={error} onRetry={handleRetry} />
        ) : rates ? (
          <RateGrid
            rates={rates}
            baseCurrency={baseCurrency}
            loading={loading}
          />
        ) : null}
      </main>

      <footer className="footer">
        <p>
          📡 Data aggregated from ExchangeRate-API, Frankfurter (ECB), and Fawaz Ahmed API
        </p>
        <p className="refresh-note">
          🔄 Auto-refreshes every 60 seconds • Rates are aggregated from multiple sources for accuracy
        </p>
      </footer>
    </div>
  )
}

export default App
