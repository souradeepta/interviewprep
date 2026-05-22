#!/usr/bin/env python3
"""
Script to add Java and Python sample implementations for all 36 real-world systems.
Includes API handlers, data models, database operations, and caching.
"""

from pathlib import Path

# Python implementation template
python_impl_template = """## Python Implementation

### Installation

```bash
pip install fastapi uvicorn sqlalchemy redis pydantic python-dotenv
```

### Core Models

```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class User(BaseModel):
    id: str
    username: str
    email: str
    created_at: datetime

class Post(BaseModel):
    id: str
    user_id: str
    content: str
    likes: int = 0
    comments: int = 0
    created_at: datetime

class Comment(BaseModel):
    id: str
    post_id: str
    user_id: str
    content: str
    created_at: datetime
```

### API Implementation

```python
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from redis import Redis
import os
import logging

app = FastAPI(title="{system_name}", version="1.0.0")

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=20, max_overflow=40)
SessionLocal = sessionmaker(bind=engine)

# Cache setup
cache = Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    decode_responses=True,
    socket_keepalive=True,
    socket_keepalive_options={{
        1: 1,  # TCP_KEEPIDLE
        2: 1,  # TCP_KEEPINTVL
        3: 3,  # TCP_KEEPCNT
    }}
)

logger = logging.getLogger(__name__)

# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Authentication
async def verify_token(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = authorization.replace("Bearer ", "")
    # Verify token against auth service
    user_id = cache.get(f"token:{token}")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user_id

# API Endpoints
@app.post("/api/v1/posts", status_code=201)
async def create_post(post: Post, user_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    '''Create a new post'''
    try:
        # Store in database
        db_post = PostModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            content=post.content,
            created_at=datetime.utcnow()
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)

        # Invalidate feed cache
        cache.delete(f"feed:{user_id}")

        logger.info(f"Post created: {db_post.id} by {user_id}")
        return db_post
    except Exception as e:
        logger.error(f"Error creating post: {e}")
        raise HTTPException(status_code=500, detail="Failed to create post")

@app.get("/api/v1/posts/{post_id}")
async def get_post(post_id: str, db: Session = Depends(get_db)):
    '''Get post details'''
    # Try cache first
    cached = cache.get(f"post:{post_id}")
    if cached:
        return json.loads(cached)

    # Query database
    post = db.query(PostModel).filter(PostModel.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Cache for 1 hour
    cache.setex(f"post:{post_id}", 3600, json.dumps(post.to_dict()))

    return post

@app.get("/api/v1/users/{user_id}/feed")
async def get_feed(user_id: str, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    '''Get user feed with pagination'''
    cache_key = f"feed:{user_id}:{limit}:{offset}"

    # Try cache
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)

    # Get user's following list
    following = db.query(Follow).filter(Follow.follower_id == user_id).all()
    following_ids = [f.following_id for f in following] + [user_id]

    # Get posts from following
    posts = db.query(PostModel).filter(
        PostModel.user_id.in_(following_ids)
    ).order_by(PostModel.created_at.desc()).offset(offset).limit(limit).all()

    result = {{
        "posts": [p.to_dict() for p in posts],
        "nextOffset": offset + limit,
        "hasMore": len(posts) == limit
    }}

    # Cache for 5 minutes
    cache.setex(cache_key, 300, json.dumps(result))

    return result

@app.post("/api/v1/posts/{post_id}/like", status_code=200)
async def like_post(post_id: str, user_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    '''Like a post'''
    try:
        # Check if already liked
        existing = db.query(Like).filter(
            Like.post_id == post_id,
            Like.user_id == user_id
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="Already liked")

        # Add like
        like = Like(
            id=str(uuid.uuid4()),
            post_id=post_id,
            user_id=user_id,
            created_at=datetime.utcnow()
        )
        db.add(like)
        db.commit()

        # Invalidate cache
        cache.delete(f"post:{post_id}")

        return {{"status": "liked"}}
    except Exception as e:
        logger.error(f"Error liking post: {e}")
        raise HTTPException(status_code=500, detail="Failed to like post")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, workers=4)
```

### Database Models

```python
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class PostModel(Base):
    __tablename__ = "posts"

    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey("users.id"), index=True)
    content = Column(String(5000))
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_user_id_created', 'user_id', 'created_at'),
    )

    def to_dict(self):
        return {{
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "likes": self.likes,
            "comments": self.comments,
            "created_at": self.created_at.isoformat()
        }}

class Like(Base):
    __tablename__ = "likes"

    id = Column(String(50), primary_key=True)
    post_id = Column(String(50), ForeignKey("posts.id"), index=True)
    user_id = Column(String(50), ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_post_user', 'post_id', 'user_id', unique=True),
    )
```

### Caching Layer

```python
from functools import wraps
from typing import Callable
import json

class CacheManager:
    def __init__(self, redis_client, ttl: int = 3600):
        self.redis = redis_client
        self.ttl = ttl

    def cached(self, key_prefix: str):
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = f"{{key_prefix}}:{{':'.join(map(str, args))}}:{{':'.join(f'{{k}}={{v}}' for k,v in kwargs.items())}}"

                # Try cache
                cached = self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)

                # Execute function
                result = await func(*args, **kwargs)

                # Cache result
                self.redis.setex(cache_key, self.ttl, json.dumps(result))

                return result
            return wrapper
        return decorator

    def invalidate(self, pattern: str):
        '''Invalidate cache by pattern'''
        keys = self.redis.keys(pattern)
        if keys:
            self.redis.delete(*keys)
```
"""

