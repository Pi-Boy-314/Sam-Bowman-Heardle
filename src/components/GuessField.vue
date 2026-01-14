<script setup lang="ts">
import IconFailedCross from "@/components/icons/IconFailedCross.vue";
import settings from "@/settings/settings.json"
import { SelectedMusic, ParseStringWithVariable } from "@/main";
import IconEmptyBox from "@/components/icons/IconEmptyBox.vue";

const props = defineProps<{
  active?: boolean;
  music?: { name: string, "equal-to": { title: string, url: string, album: string }, isCorrect: boolean };
}>();

console.log("")

</script>

<template>
  <div :class="'parent ' + (active ? 'active' : '')">
    <div class="empty-guess" v-if="music === undefined"></div>

    <IconFailedCross v-if="music != undefined && music.name != 'Skipped'" class="cross"/>
    <IconEmptyBox v-else-if="music != undefined" class="cross"/>

    <div class="name-parent" v-if="music != undefined">
      <div class="name font-medium" v-if="music.name != 'Skipped'">
        {{ music.name }}<span v-if="music['equal-to'] && music['equal-to'].album"> — {{ music['equal-to'].album }}</span>
      </div>
      <div class="skipped" v-else >  {{ ParseStringWithVariable(settings["phrases"]["skipped"]) }}  </div>
    </div>

    <!-- Tag logic removed: no songs have tags -->
  </div>
</template>

<style scoped lang="scss">
.active {
  border-color: var(--color-active-field) !important;
}

.parent {
  display: flex;

  padding: 0.5rem;
  margin-bottom: 0.5rem;
  border-width: 1px;
  align-items: center;
  border-color: var(--color-inactive-field);

  box-sizing: border-box;
  border-style: solid;
  .empty-guess {
    height: 1.25rem;
    width: 1.25rem;
  }
}

.cross {
  margin-right: 0.5rem;
}

.name-parent {
  justify-content: space-between;
  align-items: center;
  flex: 1 1 0%;
  display: flex;

  .name {
    --tw-text-opacity: 1;
    color: rgba(255, 255, 255, var(--tw-text-opacity));
  }

  .skipped {
    text-indent: 0.25em;
    color: var(--color-mg);
    letter-spacing: 0.2em;
    font-weight: 10;
  }
}

</style>