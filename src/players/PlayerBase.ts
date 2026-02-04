export abstract class Player {
    isPlaying: boolean = false;
    musicUrl: string = "";

    constructor(url: string){
        this.musicUrl = url;
    }

    abstract PlayMusicUntilEnd(started_callback: () => void | null, finished_callback: () => void | null): void;
    abstract PlayMusic(timer: number, started_callback: () => void | null, finished_callback: () => void | null): void;
    abstract StopMusic(): void;

    abstract GetCurrentMusicTime(callback: (percentage: number)=>void): void;
    abstract GetCurrentMusicLength(callback: (length: number) => void): void;

    abstract GetVolume(): number;
    abstract SetVolume(volume: number): void;

    abstract Destroy(): void;
}