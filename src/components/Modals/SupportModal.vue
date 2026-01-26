<script setup lang="ts">
import {onMounted} from "vue";
import settings from "@/settings/settings.json"

onMounted(()=>{
  document.getElementById("modal-title").innerHTML = "Support";
})
</script>

<template>  
  <div class="section">
    <h3 class="section-title">Check Out Matthew Parker's Music</h3>
    <div class="link-container">
      <div class="link-item">
        <span class="link-label">YouTube</span>
        <a href="https://www.youtube.com/@MatthewParkerTunes" target="_blank" rel="noopener noreferrer">youtube.com/@matthewparkermusic</a>
      </div>
      <div class="link-item">
        <span class="link-label">Spotify</span>
        <a href="https://open.spotify.com/artist/0QT3cPPXMGYtTG3kN8Ez54" target="_blank" rel="noopener noreferrer">open.spotify.com/artist/0QT3cPPXMGYtTG3kN8Ez54</a>
      </div>
      <div class="link-item">
        <span class="link-label">Apple Music</span>
        <a href="https://music.apple.com/us/artist/matthew-parker/79499070" target="_blank" rel="noopener noreferrer">music.apple.com/us/artist/matthew-parker/79499070</a>
      </div>
      <div class="link-item">
        <span class="link-label">Official Website</span>
        <a href="https://matthewparkermusic.com" target="_blank" rel="noopener noreferrer">matthewparkermusic.com</a>
      </div>
      <div class="link-item">
        <span class="link-label">Join the Discord</span>
        <a href="https://discord.gg/5QRXAcUMkN" target="_blank" rel="noopener noreferrer">https://discord.gg/5QRXAcUMkN</a>
      </div>
    </div>

  </div>
  <div class="section" style="margin-top: 1.5rem;">
    <p>Like the game or have questions? Let @pi_boy_314 know in Discord</p>
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
}

.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: var(--color-fg);
}

.link-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.link-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.link-label {
  font-weight: 600;
  color: var(--color-line);
  font-size: 0.95rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.link-item a {
  color: var(--color-button-highlight);
  text-decoration: none;
  word-break: break-all;
  font-size: 0.9rem;
  transition: text-decoration 0.2s ease;
}

.link-item a:hover {
  text-decoration: underline;
}
</style>