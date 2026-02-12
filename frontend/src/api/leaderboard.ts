import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api/leaderboard',
    timeout: 5000,
});

export interface LeaderboardEntry {
    user_id: number;
    total_score: number;
    rank: number;
}

export interface UserRank {
    user_id: number;
    rank: number;
    total_score: number;
}

export const fetchLeaderboard = async (): Promise<LeaderboardEntry[]> => {
    try {
        const response = await api.get<{ top_players: LeaderboardEntry[] }>('/top');
        return response.data.top_players;
    } catch (error) {
        console.error("Error fetching leaderboard:", error);
        throw error;
    }
};

export const fetchUserRank = async (userId: number): Promise<UserRank> => {
    try {
        const response = await api.get<UserRank>(`/rank/${userId}`);
        return response.data;
    } catch (error) {
        console.error("Error fetching user rank:", error);
        throw error;
    }
};

export interface GameSessionCreate {
    user_id: number;
    score: number;
    game_mode: 'solo' | 'team';
}

export const submitScore = async (data: GameSessionCreate): Promise<{ message: string }> => {
    try {
        const response = await api.post<{ message: string }>('/submit', data);
        return response.data;
    } catch (error) {
        console.error("Error submitting score:", error);
        throw error;
    }
};
