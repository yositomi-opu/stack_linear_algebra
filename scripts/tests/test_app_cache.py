import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location('mcq_server_cache_test', Path(__file__).resolve().parents[2] / 'app/mcq-webapp/server.py')
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class AppCacheTests(unittest.TestCase):
    def test_app_shell_and_assets_revalidate(self):
        for path in ('/', '/index.html', '/app.js?v=old', '/i18n.js?v=old', '/styles.css?v=old'):
            with self.subTest(path=path):
                handler = server.McqRequestHandler.__new__(server.McqRequestHandler)
                handler.path = path
                handler.send_header = Mock()
                with patch.object(server.SimpleHTTPRequestHandler, 'end_headers') as finish:
                    handler.end_headers()
                handler.send_header.assert_called_once_with('Cache-Control', 'no-cache, must-revalidate')
                finish.assert_called_once()

    def test_api_cache_policy_is_not_overridden(self):
        handler = server.McqRequestHandler.__new__(server.McqRequestHandler)
        handler.path = '/api/repository/include?path=001/Sample.txt'
        handler.send_header = Mock()
        with patch.object(server.SimpleHTTPRequestHandler, 'end_headers'):
            handler.end_headers()
        handler.send_header.assert_not_called()
