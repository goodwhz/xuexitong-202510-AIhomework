from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if self.path == '/api/health':
            response = {"status": "healthy", "message": "服务运行正常"}
        elif self.path.startswith('/api/search'):
            # 解析查询参数
            from urllib.parse import urlparse, parse_qs
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            q = query_params.get('q', [''])[0]
            
            response = {
                "query": q,
                "results": [
                    {
                        "id": "2401.12345",
                        "title": "深度学习在自然语言处理中的应用",
                        "authors": ["张三", "李四"],
                        "abstract": "本文探讨了深度学习技术在自然语言处理领域的应用...",
                        "published": "2024-01-15",
                        "categories": ["cs.CL", "cs.AI"]
                    }
                ],
                "total": 1
            }
        else:
            response = {"message": "论文搜索引擎API", "status": "running"}
        
        self.wfile.write(json.dumps(response).encode())
        return