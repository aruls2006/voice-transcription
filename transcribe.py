import sys
import os
import wave
import struct
import tempfile
import time

TARGET_SAMPLE_RATE = 16000

def downsample_wav(input_path, output_path, target_rate=TARGET_SAMPLE_RATE):
    """Downsample a WAV file to target_rate Hz using linear interpolation.
    Returns the output path and True if downsampled, or input_path and False if already at target rate."""
    with wave.open(input_path, 'rb') as wav_in:
        params = wav_in.getparams()
        src_rate = params.framerate
        n_channels = params.nchannels
        sampwidth = params.sampwidth
        n_frames = params.nframes

        if src_rate <= target_rate:
            return input_path, False

        print(f"[TRANSCRIPT] Downsampling from {src_rate}Hz to {target_rate}Hz...")

        raw_data = wav_in.readframes(n_frames)

    # Decode samples
    if sampwidth == 2:
        fmt = f"<{n_frames * n_channels}h"
        samples = list(struct.unpack(fmt, raw_data))
    elif sampwidth == 1:
        samples = [s - 128 for s in raw_data]  # unsigned 8-bit to signed
    else:
        # Fallback: treat as 16-bit
        fmt = f"<{len(raw_data) // 2}h"
        samples = list(struct.unpack(fmt, raw_data))

    # If stereo, mix down to mono by averaging channels
    if n_channels > 1:
        mono_samples = []
        for i in range(0, len(samples), n_channels):
            avg = sum(samples[i:i + n_channels]) // n_channels
            mono_samples.append(avg)
        samples = mono_samples
        n_channels = 1

    # Linear interpolation resampling
    ratio = src_rate / target_rate
    new_length = int(len(samples) / ratio)
    resampled = []
    for i in range(new_length):
        src_pos = i * ratio
        idx = int(src_pos)
        frac = src_pos - idx
        if idx + 1 < len(samples):
            val = samples[idx] * (1 - frac) + samples[idx + 1] * frac
        else:
            val = samples[idx] if idx < len(samples) else 0
        # Clamp to 16-bit range
        val = max(-32768, min(32767, int(val)))
        resampled.append(val)

    # Write output WAV at target rate
    with wave.open(output_path, 'wb') as wav_out:
        wav_out.setnchannels(1)
        wav_out.setsampwidth(2)  # 16-bit
        wav_out.setframerate(target_rate)
        wav_out.writeframes(struct.pack(f"<{len(resampled)}h", *resampled))

    print(f"[TRANSCRIPT] Downsampled: {len(samples)} frames -> {len(resampled)} frames")
    return output_path, True


