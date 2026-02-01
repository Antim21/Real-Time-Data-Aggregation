import PropTypes from 'prop-types'
import RateCard from './RateCard'

// Grid layout for displaying all currency rate cards
function RateGrid({ rates, baseCurrency, loading }) {
    if (!rates || Object.keys(rates).length === 0) {
        return null
    }

    // Filter out base currency and sort alphabetically
    const sortedRates = Object.values(rates)
        .filter(rate => rate.code !== baseCurrency)
        .sort((a, b) => a.code.localeCompare(b.code))

    return (
        <div className="rate-grid">
            {sortedRates.map(rate => (
                <RateCard
                    key={rate.code}
                    currency={rate}
                    baseCurrency={baseCurrency}
                    loading={loading}
                />
            ))}
        </div>
    )
}

RateGrid.propTypes = {
    rates: PropTypes.objectOf(
        PropTypes.shape({
            code: PropTypes.string.isRequired,
            name: PropTypes.string.isRequired,
            rate: PropTypes.number.isRequired,
            inverse_rate: PropTypes.number.isRequired
        })
    ),
    baseCurrency: PropTypes.string.isRequired,
    loading: PropTypes.bool
}

export default RateGrid
