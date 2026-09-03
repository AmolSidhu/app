CHUNK_SIZE = 8192

def resume_play_conversion(seconds, bitrate_kbps):
    if seconds <= 0:
        return 0
    bytes_per_second = (bitrate_kbps * 1000) / 8
    return int(seconds * bytes_per_second)


def stream_audio(file_path: str, start_byte: int, end_byte: int, on_disconnect):
    bytes_sent = start_byte
    try:
        with open(file_path, 'rb') as audio_file:
            audio_file.seek(start_byte)

            while bytes_sent <= end_byte:
                remaining = end_byte - bytes_sent + 1
                chunk = audio_file.read(min(CHUNK_SIZE, remaining))
                if not chunk:
                    break

                bytes_sent += len(chunk)
                yield chunk

    except GeneratorExit:
        on_disconnect(bytes_sent)
        raise
    finally:
        on_disconnect(bytes_sent)