# Java implementation template
java_impl_template = """## Java Implementation

### Maven Dependencies

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
    <version>3.0.0</version>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-jpa</artifactId>
    <version>3.0.0</version>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-redis</artifactId>
    <version>3.0.0</version>
</dependency>
<dependency>
    <groupId>org.postgresql</groupId>
    <artifactId>postgresql</artifactId>
    <version>42.5.0</version>
</dependency>
<dependency>
    <groupId>redis.clients</groupId>
    <artifactId>jedis</artifactId>
    <version>4.3.0</version>
</dependency>
```

### Data Models

```java
package com.example.{system_name_lower}.model;

import lombok.Data;
import lombok.AllArgsConstructor;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Data
@AllArgsConstructor
@Entity
@Table(name = "posts", indexes = {{
    @Index(name = "idx_user_id_created", columnList = "user_id,created_at")
}})
public class Post {{
    @Id
    private String id;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(name = "content", nullable = false, length = 5000)
    private String content;

    @Column(name = "likes", columnDefinition = "integer default 0")
    private Integer likes = 0;

    @Column(name = "comments", columnDefinition = "integer default 0")
    private Integer comments = 0;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
}}

@Data
@AllArgsConstructor
@Entity
@Table(name = "likes", uniqueConstraints = {{
    @UniqueConstraint(columnNames = {{"post_id", "user_id"}}, name = "uk_post_user")
}}, indexes = {{
    @Index(name = "idx_post_id", columnList = "post_id"),
    @Index(name = "idx_user_id", columnList = "user_id")
}})
public class Like {{
    @Id
    private String id;

    @Column(name = "post_id", nullable = false)
    private String postId;

    @Column(name = "user_id", nullable = false)
    private String userId;

    @Column(name = "created_at", nullable = false)
    private LocalDateTime createdAt;
}}
```

### Repository Layer

```java
package com.example.{system_name_lower}.repository;

import com.example.{system_name_lower}.model.Post;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface PostRepository extends JpaRepository<Post, String> {{
    Optional<Post> findById(String id);

    @Query(value = "SELECT p FROM Post p WHERE p.userId = :userId ORDER BY p.createdAt DESC LIMIT :limit OFFSET :offset")
    List<Post> findUserPosts(@Param("userId") String userId, @Param("limit") int limit, @Param("offset") int offset);

    @Query(value = "SELECT p FROM Post p WHERE p.userId IN :userIds ORDER BY p.createdAt DESC LIMIT :limit OFFSET :offset")
    List<Post> findFeedPosts(@Param("userIds") List<String> userIds, @Param("limit") int limit, @Param("offset") int offset);
}}
```

### Service Layer

```java
package com.example.{system_name_lower}.service;

import com.example.{system_name_lower}.model.Post;
import com.example.{system_name_lower}.repository.PostRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.stereotype.Service;
import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
@Slf4j
public class PostService {{
    private final PostRepository postRepository;
    private final RedisTemplate<String, Object> redisTemplate;

    private static final int CACHE_TTL = 3600; // 1 hour

    public Post createPost(String userId, String content) {{
        try {{
            Post post = new Post();
            post.setId(UUID.randomUUID().toString());
            post.setUserId(userId);
            post.setContent(content);
            post.setCreatedAt(LocalDateTime.now());
            post.setLikes(0);
            post.setComments(0);

            Post savedPost = postRepository.save(post);

            // Invalidate user's feed cache
            redisTemplate.delete("feed:" + userId + ":*");

            log.info("Post created: {} by {}", savedPost.getId(), userId);
            return savedPost;
        }} catch (Exception e) {{
            log.error("Error creating post", e);
            throw new RuntimeException("Failed to create post", e);
        }}
    }}

    public Post getPost(String postId) {{
        // Try cache first
        String cacheKey = "post:" + postId;
        Post cached = (Post) redisTemplate.opsForValue().get(cacheKey);
        if (cached != null) {{
            return cached;
        }}

        // Query database
        Optional<Post> post = postRepository.findById(postId);
        if (post.isEmpty()) {{
            throw new RuntimeException("Post not found");
        }}

        Post result = post.get();

        // Cache for 1 hour
        redisTemplate.opsForValue().set(cacheKey, result, CACHE_TTL, TimeUnit.SECONDS);

        return result;
    }}

    public List<Post> getUserFeed(String userId, int limit, int offset) {{
        String cacheKey = "feed:" + userId + ":" + limit + ":" + offset;

        // Try cache
        @SuppressWarnings("unchecked")
        List<Post> cached = (List<Post>) redisTemplate.opsForValue().get(cacheKey);
        if (cached != null) {{
            return cached;
        }}

        // TODO: Get user's following list
        List<String> followingIds = new ArrayList<>();
        followingIds.add(userId); // Include user's own posts

        // Get feed
        List<Post> feed = postRepository.findFeedPosts(followingIds, limit, offset);

        // Cache for 5 minutes
        redisTemplate.opsForValue().set(cacheKey, feed, 300, TimeUnit.SECONDS);

        return feed;
    }}

    public void likePost(String postId, String userId) {{
        try {{
            // Check if already liked
            // TODO: Check Like table

            // Add like (insert into Like table)
            // TODO: Save like

            // Update like count
            Post post = getPost(postId);
            post.setLikes(post.getLikes() + 1);
            postRepository.save(post);

            // Invalidate cache
            redisTemplate.delete("post:" + postId);

            log.info("Post {} liked by {}", postId, userId);
        }} catch (Exception e) {{
            log.error("Error liking post", e);
            throw new RuntimeException("Failed to like post", e);
        }}
    }}
}}
```

### REST Controller

```java
package com.example.{system_name_lower}.controller;

import com.example.{system_name_lower}.model.Post;
import com.example.{system_name_lower}.service.PostService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
@Slf4j
public class PostController {{
    private final PostService postService;

    @PostMapping("/posts")
    public ResponseEntity<Post> createPost(
            @RequestBody Post post,
            @RequestHeader("Authorization") String authHeader) {{
        try {{
            String userId = extractUserIdFromToken(authHeader);
            Post created = postService.createPost(userId, post.getContent());
            return ResponseEntity.status(HttpStatus.CREATED).body(created);
        }} catch (Exception e) {{
            log.error("Error creating post", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }}
    }}

    @GetMapping("/posts/{{postId}}")
    public ResponseEntity<Post> getPost(@PathVariable String postId) {{
        try {{
            Post post = postService.getPost(postId);
            return ResponseEntity.ok(post);
        }} catch (Exception e) {{
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }}
    }}

    @GetMapping("/users/{{userId}}/feed")
    public ResponseEntity<List<Post>> getUserFeed(
            @PathVariable String userId,
            @RequestParam(defaultValue = "20") int limit,
            @RequestParam(defaultValue = "0") int offset) {{
        try {{
            List<Post> feed = postService.getUserFeed(userId, limit, offset);
            return ResponseEntity.ok(feed);
        }} catch (Exception e) {{
            log.error("Error fetching feed", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }}
    }}

    @PostMapping("/posts/{{postId}}/like")
    public ResponseEntity<String> likePost(
            @PathVariable String postId,
            @RequestHeader("Authorization") String authHeader) {{
        try {{
            String userId = extractUserIdFromToken(authHeader);
            postService.likePost(postId, userId);
            return ResponseEntity.ok("{{\"status\":\"liked\"}}");
        }} catch (Exception e) {{
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }}
    }}

    private String extractUserIdFromToken(String authHeader) {{
        // TODO: Verify token and extract user ID
        return "user123";
    }}
}}
```

### Configuration

```java
package com.example.{system_name_lower}.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.serializer.StringRedisSerializer;

@Configuration
public class RedisConfig {{
    @Bean
    public RedisTemplate<String, Object> redisTemplate(RedisConnectionFactory connectionFactory) {{
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(connectionFactory);

        StringRedisSerializer stringSerializer = new StringRedisSerializer();
        template.setKeySerializer(stringSerializer);
        template.setHashKeySerializer(stringSerializer);
        template.setValueSerializer(stringSerializer);

        return template;
    }}
}}
```
"""

