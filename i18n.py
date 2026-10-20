"""Application text, live widget translation, and thread-local task language."""
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from weakref import ref


LANGUAGES = {'zh_CN': '简体中文', 'en_US': 'English'}
_language = ContextVar('musicdl_language', default='zh_CN')

ENGLISH = {
    'MusicdlGUI · 音乐搜索与下载': 'MusicdlGUI · Music Search & Download',
    '搜索音乐，收藏喜欢的声音': 'Find music. Keep the sounds you love.',
    '切换主题': 'Switch theme',
    '设置': 'Settings',
    '设置 / Settings': 'Settings',
    '音乐来源': 'Music sources',
    'QQ 音乐': 'QQ Music',
    '酷我音乐': 'Kuwo Music',
    '咪咕音乐': 'Migu Music',
    '千千音乐': 'Qianqian Music',
    '酷狗音乐': 'Kugou Music',
    '网易云音乐': 'NetEase Music',
    '输入歌名、歌手或专辑，按 Enter 搜索': 'Enter a song, artist or album, then press Enter',
    '搜索': 'Search',
    '选择音乐来源，开始第一次搜索。': 'Choose music sources to start your first search.',
    '各来源搜索状态': 'Search status by source',
    '全选可见结果': 'Select visible',
    '清空选择': 'Clear selection',
    '下载选中': 'Download selected',
    '下载选中（{count}）': 'Download selected ({count})',
    '重试失败来源': 'Retry failed sources',
    '筛选当前结果': 'Filter current results',
    '选择': 'Select',
    '歌曲': 'Song',
    '歌手': 'Artist',
    '专辑': 'Album',
    '时长': 'Duration',
    '大小': 'Size',
    '源格式': 'Source format',
    '来源': 'Source',
    '下载状态': 'Download status',
    '暂无结果': 'No results yet',
    '勾选歌曲后点击“下载选中”，也可以右键下载。': 'Check songs and click "Download selected", or right-click a song to download.',
    '等待下载': 'Queued',
    '取消下载': 'Cancel download',
    '重试失败下载': 'Retry failed downloads',
    '保存格式': 'Save format',
    '保留原格式': 'Keep original',
    'WAV（无损 PCM）': 'WAV (lossless PCM)',
    'MP3（有损压缩）': 'MP3 (lossy)',
    '下载后自动转换，仅保存目标文件。MP3 转换使用 320 kbps；已是该格式时保留原音频。': 'Convert after downloading and keep only the target file. MP3 conversion uses 320 kbps; matching formats keep the original audio.',
    '打开下载目录': 'Open download folder',
    '无法保存设置：{error}': 'Could not save settings: {error}',
    '设置已保存。Cookie 修改将在下一次搜索时生效。': 'Settings saved. Cookie changes apply to the next search.',
    '平铺': 'Flat',
    '按来源': 'By source',
    '按日期和关键词': 'By date and keyword',
    '保存到 {directory} · {structure}': 'Save to {directory} · {structure}',
    '系统文件管理器未能打开目录': 'The system file manager could not open the folder',
    '无法打开目录：{error}': 'Could not open folder: {error}',
    '请输入搜索关键词。': 'Enter a search keyword.',
    '请至少选择一个音乐来源。': 'Select at least one music source.',
    '等待搜索': 'Queued',
    '正在搜索“{keyword}”… 可用结果会陆续显示。': 'Searching for "{keyword}"... Available results will appear as they arrive.',
    '搜索中…': 'Searching...',
    '{count} 首': 'Tracks: {count}',
    '未找到可下载歌曲': 'No downloadable tracks found',
    '（部分失败）': ' (some requests failed)',
    '已找到 {count} 首，正在等待其他来源…': 'Results: {count}. Waiting for other sources...',
    '搜索失败': 'Search failed',
    '已取消': 'Cancelled',
    '搜索已取消，保留 {count} 首可用结果。': 'Search cancelled. Available tracks kept: {count}.',
    '找到 {count} 首，{failed} 个来源失败。可重试失败来源，或查看下方原因。': 'Results: {count}; failed sources: {failed}. Retry failed sources or see the details below.',
    '找到 {count} 首。勾选后下载，可按列排序或筛选结果。': 'Results: {count}. Check tracks to download, sort columns or filter results.',
    '没有找到可下载歌曲。请换关键词或音乐来源；需要登录的平台可在设置中更新 Cookie。': 'No downloadable tracks found. Try another keyword or source; update cookies in Settings if a source requires login.',
    '正在取消…': 'Cancelling...',
    '未下载': 'Not downloaded',
    '{total} 首结果 · 当前显示 {visible} 首': 'Results: {total} · Visible: {visible}',
    '取消搜索': 'Cancel search',
    '下载这首歌曲': 'Download this song',
    '下载进程未返回结果': 'The download process returned no result',
    '下载中': 'Downloading',
    '正在下载 {current}/{total}：{song} · {artist}': 'Downloading {current}/{total}: {song} · {artist}',
    '正在连接…': 'Connecting...',
    '转换中': 'Converting',
    '已下载': 'Downloaded',
    '失败 · 可重试': 'Failed · Retry available',
    '成功 {success}/{total}': 'Succeeded {success}/{total}',
    '下载已取消': 'Download cancelled',
    '下载完成': 'Download complete',
    '{message} · 成功 {success}/{total} 首{details}{more}': '{message} · {success}/{total} tracks succeeded{details}{more}',
    '其余失败原因可在“下载状态”列悬停查看。': 'Hover over the "Download status" column for the remaining errors.',
    '正在取消下载并清理临时文件…': 'Cancelling download and cleaning up temporary files...',
    '搜索设置': 'Search settings',
    ' 秒': ' s',
    '每个来源最多结果': 'Results per source',
    '每个来源搜索时限': 'Timeout per source',
    '外观': 'Appearance',
    '浅色模式': 'Light mode',
    '深色模式': 'Dark mode',
    '下载目录': 'Download folder',
    '浏览': 'Browse',
    '保存到': 'Save to',
    '下载后自动转换，仅保存目标文件。WAV 文件较大；MP3 转换时使用 320 kbps，已有 MP3 保持原码率。': 'Convert after downloading and keep only the target file. WAV files are larger; MP3 conversion uses 320 kbps, while existing MP3 files keep their bitrate.',
    '文件组织方式': 'Folder organization',
    '平铺（所有音乐直接保存到所选目录）': 'Flat (save all music directly to the selected folder)',
    '按音乐来源分类（为每个平台创建子文件夹）': 'By source (create a subfolder for each platform)',
    '按日期分类 (音乐源/日期 关键词/)': 'By date (source/date keyword/)',
    '日志与排查': 'Logs and troubleshooting',
    '当前日志文件: {filename}': 'Current log file: {filename}',
    '日志文件: 尚未初始化': 'Log file: not initialized yet',
    '日志目录不可写': 'The log folder is not writable',
    '日志目录: {directory}': 'Log folder: {directory}',
    '打开日志目录': 'Open log folder',
    '打开当前日志': 'Open current log',
    '系统文件管理器未能打开日志目录': 'The system file manager could not open the log folder',
    'Warning - 警告': 'Warning',
    'Info - 信息': 'Information',
    '无法打开日志目录: {error}': 'Could not open log folder: {error}',
    '日志文件尚未创建': 'The log file has not been created yet',
    '系统未能打开日志文件': 'The system could not open the log file',
    '无法打开日志文件: {error}': 'Could not open log file: {error}',
    '平台登录 Cookie（按账号已有权限访问）': 'Platform login cookies (access within your account permissions)',
    '下载 Cookie 留空时沿用搜索 Cookie。修改后请重新搜索。': 'Leave download cookies empty to use search cookies. Search again after making changes.',
    '搜索 Cookie': 'Search cookies',
    '例如: uin=123456; qm_keyst=xxxxx; ...': 'Example: uin=123456; qm_keyst=xxxxx; ...',
    '下载 Cookie': 'Download cookies',
    '留空时沿用搜索 Cookie': 'Leave empty to use search cookies',
    '复制搜索 Cookie 到下载': 'Copy search cookies to download cookies',
    '保存': 'Save',
    '取消': 'Cancel',
    'Select Download Directory - 选择下载目录': 'Select download folder',
    '下载目录为空': 'Download folder is empty',
    '请选择下载保存目录。': 'Choose a folder to save downloads.',
    '目录无效': 'Invalid folder',
    '所选路径是文件，请选择文件夹。': 'The selected path is a file. Choose a folder.',
    '无法连接代理，请检查系统代理设置': 'Could not connect to the proxy. Check your system proxy settings.',
    'HTTPS 证书验证失败，请检查系统时间、证书或代理': 'HTTPS certificate verification failed. Check the system time, certificates or proxy.',
    '网络请求超时，请重试或切换音乐源': 'The network request timed out. Retry or switch music sources.',
    '网络连接失败，请检查网络或切换音乐源': 'The network connection failed. Check your connection or switch music sources.',
    '未知': 'unknown',
    '平台返回 HTTP {code}，请重试；登录失效时请更新 Cookie': 'The platform returned HTTP {code}. Retry, or update cookies if your login has expired.',
    '[链接已隐藏]': '[URL hidden]',
    '[已隐藏]': '[hidden]',
    '部分请求失败，已保留可用结果': 'Some requests failed; available results have been kept',
    '此结果不是直链音频，请选择同一歌曲的其他结果': 'This result is not a direct audio link. Choose another result for the same song.',
    '没有可用下载地址，请重新搜索': 'No download URL is available. Search again.',
    '下载响应不完整（HTTP {code}），请重新搜索': 'Incomplete download response (HTTP {code}). Search again.',
    '平台返回了网页或错误信息，下载链接可能已过期，请重新搜索': 'The platform returned a web page or error. The download link may have expired; search again.',
    '下载地址返回了错误页面，请重新搜索': 'The download URL returned an error page. Search again.',
    '音频文件为空或传输不完整，请重试': 'The audio file is empty or the transfer is incomplete. Retry.',
    '不支持的保存格式，请重新选择': 'Unsupported save format. Choose another format.',
    '正在下载': 'Downloading',
    '正在转换为 {format}': 'Converting to {format}',
    '正在读取音频…': 'Reading audio...',
    '无法加载音频转换组件，请重新安装完整依赖或使用完整安装包': 'Could not load the audio converter. Reinstall all dependencies or use a complete application package.',
    '转换为 {format} 失败：{error}': 'Conversion to {format} failed: {error}',
    '音乐源进程意外退出，请重试或检查依赖版本': 'The background process exited unexpectedly. Retry or check dependency versions.',
    '搜索超过 {timeout} 秒，已停止；可在设置中延长时限或切换音乐源': 'Search stopped after {timeout} s. Increase the timeout in Settings or switch music sources.',
    '已取消下载': 'Download cancelled',
    '下载或转换超过 10 分钟，已停止，请重试': 'Download or conversion stopped after 10 minutes. Retry.',
    '不支持的目标格式': 'Unsupported target format',
    '下载的文件中没有音频': 'The downloaded file contains no audio',
    '音频为空或无法解码': 'The audio is empty or could not be decoded',
    '已是 {format}，保留原音频': 'Already {format}; keeping the original audio',
    '不支持的音频采样格式：{format}': 'Unsupported audio sample format: {format}',
    '正在转换为 {format} · 已处理 {seconds:.1f} 秒音频': 'Converting to {format} · {seconds:.1f} seconds processed',
    '转换结果没有可播放的音频': 'The converted file contains no playable audio',
    '{format} 转换完成 · {size:.1f} MB': '{format} conversion complete · {size:.1f} MB',
    '无法读取设置，已使用默认值；原文件保留在 {path}（{error}）': 'Could not read settings; using defaults. The original file is preserved at {path} ({error}).',
    '已读取原设置，但无法迁移到 {path}，请检查目录权限。': 'Loaded the old settings but could not migrate them to {path}. Check folder permissions.',
}


