from pathlib import Path
import struct

import av
import pytest

from audio_conversion import convert_audio
from backend import BackendError, prepare_download


def decoded_pcm(path):
    with av.open(str(path)) as container:
        return b''.join(bytes(frame.planes[0])[:frame.samples * len(frame.layout.channels) * frame.format.bytes]
                        for frame in container.decode(audio=0))


def test_flac_to_wav_preserves_samples_and_metadata(tmp_path, flac_audio):
    content, pcm = flac_audio
    source, target = tmp_path / 'source.part', tmp_path / 'output.wav'
    source.write_bytes(content)
    progress = []
    result = convert_audio(source, target, 'wav', lambda *args: progress.append(args))
    assert result == str(target)
    assert decoded_pcm(target) == pcm
    with av.open(result) as output:
        assert output.format.name == 'wav'
        assert output.streams.audio[0].codec_context.name == 'pcm_s16le'
        assert output.streams.audio[0].rate == 44100
        assert output.metadata['title'] == 'Test recording'
    assert progress[-1][0] == 100
    assert source.read_bytes() == content


def test_high_precision_flac_to_wav_does_not_reduce_bit_depth(tmp_path):
    source, target = tmp_path / 'high-res.flac', tmp_path / 'output.wav'
    # 24-bit samples occupy the high 24 bits of PyAV's s32 sample format.
    pcm = b''.join(struct.pack('<i', value * 256) for value in range(-4096, 4096))
    with av.open(str(source), 'w') as container:
        stream = container.add_stream('flac', rate=96000)
        stream.layout = 'mono'
        stream.codec_context.format = 's32'
        frame = av.AudioFrame(format='s32', layout='mono', samples=8192)
        frame.sample_rate = 96000
        frame.planes[0].update(pcm)
        for packet in stream.encode(frame):
            container.mux(packet)
        for packet in stream.encode(None):
            container.mux(packet)
    convert_audio(source, target, 'wav', lambda *args: None)
    assert decoded_pcm(target) == decoded_pcm(source)
    with av.open(str(target)) as output:
        assert output.streams.audio[0].codec_context.name == 'pcm_s32le'
        assert output.streams.audio[0].rate == 96000


def test_flac_to_mp3_is_playable_and_same_format_is_not_reencoded(tmp_path, flac_audio):
    source, target = tmp_path / 'source.flac', tmp_path / 'output.mp3'
    source.write_bytes(flac_audio[0])
    convert_audio(source, target, 'mp3', lambda *args: None, {'artist': 'Test artist'})
    with av.open(str(target)) as output:
        assert output.format.name == 'mp3'
        assert output.streams.audio[0].bit_rate == 320000
        assert output.metadata['artist'] == 'Test artist'
        duration = sum(frame.samples / frame.sample_rate for frame in output.decode(audio=0))
        assert duration == pytest.approx(0.25, abs=0.03)
    original = target.read_bytes()
    unused = tmp_path / 'should-not-exist.mp3'
    assert convert_audio(target, unused, 'mp3', lambda *args: None) == str(target)
    assert target.read_bytes() == original and not unused.exists()


def test_conversion_failure_has_clear_phase_and_no_final_file(tmp_path):
    phases = []
    with pytest.raises(BackendError, match='转换为 WAV 失败'):
        prepare_download({'downloaded_contents': b'not audio'}, str(tmp_path / 'audio.part'),
                         'wav', lambda *args: None, lambda *args: phases.append(args))
    assert [phase[0] for phase in phases] == ['download', 'convert']
    assert not (tmp_path / 'audio.wav').exists()


def test_original_format_does_not_decode_or_change_bytes(tmp_path, flac_audio):
    phases = []
    staging = str(tmp_path / 'audio.part')
    result = prepare_download({'downloaded_contents': flac_audio[0]}, staging, 'original',
                              lambda *args: None, lambda *args: phases.append(args))
    assert result == staging
    assert Path(result).read_bytes() == flac_audio[0]
    assert [phase[0] for phase in phases] == ['download']