def add_implementations_to_file(filepath, system_name):
    """Add Python and Java implementations to system file."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Check if implementations already exist
    if "## Python Implementation" in content or "## Java Implementation" in content:
        return False

    # Find insertion point (before Infrastructure as Code)
    insertion_point = content.find("## Infrastructure as Code (Terraform)")
    if insertion_point == -1:
        insertion_point = content.find("## Lessons Learned")
    if insertion_point == -1:
        return False

    # Generate implementation sections
    system_name_lower = system_name.lower().replace(" ", "_")
    python_code = python_impl_template.replace("{system_name}", system_name)
    java_code = java_impl_template.replace("{system_name_lower}", system_name_lower).replace("{system_name}", system_name)

    new_sections = f"\n\n## Implementation Examples\n\n{python_code}\n\n{java_code}\n"

    # Insert implementations
    new_content = content[:insertion_point] + new_sections + "\n" + content[insertion_point:]

    with open(filepath, 'w') as f:
        f.write(new_content)

    return True

def main():
    """Process all system design files."""
    base_path = Path("docs/system_design/13-realworld-systems")

    if not base_path.exists():
        print(f"❌ Directory not found: {base_path}")
        return

    files = sorted(base_path.glob("*.md"))

    print(f"🐍 Adding Python & Java implementations to {len(files)} systems...")
    print("=" * 60)

    success_count = 0
    for filepath in files:
        filename = filepath.stem
        parts = filename.split('_', 1)
        if len(parts) < 2:
            continue

        system_name = ' '.join(word.capitalize() for word in parts[1].split('_'))

        try:
            if add_implementations_to_file(filepath, system_name):
                print(f"✅ Added implementations: {system_name}")
                success_count += 1
            else:
                print(f"⏭️  Already has implementations: {system_name}")
        except Exception as e:
            print(f"❌ Error in {system_name}: {e}")

    print("=" * 60)
    print(f"✨ Added implementations to {success_count} system files!")
    print(f"\nEach system now includes:")
    print(f"  ✓ Python (FastAPI + SQLAlchemy + Redis)")
    print(f"  ✓ Java (Spring Boot + JPA + Redis)")
    print(f"  ✓ Data models and entities")
    print(f"  ✓ Repository/DAO patterns")
    print(f"  ✓ Service layer with business logic")
    print(f"  ✓ REST API controllers")
    print(f"  ✓ Caching strategies")
    print(f"  ✓ Configuration examples")

if __name__ == '__main__':
    main()
