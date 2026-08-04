<script setup lang="ts">

import { ref, onMounted, onUnmounted } from 'vue';
import YouTubeMusicLink from "@/components/YouTubeMusicLink.vue";
import GuessSummary from "@/components/GuessSummary.vue";
import IconShare from "@/components/icons/IconShare.vue";

import settings from "@/settings/settings.json"

import { currentGameState, ParseStringWithVariable, dayIndex } from "@/game";
import TransportBar from "@/components/TransportBar.vue";

const copied = ref(false);
const showShareModal = ref(false);
const shareText = ref('');

let timerInterval: ReturnType<typeof setInterval> | null = null;

async function copyShareText() {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(String(shareText.value));
    } else {
      const ta = document.createElement('textarea');
      ta.value = String(shareText.value);
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
    }

    copied.value = true;
    setTimeout(() => (copied.value = false), 2000);
  } catch (e) {
    console.error('Copy failed', e);
  }
}

async function share() {
  const guessed = currentGameState.value.guessed || [];
  const guesses = guessed.length;
  const won = guesses > 0 && guessed[guesses - 1].isCorrect;

  // build emoji pattern (🟩 green for correct, 🟥 red for incorrect, ⬛ gray for skip, ⬜ white for unused)
  const total = settings["guess-number"] || 6;
  let pattern = '';
  for (let i = 0; i < total; i++) {
    const g = guessed[i];
    if (g === undefined) {
      pattern += '⬜';
    } else if (g.isCorrect) {
      pattern += '🟩';
    } else if (g.name === "Skipped") {
      pattern += '⬛';
    } else {
      pattern += '🟥';
    }
  }

  const scoreText = won ? `${guesses}/${total}` : `X/${total}`;
  const text = `${settings["heardle-name"]} Heardle #${dayIndex + 1} - ${scoreText}\n${pattern}`;

  // populate modal; do NOT invoke navigator.share to avoid opening the OS share window
  shareText.value = text;
  console.debug('Share text set for modal:', String(text));

  // attempt background copy but don't rely on it
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(String(text));
      copied.value = true;
      setTimeout(() => (copied.value = false), 2000);
    }
  } catch (e) {
    console.debug('background clipboard write failed', e);
  }

  showShareModal.value = true;
}

// Countdown to the next puzzle, which rolls over at midnight Central Time.
//
// The formatter is built once here rather than inside the tick: constructing an
// Intl.DateTimeFormat is expensive, and the old code built two identical ones on
// every one of its 300ms ticks.
const ctFormatter = new Intl.DateTimeFormat('en-US', {
  timeZone: 'America/Chicago',
  year: 'numeric', month: 'numeric', day: 'numeric',
  hour: 'numeric', minute: 'numeric', second: 'numeric',
  hour12: false,
});

function updateTimer() {
  const timer = document.getElementById("timer");
  if (!timer) return;

  const now = new Date();
  const parts = ctFormatter.formatToParts(now).reduce((acc: Record<string, string>, p) => { acc[p.type] = p.value; return acc; }, {});

  // Wall-clock "now" in CT, expressed as a UTC timestamp. Comparing it against
  // the real timestamp yields the current CT offset, which handles DST without
  // hardcoding UTC-5/UTC-6.
  const nowInCTUtc = Date.UTC(Number(parts.year), Number(parts.month) - 1, Number(parts.day), Number(parts.hour), Number(parts.minute), Number(parts.second));
  const todayMidnightCTUtc = Date.UTC(Number(parts.year), Number(parts.month) - 1, Number(parts.day));
  const offsetMs = now.getTime() - nowInCTUtc;
  const nextMidnightCT = todayMidnightCTUtc + 24 * 60 * 60 * 1000 + offsetMs;

  const totalSeconds = Math.floor((nextMidnightCT - now.getTime()) / 1000);

  if (totalSeconds <= 0) {
    window.location.reload();
    return;
  }

  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  timer.innerHTML = `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds.toString().padStart(2, "0")}`;
}

// Fill the countdown on mount so the placeholder in the template is never
// visible; the interval then keeps it ticking once a second.
onMounted(updateTimer);
timerInterval = setInterval(updateTimer, 1000);

