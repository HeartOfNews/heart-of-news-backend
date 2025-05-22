"""
Locust load testing for Heart of News backend API.
"""

import json
import random
import time
from datetime import datetime, timedelta

import jwt
from locust import HttpUser, between, task, tag

# Configuration
# Replace these with actual test values for your environment
API_PREFIX = "/api/v1"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "adminpassword"
USER_EMAIL = "user@example.com"
USER_PASSWORD = "userpassword"
SECRET_KEY = "test-secret-key"  # Use the same secret key as your test environment


class HeartOfNewsUser(HttpUser):
    """
    Simulates user behavior for the Heart of News API.
    """
    wait_time = between(1, 5)  # Wait between 1-5 seconds between tasks
    
    def on_start(self):
        """
        Initialize user session on start.
        """
        self.token = None
        self.sources = []
        self.articles = []
        self.headers = {"Content-Type": "application/json"}
    
    @tag("health")
    @task(10)  # Higher weight for health check
    def check_health(self):
        """
        Check API health endpoint.
        """
        self.client.get(f"{API_PREFIX}/health")
    
    @tag("auth")
    @task(2)
    def login(self):
        """
        Log in to the API.
        """
        credentials = {
            "email": USER_EMAIL,
            "password": USER_PASSWORD
        }
        response = self.client.post(
            f"{API_PREFIX}/auth/login",
            json=credentials
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers["Authorization"] = f"Bearer {self.token}"
    
    @tag("auth")
    @task(1)
    def refresh_token(self):
        """
        Refresh authentication token.
        """
        if not self.token:
            self.login()
            return
            
        response = self.client.post(
            f"{API_PREFIX}/auth/refresh",
            headers=self.headers
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers["Authorization"] = f"Bearer {self.token}"
    
    @tag("sources")
    @task(5)
    def get_sources(self):
        """
        Get list of news sources.
        """
        response = self.client.get(
            f"{API_PREFIX}/sources/",
            headers=self.headers
        )
        if response.status_code == 200:
            data = response.json()
            if data and "items" in data and data["items"]:
                self.sources = [source["id"] for source in data["items"]]
    
    @tag("sources")
    @task(2)
    def get_source_details(self):
        """
        Get details for a specific source.
        """
        if not self.sources:
            self.get_sources()
            return
            
        source_id = random.choice(self.sources) if self.sources else 1
        self.client.get(
            f"{API_PREFIX}/sources/{source_id}",
            headers=self.headers
        )
    
    @tag("articles")
    @task(8)
    def get_articles(self):
        """
        Get list of articles with random filters.
        """
        # Add random filters sometimes
        params = {}
        if random.random() > 0.7 and self.sources:
            params["source_id"] = random.choice(self.sources)
        
        if random.random() > 0.8:
            # Add date filter for last week
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            params["date_from"] = start_date.strftime("%Y-%m-%d")
            params["date_to"] = end_date.strftime("%Y-%m-%d")
        
        # Add pagination sometimes
        if random.random() > 0.6:
            params["skip"] = random.randint(0, 50)
            params["limit"] = random.randint(10, 50)
            
        response = self.client.get(
            f"{API_PREFIX}/articles/",
            params=params,
            headers=self.headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data and "items" in data and data["items"]:
                self.articles = [article["id"] for article in data["items"]]
    
    @tag("articles")
    @task(4)
    def get_article_details(self):
        """
        Get details for a specific article.
        """
        if not self.articles:
            self.get_articles()
            return
            
        article_id = random.choice(self.articles) if self.articles else 1
        self.client.get(
            f"{API_PREFIX}/articles/{article_id}",
            headers=self.headers
        )
    
    @tag("articles")
    @task(2)
    def search_articles(self):
        """
        Search articles with random search terms.
        """
        search_terms = ["news", "politics", "economy", "technology", "science", "health", "sports"]
        term = random.choice(search_terms)
        
        self.client.get(
            f"{API_PREFIX}/articles/search",
            params={"q": term},
            headers=self.headers
        )
    
    @tag("tasks")
    @task(1)
    def get_tasks(self):
        """
        Get background tasks status.
        """
        if not self.token:
            self.login()
            return
            
        self.client.get(
            f"{API_PREFIX}/tasks/",
            headers=self.headers
        )


class HeartOfNewsAdminUser(HttpUser):
    """
    Simulates admin user behavior for the Heart of News API.
    """
    wait_time = between(3, 8)  # Wait between 3-8 seconds between tasks
    
    def on_start(self):
        """
        Initialize admin session on start.
        """
        self.token = None
        self.sources = []
        self.articles = []
        self.headers = {"Content-Type": "application/json"}
        self.login()
    
    def login(self):
        """
        Log in as an admin user.
        """
        credentials = {
            "email": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        }
        response = self.client.post(
            f"{API_PREFIX}/auth/login",
            json=credentials
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers["Authorization"] = f"Bearer {self.token}"
        else:
            # Fallback to creating a mock token with admin role for testing
            payload = {
                "sub": "admin-test",
                "email": ADMIN_EMAIL,
                "role": "admin",
                "exp": datetime.utcnow() + timedelta(hours=1)
            }
            self.token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            self.headers["Authorization"] = f"Bearer {self.token}"
    
    @tag("admin", "sources")
    @task(2)
    def create_source(self):
        """
        Create a new news source.
        """
        if not self.token:
            self.login()
            return
            
        source_data = {
            "name": f"Test Source {int(time.time())}",
            "url": f"https://test-{int(time.time())}.example.com",
            "rss_feed": f"https://test-{int(time.time())}.example.com/feed",
            "is_active": True,
            "reliability_score": random.uniform(0, 1.0),
            "bias_score": random.uniform(-1.0, 1.0)
        }
        
        self.client.post(
            f"{API_PREFIX}/sources/",
            json=source_data,
            headers=self.headers
        )
    
    @tag("admin", "sources")
    @task(1)
    def update_source(self):
        """
        Update an existing source.
        """
        if not self.token:
            self.login()
            return
            
        if not self.sources:
            # Get sources first
            response = self.client.get(
                f"{API_PREFIX}/sources/",
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                if data and "items" in data and data["items"]:
                    self.sources = [source["id"] for source in data["items"]]
        
        if not self.sources:
            return
            
        source_id = random.choice(self.sources)
        update_data = {
            "is_active": random.choice([True, False]),
            "reliability_score": random.uniform(0, 1.0),
            "bias_score": random.uniform(-1.0, 1.0)
        }
        
        self.client.patch(
            f"{API_PREFIX}/sources/{source_id}",
            json=update_data,
            headers=self.headers
        )
    
    @tag("admin", "tasks")
    @task(3)
    def trigger_scraper(self):
        """
        Trigger scraping tasks.
        """
        if not self.token:
            self.login()
            return
            
        task_data = {
            "task_type": "scrape",
            "source_id": None  # Scrape all sources
        }
        
        self.client.post(
            f"{API_PREFIX}/tasks/",
            json=task_data,
            headers=self.headers
        )
    
    @tag("admin", "articles")
    @task(1)
    def delete_article(self):
        """
        Delete an article (simulated, not actually deleting).
        """
        if not self.token:
            self.login()
            return
            
        if not self.articles:
            # Get articles first
            response = self.client.get(
                f"{API_PREFIX}/articles/",
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                if data and "items" in data and data["items"]:
                    self.articles = [article["id"] for article in data["items"]]
        
        if not self.articles:
            return
            
        article_id = random.choice(self.articles)
        
        # Just simulate the request without actually deleting
        # Comment out in a real test to actually delete
        # self.client.delete(
        #     f"{API_PREFIX}/articles/{article_id}",
        #     headers=self.headers
        # )
        
        # Instead just get the article details again
        self.client.get(
            f"{API_PREFIX}/articles/{article_id}",
            headers=self.headers
        )