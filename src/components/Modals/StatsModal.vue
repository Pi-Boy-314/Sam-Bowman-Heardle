<script setup lang="ts">
import { ref, onMounted } from "vue";
import settings from "@/settings/settings.json";

const guessDistribution = ref<number[]>([]);
const maxGuesses = ref(0);
const gamesPlayed = ref(0);
const gamesWon = ref(0);
const currentStreak = ref(0);
const maxStreak = ref(0);

onMounted(() => {
  document.getElementById("modal-title").innerHTML = "Stats";
  guessDistribution.value = calculateAverageGuesses();
  maxGuesses.value = Math.max(...guessDistribution.value) ? Math.max(...guessDistribution.value) : 1;
  calculateStreaks();
});

function calculateAverageGuesses() {
  const statDistribution = Array(settings["guess-number"] + 1).fill(0);

  const stats = localStorage.getItem("userStats");
  if (!stats) return statDistribution;

  const parsedStats = JSON.parse(stats);
  for (const stat of parsedStats) {
    if (stat.isFinished) {
      statDistribution[stat.guess] += 1;
    }
  }
  return statDistribution;
}

function calculateStreaks() {
  const stats = localStorage.getItem("userStats");
  if (!stats) return;

  const parsedStats = JSON.parse(stats);
  let played = 0;
  let won = 0;
  let streak = 0;
  let maxStreakVal = 0;

  // Sort by ID to get chronological order
  parsedStats.sort((a, b) => a.id - b.id);

  for (const stat of parsedStats) {
    if (stat.isFinished) {
      played++;
      // Check if they won (last guess was correct)
      const lastGuess = stat.guessed && stat.guessed.length > 0 ? stat.guessed[stat.guessed.length - 1] : null;
      if (lastGuess && lastGuess.isCorrect) {
        won++;
        streak++;
        if (streak > maxStreakVal) {
          maxStreakVal = streak;
        }
      } else {
        streak = 0;
      }
    }
  }

  gamesPlayed.value = played;
  gamesWon.value = won;
  currentStreak.value = streak;
  maxStreak.value = maxStreakVal;
}
</script>

<template>
  <div>
    <div class="stats-header">Game Stats</div>
    <div class="stats-row">
      <div class="stats-label">Played</div>
      <div class="stats-value">{{ gamesPlayed }}</div>
    </div>
    <div class="stats-row">
      <div class="stats-label">Wins</div>
      <div class="stats-value">{{ gamesWon }}</div>
    </div>
    <div class="stats-row">
      <div class="stats-label">Streak</div>
      <div class="stats-value">{{ currentStreak }}</div>
    </div>
    <div class="stats-row">
      <div class="stats-label">Max Streak</div>
      <div class="stats-value">{{ maxStreak }}</div>
    </div>
    <div class="stats-header" style="margin-top: 20px; border-top: 1px solid var(--color-line); padding-top: 15px;">Guess Distribution</div>
    <div class="bar-graph-container">
      <div class="bar-graph-row" v-for="(value, index) in guessDistribution" :key="index">
        <div v-if="index === settings['guess-number']">
          <p class="bar-graph-label">Skipped:</p>
        </div>
        <div v-else>
          <p class="bar-graph-label">{{ settings['times'][index] }} sec:</p>
        </div>

        <div class="bar-graph-bar-outer">
          <div class="bar-graph-bar-inner" :style="{ width: (value / maxGuesses) * 100 + '%' }" ></div>
        </div>

        <p class="bar-graph-value">{{ value }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-header {
  font-size: 1.4rem;
  font-weight: bold;
  margin-bottom: 15px;
  text-align: center;
}
.stats-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}
.stats-label {
  font-weight: 500;
}
.stats-value {
  font-weight: 700;
}
.bar-graph-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
  width: 100%;
}
.bar-graph-row {
  display: flex;
  align-items: center;
  gap: 10px;
}
.bar-graph-label {
  width: 80px;
  text-align: right;
}
.bar-graph-bar-outer {
  flex-grow: 1;
  background-color: var(--color-dg, #222);
  height: 20px;
  overflow: hidden;
}
.bar-graph-bar-inner {
  height: 100%;
  background-color: var(--color-positive);
}
.bar-graph-value {
  width: 30px;
  text-align: left;
}
</style>
