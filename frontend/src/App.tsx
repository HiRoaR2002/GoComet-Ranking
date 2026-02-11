import { useState } from 'react';
import LeaderboardTable from './components/LeaderboardTable';
import RankLookup from './components/RankLookup';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState<'leaderboard' | 'rank'>('leaderboard');

  return (
    <div className="container">
      <header className="header">
        <h1>Gaming Leaderboard</h1>
        <p className="subtitle">Real-time Global Rankings</p>
      </header>

      <div className="tabs">
        <button 
          className={activeTab === 'leaderboard' ? 'tab-btn active' : 'tab-btn'}
          onClick={() => setActiveTab('leaderboard')}
        >
          Top 10 Leaderboard
        </button>
        <button 
          className={activeTab === 'rank' ? 'tab-btn active' : 'tab-btn'}
          onClick={() => setActiveTab('rank')}
        >
          Check My Rank
        </button>
      </div>

      <div className="content">
        {activeTab === 'leaderboard' ? (
          <LeaderboardTable />
        ) : (
          <RankLookup />
        )}
      </div>
      
      <footer className="footer">
        <p>Built with FastAPI, Redis, PostgreSQL, and React</p>
      </footer>
    </div>
  );
}

export default App;