onUnmounted(() => {
  if (timerInterval !== null) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
});
</script>

<template>
  <div class="max-w-screen-sm main-container">
    <div v-if="currentGameState.guessed.length > 0" class="end-content">
      <YouTubeMusicLink :is-won="currentGameState.guessed[currentGameState.guessed.length-1].isCorrect"/>
      <div class="summary-container">
        <p class="guess-number font-big"> 
          {{ currentGameState.guessed[currentGameState.guessed.length-1].isCorrect ? currentGameState.guessed.length.toString() : '0' }} 
        </p>
        <GuessSummary class="summary"/>
        <div class="share">
          <button class="font-medium" @click="share">
            {{ copied ? 'Copied!' : ParseStringWithVariable(settings["phrases"]["share-button"]) }}
            <IconShare class="inline-block ml-2"/>
          </button>
        </div>
      </div>

      <!-- Share modal -->
      <div v-if="showShareModal" class="share-modal-overlay" @click.self="showShareModal = false">
        <div class="share-modal">
          <h3 class="font-medium">Share result</h3>
          <textarea v-model="shareText" rows="3" class="share-textarea"></textarea>
          <div class="share-actions">
            <button class="copy" @click="copyShareText">{{ copied ? 'Copied!' : 'Copy' }}</button>
            <button class="close" @click="showShareModal = false">Close</button>
          </div>
        </div>
      </div>

      <div class="timer-container">
        <div class="next-text font-medium"> 
          {{ ParseStringWithVariable(settings["phrases"]["timer-text"]) }} 
        </div>
        <div id="timer" class="font-big">14:25:42</div>
      </div>
    </div> <div v-else>
      <div class="next-button-container">
        <button class="font-medium" onclick="window.location.reload()"> 
          {{ ParseStringWithVariable(settings["phrases"]["next-button"]) }} 
        </button>
      </div>
    </div>
  </div>
  <TransportBar/>
</template>

<style scoped>
.main-container{
  display: flex;
  flex-direction: column;

  justify-content: space-around;

  width: 100%;
  height: 100%;

  margin: 0 auto;

  overflow: auto
}

.end-content {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  gap: 3rem;
  flex: 1;
}

.summary-container {
  text-align: center;
  padding: 0 0.75rem;

  .guess-number {
    color: var(--color-lg)
  }
  .summary{
    justify-content: center;
    display: flex;
    margin: 0.5rem 0;
  }
  .second-text {
    padding: 0.25rem 0;
    line-height: 1.75rem;
  }
  .share {
    display: flex;

    flex-direction: column;
    justify-content: center;
    align-items: center;

    padding-top: 0.75rem;

    button {
      display: flex;

      align-items: center;

      padding: 0.5rem;
      text-transform: uppercase;

      text-indent: 0.25em;
      letter-spacing: 0.2em;

      border: none;

      background-color: var(--color-positive);
    }
  }
}

.timer-container{
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin: 0 0.75rem 1.5rem;

  .next-text{
    text-align: center;
    color: var(--color-lg);
    margin-bottom: 0.25rem;
  }

  #timer {
    text-indent: 0.25em;
    letter-spacing: 0.2em;
  }
}

.next-button-container{
  display: flex;
  align-items: center;
  justify-content: center;

  margin: 3.5rem 0;

  button {
    text-transform: uppercase;

    text-indent: 0.25em;
    letter-spacing: 0.2em;
    font-weight: 10;

    padding: 0.5rem;

    background: var(--color-submit);

    border-style: none;

    align-items: center;
    display: flex;

    cursor: pointer;
  }
}

/* Share modal styles */
.share-modal-overlay{
  position: fixed;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
.share-modal{
  background: var(--color-bg);
  color: var(--color-fg);
  padding: 1rem;
  border-radius: 8px;
  width: min(90%, 480px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}
.share-textarea{
  width: 100%;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: var(--color-bg);
  color: var(--color-fg);
  border: 1px solid var(--color-mg);
}
.share-actions{
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.share-actions .copy{
  background: var(--color-positive);
  border: none;
  padding: 0.5rem 0.75rem;
}
.share-actions .close{
  background: var(--color-mg);
  border: none;
  padding: 0.5rem 0.75rem;
}
</style>