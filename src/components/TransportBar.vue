<script setup lang="ts">
import {onMounted, onUnmounted, ref} from "vue";
import IconPlay from "@/components/icons/IconPlay.vue";
import IconPlaying from "@/components/icons/IconPlaying.vue";

import settings from "@/settings/settings.json"
import {YoutubeMusicPlayer} from "@/players/YoutubePlayer";
import {LocalAudioPlayer} from "@/players/LocalAudioPlayer";

import {currentGameState, SelectedMusic} from "@/main"
import {Player} from "@/players/PlayerBase";

const isPlaying = ref(false);

let player: Player;

let isFinished = ref(false);

let lengthInSecond = ref(0);

let seekBarInterval = setInterval(() => {
  const sb = document.getElementById('seekbar');
  const item1 = document.getElementsByClassName('item1')[0];

  if(isPlaying.value){
    let percentage = 0;
    if(isFinished.value){
      player.GetCurrentMusicLength((n: number)=>{
        let duration = n;

        player.GetCurrentMusicTime((n2: number)=>{
          percentage = n2 / duration;

          sb.style.width = (percentage*100) + "%";

          item1.innerHTML = Math.floor((n2/1000)/60).toString() + ':' + Math.round(Math.floor(n2/1000)%60).toString().padStart(2, "0");
        })
      });
    } else {
      player.GetCurrentMusicTime((n2: number)=>{
        percentage = n2 / (settings["times"][currentGameState.value.guess]*1000);

        sb.style.width = (percentage*100) + "%";

        item1.innerHTML = Math.floor((n2/1000)/60).toString() + ':' + Math.round(Math.floor(n2/1000)%60).toString().padStart(2, "0");
      });
    }

  } else {
    sb.style.width = '0%';
  }
}, 20);

let sepSelectInterval = setInterval(() => {
  if(!isFinished){
    const bar = document.getElementById("bar");
    for(let i = 0; i < bar.children.length; i++){
      const child = bar.children[i+1];
      if(child !== undefined)
      child.classList.remove("sep-selected");
      if(i === currentGameState.value.guess){
        child.classList.add("sep-selected");
      }
    }
  }
}, 30);

onMounted(()=>{
  // During gameplay, use local 32-second clips to prevent spoilers
  // After win, switch to YouTube for full song playback
  if(SelectedMusic.id && !currentGameState.value.isFinished) {
    // Use API endpoint for protected 32-second clips during gameplay
    const audioUrl = import.meta.env.PROD 
      ? `/api/audio?id=${SelectedMusic.id}`
      : `/audio/${SelectedMusic.id}.mp3`;
    player = new LocalAudioPlayer(audioUrl);
  } else if (SelectedMusic.url.indexOf("youtube.com") !== -1) {
    // Use YouTube for full song (after game finished or no local audio)
    player = new YoutubeMusicPlayer(SelectedMusic.url);
  } else {
    // Fallback to local audio if URL doesn't match known services
    player = new LocalAudioPlayer(SelectedMusic.url);
  }

  isFinished.value = currentGameState.value.isFinished;

  if(!currentGameState.value.isFinished) {

    const bar = document.getElementById("bar");

    const lastChild = bar.lastChild;
    bar.removeChild(lastChild);

    for(let i = 0; i < settings["guess-number"]; i++){
      const el = document.createElement("div");
      el.classList.add("separator");
      if(i == 0) {
        el.classList.add("sep-selected");
      }
      el.style.setProperty("left", settings["separator"][i] + "%");
      bar.appendChild(el);
    }

    bar.appendChild(lastChild);
  }

  player.GetCurrentMusicLength((n: number)=>{
    lengthInSecond.value = Math.round(n/1000);
  })
})

onUnmounted(()=>{
  clearInterval(seekBarInterval);
  clearInterval(sepSelectInterval);
  
  // Properly cleanup the player to prevent audio persistence
  if (player && typeof player.Destroy === 'function') {
    player.Destroy();
  }
})

function ButtonClick(){
  if(isPlaying.value) Stop()
  else Play()
}

function Play(){
  const button = document.getElementById("play-button");
  const icon = document.getElementById("icon");

  console.log(SelectedMusic.title);

  isPlaying.value = true;

  if(currentGameState.value.isFinished){
    player.PlayMusicUntilEnd(null, null);
  } else {
    player.PlayMusic(settings["times"][currentGameState.value.guess], null, ()=>{
      Stop();
    });
  }

  icon.classList.add("playing");

}

