"use client";

import { useEffect, useRef, useState } from "react";
import { ApiError, api } from "@/lib/api/client";

type Prompt = { id: string; type: string; prompt: string; expected_minutes: number };
type VoiceResult = {
  attempt_id: string;
  evaluation_id: string;
  transcript: string;
  result_json: { overall_score?: number; overall_max?: number; disclaimer?: string; gaps?: string[] };
  is_provisional: boolean;
  model_version: string;
};

export default function VoicePracticePage() {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [recording, setRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<VoiceResult | null>(null);
  const [seconds, setSeconds] = useState(0);
  const mediaRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const timerRef = useRef<number | null>(null);

  useEffect(() => {
    api<Prompt[]>("/voice/prompts").then((rows) => {
      setPrompts(rows);
      if (rows[0]) setSelected(rows[0].id);
    });
  }, []);

  function startRecognition() {
    const SR = (window as unknown as { webkitSpeechRecognition?: typeof SpeechRecognition }).webkitSpeechRecognition
      || window.SpeechRecognition;
    if (!SR) return;
    const recognition = new SR();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";
    recognition.onresult = (event: SpeechRecognitionEvent) => {
      let text = "";
      for (let i = 0; i < event.results.length; i++) {
        text += event.results[i][0].transcript + " ";
      }
      setTranscript(text.trim());
    };
    recognition.onerror = () => {
      /* user can edit transcript manually */
    };
    recognition.start();
    recognitionRef.current = recognition;
  }

  async function startRecording() {
    setError(null);
    setResult(null);
    setTranscript("");
    setSeconds(0);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      chunksRef.current = [];
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };
      recorder.start();
      mediaRef.current = recorder;
      setRecording(true);
      startRecognition();
      timerRef.current = window.setInterval(() => setSeconds((s) => s + 1), 1000);
    } catch {
      setError("Microphone permission is required for voice practice.");
    }
  }

  function stopRecording() {
    mediaRef.current?.stop();
    mediaRef.current?.stream.getTracks().forEach((t) => t.stop());
    recognitionRef.current?.stop();
    setRecording(false);
    if (timerRef.current) window.clearInterval(timerRef.current);
  }

  async function submit() {
    if (!selected || !transcript.trim()) {
      setError("Add or capture a transcript before submitting.");
      return;
    }
    setError(null);
    try {
      const blob = chunksRef.current.length
        ? new Blob(chunksRef.current, { type: "audio/webm" })
        : null;
      if (blob) {
        const body = new FormData();
        body.set("practice_item_id", selected);
        body.set("transcript", transcript);
        body.set("duration_seconds", String(seconds));
        body.set("file", blob, "practice.webm");
        const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
        const res = await fetch(`${API_BASE}/voice/upload`, {
          method: "POST",
          body,
          credentials: "include",
        });
        const data = await res.json();
        if (!res.ok) throw new ApiError(res.status, data?.error?.code || "voice_failed", data?.error?.message || "Failed");
        setResult(data);
      } else {
        const data = await api<VoiceResult>("/voice/submit", {
          method: "POST",
          json: {
            practice_item_id: selected,
            transcript,
            duration_seconds: seconds || null,
            confidence: 0.55,
          },
        });
        setResult(data);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Submit failed");
    }
  }

  const current = prompts.find((p) => p.id === selected);

  return (
    <div className="space-y-6">
      <div>
        <p className="font-mono text-xs uppercase tracking-[0.18em] text-accent-strong">Voice practice</p>
        <h1 className="mt-2 font-display text-4xl font-semibold text-ink-950">Explain out loud</h1>
        <p className="mt-2 text-ink-600">
          Record a spoken answer. Browser speech recognition builds a transcript you can edit, then we evaluate against
          the rubric. Audio is optional storage — never used as a covert interview aid.
        </p>
      </div>

      <div className="panel space-y-4 p-6">
        <label className="label" htmlFor="prompt">
          Prompt
        </label>
        <select className="input" id="prompt" value={selected} onChange={(e) => setSelected(e.target.value)}>
          {prompts.map((p) => (
            <option key={p.id} value={p.id}>
              [{p.type}] {p.prompt.slice(0, 80)}
            </option>
          ))}
        </select>
        {current && <p className="text-sm text-ink-700">{current.prompt}</p>}

        <div className="flex flex-wrap gap-3">
          {!recording ? (
            <button className="btn-primary" onClick={startRecording}>
              Start recording
            </button>
          ) : (
            <button className="btn-secondary" onClick={stopRecording}>
              Stop ({seconds}s)
            </button>
          )}
          <button className="btn-primary" onClick={submit} disabled={!transcript.trim()}>
            Submit for feedback
          </button>
        </div>

        <div>
          <label className="label" htmlFor="transcript">
            Transcript (editable)
          </label>
          <textarea
            id="transcript"
            className="input min-h-40"
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            placeholder="Speak, or type your spoken answer here if speech recognition is unavailable."
          />
        </div>
        {error && <p className="text-sm text-evidence">{error}</p>}
      </div>

      {result && (
        <div className="panel space-y-3 p-6">
          <h2 className="font-display text-2xl text-ink-950">
            Score {result.result_json.overall_score}/{result.result_json.overall_max || 5}
            {result.is_provisional ? " · provisional" : ""}
          </h2>
          <p className="text-sm text-ink-500">Model {result.model_version}</p>
          <p className="text-ink-600">{result.result_json.disclaimer}</p>
          {(result.result_json.gaps || []).length > 0 && (
            <ul className="list-disc pl-5 text-sm text-ink-600">
              {result.result_json.gaps!.map((g) => (
                <li key={g}>{g}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
