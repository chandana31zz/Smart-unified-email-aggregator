# voice_reader.py
import subprocess
import threading

_voice_process = None
_lock = threading.Lock()


def speak_or_stop(text):
    """
    Toggle behavior:
    - Click once  -> speak summary (female voice)
    - Click again -> stop speaking
    - Click again -> speak again
    """

    global _voice_process

    if not text:
        return

    with _lock:
        # 🔴 If already speaking → STOP
        if _voice_process and _voice_process.poll() is None:
            try:
                _voice_process.terminate()
                _voice_process.wait(timeout=1)
            except Exception:
                pass
            _voice_process = None
            return

        # 🟢 Else → START speaking (FEMALE VOICE)
        safe_text = text.replace('"', "'").strip()

        command = f'''
        Add-Type -AssemblyName System.Speech;
        $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer;
        $synth.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::Female);
        $synth.Rate = 0;
        $synth.Speak("{safe_text}");
        '''

        try:
            _voice_process = subprocess.Popen(
                ["powershell", "-Command", command],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            _voice_process = None
