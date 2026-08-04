<script setup lang="ts">

import GuessBar from "@/components/GuessBar.vue";
import TransportBar from "@/components/TransportBar.vue";
import GuessField from "@/components/GuessField.vue";
import settings from "@/settings/settings.json";

import { currentGameState } from "@/game";

</script>

<template>
  <div class="game-container">
    <div class="max-w-screen-sm">
      <div class="guess-container">
        <template v-for="n in settings['guess-number']">
          <GuessField v-if="currentGameState.guessed[n-1] === undefined" :active="(n === currentGameState.guess+1)"/>
          <GuessField v-else :active="(n===currentGameState.guess+1)" :music="(currentGameState.guessed[n-1])"/>
        </template>
      </div>
    </div>
  </div>
  <TransportBar/>
  <GuessBar/>
</template>

<style scoped>
.game-container {
  width: 100%;

  display: flex;
  flex-direction: column;
  flex-grow: 1;
  position: relative;
  .max-w-screen-sm {
    width: 100%;
    height: 100%;

    overflow: auto;
    justify-content: space-between;

    margin-left : auto;
    margin-right : auto;
    flex-direction: column;
  }
}
.guess-container {
  padding: 0.75rem;
}
</style>
