<script setup lang="ts">

import IconInfo from "@/components/icons/IconInfo.vue";
import IconHeart from "@/components/icons/IconHeart.vue";
import IconAbout from "@/components/icons/IconAbout.vue";
import IconStats from "@/components/icons/IconStats.vue";


import AboutModal from "@/components/Modals/AboutModal.vue";
import SupportModal from "@/components/Modals/SupportModal.vue";
import TutorialModal from "@/components/Modals/TutorialModal.vue";
import StatsModal from "@/components/Modals/StatsModal.vue";

import settings from "@/settings/settings.json"

const emit = defineEmits(['create-modal']);
</script>

<template>
  <header>
    <div class="max-w-screen-md mx-auto">
      <div class="main-container">
        <div class="button-container">
          <button @click="emit('create-modal', AboutModal)">
            <IconInfo/>
          </button>
          <button @click="emit('create-modal', SupportModal)">
            <IconHeart/>
          </button>
        </div>
        <h1 class="font-title">
          <span>{{ settings["heardle-name"] }}</span><br/>
          Heardle
        </h1>
        <div class="button-container justify-end">
          <button @click="emit('create-modal', StatsModal)">
            <IconStats/>
          </button>
          <button @click="emit('create-modal', TutorialModal)">
            <IconAbout/>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped lang="scss">
  header {
  }

  .main-container{
    display: flex;
    justify-content: space-evenly;
    color: var(--color-fg);
    padding: 0.75rem;
    align-items: center;
    border-style: solid;
    border-color: var(--color-line);
    border-bottom-width: 1px;
  }

  .button-container {
    display: flex;
    flex: 1 1 0%;

    button{
      border: none;
      cursor: pointer;
    }
  }

  h1 {
    font-weight: 10;
    text-align: center;
    flex: 1 1 0%;
  }

  .justify-end {
    justify-content: flex-end;
  }
</style>