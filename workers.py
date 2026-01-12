'''
Function:
    Worker Threads for MusicdlGUI
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import os
import requests
from PyQt5.QtCore import QThread, pyqtSignal
from musicdl import musicdl
from musicdl.modules.utils.misc import sanitize_filepath
from logger import log_info, log_error, log_exception, log_debug


class SearchWorker(QThread):
    """
    Background thread for searching music from multiple sources
    """
    finished_sig = pyqtSignal(str, list)  # source_name, results_list
    error_sig = pyqtSignal(str, str)  # source_name, error_msg
    client_ready_sig = pyqtSignal(object)  # music_client object

    def __init__(self, music_sources, keyword, settings):
        """
        Initialize search worker
        
        Args:
            music_sources (list): List of music source names to search
            keyword (str): Search keyword
            settings (dict): Application settings including cookies and work directory
        """
        super().__init__()
        self.music_sources = music_sources
        self.keyword = keyword
        self.settings = settings

    def run(self):
        """
        Execute search in background thread
        Emits finished_sig for successful searches and error_sig for failures
        """
        try:
            log_debug(f'SearchWorker 开始执行，关键词: {self.keyword}')
            # Build config for this specific source
            init_music_clients_cfg = {}
            for source in self.music_sources:
                cookie_data = self.settings.get('cookies', {}).get(source, {})
                init_music_clients_cfg[source] = {
                    'work_dir': self.settings.get('work_dir', 'musicdl_outputs'),
                    'default_search_cookies': cookie_data.get('search', '').strip(),
                    'default_download_cookies': cookie_data.get('download', '').strip() or cookie_data.get('search', '').strip(),
                    'max_retries': 1,
                    'search_size_per_source': 5,
                    'search_size_per_page': 5,
                }
            
            # Handle Quark sites
            quark_cookie = self.settings.get('quark_cookies', '').strip()
            if quark_cookie:
                quark_sites = ['MituMusicClient', 'GequbaoMusicClient', 'YinyuedaoMusicClient', 'BuguyyMusicClient', 
                               'JCPOOMusicClient', 'GequhaiMusicClient', 'LivePOOMusicClient', 'KKWSMusicClient', 'FLMP3MusicClient']
                for site in quark_sites:
                    if site in self.music_sources:
                        init_music_clients_cfg[site]['quark_parser_config'] = {'cookies': quark_cookie}

            client = musicdl.MusicClient(
                music_sources=self.music_sources, 
                init_music_clients_cfg=init_music_clients_cfg,
                requests_overrides={s: {'timeout': (4, 8)} for s in self.music_sources},
                clients_threadings={s: 3 for s in self.music_sources}
            )
            
            # Emit the music client for download use
            self.client_ready_sig.emit(client)
            
            results = client.search(keyword=self.keyword)
            
            for source_name, source_results in results.items():
                log_debug(f'SearchWorker 源 {source_name} 返回 {len(source_results)} 条结果')
                self.finished_sig.emit(source_name, source_results)
            
            # If some sources didn't return any results (even empty list), they might have failed
            for source in self.music_sources:
                if source not in results:
                    log_error(f'SearchWorker 源 {source} 无响应')
                    self.error_sig.emit(source, "No response")
                    
        except Exception as e:
            log_exception(f'SearchWorker 执行出错: {str(e)}')
            for source in self.music_sources:
                self.error_sig.emit(source, str(e))


class DownloadWorker(QThread):
    """
    Background thread for downloading music files
    """
    progress_sig = pyqtSignal(int, str)  # percentage, detailed_text
    finished_sig = pyqtSignal(bool, str, str)  # success, msg, file_path

    def __init__(self, song_info, download_dir, filename, music_client):
        """
        Initialize download worker
        
        Args:
            song_info (dict): Song information including download URL and metadata
            download_dir (str): Directory to save the downloaded file
            filename (str): Filename for the downloaded file
            music_client: MusicClient instance for accessing download headers
        """
        super().__init__()
        self.song_info = song_info
        self.download_dir = download_dir
        self.filename = filename
        self.music_client = music_client

    def run(self):
        """
        Execute download in background thread
        Emits progress_sig during download and finished_sig when complete
        """
        try:
            log_debug(f'DownloadWorker 开始执行，歌曲: {self.song_info.get("song_name", "Unknown")}')
            download_music_file_path = sanitize_filepath(os.path.join(self.download_dir, self.filename))
            
            # Handle duplicate filenames
            if os.path.exists(download_music_file_path):
                base_name = os.path.splitext(self.filename)[0]
                ext = self.song_info['ext']
                counter = 1
                while os.path.exists(download_music_file_path):
                    self.filename = f"{base_name} ({counter}).{ext}"
                    download_music_file_path = sanitize_filepath(os.path.join(self.download_dir, self.filename))
                    counter += 1

            headers = self.music_client.music_clients[self.song_info['source']].default_download_headers
            with requests.get(self.song_info['download_url'], headers=headers, stream=True, verify=False, timeout=60) as resp:
                if resp.status_code in (200, 206):  # 200 OK or 206 Partial Content
                    total_size = int(resp.headers.get('content-length', 0))
                    chunk_size = 1024 * 16  # 16KB chunks
                    download_size = 0
                    
                    with open(download_music_file_path, 'wb') as fp:
                        for chunk in resp.iter_content(chunk_size=chunk_size):
                            if not chunk:
                                continue
                            fp.write(chunk)
                            download_size += len(chunk)
                            
                            if total_size > 0:
                                percent = int(download_size / total_size * 100)
                                detail = f"{download_size/1024/1024:.1f}MB / {total_size/1024/1024:.1f}MB"
                                self.progress_sig.emit(percent, detail)
                            else:
                                detail = f"{download_size/1024/1024:.1f}MB / Unknown"
                                self.progress_sig.emit(0, detail)
                    
                    log_info(f'DownloadWorker 下载完成: {download_music_file_path}')
                    self.finished_sig.emit(True, f"Finished downloading {self.song_info['song_name']}", download_music_file_path)
                else:
                    log_error(f'DownloadWorker 下载失败，状态码: {resp.status_code}')
                    self.finished_sig.emit(False, f"Download failed with status code: {resp.status_code}", "")
        except Exception as e:
            log_exception(f'DownloadWorker 执行出错: {str(e)}')
            self.finished_sig.emit(False, f"Download error: {str(e)}", "")
