import { useEffect, useState } from 'react';
import { fetchLeaderboard, type LeaderboardEntry } from '../api/leaderboard';

const LeaderboardTable = () => {
    const [players, setPlayers] = useState<LeaderboardEntry[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const loadData = async () => {
            try {
                const data = await fetchLeaderboard();
                data.sort((a, b) => a.rank - b.rank);
                setPlayers(data);
                setLoading(false);
            } catch (error) {
                console.error(error);
            }
        };

        // Poll every 3 seconds for live updates
        const interval = setInterval(loadData, 3000);
        loadData();

        return () => clearInterval(interval);
    }, []);

    const getRankBadge = (rank: number) => {
        if (rank === 1) return '🥇';
        if (rank === 2) return '🥈';
        if (rank === 3) return '🥉';
        return rank;
    };

    return (
        <div className="leaderboard-card">
            <div className="card-header">
                <h2>🏆 Top 10 Global Rankings</h2>
            </div>
            
            <div className="table-wrapper">
                <table className="leaderboard-table">
                    <thead>
                        <tr>
                            <th className="rank-col">Rank</th>
                            <th className="user-col">User</th>
                            <th className="score-col">Total Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading && (
                            <tr>
                                <td colSpan={3} style={{ textAlign: 'center', padding: '2rem' }}>
                                    Loading...
                                </td>
                            </tr>
                        )}
                        {!loading && players.length === 0 && (
                            <tr>
                                <td colSpan={3} style={{ textAlign: 'center', padding: '2rem' }}>
                                    No data yet. Start the simulation!
                                </td>
                            </tr>
                        )}
                        {players.map((player) => (
                            <tr key={player.user_id} className={player.rank <= 3 ? 'top-rank' : ''}>
                                <td className="rank-col">
                                    <span className="rank-badge">
                                        {getRankBadge(player.rank)}
                                    </span>
                                </td>
                                <td className="user-col">
                                    User_{player.user_id}
                                </td>
                                <td className="score-col">
                                    <span className="score-value">
                                        {player.total_score.toLocaleString()}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default LeaderboardTable;
