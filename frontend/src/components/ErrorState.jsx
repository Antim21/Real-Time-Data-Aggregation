import PropTypes from 'prop-types'

function ErrorState({ message, onRetry }) {
    return (
        <div className="error-state">
            <div className="error-icon">⚠️</div>
            <h2>Rates Temporarily Unavailable</h2>
            <p>{message || 'We\'re having trouble fetching the latest rates. Please try again.'}</p>
            <button className="retry-button" onClick={onRetry}>
                Try Again
            </button>
        </div>
    )
}

ErrorState.propTypes = {
    message: PropTypes.string,
    onRetry: PropTypes.func.isRequired
}

export default ErrorState
