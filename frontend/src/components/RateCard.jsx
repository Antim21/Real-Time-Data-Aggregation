import PropTypes from 'prop-types'

// Currency symbols and flags
const CURRENCY_DATA = {
    USD: { symbol: '$', flag: '🇺🇸' },
    EUR: { symbol: '€', flag: '🇪🇺' },
    GBP: { symbol: '£', flag: '🇬🇧' },
    JPY: { symbol: '¥', flag: '🇯🇵' },
    CAD: { symbol: 'C$', flag: '🇨🇦' },
    AUD: { symbol: 'A$', flag: '🇦🇺' },
    CHF: { symbol: 'Fr', flag: '🇨🇭' },
    INR: { symbol: '₹', flag: '🇮🇳' },
    CNY: { symbol: '¥', flag: '🇨🇳' },
    MXN: { symbol: '$', flag: '🇲🇽' }
}

function RateCard({ currency, baseCurrency, loading }) {
    const data = CURRENCY_DATA[currency.code] || { symbol: currency.code.charAt(0), flag: '🏳️' }

    return (
        <div className={`rate-card ${loading ? 'loading' : ''}`}>
            <div className="rate-card-header">
                <div className="currency-icon">
                    {data.flag}
                </div>
                <div className="currency-info">
                    <h3>{currency.code}</h3>
                    <p>{currency.name}</p>
                </div>
            </div>

            <div className="rate-display">
                <div className="rate-label">1 {baseCurrency} equals</div>
                <div className="rate-value">
                    {data.symbol}{currency.rate.toFixed(4)}
                    <span className="base-indicator">{currency.code}</span>
                </div>
            </div>

            <div className="rate-inverse">
                Reverse: <strong>1 {currency.code} = {currency.inverse_rate.toFixed(4)} {baseCurrency}</strong>
            </div>
        </div>
    )
}

RateCard.propTypes = {
    currency: PropTypes.shape({
        code: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        rate: PropTypes.number.isRequired,
        inverse_rate: PropTypes.number.isRequired
    }).isRequired,
    baseCurrency: PropTypes.string.isRequired,
    loading: PropTypes.bool
}

export default RateCard
