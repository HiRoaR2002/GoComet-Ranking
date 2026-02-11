import React, { useState } from 'react';
import { fetchUserRank, type UserRank } from '../api/leaderboard';

const RankLookup = () => {
    const [userId, setUserId] = useState('');
    const [rankData, setRankData] = useState<UserRank | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!userId) return;

        setLoading(true);
        setError(null);
        setRankData(null);

        try {
            const data = await fetchUserRank(parseInt(userId));
            setRankData(data);
        } catch (err) {
            setError('User not found or connection issue.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="rank-lookup-card">
            <div className="card-header">
                <h2>🔍 User Rank Lookup</h2>
            </div>
            
            <form onSubmit={handleSearch} className="search-form">
                <input
                    type="number"
                    placeholder="Enter User ID..."
                    value={userId}
                    onChange={(e) => setUserId(e.target.value)}
                    className="user-input"
                    min="1"
                    max="1000000"
                />
                <button type="submit" disabled={loading} className="search-btn">
                    {loading ? 'Searching...' : 'Search'}
                </button>
            </form>

            {rankData && (
                <div className="result-card">
                    <div className="result-row">
                        <span className="result-label">User ID:</span>
                        <span className="result-value">{rankData.user_id}</span>
                    </div>
                    <div className="result-row">
                        <span className="result-label">Global Rank:</span>
                        <span className="result-value rank-highlight">#{rankData.rank}</span>
                    </div>
                    <div className="result-row">
                        <span className="result-label">Total Score:</span>
                        <span className="result-value score-highlight">
                            {rankData.total_score.toLocaleString()}
                        </span>
                    </div>
                </div>
            )}

            {error && (
                <div className="error-message">
                    {error}
                </div>
            )}
        </div>
    );
};

export default RankLookup;