def transcribe_wav(file_path, language='en-US'):
    print(f"[TRANSCRIPT] Starting transcription for {file_path} in language: {language}...")
    try:
        import speech_recognition as sr
    except ImportError:
        import subprocess
        print("[TRANSCRIPT] SpeechRecognition module not found. Installing now...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "SpeechRecognition"], stdout=subprocess.DEVNULL)
            import speech_recognition as sr
            print("[TRANSCRIPT] SpeechRecognition module installed successfully.")
        except Exception as install_err:
            return f"Failed to auto-install SpeechRecognition module: {str(install_err)}"

    if not os.path.exists(file_path):
        return f"Error: Audio file not found at path {file_path}"

    r = sr.Recognizer()

    # Read audio duration and sample rate
    try:
        with wave.open(file_path, 'rb') as wav:
            params = wav.getparams()
            sample_rate = params.framerate
            total_frames = wav.getnframes()
            duration = total_frames / sample_rate

        print(f"[TRANSCRIPT] Audio duration: {duration:.2f}s, Sample rate: {sample_rate}Hz, Channels: {params.nchannels}")
    except Exception as e:
        return f"Error reading audio file format: {str(e)}"

    # Downsample to 16kHz if needed (Google Speech API works best at 16kHz)
    downsampled_path = None
    working_path = file_path
    if sample_rate > TARGET_SAMPLE_RATE:
        try:
            temp_dir = tempfile.gettempdir()
            downsampled_path = os.path.join(temp_dir, f"smng_ds_{int(time.time())}_{os.getpid()}.wav")
            working_path, was_downsampled = downsample_wav(file_path, downsampled_path, TARGET_SAMPLE_RATE)
            if was_downsampled:
                # Recalculate duration based on downsampled file
                with wave.open(working_path, 'rb') as wav_ds:
                    ds_params = wav_ds.getparams()
                    duration = ds_params.nframes / ds_params.framerate
                    print(f"[TRANSCRIPT] Working with downsampled file: {duration:.2f}s at {ds_params.framerate}Hz")
        except Exception as ds_err:
            print(f"[TRANSCRIPT] Warning: Downsampling failed ({ds_err}), using original file.")
            working_path = file_path
            downsampled_path = None

    try:
        result = _transcribe_file(r, working_path, language, duration)
        return result
    finally:
        # Clean up downsampled temp file
        if downsampled_path and os.path.exists(downsampled_path):
            try:
                os.remove(downsampled_path)
            except:
                pass


def _transcribe_file(r, file_path, language, duration):
    """Core transcription logic operating on a 16kHz mono WAV file."""
    import speech_recognition as sr

    # If the file is very short (under 15 seconds), transcribe in one go
    if duration <= 15:
        try:
            with sr.AudioFile(file_path) as source:
                audio_data = r.record(source)
                return r.recognize_google(audio_data, language=language)
        except sr.UnknownValueError:
            return "[No speech recognized in audio]"
        except Exception as e:
            return f"Transcription error: {str(e)}"

    # Split long audio into 10-second chunks to capture both voices without cutoff/loss
    chunk_duration = 10
    chunks_text = []

    try:
        with wave.open(file_path, 'rb') as wav:
            params = wav.getparams()
            sample_rate = params.framerate
            frames_per_chunk = int(sample_rate * chunk_duration)
            total_frames = wav.getnframes()

            offset = 0
            chunk_idx = 1
            timestamp = time.time()

            while offset < total_frames:
                wav.setpos(offset)
                data = wav.readframes(frames_per_chunk)
                if not data:
                    break

                # Create a temporary chunk file
                temp_dir = tempfile.gettempdir()
                chunk_path = os.path.join(temp_dir, f"smng_chunk_{chunk_idx}_{int(timestamp)}_{offset}.wav")
                with wave.open(chunk_path, 'wb') as chunk_wav:
                    chunk_wav.setparams(params)
                    chunk_wav.writeframes(data)

                # Transcribe this chunk
                try:
                    with sr.AudioFile(chunk_path) as source:
                        # Auto-calibrate thresholding to capture quieter/remote voices
                        r.adjust_for_ambient_noise(source, duration=0.15)
                        audio_data = r.record(source)
                        chunk_text = r.recognize_google(audio_data, language=language)
                        if chunk_text.strip():
                            chunks_text.append(chunk_text.strip())
                            print(f"[TRANSCRIPT] Chunk {chunk_idx}: \"{chunk_text.strip()[:60]}...\"")
                except sr.UnknownValueError:
                    # Ignore silent/empty speech chunks
                    pass
                except Exception as chunk_err:
                    print(f"[TRANSCRIPT] Warning: Failed to transcribe chunk {chunk_idx}: {chunk_err}")
                finally:
                    # Clean up temp file immediately
                    try:
                        if os.path.exists(chunk_path):
                            os.remove(chunk_path)
                    except:
                        pass

                offset += frames_per_chunk
                chunk_idx += 1

        if not chunks_text:
            return "[Audio captured but no speech was recognized or understood by the transcriber.]"

        return " ".join(chunks_text)

    except Exception as e:
        return f"Unexpected chunking error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <path_to_wav> [language]")
        sys.exit(1)

    wav_path = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else 'en-US'
    result = transcribe_wav(wav_path, language)
    print(result)
