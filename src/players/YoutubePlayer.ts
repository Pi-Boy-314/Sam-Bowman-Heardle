import {Player} from "@/players/PlayerBase";
import PlayerFactory from "youtube-player";
import PlayerStates from "youtube-player/dist/constants/PlayerStates";
import { YouTubePlayer } from "youtube-player/dist/types";

export class YoutubeMusicPlayer extends Player {
    p: YouTubePlayer
    Playing: boolean
    Volume: number
    startSeconds: number
    private playerStateInterval: ReturnType<typeof setInterval> | null = null
    private container: HTMLElement | null = null

    constructor(url: string) {
        super(url);

        const parseStartSeconds = (value: string | null): number => {
            if (!value) return 0;

            // Support plain seconds ("7"), suffixed seconds ("7s"), or h/m/s combos ("1m30s").
            const numericOnly = Number(value.replace(/[^0-9]/g, ""));
            if (!Number.isNaN(numericOnly) && numericOnly > 0) return numericOnly;

            const parts = value.match(/(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s?)?/i);
            if (!parts) return 0;

            const hours = parts[1] ? Number(parts[1]) * 3600 : 0;
            const minutes = parts[2] ? Number(parts[2]) * 60 : 0;
            const seconds = parts[3] ? Number(parts[3]) : 0;

            return hours + minutes + seconds;
        };

        const normalizedUrl = url.startsWith("http") ? url : `https://${url}`;
        let videoId = "";
        this.startSeconds = 0;

        const main = document.getElementsByTagName("main")[0];
        this.container = document.createElement("div");
        this.container.classList.add("hidden");

        const iframe = document.createElement("div");
        iframe.id = "video-player";
        iframe.className = "hidden";
        this.container.appendChild(iframe);

        main.appendChild(this.container);

        // Set initial media session metadata for the YouTube player
        this.updateMediaSession();
        
        // Track player state for UI updates
        this.playerStateInterval = window.setInterval(()=>{
            this.p.getPlayerState().then((state)=>{
                this.Playing = (state == 1);
            });
        }, 100);

        try {
            const parsed = new URL(normalizedUrl);
            videoId = parsed.searchParams.get("v") ?? "";
            this.startSeconds = parseStartSeconds(parsed.searchParams.get("t") ?? parsed.searchParams.get("start"));
        } catch (err) {
            // Fallback to the previous simple parsing if URL construction fails (e.g., malformed input)
            const videoURL = url;
            const splited = videoURL.split("v=");
            const splitedAgain = splited[1]?.split("&");
            videoId = splitedAgain ? splitedAgain[0] : "";
            this.startSeconds = 0;
        }

        this.p = PlayerFactory("video-player", {
            videoId: videoId,
            playerVars: {
                autoplay: 0,
                controls: 0,
                disablekb: 1,
                fs: 0,
                modestbranding: 1,
                rel: 0,
                enablejsapi: 1
            }
        });
        this.p.setSize(0, 0);

        console.log("Youtube ID is : %s", videoId);

        this.Volume = 50
        this.p.setVolume(this.Volume)
    }

    // Helper method to set/update media session metadata
    // Called repeatedly to fight iOS stealing media session control
    private updateMediaSession(): void {
        if ('mediaSession' in navigator) {
            const baseUrl = window.location.origin;
            navigator.mediaSession.metadata = new MediaMetadata({
                title: 'Sam Bowman Heardle',
                artist: 'Guess the song!',
                album: 'Music Quiz Game',
                artwork: [
                    { src: `${baseUrl}/favicon.ico`, sizes: '48x48', type: 'image/x-icon' },
                    { src: `${baseUrl}/favicon.ico`, sizes: '96x96', type: 'image/x-icon' },
                    { src: `${baseUrl}/favicon.ico`, sizes: '128x128', type: 'image/x-icon' },
                    { src: `${baseUrl}/favicon.ico`, sizes: '256x256', type: 'image/x-icon' }
                ]
            });
            
            // Set action handlers for media session
            navigator.mediaSession.setActionHandler('play', () => {
                this.p.playVideo().catch(() => {});
            });
            navigator.mediaSession.setActionHandler('pause', () => {
                this.p.pauseVideo();
            });
            navigator.mediaSession.setActionHandler('seekbackward', null);
            navigator.mediaSession.setActionHandler('seekforward', null);
            navigator.mediaSession.setActionHandler('previoustrack', null);
            navigator.mediaSession.setActionHandler('nexttrack', null);
        }
    }

    override PlayMusicUntilEnd(started_callback: () => void | null, finished_callback: () => void | null): void
    {
        if(started_callback != null) started_callback();
        this.p.seekTo(this.startSeconds, true);
        this.p.playVideo();
    }

    override PlayMusic(timer: number, started_callback: () => void | null, finished_callback: () => void | null): void
    {
        let hasStarted = false;

        this.p.seekTo(this.startSeconds, true);
        
        let onPlay = (event)=>{
            if(event.data == PlayerStates.PLAYING && !hasStarted){
                hasStarted = true;
                if(started_callback != null) started_callback();
                window.setTimeout(()=>{
                    this.p.getPlayerState().then((state)=>{
                        if(!(state == 2)){
                            this.StopMusic();
                            if(finished_callback != null)finished_callback();
                        }
                    });
                }, timer*1000);
            }
        }

        this.p.on("stateChange", onPlay);
        this.p.playVideo();
    }

    override StopMusic(): void
    {
        this.p.pauseVideo();
        this.p.seekTo(this.startSeconds, true);
    }

    override async GetCurrentMusicTime(callback: (percentage: number)=>void)
    {
        if(!this.Playing) callback(0);

        this.p.getCurrentTime().then((n)=>{
            const adjustedMs = Math.max(0, (n - this.startSeconds) * 1000);
            callback(adjustedMs);
        })
    }

    override async GetCurrentMusicLength(callback: (length: number)=>void)
    {
        this.p.getDuration().then((n)=>{
            console.log("Length is : %d", n)
            const adjustedMs = Math.max(0, (n - this.startSeconds) * 1000);
            callback(adjustedMs);
        })
    }

    override GetVolume(): number {
        return this.Volume;
    }

    override SetVolume(volume: number): void {
        this.Volume = volume
        this.p.setVolume(this.Volume)
    }

    override Destroy(): void {
        // Clear stored interval
        if (this.playerStateInterval !== null) {
            clearInterval(this.playerStateInterval);
            this.playerStateInterval = null;
        }
        
        // Stop the YouTube player
        this.p.stopVideo();
        this.p.seekTo(this.startSeconds, true);
        
        // Remove the container if it exists
        if (this.container && this.container.parentElement) {
            this.container.parentElement.removeChild(this.container);
            this.container = null;
        }
        
        // Reset media session
        if ('mediaSession' in navigator) {
            navigator.mediaSession.metadata = null;
            navigator.mediaSession.setActionHandler('play', null);
            navigator.mediaSession.setActionHandler('pause', null);
        }
    }
}