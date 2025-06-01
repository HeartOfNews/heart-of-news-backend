#!/usr/bin/env python3
"""
Heart of News - Simple Demo API
Using only built-in Python modules for demonstration
"""

import json
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
import os

PORT = 8002

# Sample data
SAMPLE_ARTICLES = [
    {
        "id": "1",
        "title": "European Council Approves New Climate Initiatives",
        "content": "The European Council has unanimously approved a comprehensive package of climate initiatives aimed at reducing carbon emissions by 55% by 2030. The package includes new renewable energy targets, carbon pricing mechanisms, and substantial funding for green technology development across member states.",
        "summary": "EU leaders approve ambitious climate package with 55% emission reduction target by 2030, including renewable energy goals and green tech funding.",
        "source": "BBC News",
        "author": "Sarah Johnson",
        "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        "url": "https://bbc.com/news/climate-2024",
        "image_url": "https://images.unsplash.com/photo-1569163139394-de4e4f43e4e3?w=800",
        "verified": True,
        "bias_score": 0.05,
        "reliability_score": 0.95
    },
    {
        "id": "2",
        "title": "Tech Giants Announce AI Safety Partnership",
        "content": "Major technology companies including Google, Microsoft, and OpenAI have announced a groundbreaking partnership focused on AI safety and responsible development. The initiative will establish common standards for AI testing, deployment, and monitoring to ensure beneficial outcomes for society.",
        "summary": "Google, Microsoft, and OpenAI form partnership for AI safety standards and responsible development practices.",
        "source": "Reuters",
        "author": "Michael Chen",
        "published_at": (datetime.now() - timedelta(hours=4)).isoformat(),
        "url": "https://reuters.com/tech/ai-safety-2024",
        "image_url": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800",
        "verified": True,
        "bias_score": 0.0,
        "reliability_score": 0.97
    },
    {
        "id": "3",
        "title": "Global Health Organization Reports Vaccine Progress",
        "content": "The World Health Organization announced significant progress in global vaccination efforts, with over 70% of the world's population now having access to essential vaccines. The organization highlighted improved distribution networks and international cooperation as key factors in this achievement.",
        "summary": "WHO reports 70% global vaccine accessibility through improved distribution and international cooperation.",
        "source": "Associated Press",
        "author": "Dr. Emma Rodriguez",
        "published_at": (datetime.now() - timedelta(hours=6)).isoformat(),
        "url": "https://apnews.com/health/vaccines-2024",
        "image_url": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800",
        "verified": True,
        "bias_score": 0.02,
        "reliability_score": 0.98
    },
    {
        "id": "4",
        "title": "International Space Station Celebrates 25 Years",
        "content": "The International Space Station marks its 25th anniversary of continuous human presence in space. During this quarter-century, the ISS has hosted over 260 astronauts from 19 countries and has been the site of thousands of scientific experiments that have advanced our understanding of space and Earth.",
        "summary": "ISS celebrates 25 years of continuous operation with 260+ astronauts and thousands of scientific experiments.",
        "source": "NASA News",
        "author": "Commander Lisa Park",
        "published_at": (datetime.now() - timedelta(hours=8)).isoformat(),
        "url": "https://nasa.gov/iss/anniversary-2024",
        "image_url": "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=800",
        "verified": True,
        "bias_score": 0.0,
        "reliability_score": 0.99
    },
    {
        "id": "5",
        "title": "Renewable Energy Surpasses Coal in Power Generation",
        "content": "For the first time in modern history, renewable energy sources have generated more electricity globally than coal-fired power plants. Solar and wind power led the growth, with hydroelectric and geothermal contributing significantly to this historic milestone in clean energy adoption.",
        "summary": "Renewable energy overtakes coal in global electricity generation, led by solar and wind power growth.",
        "source": "Financial Times",
        "author": "David Kumar",
        "published_at": (datetime.now() - timedelta(hours=10)).isoformat(),
        "url": "https://ft.com/energy/renewables-2024",
        "image_url": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=800",
        "verified": True,
        "bias_score": 0.0,
        "reliability_score": 0.94
    }
]

SAMPLE_SOURCES = [
    {"id": 1, "name": "BBC News", "url": "https://bbc.com", "reliability_score": 0.95, "verified": True},
    {"id": 2, "name": "Reuters", "url": "https://reuters.com", "reliability_score": 0.97, "verified": True},
    {"id": 3, "name": "Associated Press", "url": "https://apnews.com", "reliability_score": 0.98, "verified": True},
    {"id": 4, "name": "NASA News", "url": "https://nasa.gov", "reliability_score": 0.99, "verified": True},
    {"id": 5, "name": "Financial Times", "url": "https://ft.com", "reliability_score": 0.94, "verified": True}
]

class HeartOfNewsHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        # Add CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_data = {}
        
        # API routes
        if path == '/':
            response_data = {
                "message": "Welcome to Heart of News API (Demo)",
                "version": "0.1.0",
                "docs": "API endpoints: /api/v1/articles, /api/v1/sources, /api/v1/stats",
                "demo_note": "This is a simplified demo version"
            }
        elif path == '/health':
            response_data = {"status": "healthy", "timestamp": datetime.now().isoformat()}
            
        elif path == '/api/v1/articles':
            # Get query parameters
            page = int(query_params.get('page', [1])[0])
            size = int(query_params.get('size', [10])[0])
            skip = (page - 1) * size
            
            # Return paginated articles in expected format
            articles = SAMPLE_ARTICLES[skip:skip+size]
            # Add source object to each article
            for article in articles:
                article['source'] = {
                    "id": "1",
                    "name": article['source'],
                    "url": "https://example.com",
                    "is_active": True,
                    "reliability_score": article['reliability_score'],
                    "bias_score": 0.1
                }
                article['source_id'] = "1"
                article['categories'] = ["News", "Politics"]
                article['bias_score'] = {
                    "political_bias": 0.0,
                    "emotional_tone": 0.1,
                    "propaganda_techniques": [],
                    "overall_score": 0.05
                }
            
            response_data = {
                "items": articles,
                "total": len(SAMPLE_ARTICLES),
                "page": page,
                "size": size,
                "pages": (len(SAMPLE_ARTICLES) + size - 1) // size
            }
            
        elif path.startswith('/api/v1/articles/'):
            # Get specific article
            try:
                article_id = int(path.split('/')[-1])
                article = next((a for a in SAMPLE_ARTICLES if a['id'] == article_id), None)
                if article:
                    response_data = article
                else:
                    self.send_error(404, "Article not found")
                    return
            except ValueError:
                self.send_error(400, "Invalid article ID")
                return
                
        elif path == '/api/v1/sources':
            response_data = {
                "items": SAMPLE_SOURCES,
                "total": len(SAMPLE_SOURCES),
                "page": 1,
                "size": 10,
                "pages": 1
            }
            
        elif path == '/api/v1/stats':
            response_data = {
                "total_articles": len(SAMPLE_ARTICLES),
                "total_sources": len(SAMPLE_SOURCES),
                "average_reliability": 0.966,
                "average_bias_score": 0.014,
                "system_status": "operational",
                "last_updated": datetime.now().isoformat()
            }
            
        elif path == '/api/v1/admin/dashboard':
            response_data = {
                "source_stats": [
                    {"source": "Associated Press", "count": 1, "avg_reliability": 0.98},
                    {"source": "NASA News", "count": 1, "avg_reliability": 0.99},
                    {"source": "Reuters", "count": 1, "avg_reliability": 0.97},
                    {"source": "BBC News", "count": 1, "avg_reliability": 0.95},
                    {"source": "Financial Times", "count": 1, "avg_reliability": 0.94}
                ],
                "recent_articles": [
                    {"title": article["title"][:50] + "...", "source": article["source"], 
                     "published_at": article["published_at"], "bias_score": article["bias_score"],
                     "reliability_score": article["reliability_score"]} 
                    for article in SAMPLE_ARTICLES[:5]
                ],
                "timestamp": datetime.now().isoformat()
            }
        else:
            self.send_error(404, "Endpoint not found")
            return
        
        # Send JSON response
        self.wfile.write(json.dumps(response_data, indent=2).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

if __name__ == "__main__":
    print(f"🚀 Heart of News Demo API starting on port {PORT}")
    print(f"📊 API Base: http://localhost:{PORT}")
    print(f"📝 Articles: http://localhost:{PORT}/api/v1/articles")
    print(f"🔧 Admin: http://localhost:{PORT}/api/v1/admin/dashboard")
    print(f"📈 Stats: http://localhost:{PORT}/api/v1/stats")
    print("=" * 60)
    
    with socketserver.TCPServer(("", PORT), HeartOfNewsHandler) as httpd:
        print(f"✅ Server running at http://localhost:{PORT}/")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")