def normalize_language(language):
    return language if isinstance(language, str) and language in LANGUAGES else 'zh_CN'


@dataclass
class Text:
    """A nested application message that can be translated again later."""
    source: str
    values: dict = field(default_factory=dict)


def translate(template, language=None, **values):
    language = normalize_language(_language.get() if language is None else language)
    text = ENGLISH.get(template, template) if language == 'en_US' else template
    values = {key: translate(value.source, language, **value.values) if isinstance(value, Text) else value
              for key, value in values.items()}
    return text.format(**values) if values else text


@contextmanager
def language_context(language):
    token = _language.set(normalize_language(language))
    try:
        yield
    finally:
        _language.reset(token)


class Translator:
    """Keep source templates so changing language preserves widget state."""
    def __init__(self, language='zh_CN'):
        self.language = normalize_language(language)
        self._bindings = {}

    def __call__(self, template, **values):
        return translate(template, self.language, **values)

    def bind(self, widget, template, *, method='setText', args=(), **values):
        identity = id(widget)
        if identity not in self._bindings:
            self._bindings[identity] = (ref(widget, lambda unused: self._bindings.pop(identity, None)), {})
        self._bindings[identity][1][(method, args)] = (template, values)
        getattr(widget, method)(*args, self(template, **values))
        return widget

    def set_language(self, language):
        self.language = normalize_language(language)
        for identity, (reference, bindings) in list(self._bindings.items()):
            widget = reference()
            if widget is None:
                continue
            try:
                for (method, args), (source, values) in bindings.items():
                    getattr(widget, method)(*args, self(source, **values))
            except RuntimeError:
                # Qt may already have deleted rows or labels from an older search.
                self._bindings.pop(identity, None)
