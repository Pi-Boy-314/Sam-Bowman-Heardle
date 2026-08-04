// Game state, daily song selection, and persistence.
//
// This lives outside main.js on purpose. main.js is the entry point that mounts
// App.vue, and nearly every component needs `currentGameState` -- so when this
// code lived in main.js, main.js -> App.vue -> component -> main.js formed an
// import cycle. It happened to work on a cold load but broke Vite's HMR, so any
// edit during development required a hard reload ("Cannot access 'App' before
// initialization"). Keeping state in its own leaf module removes the cycle.

import { ref, watch } from 'vue'

import settings from '@/settings/settings.json'
import music from '@/settings/music.json'

export function ParseStringWithVariable(string) {
    let nString = "";
    for (let i = 0; i < string.length; i++) {
        if(string[i] === '{'){
            let testStr = string.slice(i, string.length);

            let key = "";
            key = string.slice(i, i+testStr.indexOf("}")).replace("{", "").replace("}", "");

            switch(key) {
                case "heardle-name":
                    nString += settings["heardle-name"];
                    break;
                case "unlocked-time":
                    nString += settings["times"][currentGameState.value.guessed.length-1];
                    break;
                default:
                    nString += key;
                    break;
            }

            i += testStr.indexOf("}");
        }
        else {
            nString += string[i];
        }
    }

    return nString;
}

/**
 * Whole days elapsed between `startISO` and now, measured in Central Time.
 *
 * Central Time is the reference zone for the daily rollover, so both endpoints
 * are reduced to their CT calendar date before subtracting. That keeps the
 * result stable regardless of the player's own timezone or DST.
 */
export function daysSinceStartInCT(startISO) {
    const fmt = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Chicago', year: 'numeric', month: 'numeric', day: 'numeric' });
    const partsNow = fmt.formatToParts(new Date()).reduce((acc, p) => { acc[p.type] = p.value; return acc; }, {});

    const startDate = startISO ? new Date(startISO) : new Date(0);
    const partsStart = fmt.formatToParts(startDate).reduce((acc, p) => { acc[p.type] = p.value; return acc; }, {});

    const nowMidCTUtc = Date.UTC(Number(partsNow.year), Number(partsNow.month) - 1, Number(partsNow.day));
    const startMidCTUtc = Date.UTC(Number(partsStart.year), Number(partsStart.month) - 1, Number(partsStart.day));

    return Math.floor((nowMidCTUtc - startMidCTUtc) / 86400000);
}

function random(seed) {
  var x = Math.sin(seed++) * 10000;
  return x - Math.floor(x);
}

function shuffle(array, seed) {                // <-- ADDED ARGUMENT
  var m = array.length, t, i;

  // While there remain elements to shuffle…
  while (m) {

    // Pick a remaining element…
    i = Math.floor(random(seed) * m--);        // <-- MODIFIED LINE

    // And swap it with the current element.
    t = array[m];
    array[m] = array[i];
    array[i] = t;
    ++seed                                     // <-- ADDED LINE
  }

  return array;
}

export const _currentGameState = ref({
    guess: 0,
    guessed: [],
    isFinished: false,
});

let listIndex = 0;
let id = 0;

const shuffledMusic = music.slice();

// Create a single deterministic permutation of the music list so each song
// appears once per cycle (no repeats within a cycle). The seed is derived
// from `settings.start-date` (days since epoch) to keep the ordering stable.
const globalSeed = Math.floor((settings["start-date"] ? new Date(settings["start-date"]).getTime() : 0) / 86400000);
shuffle(shuffledMusic, globalSeed);

if(settings["infinite"]){
    listIndex = Math.round(Math.random() * (music.length-1));

} else {
        id = daysSinceStartInCT(settings["start-date"]);
        listIndex = id % music.length;

    const usString = localStorage.getItem("userStats");
    if(usString !== null && usString !== ""){
        let stats = JSON.parse(usString);
        let item = stats.find((item)=>{
            return item.id === id;
        })

        if(item !== undefined){
            _currentGameState.value.guess = item.guess;
            _currentGameState.value.guessed = item.guessed;
            _currentGameState.value.isFinished = item.isFinished;
        }
    }

    // previously shuffled per-block; keep the single global shuffle above
    // so the order is random-looking but each song appears exactly once per cycle
}

export const SelectedMusic = shuffledMusic[listIndex];

/** Day number of the current puzzle; also the key used in saved stats. */
export const dayId = id;

/** Position in the rotation, used for the "#N" in shared results. */
export const dayIndex = listIndex;

function save(){
    if(!settings["infinite"]){
        const usString = localStorage.getItem("userStats");
        let stats;

        if(usString === null || usString === ""){
            stats = [];
        } else {
            stats = JSON.parse(usString);
        }

        let item = stats.find((item)=>{
            return item.id === id;
        })

        if(item === undefined){
            stats.push({
                id: id,
                guess: _currentGameState.value.guess,
                guessed: _currentGameState.value.guessed,
                isFinished: _currentGameState.value.isFinished,
            });
        }
        else {
            stats[stats.indexOf(item)] = {
                id: id,
                guess: _currentGameState.value.guess,
                guessed: _currentGameState.value.guessed,
                isFinished: _currentGameState.value.isFinished,
            };
        }

        localStorage.setItem("userStats", JSON.stringify(stats));
    }
}

// The game state is a plain ref; persistence is driven by a deep watcher so a
// write to localStorage happens once per actual state change.
//
// This used to be a Proxy that called save() from its `get` trap, which meant
// every *read* re-serialised the whole stats array -- roughly 50 writes a second
// while a clip was playing, since the playback timer reads .guess on each tick.
// The `set` trap was also dead code: it called the non-existent `Object.set`,
// and would have thrown had anything ever assigned to a top-level property.
export const currentGameState = _currentGameState;

watch(_currentGameState, save, { deep: true });
