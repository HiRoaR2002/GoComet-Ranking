import React, { useState } from 'react';
import { submitScore } from '../api/leaderboard';

const SubmitScore = () => {
    const [userId, setUserId] = useState('');
    const [score, setScore] = useState('');
    const [gameMode, setGameMode] = useState<'solo' | 'team'>('solo');
    const [loading, setLoading] = useState(false);
    const [success, setSuccess] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!userId || !score) return;

        setLoading(true);
        setError(null);
        setSuccess(false);

        try {
            await submitScore({
                user_id: parseInt(userId),
                score: parseInt(score),
                game_mode: gameMode
            });
            setSuccess(true);
            // Clear form after successful submission
            setTimeout(() => {
                setUserId('');
                setScore('');
                setSuccess(false);
            }, 2000);
        } catch (err) {
            setError('Failed to submit score. Please try again.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="submit-score-card">
            <div className="card-header">
                <h2>🎮 Submit Your Score</h2>
            </div>
            
            <form onSubmit={handleSubmit} className="submit-form">
                <div className="form-group">
                    <label htmlFor="userId">User ID</label>
                    <input
                        id="userId"
                        type="number"
                        placeholder="Enter your user ID (1-1000000)"
                        value={userId}
                        onChange={(e) => setUserId(e.target.value)}
                        className="form-input"
                        min="1"
                        max="1000000"
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="score">Score</label>
                    <input
                        id="score"
                        type="number"
                        placeholder="Enter your score"
                        value={score}
                        onChange={(e) => setScore(e.target.value)}
                        className="form-input"
                        min="1"
                        required
                    />
                </div>

                <div className="form-group">
                    <label htmlFor="gameMode">Game Mode</label>
                    <select
                        id="gameMode"
                        value={gameMode}
                        onChange={(e) => setGameMode(e.target.value as 'solo' | 'team')}
                        className="form-select"
                    >
                        <option value="solo">Solo</option>
                        <option value="team">Team</option>
                    </select>
                </div>

                <button 
                    type="submit" 
                    disabled={loading || !userId || !score} 
                    className="submit-btn"
                >
                    {loading ? 'Submitting...' : 'Submit Score'}
                </button>
            </form>

            {success && (
                <div className="success-message">
                    ✅ Score submitted successfully!
                </div>
            )}

            {error && (
                <div className="error-message">
                    ❌ {error}
                </div>
            )}
        </div>
    );
};

export default SubmitScore;
