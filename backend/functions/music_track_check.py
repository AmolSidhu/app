import os
import numpy as np
import librosa
from pydub import AudioSegment
from librosa.sequence import dtw
from scipy.spatial.distance import cosine

def compare_tracks(
    ref_path='',
    ref_serial='',
    test_path='',
    test_serial='',
    sample_rate=None,
    hop_length=512,
    n_mels=64,
    chroma_shift_search=True,
    mel_weight=0.15
):

    def convert_mp3_to_wav(input_path):
        if input_path.lower().endswith(".mp3"):
            temporary_wav_path = os.path.splitext(input_path)[0] + ".__tmp__.wav"
            AudioSegment.from_mp3(input_path).export(temporary_wav_path, format="wav")
            return temporary_wav_path, True
        return input_path, False

    def extract_audio_features(audio_file_path):

        waveform, sr = librosa.load(audio_file_path, sr=sample_rate, mono=True)

        harmonic_signal, percussive_signal = librosa.effects.hpss(waveform)

        tempo, beat_frames = librosa.beat.beat_track(
            y=percussive_signal, sr=sr, hop_length=hop_length
        )

        if beat_frames.size < 2:
            frame_count = librosa.util.frame(
                waveform,
                frame_length=hop_length * 4,
                hop_length=hop_length * 4
            ).shape[1]
            beat_frames = np.arange(frame_count, dtype=int)

        chroma_cens = librosa.feature.chroma_cens(
            y=harmonic_signal, sr=sr, hop_length=hop_length
        )
        chroma_beatsync = librosa.util.sync(
            chroma_cens, beat_frames, aggregate=np.median)

        mel_spectrogram = librosa.feature.melspectrogram(
            y=harmonic_signal, sr=sr, n_mels=n_mels, hop_length=hop_length
        )
        mel_spectrogram_db = librosa.power_to_db(mel_spectrogram + 1e-12)
        mel_beatsync = librosa.util.sync(
            mel_spectrogram_db, beat_frames, aggregate=np.median)

        def z_normalize(feature_matrix):
            feature_mean = feature_matrix.mean(axis=1, keepdims=True)
            feature_std = feature_matrix.std(axis=1, keepdims=True) + 1e-6
            return (feature_matrix - feature_mean) / feature_std

        return z_normalize(chroma_beatsync), z_normalize(mel_beatsync)

    reference_mp3_path = os.path.join(ref_path, ref_serial + ".mp3")
    test_mp3_path = os.path.join(test_path, test_serial + ".mp3")

    reference_audio_path, reference_is_temp = convert_mp3_to_wav(reference_mp3_path)
    test_audio_path, test_is_temp = convert_mp3_to_wav(test_mp3_path)

    try:
        chroma_ref, mel_ref = extract_audio_features(reference_audio_path)
        chroma_test, mel_test = extract_audio_features(test_audio_path)

        if chroma_ref.shape[1] > chroma_test.shape[1]:
            chroma_ref, chroma_test = chroma_test, chroma_ref
            mel_ref, mel_test = mel_test, mel_ref

        def rotate_chroma_pitch(chroma_matrix, semitone_shift):
            return np.roll(chroma_matrix, shift=semitone_shift, axis=0)

        best_alignment_cost = np.inf
        best_alignment_length = 1

        pitch_shift_candidates = range(12) if chroma_shift_search else [0]

        for semitone_shift in pitch_shift_candidates:
            shifted_chroma_ref = rotate_chroma_pitch(chroma_ref, semitone_shift)

            dtw_cost_matrix, warp_path = dtw(
                shifted_chroma_ref,
                chroma_test,
                subseq=True,
                metric="cosine"
            )

            shift_cost = float(np.min(dtw_cost_matrix[-1, :]))
            warp_path_length = len(warp_path)

            if shift_cost < best_alignment_cost:
                best_alignment_cost = shift_cost
                best_alignment_length = warp_path_length


        chroma_avg_cost = best_alignment_cost / max(best_alignment_length, 1)
        chroma_similarity = float(np.exp(-chroma_avg_cost))

        mel_ref_mean_vector = mel_ref.mean(axis=1)
        mel_test_mean_vector = mel_test.mean(axis=1)

        mel_cosine_similarity = 1.0 - cosine(
            mel_ref_mean_vector, mel_test_mean_vector)
        mel_cosine_similarity = float(
            np.clip((mel_cosine_similarity + 1) / 2, 0.0, 1.0)
        )

        overall_similarity = (
            (1 - mel_weight) * chroma_similarity +
            (mel_weight)      * mel_cosine_similarity
        )

        overall_similarity = float(np.clip(overall_similarity, 0.0, 1.0))
        return overall_similarity

    finally:
        if reference_is_temp and os.path.exists(reference_audio_path):
            os.remove(reference_audio_path)
        if test_is_temp and os.path.exists(test_audio_path):
            os.remove(test_audio_path)
