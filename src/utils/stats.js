// src/utils/stats.js
// Utility for tracking and updating game stats in localStorage

const STATS_KEY = 'userStats';

export function getStats() {
  const stats = localStorage.getItem(STATS_KEY);
  if (!stats) {
    return {
      gamesPlayed: 0,
      gamesWon: 0,
      currentStreak: 0,
      maxStreak: 0,
      guessDistribution: [],
      lastPlayed: null
    };
  }
  return JSON.parse(stats);
}

export function saveStats(stats) {
  localStorage.setItem(STATS_KEY, JSON.stringify(stats));
}

export function updateStats({ won, guessAttempt }) {
  const stats = getStats();
  stats.gamesPlayed += 1;
  if (won) {
    stats.gamesWon += 1;
    stats.currentStreak += 1;
    if (stats.currentStreak > stats.maxStreak) {
      stats.maxStreak = stats.currentStreak;
    }
  } else {
    stats.currentStreak = 0;
  }
  if (!stats.guessDistribution) {
    stats.guessDistribution = [];
  }
  // guessAttempt is the index (0-5 for attempts, 6 for skipped/lost)
  stats.guessDistribution[guessAttempt] = (stats.guessDistribution[guessAttempt] || 0) + 1;
  stats.lastPlayed = new Date().toISOString();
  saveStats(stats);
  console.log('Stats saved:', stats);
}
