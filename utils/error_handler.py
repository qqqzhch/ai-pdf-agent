"""错误处理"""

import click


class AI_PDF_Error(Exception):
    """基础错误类"""
    exit_code = 1


class ParamError(AI_PDF_Error):
    """参数错误"""
    exit_code = 1


class FileNotFoundError(AI_PDF_Error):
    """文件不存在"""
    exit_code = 2


class PDFFormatError(AI_PDF_Error):
    """PDF 格式错误"""
    exit_code = 3


class ProcessError(AI_PDF_Error):
    """处理失败"""
    exit_code = 4


class PermissionError(AI_PDF_Error):
    """权限错误"""
    exit_code = 5


class PluginError(AI_PDF_Error):
    """插件错误"""
    exit_code = 6


def handle_errors(f):
    """错误处理装饰器"""
    def wrapper(*args, **kwargs):
        ctx = click.get_current_context()
        try:
            return f(*args, **kwargs)
        except AI_PDF_Error as e:
            if ctx and ctx.obj.get('quiet'):
                raise click.ClickException(str(e))
            else:
                click.echo(f"Error: {e}", err=True)
                raise SystemExit(e.exit_code)
        except Exception as e:
            if ctx and ctx.obj.get('quiet'):
                raise click.ClickException(str(e))
            else:
                click.echo(f"Unexpected error: {e}", err=True)
                raise SystemExit(4)
    return wrapper
