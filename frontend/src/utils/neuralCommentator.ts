import type { Language } from "../types";

let currentAudio: HTMLAudioElement | null = null;

export function playNeuralCommentary(
  text: string,
  language: Language,
  isGoal: boolean = false
): void {
  // Strip emojis, technical brackets and symbols for crystal-clear broadcast speech
  const cleanText = text
    .replace(/\[.*?\]/g, "")
    .replace(/[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}⭐⚡🔥🛡️⚽👀🎯🚩💥🧤⚠️]/gu, "")
    .trim();

  if (!cleanText) return;

  // If a goal occurred, cancel any previous audio immediately
  if (isGoal && currentAudio) {
    currentAudio.pause();
    currentAudio = null;
  } else if (currentAudio && !currentAudio.paused) {
    // If commentator is already speaking and this isn't a goal, avoid clashing
    return;
  }

  const audioUrl = `http://localhost:8000/api/audio/tts?text=${encodeURIComponent(cleanText)}&lang=${language}`;
  const audio = new Audio(audioUrl);
  currentAudio = audio;

  audio.play().catch((err) => {
    console.warn("[Neural Audio] Server audio stream failed, falling back to Web Speech:", err);
    // Fallback to Web Speech API
    if (window.speechSynthesis) {
      if (isGoal) window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(cleanText);
      utterance.lang = language === "ro" ? "ro-RO" : language === "es" ? "es-ES" : "en-GB";
      const voices = window.speechSynthesis.getVoices();
      const matched = voices.find((v) =>
        language === "ro"
          ? (v.lang.startsWith("ro") || v.name.toLowerCase().includes("romanian") || v.name.toLowerCase().includes("emil") || v.name.toLowerCase().includes("alina"))
          : language === "es"
          ? (v.lang.startsWith("es") || v.name.toLowerCase().includes("spanish"))
          : (v.lang.startsWith("en") || v.name.toLowerCase().includes("english"))
      );
      if (matched) utterance.voice = matched;
      window.speechSynthesis.speak(utterance);
    }
  });
}

export function stopNeuralCommentary(): void {
  if (currentAudio) {
    currentAudio.pause();
    currentAudio = null;
  }
  if (window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }
}
