<script setup lang="ts">
import {onMounted} from "vue";

onMounted(()=>{
  document.getElementById("modal-title").innerHTML = "About";
})
</script>

<template>
  <div class="section">
    <h3 class="section-title">About This Game</h3>
    <p>Matthew Parker Heardle is a version of Heardle that features songs from Matthew Parker's discography.</p>
  </div>
  
  <div class="section">
    <h3 class="section-title">Credits</h3>
    <p>Adapted by <a href="https://github.com/pi-boy-314" target="_blank" rel="noopener noreferrer">Pi Boy 314</a></p>
    <p>Forked from <a href="https://github.com/s4pph1r3-dev/Heardle-Base" target="_blank" rel="noopener noreferrer">Heardle-Base</a></p>
  </div>
</template>

<style scoped>
p {
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

a {
  color: var(--color-button-highlight);
  text-decoration: none;
  transition: text-decoration 0.2s ease;
}

a:hover {
  text-decoration: underline;
}

.section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-fg);
}
</style>