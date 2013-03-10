# -*- coding: utf-8 -*-
import mock

__all__ = ['mock_smtp_start', 'mock_ftp_start']


def mock_smtp_start():
    mock_smtp = mock.Mock()
    mock.patch('smtplib.SMTP', return_value=mock_smtp).start()
    return mock_smtp


def mock_ftp_start():
    mock_ftp = mock.Mock()
    mock.patch('ftplib.FTP', return_value=mock_ftp).start()
    return mock_ftp
