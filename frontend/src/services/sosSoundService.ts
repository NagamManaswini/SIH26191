/**
 * Emergency SOS Sound Service.
 * 
 * Uses Web Audio API Synthesizer to emit international SOS tone patterns (... --- ...)
 * handling browser audio autoplay permissions, test tones, mute controls, and visual fallbacks.
 */

class SOSSoundService {
  private audioCtx: AudioContext | null = null;
  private isAudioAllowed: boolean = false;
  private isMuted: boolean = false;
  private isPlaying: boolean = false;
  private timerId: number | null = null;

  constructor() {
    // Check if AudioContext is available
    if (typeof window !== "undefined") {
      const savedPermission = localStorage.getItem("sos_audio_enabled");
      if (savedPermission === "true") {
        this.isAudioAllowed = true;
      }
    }
  }

  /** Unlocks browser audio context on user interaction */
  public enableAudio(): boolean {
    try {
      if (!this.audioCtx) {
        const AudioContextClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
        this.audioCtx = new AudioContextClass();
      }
      if (this.audioCtx.state === "suspended") {
        this.audioCtx.resume();
      }
      this.isAudioAllowed = true;
      localStorage.setItem("sos_audio_enabled", "true");
      return true;
    } catch (e) {
      console.warn("[SOS Audio] Could not enable AudioContext:", e);
      return false;
    }
  }

  public disableAudio() {
    this.isAudioAllowed = false;
    localStorage.setItem("sos_audio_enabled", "false");
    this.stopSOS();
  }

  public toggleMute(): boolean {
    this.isMuted = !this.isMuted;
    if (this.isMuted) {
      this.stopSOS();
    }
    return this.isMuted;
  }

  public getIsMuted(): boolean {
    return this.isMuted;
  }

  public getIsAudioAllowed(): boolean {
    return this.isAudioAllowed;
  }

  /** Plays a single SOS beep pattern (... --- ...) */
  public playSOSToneSequence() {
    if (!this.isAudioAllowed || this.isMuted) return;

    if (!this.audioCtx) {
      const enabled = this.enableAudio();
      if (!enabled || !this.audioCtx) return;
    }

    const ctx = this.audioCtx;
    const now = ctx.currentTime;

    const dotDuration = 0.12;
    const dashDuration = 0.36;
    const pause = 0.1;
    const freq = 880; // High frequency alarm tone (A5)

    let t = now + 0.05;

    const playBeep = (startTime: number, duration: number) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, startTime);

      // Envelope to avoid click sounds
      gain.gain.setValueAtTime(0.001, startTime);
      gain.gain.exponentialRampToValueAtTime(0.5, startTime + 0.01);
      gain.gain.setValueAtTime(0.5, startTime + duration - 0.01);
      gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(startTime);
      osc.stop(startTime + duration);
    };

    // 3 Dots (...)
    for (let i = 0; i < 3; i++) {
      playBeep(t, dotDuration);
      t += dotDuration + pause;
    }

    t += pause * 2; // Pause between letters

    // 3 Dashes (---)
    for (let i = 0; i < 3; i++) {
      playBeep(t, dashDuration);
      t += dashDuration + pause;
    }

    t += pause * 2; // Pause between letters

    // 3 Dots (...)
    for (let i = 0; i < 3; i++) {
      playBeep(t, dotDuration);
      t += dotDuration + pause;
    }
  }

  /** Starts repeating emergency SOS alarm loop */
  public startRepeatingSOS() {
    if (this.isPlaying) return;
    this.isPlaying = true;
    this.playSOSToneSequence();

    this.timerId = window.setInterval(() => {
      if (this.isPlaying && !this.isMuted) {
        this.playSOSToneSequence();
      }
    }, 4500);
  }

  /** Stops active repeating SOS alarm */
  public stopSOS() {
    this.isPlaying = false;
    if (this.timerId !== null) {
      clearInterval(this.timerId);
      this.timerId = null;
    }
  }

  /** Sound test trigger */
  public testSound() {
    this.enableAudio();
    this.playSOSToneSequence();
  }
}

export const sosSoundService = new SOSSoundService();
