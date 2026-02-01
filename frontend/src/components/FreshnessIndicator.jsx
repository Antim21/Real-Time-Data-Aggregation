import PropTypes from 'prop-types'
import { useMemo } from 'react'

function FreshnessIndicator({ freshness, lastUpdated, sourcesUsed, sourcesAvailable, isCached }) {
    const timeAgo = useMemo(() => {
        if (!lastUpdated) return 'Unknown'

        const now = new Date()
        const diffMs = now - new Date(lastUpdated)
        const diffSeconds = Math.floor(diffMs / 1000)
        const diffMinutes = Math.floor(diffSeconds / 60)
        const diffHours = Math.floor(diffMinutes / 60)

        if (diffSeconds < 30) return 'Just now'
        if (diffSeconds < 60) return `${diffSeconds}s ago`
        if (diffMinutes < 60) return `${diffMinutes} min ago`
        if (diffHours < 24) return `${diffHours}h ago`
        return 'Over a day ago'
    }, [lastUpdated])

    const freshnessLabel = useMemo(() => {
        switch (freshness) {
            case 'fresh':
                return '🟢 Live Data'
            case 'recent':
                return '🟡 Recent Data'
            case 'stale':
                return '🔴 Outdated'
            default:
                return 'Unknown'
        }
    }, [freshness])

    return (
        <div className="freshness-indicator">
            <div className="freshness-status">
                <span className={`freshness-dot ${freshness}`}></span>
                <span className={`freshness-text ${freshness}`}>
                    {freshnessLabel}
                </span>
            </div>

            <div className="sources-info">
                <span>⏱️ {timeAgo}</span>
                <span>•</span>
                <span>📡 {sourcesUsed}/{sourcesAvailable} sources</span>
                {isCached && <span>• 💾 Cached</span>}
            </div>
        </div>
    )
}

FreshnessIndicator.propTypes = {
    freshness: PropTypes.oneOf(['fresh', 'recent', 'stale']).isRequired,
    lastUpdated: PropTypes.instanceOf(Date),
    sourcesUsed: PropTypes.number.isRequired,
    sourcesAvailable: PropTypes.number.isRequired,
    isCached: PropTypes.bool
}

export default FreshnessIndicator
