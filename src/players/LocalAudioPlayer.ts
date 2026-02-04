import { Player } from "./PlayerBase";

export class LocalAudioPlayer extends Player {
    audio: HTMLAudioElement
    Playing: boolean
    Volume: number
    startSeconds: number

    constructor(url: string) {
        super(url);
        
        this.audio = new Audio();
        this.audio.crossOrigin = "anonymous";
        this.audio.src = url; // url should be like "/api/audio?id=song-1"
        
        this.Playing = false;
        this.Volume = 50;
        this.startSeconds = 0;

        // Update playing state
        this.audio.addEventListener('play', () => {
            this.Playing = true;
            this.updateMediaSession();
        });

        this.audio.addEventListener('pause', () => {
            this.Playing = false;
        });

        this.audio.addEventListener('ended', () => {
            this.Playing = false;
        });

        // Set media session metadata
        this.updateMediaSession();

        this.audio.volume = this.Volume / 100;
    }

    private updateMediaSession(): void {
        if ('mediaSession' in navigator) {
            const baseUrl = window.location.origin;
            navigator.mediaSession.metadata = new MediaMetadata({
                title: 'Chapstick for Glue',
                artist: 'Sam Bowman',
                album: 'Chapstick for Glue',
                artwork: [
                    { src: `${baseUrl}/favicon.ico`, sizes: '48x48', type: 'image/x-icon' },
                    { src: `${baseUrl}/favicon.ico`, sizes: '96x96', type: 'image/x-icon' },
                    { src: `${baseUrl}/favicon.ico`, sizes: '128x128', type: 'image/x-icon' },
                    { src: `${baseUrl}/favicon.ico`, sizes: '256x256', type: 'image/x-icon' }
                ]
            });

            // Set action handlers
            navigator.mediaSession.setActionHandler('play', () => {
                this.audio.play().catch(() => {});
            });
            navigator.mediaSession.setActionHandler('pause', () => {
                this.audio.pause();
            });
            navigator.mediaSession.setActionHandler('seekbackward', null);
            navigator.mediaSession.setActionHandler('seekforward', null);
            navigator.mediaSession.setActionHandler('previoustrack', null);
            navigator.mediaSession.setActionHandler('nexttrack', null);
        }
    }

    override PlayMusicUntilEnd(started_callback: () => void | null, finished_callback: () => void | null): void {
        let hasStarted = false;

        const onPlay = () => {
            if (!hasStarted) {
                hasStarted = true;
                if (started_callback != null) started_callback();
            }
        };

        const onEnded = () => {
            this.audio.removeEventListener('play', onPlay);
            this.audio.removeEventListener('ended', onEnded);
            if (finished_callback != null) finished_callback();
        };

        this.audio.addEventListener('play', onPlay);
        this.audio.addEventListener('ended', onEnded);

        // Always reset to start position before playing
        this.audio.currentTime = this.startSeconds;

        this.audio.play().catch(e => console.log('Audio play failed:', e));
    }

    override PlayMusic(timer: number, started_callback: () => void | null, finished_callback: () => void | null): void {
        let hasStarted = false;
        let timeoutId: ReturnType<typeof setTimeout>;

        const onPlay = () => {
            if (!hasStarted) {
                hasStarted = true;
                if (started_callback != null) started_callback();
                
                // Set timeout to stop playback after timer
                timeoutId = setTimeout(() => {
                    this.StopMusic();
                    if (finished_callback != null) finished_callback();
                }, timer * 1000);
            }
        };

        const onPause = () => {
            if (timeoutId) clearTimeout(timeoutId);
        };

        this.audio.addEventListener('play', onPlay);
        this.audio.addEventListener('pause', onPause);

        // Always reset to start position before playing
        this.audio.currentTime = this.startSeconds;

        this.audio.play().catch(e => console.log('Audio play failed:', e));
    }

    override StopMusic(): void {
        this.audio.pause();
        if (this.startSeconds > 0) {
            this.audio.currentTime = this.startSeconds;
        }
    }

    override async GetCurrentMusicTime(callback: (percentage: number) => void) {
        if (!this.Playing) {
            callback(0);
            return;
        }

        const adjustedMs = Math.max(0, (this.audio.currentTime - this.startSeconds) * 1000);
        callback(adjustedMs);
    }

    override async GetCurrentMusicLength(callback: (length: number) => void) {
        if (this.audio.duration && !isNaN(this.audio.duration)) {
            const adjustedMs = Math.max(0, (this.audio.duration - this.startSeconds) * 1000);
            callback(adjustedMs);
        } else {
            // Wait for metadata to load
            this.audio.addEventListener('loadedmetadata', () => {
                const adjustedMs = Math.max(0, (this.audio.duration - this.startSeconds) * 1000);
                callback(adjustedMs);
            }, { once: true });
        }
    }

    override GetVolume(): number {
        return this.Volume;
    }

    override SetVolume(volume: number): void {
        this.Volume = volume;
        this.audio.volume = volume / 100;
    }

    override Destroy(): void {
        // Stop playback
        this.audio.pause();
        this.audio.currentTime = this.startSeconds;
        
        // Remove all event listeners to prevent memory leaks
        this.audio.removeEventListener('play', this.audio.onplay as any);
        this.audio.removeEventListener('pause', this.audio.onpause as any);
        this.audio.removeEventListener('ended', this.audio.onended as any);
        
        // Clear all listeners by replacing the audio element
        this.audio.src = '';
        
        // Reset media session
        if ('mediaSession' in navigator) {
            navigator.mediaSession.metadata = null;
            navigator.mediaSession.setActionHandler('play', null);
            navigator.mediaSession.setActionHandler('pause', null);
        }
    }
}