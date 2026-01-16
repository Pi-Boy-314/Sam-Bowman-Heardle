<script setup lang="ts">

import IconMusicNote from "@/components/icons/iconMusicNote.vue";
import IconSpeaker from "@/components/icons/IconSpeaker.vue";
import IconThumbUp from "@/components/icons/IconThumbUp.vue";

import {onMounted} from "vue";

import settings from "@/settings/settings.json"

onMounted(()=>{
  document.getElementById("modal-title").innerHTML = "How to play";
})

</script>

<template>
  <div>
    <div class="info">
      <div class="icon">
        <IconMusicNote/>
      </div>
      <div>
        <p>Listen to the intro, then type to find the correct {{ settings["heardle-name"] }} song in the list.</p>
      </div>
    </div>
    <div class="info">
      <div class="icon">
        <IconSpeaker/>
      </div>
      <div>
        <p>Skipped or incorrect attempts unlock more of the song</p>
      </div>
    </div>
    <div class="info">
      <div class="icon">
        <IconThumbUp/>
      </div>
      <div>
        <p>Answer in as few tries as possible and share your score!</p>
      </div>
    </div>
    <div class="button-container font-medium">
      <button @click="$parent.$emit('close');">Play</button>
    </div>
  </div>
</template>

<style scoped>
.info {
  display: flex;
  align-items: center;

  margin-bottom: 1.5rem;
}

.info .icon {
  color: var(--color-line);
  width: 2rem;
  margin-right: 1rem;
}

.button-container {
  display: flex;
  justify-content: center;

  padding-top: 0.5rem;
  padding-bottom: 0.5rem;

  margin-top: 0.5rem;
}

.button-container button {
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
</style>