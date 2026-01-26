import {Player} from "@/players/PlayerBase";
import PlayerFactory from "youtube-player";
import PlayerStates from "youtube-player/dist/constants/PlayerStates";
import { YouTubePlayer } from "youtube-player/dist/types";

export class YoutubeMusicPlayer extends Player {
    p: YouTubePlayer
    Playing: boolean
    Volume: number
    dummyAudio: HTMLAudioElement
    startSeconds: number

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
        const container = document.createElement("div");
        container.classList.add("hidden");

        const iframe = document.createElement("div");
        iframe.id = "video-player";
        iframe.className = "hidden";
        container.appendChild(iframe);

        main.appendChild(container);

        // Create a looping silent audio element to control media session
        this.dummyAudio = new Audio();
        this.dummyAudio.loop = true;
        this.dummyAudio.volume = 0;
        // Use a data URL for a very short silent audio file
        this.dummyAudio.src = 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA';
        
        // Start playing immediately (will work after user interaction)
        this.dummyAudio.play().catch(() => {
            // If autoplay is blocked, it will play when PlayMusic is called
            console.log('Dummy audio autoplay blocked, will play on first interaction');
        });
        
        // Set media session metadata for the dummy audio
        if ('mediaSession' in navigator) {
            const baseUrl = window.location.origin;
            navigator.mediaSession.metadata = new MediaMetadata({
                title: 'Chapstick for Glue',
                artist: 'Matthew Parker',
                album: '',
                artwork: [
                    { src: `${baseUrl}/favicon.ico`, sizes: '48x48', type: 'image/x-icon' },
                    { src: `${baseUrl}/favicon.ico`, sizes: '96x96', type: 'image/x-icon' },
                    { src: `${baseUrl}/favicon.ico`, sizes: '128x128', type: 'image/x-icon' },
                    { src: `${baseUrl}/favicon.ico`, sizes: '256x256', type: 'image/x-icon' }
                ]
            });
            
            // Set dummy handlers to make media session active
            navigator.mediaSession.setActionHandler('play', () => {});
            navigator.mediaSession.setActionHandler('pause', () => {});
        }

        window.setInterval(()=>{
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

    override PlayMusicUntilEnd(started_callback: () => void | null, finished_callback: () => void | null): void
    {
        this.dummyAudio.play().catch(e => console.log('Dummy audio play failed:', e));
        if(started_callback != null) started_callback();
        this.p.seekTo(this.startSeconds, true);
        this.p.playVideo();
    }

    override PlayMusic(timer: number, started_callback: () => void | null, finished_callback: () => void | null): void
    {
        let hasStarted = false;
        this.dummyAudio.play().catch(e => console.log('Dummy audio play failed:', e));

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
        // Keep dummy audio playing to maintain media session control
        // Don't pause or reset it - we want it running continuously
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
}