function Stop(){
  const button = document.getElementById("play-button");
  const icon = document.getElementById("icon");

  isPlaying.value = false;

  player.StopMusic();

  icon.classList.remove("playing");
}

function getUnlockedBarWidth() : number{
  if(currentGameState.value.isFinished) return 100;
  return settings.separator[currentGameState.value.guess];
}

</script>

<template>
  <!-- PlayBar -->
  <div class="playbar">
    <div class="max-w-screen-sm bar-grid-container">
      <div class="bar-grid">
        <div id="unlocked-bar" :style="'width: ' + getUnlockedBarWidth() + '%'">
          <div id="seekbar"></div>
        </div>
        <div id="bar">
          <div></div>
          <div></div>
        </div>
      </div>
    </div>
  </div>
  <!-- Button -->
  <div class="transport">
    <div class="max-w-screen-sm">
      <div class="transport-container">
        <div class="container">
          <div class="item1" v-if="!isPlaying">0:00</div>
          <div class="item1" v-else> </div>
          <div class="item3">
            <button id="play-button" @click="ButtonClick">
              <div class="border">
                <div id="icon">
                  <IconPlay v-if="!isPlaying"/>
                  <IconPlaying v-else/>
                </div>
              </div>
            </button>
          </div>
          <div class="item4" v-if="!isFinished">{{ Math.floor(settings["times"][settings["guess-number"]-1]/60).toString() + ':' + (settings["times"][settings["guess-number"]-1]%60).toString().padStart(2, "0") }}</div>
          <div class="item4" v-else>{{ Math.floor(lengthInSecond / 60).toString()  + ':' + (lengthInSecond%60).toString().padStart(2, "0") }}</div>
        </div>
      </div>
    </div>
  </div>

</template>

<style scoped>
.playbar {
}

#seekbar {
  background-color: var(--color-positive);
  height: 100%;
  position: absolute;
}

.bar-grid-container {
  padding-left: 0.75rem;
  padding-right: 0.75rem;

  width: 100%;
  margin-left: auto;
  margin-right: auto;

  border-top-width: 1px;
  border-color: var(--color-line);
  border-style: solid;

  .bar-grid{
    overflow: hidden;
    width: 100%;
    height: 0.75rem;
    position: relative;

    #unlocked-bar{
      background-color: var(--color-mg);
      overflow: hidden;
      height: 100%;
      position: absolute;
    }

    #bar {
      width: 100%;
      height: 100%;
      position: absolute;

      :first-child {
        background-color: var(--color-line);
        width: 1px;
        height: 100%;
        right: 0px;

        position: absolute;
      }

      :last-child{
        background-color: var(--color-mg);
        width: 1px;
        height: 100%;
        right: 0px;

        position: absolute;
      }
    }
  }
}

.transport{
  width: 100%;

  .max-w-screen-sm{
    margin-left: auto;
    margin-right: auto;
  }

  .transport-container {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
    border-top-width: 1px;
    border-color: var(--color-line);
    border-style: solid;
  }
}

.container {
  display: grid;
  grid-template-columns: 1fr 2fr 1fr;
  align-items: center;
  padding: 0.75rem 0;
}

.item1 {
  align-items: center;
  display: flex;
}
.item3 {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0.25rem;
  justify-self: center;
}
.item4{
  justify-self: right;
}

#play-button{
  padding: 0.5rem;
  text-transform: uppercase;

  text-indent: 0.25em;
  letter-spacing: 0.2em;

  font-weight: 10;

  font-size: 1.75rem;
  line-height: 1.3rem;

  border-style: none;

  align-items: center;
  display: flex;

  .border {
    display: flex;
    justify-content: center;
    align-items: center;

    color: var(--color-fg);

    height: 3.5rem;
    width: 3.5rem;

    border-width: 2px;

    border-radius: 9999px;

    position: relative;

    overflow: hidden;

    #icon{
      margin-right: 0.65rem;
      z-index: 10;
      position: relative;

      &.playing{
        transform: scale(1.5);
        margin-right: 0rem !important;
      }
      &:not(.playing){
        width: 24px;
        height: 24px;
      }
    }
  }
}

</style>

<style>
.separator {
  background-color: white;
  width: 1px;
  height: 100%;
  position: absolute;
}

.sep-selected{
  background-color: white;
}
</style>