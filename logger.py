'''
Function:
    Logging module for MusicdlGUI
Author:
    Zhenchao Jin
WeChat Official Account (微信公众号):
    Charles的皮卡丘
'''
import os
import sys
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler


# 全局 logger 实例
_logger = None
_log_file_path = None


def get_log_directory():
    """
    获取日志目录路径
    
    Returns:
        str: 日志目录的绝对路径
    """
    # 使用应用程序所在目录下的 logs 文件夹
    if getattr(sys, 'frozen', False):
        # 打包后的可执行文件
        app_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境
        app_dir = os.path.dirname(os.path.abspath(__file__))
    
    log_dir = os.path.join(app_dir, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir


def get_log_file_path():
    """
    获取当前日志文件路径
    
    Returns:
        str: 日志文件路径，如果日志未初始化则返回 None
    """
    return _log_file_path


def setup_logger(log_level=logging.INFO, log_to_console=False, max_bytes=5*1024*1024, backup_count=5):
    """
    初始化并配置日志记录器
    
    Args:
        log_level: 日志级别，默认 INFO
        log_to_console: 是否同时输出到控制台，默认 False
        max_bytes: 单个日志文件最大大小，默认 5MB
        backup_count: 保留的日志文件数量，默认 5
    
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    global _logger, _log_file_path
    
    if _logger is not None:
        return _logger
    
    # 创建 logger
    _logger = logging.getLogger('MusicdlGUI')
    _logger.setLevel(log_level)
    
    # 清除已有的处理器
    _logger.handlers.clear()
    
    # 日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 文件处理器 - 按日期命名，带轮转
    log_dir = get_log_directory()
    date_str = datetime.now().strftime('%Y-%m-%d')
    _log_file_path = os.path.join(log_dir, f'musicdlgui_{date_str}.log')
    
    file_handler = RotatingFileHandler(
        _log_file_path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)
    
    # 控制台处理器（可选）
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        _logger.addHandler(console_handler)
    
    return _logger


def get_logger():
    """
    获取日志记录器实例
    
    Returns:
        logging.Logger: 日志记录器，如果未初始化则自动初始化
    """
    global _logger
    if _logger is None:
        _logger = setup_logger()
    return _logger


# 便捷日志函数
def log_info(message):
    """记录 INFO 级别日志"""
    get_logger().info(message)


def log_debug(message):
    """记录 DEBUG 级别日志"""
    get_logger().debug(message)


def log_warning(message):
    """记录 WARNING 级别日志"""
    get_logger().warning(message)


def log_error(message):
    """记录 ERROR 级别日志"""
    get_logger().error(message)


def log_exception(message):
    """记录异常信息，包含堆栈跟踪"""
    get_logger().exception(message)


# 特定操作的日志函数
def log_app_start():
    """记录应用启动"""
    log_info('=' * 60)
    log_info('MusicdlGUI 应用启动')
    log_info(f'日志文件: {get_log_file_path()}')
    log_info('=' * 60)


def log_app_exit():
    """记录应用退出"""
    log_info('MusicdlGUI 应用退出')
    log_info('=' * 60)


def log_search_start(keyword, sources):
    """
    记录搜索开始
    
    Args:
        keyword: 搜索关键词
        sources: 搜索源列表
    """
    sources_str = ', '.join(sources)
    log_info(f'开始搜索 - 关键词: "{keyword}", 音乐源: [{sources_str}]')


def log_search_result(source, count):
    """
    记录单个源的搜索结果
    
    Args:
        source: 音乐源名称
        count: 结果数量
    """
    log_info(f'搜索完成 - {source}: 找到 {count} 条结果')


def log_search_error(source, error):
    """
    记录搜索错误
    
    Args:
        source: 音乐源名称
        error: 错误信息
    """
    log_error(f'搜索失败 - {source}: {error}')


def log_search_complete(total_results):
    """
    记录搜索全部完成
    
    Args:
        total_results: 总结果数
    """
    log_info(f'搜索全部完成 - 共找到 {total_results} 条结果')


def log_download_start(song_name, singer, source):
    """
    记录下载开始
    
    Args:
        song_name: 歌曲名
        singer: 歌手
        source: 音乐源
    """
    log_info(f'开始下载 - "{song_name}" - {singer} [{source}]')


def log_download_progress(song_name, percent, detail):
    """
    记录下载进度（只在关键节点记录）
    
    Args:
        song_name: 歌曲名
        percent: 进度百分比
        detail: 详情
    """
    if percent in [25, 50, 75, 100]:
        log_debug(f'下载进度 - "{song_name}": {percent}% ({detail})')


def log_download_success(song_name, file_path):
    """
    记录下载成功
    
    Args:
        song_name: 歌曲名
        file_path: 保存路径
    """
    log_info(f'下载成功 - "{song_name}" -> {file_path}')


def log_download_error(song_name, error):
    """
    记录下载失败
    
    Args:
        song_name: 歌曲名
        error: 错误信息
    """
    log_error(f'下载失败 - "{song_name}": {error}')


def log_settings_saved():
    """记录设置保存"""
    log_info('用户设置已保存')


def log_theme_changed(is_dark):
    """
    记录主题切换
    
    Args:
        is_dark: 是否深色主题
    """
    theme = '深色模式' if is_dark else '浅色模式'
    log_info(f'主题切换 - {theme}')
