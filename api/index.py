from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# 添加项目路径到Python路径
sys.path.append(os.path.dirname(__file__))

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
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
        
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode())
        return

# Vercel需要这个函数来处理请求
def main(request):
    # 为了兼容性，保留这个函数
    path = request.get('path', '/')
    
    if path == '/api/health':
        response = {"status": "healthy", "message": "服务运行正常"}
        status_code = 200
    elif path.startswith('/api/search'):
        query_string = request.get('queryStringParameters', {}) or {}
        q = query_string.get('q', '')
        
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
        status_code = 200
    else:
        response = {"message": "论文搜索引擎API", "status": "running"}
        status_code = 200
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response, ensure_ascii=False)
    }