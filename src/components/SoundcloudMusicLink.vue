<script setup lang="ts">
import { SelectedMusic } from '@/main';
import SoundcloudLogo from "@/components/icons/SoundcloudLogo.vue";

const props = defineProps({
  "isWon": Boolean,
})
</script>

<template>
  <div class="soundcloud-box">
    <a :href="SelectedMusic.url" :title="'Listen to ' + SelectedMusic.album + ' - ' + SelectedMusic.title + ' on YouTube'" >
      <div class="title-card" :won="isWon ? 'true' : 'false'">
        <img v-if="SelectedMusic.art" :src="SelectedMusic.art" alt="Album art" class="album-art">
        <div class="title">
          <p class="title-text font-medium"> {{ SelectedMusic.title }} </p>
        </div>
        <SoundcloudLogo/>
      </div>
    </a>
  </div>
</template>

<style scoped lang="scss">
.soundcloud-box {
  padding: 0.75rem 0.75rem 0;

  a{
    text-decoration: none;
  }

  .title-card{
    display: flex;
    padding: 0.5rem;

    border-radius: 0.125rem;

    align-items: center;

    &[won=true]{
      background: var(--color-win-card)
    }
    &[won=false]{
      background: var(--color-lost-card)
    }

    .title {
      flex: 1 1 0%;
      margin-left: 0.75rem;
      margin-right: 0.75rem;

      p {
        margin-bottom: 0.25rem;

        &:last-child {
          margin-bottom: 0;
        }
      }

      .title-text{
        line-height: 1.3rem;
      }
    }

    .album-art {
      width: 40px;
      height: 40px;
      border-radius: 4px;
      object-fit: cover;
      margin-right: 0.5rem;
    }
  }
}
</style>