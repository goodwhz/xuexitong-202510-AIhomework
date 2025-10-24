import json

def handler(request):
    # Vercel Python函数的标准格式
    path = request.get('path', '/')
    
    if path == '/api/health':
        response = {"status": "healthy", "message": "服务运行正常"}
        status_code = 200
    elif path.startswith('/api/search'):
        # 解析查询参数
        query_string = request.get('queryStringParameters', {})
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
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(response)
    }