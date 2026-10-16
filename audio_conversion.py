"""Streaming audio conversion using the FFmpeg libraries bundled with PyAV."""
import time
from itertools import chain
from pathlib import Path


OUTPUT_FORMATS = {
    'original': '保留原格式',
    'wav': 'WAV（无损 PCM）',
    'mp3': 'MP3（有损压缩）',
}


def convert_audio(source_path, target_path, output_format, report, metadata=None):
    """Return the completed staging file; same-format audio is left untouched."""
    if output_format not in ('wav', 'mp3'):
        raise ValueError('不支持的目标格式')
    import av

    with av.open(str(source_path)) as source:
        if not source.streams.audio:
            raise ValueError('下载的文件中没有音频')
        stream = source.streams.audio[0]
        frames = source.decode(stream)
        first = next(frames, None)
        if first is None or not first.samples:
            raise ValueError('音频为空或无法解码')
        # Inspect real content instead of trusting the provider's extension.
        if output_format in source.format.name.split(','):
            if output_format == 'mp3' or stream.codec_context.name.startswith('pcm_'):
                report(100, f'已是 {output_format.upper()}，保留原音频')
                return str(source_path)

        rate, layout = first.sample_rate, first.layout
        if output_format == 'mp3':
            codec, sample_format = 'libmp3lame', 'fltp'
            rate = min((32000, 44100, 48000), key=lambda candidate: abs(candidate - rate))
            layout = 'mono' if len(first.layout.channels) == 1 else 'stereo'
        else:
            sample_format = first.format.packed.name
            codec = {
                'u8': 'pcm_u8', 's16': 'pcm_s16le', 's32': 'pcm_s32le',
                's64': 'pcm_s64le', 'flt': 'pcm_f32le', 'dbl': 'pcm_f64le',
            }.get(sample_format)
            if codec is None:
                raise ValueError(f'不支持的音频采样格式：{sample_format}')

        duration = float(stream.duration * stream.time_base) if stream.duration is not None and stream.time_base else None
        if not duration and source.duration:
            duration = source.duration / av.time_base
        elapsed, last_report = 0.0, 0.0
        with av.open(str(target_path), mode='w', format=output_format) as target:
            target.metadata.update(source.metadata)
            target.metadata.update(stream.metadata)
            target.metadata.update({key: str(value) for key, value in (metadata or {}).items()
                                    if value and value != '—'})
            output = target.add_stream(codec, rate=rate)
            output.layout = layout
            output.codec_context.format = sample_format
            if output_format == 'mp3':
                output.bit_rate = 320000
            resampler = av.AudioResampler(format=sample_format, layout=layout, rate=rate)
            for frame in chain((first,), frames):
                elapsed += frame.samples / frame.sample_rate
                # Audio is continuous even if a provider supplies discontinuous timestamps.
                frame.pts = None
                for converted in resampler.resample(frame):
                    for packet in output.encode(converted):
                        target.mux(packet)
                if time.monotonic() - last_report >= 0.1:
                    percent = min(99, int(elapsed * 100 / duration)) if duration else -1
                    report(percent, f'正在转换为 {output_format.upper()} · 已处理 {elapsed:.1f} 秒音频')
                    last_report = time.monotonic()
            for converted in resampler.resample(None):
                for packet in output.encode(converted):
                    target.mux(packet)
            for packet in output.encode(None):
                target.mux(packet)

    # Validate the actual encoder output before the worker publishes the file.
    with av.open(str(target_path)) as result:
        if not result.streams.audio or next(result.decode(audio=0), None) is None:
            raise ValueError('转换结果没有可播放的音频')
    report(100, f'{output_format.upper()} 转换完成 · {Path(target_path).stat().st_size / 1048576:.1f} MB')
    return str(target_path)
