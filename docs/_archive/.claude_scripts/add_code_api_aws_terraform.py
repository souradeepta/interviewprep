#!/usr/bin/env python3
"""
Script to add sample code, API specifications, AWS diagrams, and Terraform to systems.
"""

from pathlib import Path

# System-specific code and API examples
system_code = {
    "Facebook Social Network": {
        "api_endpoints": [
            "POST /api/v1/posts - Create a new post",
            "GET /api/v1/posts/{postId} - Get post details",
            "GET /api/v1/users/{userId}/feed - Get user feed (paginated)",
            "POST /api/v1/posts/{postId}/like - Like a post",
            "POST /api/v1/posts/{postId}/comments - Add comment",
            "GET /api/v1/users/{userId}/friends - Get friends list"
        ],
        "sample_code": """// Create Post API
POST /api/v1/posts
Content-Type: application/json

{
  "content": "Hello world!",
  "media": ["photo_url1", "photo_url2"],
  "visibility": "public"
}

Response (201 Created):
{
  "postId": "12345",
  "userId": "user123",
  "content": "Hello world!",
  "createdAt": "2026-05-15T10:30:00Z",
  "likes": 0,
  "comments": 0
}

// Get User Feed
GET /api/v1/users/user123/feed?limit=20&offset=0
Authorization: Bearer <token>

Response (200 OK):
{
  "posts": [
    {
      "postId": "12345",
      "userId": "user456",
      "content": "...",
      "likes": 100,
      "comments": 5,
      "createdAt": "2026-05-15T10:30:00Z"
    }
  ],
  "nextOffset": 20,
  "hasMore": true
}""",
        "rate_limits": "1000 requests/minute per user, 10K posts/day per user",
        "auth": "OAuth2 with Bearer tokens"
    },
    "WhatsApp Messaging": {
        "api_endpoints": [
            "POST /api/v1/messages/send - Send message",
            "GET /api/v1/messages/{chatId} - Get messages",
            "POST /api/v1/messages/{messageId}/read - Mark read",
            "POST /api/v1/contacts/sync - Sync contacts",
            "POST /api/v1/groups/create - Create group",
            "GET /api/v1/users/{userId}/status - Get user status"
        ],
        "sample_code": """// Send Message
POST /api/v1/messages/send
Content-Type: application/json
Authorization: Bearer <token>

{
  "to": "user123",
  "content": "Hello!",
  "type": "text",
  "timestamp": 1684144200000
}

Response (201 Created):
{
  "messageId": "msg_12345",
  "status": "sent",
  "timestamp": 1684144200000,
  "deliveredAt": null
}

// Get Messages
GET /api/v1/messages/chat_12345?limit=50&before=1684144200000

Response (200 OK):
{
  "messages": [
    {
      "messageId": "msg_12345",
      "from": "user456",
      "content": "Hi!",
      "status": "delivered",
      "timestamp": 1684144180000
    }
  ],
  "hasMore": true
}""",
        "rate_limits": "10000 messages/day per user",
        "auth": "Phone number verification + Bearer token"
    },
    "Slack Team Communication": {
        "api_endpoints": [
            "POST /api/v1/messages - Post message",
            "GET /api/v1/conversations/{channelId}/messages - Get messages",
            "POST /api/v1/reactions/add - Add reaction",
            "POST /api/v1/conversations/create - Create channel",
            "POST /api/v1/conversations/members/add - Add member",
            "GET /api/v1/users/list - List users"
        ],
        "sample_code": """// Post Message
POST /api/v1/messages
Content-Type: application/json
Authorization: Bearer xoxb-token

{
  "channel": "C1234567890",
  "text": "Hello team!",
  "thread_ts": "1234567890.123456"
}

Response (200 OK):
{
  "ok": true,
  "channel": "C1234567890",
  "ts": "1234567890.123456",
  "message": {
    "type": "message",
    "user": "U12345678",
    "text": "Hello team!",
    "ts": "1234567890.123456"
  }
}

// Get Channel Messages
GET /api/v1/conversations/C1234567890/messages?limit=100&oldest=1234567890

Response (200 OK):
{
  "messages": [
    {
      "type": "message",
      "user": "U12345678",
      "text": "Hello team!",
      "ts": "1234567890.123456"
    }
  ],
  "has_more": true
}""",
        "rate_limits": "50 requests/second per workspace",
        "auth": "Bearer token (xoxb for bots, xoxp for users)"
    },
    "Twitter Feed": {
        "api_endpoints": [
            "POST /2/tweets - Create tweet",
            "GET /2/tweets/{id} - Get tweet",
            "GET /2/tweets/search/recent - Search tweets",
            "POST /2/tweets/{id}/liking_by - Like tweet",
            "GET /2/users/{id}/following - Get following",
            "POST /2/users/{id}/following - Follow user"
        ],
        "sample_code": """// Create Tweet
POST /2/tweets
Content-Type: application/json
Authorization: Bearer <token>

{
  "text": "Hello Twitter!",
  "reply": {
    "in_reply_to_tweet_id": "1234567890"
  }
}

Response (201 Created):
{
  "data": {
    "id": "1234567890",
    "text": "Hello Twitter!"
  }
}

// Search Recent Tweets
GET /2/tweets/search/recent?query=python&max_results=10

Response (200 OK):
{
  "data": [
    {
      "id": "1234567890",
      "text": "Learning Python",
      "public_metrics": {
        "retweet_count": 5,
        "reply_count": 2,
        "like_count": 10,
        "quote_count": 1
      }
    }
  ],
  "meta": {
    "result_count": 10,
    "newest_id": "1234567890"
  }
}""",
        "rate_limits": "450 requests/15min for endpoints, 300 for tweets/15min",
        "auth": "OAuth2 or Bearer token"
    },
    "Discord Gaming Chat": {
        "api_endpoints": [
            "POST /api/v10/channels/{channelId}/messages - Send message",
            "GET /api/v10/channels/{channelId}/messages - Get messages",
            "POST /api/v10/channels/{channelId}/voice - Join voice",
            "POST /api/v10/guilds/{guildId} - Create guild",
            "GET /api/v10/users/{userId} - Get user",
            "POST /api/v10/interactions/{interactionId}/callback - Respond to interaction"
        ],
        "sample_code": """// Send Message
POST /api/v10/channels/123456789/messages
Content-Type: application/json
Authorization: Bot BOT_TOKEN

{
  "content": "Hello!",
  "tts": false,
  "embeds": [
    {
      "title": "My Embed",
      "description": "This is an embed"
    }
  ]
}

Response (200 OK):
{
  "id": "123456789",
  "channel_id": "123456789",
  "author": {
    "id": "123456789",
    "username": "bot_name"
  },
  "content": "Hello!",
  "timestamp": "2026-05-15T10:30:00Z"
}

// Get Channel Messages
GET /api/v10/channels/123456789/messages?limit=50

Response (200 OK):
[
  {
    "id": "123456789",
    "channel_id": "123456789",
    "author": {"id": "...", "username": "..."},
    "content": "Hello!",
    "timestamp": "2026-05-15T10:30:00Z"
  }
]""",
        "rate_limits": "50 requests/second per bot token",
        "auth": "Bot token in Authorization header"
    },
    "YouTube Video Platform": {
        "api_endpoints": [
            "POST /youtube/v3/videos - Upload video",
            "GET /youtube/v3/videos - Get videos",
            "GET /youtube/v3/search - Search videos",
            "POST /youtube/v3/subscriptions - Subscribe to channel",
            "GET /youtube/v3/channels - Get channel info",
            "POST /youtube/v3/playlists - Create playlist"
        ],
        "sample_code": """// Search Videos
GET /youtube/v3/search?q=python&maxResults=25&part=snippet

Response (200 OK):
{
  "items": [
    {
      "kind": "youtube#searchResult",
      "etag": "...",
      "id": {
        "kind": "youtube#video",
        "videoId": "dQw4w9WgXcQ"
      },
      "snippet": {
        "publishedAt": "2026-05-15T10:30:00Z",
        "title": "Learn Python",
        "description": "Complete Python tutorial",
        "thumbnails": {
          "default": {
            "url": "https://..."
          }
        },
        "channelTitle": "Python Academy"
      }
    }
  ],
  "pageInfo": {
    "totalResults": 1000000,
    "resultsPerPage": 25
  }
}

// Get Video Details
GET /youtube/v3/videos?id=dQw4w9WgXcQ&part=snippet,contentDetails,statistics

Response (200 OK):
{
  "items": [
    {
      "id": "dQw4w9WgXcQ",
      "snippet": {"title": "...", "description": "..."},
      "contentDetails": {
        "duration": "PT5M23S",
        "definition": "hd"
      },
      "statistics": {
        "viewCount": "1000000",
        "likeCount": "50000",
        "commentCount": "5000"
      }
    }
  ]
}""",
        "rate_limits": "10,000 units/day (varies by operation)",
        "auth": "OAuth2 with API key"
    },
    "Amazon E-Commerce": {
        "api_endpoints": [
            "GET /api/v1/products/search - Search products",
            "GET /api/v1/products/{productId} - Get product details",
            "POST /api/v1/carts/items - Add to cart",
            "POST /api/v1/orders - Place order",
            "GET /api/v1/orders/{orderId} - Get order status",
            "POST /api/v1/reviews - Post product review"
        ],
        "sample_code": """// Search Products
GET /api/v1/products/search?q=laptop&limit=20&offset=0

Response (200 OK):
{
  "results": [
    {
      "productId": "prod_12345",
      "title": "MacBook Pro 16-inch",
      "price": {
        "amount": 2499.99,
        "currency": "USD"
      },
      "rating": 4.5,
      "reviewCount": 1250,
      "availability": "in_stock"
    }
  ],
  "totalResults": 5000,
  "nextOffset": 20
}

// Place Order
POST /api/v1/orders
Content-Type: application/json
Authorization: Bearer <token>

{
  "items": [
    {
      "productId": "prod_12345",
      "quantity": 1
    }
  ],
  "shippingAddress": {
    "name": "John Doe",
    "street": "123 Main St",
    "city": "San Francisco",
    "state": "CA",
    "zipCode": "94105",
    "country": "US"
  },
  "paymentMethod": {
    "type": "credit_card",
    "cardToken": "tok_..."
  }
}

Response (201 Created):
{
  "orderId": "order_12345",
  "status": "pending",
  "totalAmount": 2499.99,
  "estimatedDelivery": "2026-05-22",
  "trackingNumber": "1Z999AA10123456784"
}""",
        "rate_limits": "100 requests/second per customer",
        "auth": "Bearer token (OAuth2)"
    },
    "Google Search": {
        "api_endpoints": [
            "GET /customsearch/v1 - Search web",
            "GET /customsearch/v1/siterestrict - Search within site",
            "GET /books/v1/volumes - Search books",
            "GET /knowledge/v1/entities/search - Search knowledge graph"
        ],
        "sample_code": """// Web Search
GET /customsearch/v1?q=machine+learning&key=YOUR_API_KEY&cx=YOUR_CX

Response (200 OK):
{
  "kind": "customsearch#search",
  "url": {"type": "application/json", "template": "..."},
  "queries": {
    "request": [
      {
        "title": "Google Custom Search - machine learning",
        "totalResults": "123000000",
        "searchTerms": "machine learning"
      }
    ]
  },
  "items": [
    {
      "kind": "customsearch#result",
      "title": "Machine Learning - Wikipedia",
      "htmlTitle": "Machine Learning - <b>Wikipedia</b>",
      "link": "https://en.wikipedia.org/wiki/Machine_learning",
      "displayLink": "en.wikipedia.org",
      "snippet": "Machine learning is a method of...",
      "htmlSnippet": "Machine learning is a method of..."
    }
  ],
  "searchInformation": {
    "searchTime": 0.53,
    "totalResults": "123000000"
  }
}

// Knowledge Graph Search
GET /knowledge/v1/entities/search?query=Albert%20Einstein&key=YOUR_API_KEY

Response (200 OK):
{
  "itemListElement": [
    {
      "result": {
        "@type": ["Thing", "Person"],
        "name": "Albert Einstein",
        "description": "Theoretical physicist",
        "url": "http://en.wikipedia.org/wiki/Albert_Einstein",
        "image": "https://kg.google.com/m/..."
      }
    }
  ]
}""",
        "rate_limits": "100 searches/day (free tier), custom limits for paid",
        "auth": "API key"
    },
    "Stripe Payment Api": {
        "api_endpoints": [
            "POST /v1/charges - Create charge",
            "GET /v1/charges/{chargeId} - Get charge",
            "POST /v1/payment_intents - Create payment intent",
            "POST /v1/customers - Create customer",
            "POST /v1/subscriptions - Create subscription",
            "GET /v1/invoices - List invoices"
        ],
        "sample_code": """// Create Charge
POST /v1/charges
Authorization: Bearer sk_test_...
Content-Type: application/x-www-form-urlencoded

amount=2000&currency=usd&source=tok_visa&description=My%20First%20Charge

Response (200 OK):
{
  "id": "ch_1234567890",
  "object": "charge",
  "amount": 2000,
  "amount_captured": 2000,
  "currency": "usd",
  "customer": null,
  "description": "My First Charge",
  "paid": true,
  "receipt_email": "jenny.rosen@example.com",
  "status": "succeeded",
  "created": 1684144200
}

// Create Payment Intent
POST /v1/payment_intents
Authorization: Bearer sk_test_...
Content-Type: application/x-www-form-urlencoded

amount=1099&currency=usd&payment_method_types[]=card

Response (200 OK):
{
  "id": "pi_1234567890",
  "object": "payment_intent",
  "amount": 1099,
  "currency": "usd",
  "customer": null,
  "status": "requires_payment_method",
  "client_secret": "pi_..._secret_...",
  "created": 1684144200
}""",
        "rate_limits": "100 requests/second",
        "auth": "Bearer token (secret key)"
    }
}

# AWS Mermaid Diagram Template
aws_diagram = """### AWS Architecture Diagram

```mermaid
graph TB
    Users["End Users"]
    CloudFront["CloudFront<br/>CDN"]
    ALB["Application Load Balancer<br/>Auto Scaling"]
    ECS["ECS Fargate<br/>Service Instances"]
    RDS[("RDS Aurora<br/>Primary + Replicas")]
    RDSRead[("RDS Read Replica<br/>Multi-AZ")]
    ElastiCache["ElastiCache<br/>Redis Cluster"]
    DynamoDB["DynamoDB<br/>Distributed NoSQL"]
    S3["S3<br/>Object Storage"]
    SQS["SQS<br/>Message Queue"]
    Kinesis["Kinesis<br/>Streaming"]
    Lambda["Lambda<br/>Functions"]
    CloudWatch["CloudWatch<br/>Monitoring"]
    Route53["Route53<br/>DNS"]

    Users -->|Request| Route53
    Route53 -->|Route| CloudFront
    CloudFront -->|Cache Hit/Miss| ALB
    ALB -->|Distribute| ECS
    ECS -->|Query| ElastiCache
    ECS -->|Read| RDSRead
    ECS -->|Write| RDS
    ECS -->|NoSQL| DynamoDB
    ECS -->|Store| S3
    ECS -->|Queue| SQS
    SQS -->|Trigger| Lambda
    Lambda -->|Write| RDS
    Lambda -->|Publish| Kinesis
    Kinesis -->|Stream| Lambda
    ECS -->|Metrics| CloudWatch
    Lambda -->|Metrics| CloudWatch
    RDS -->|Metrics| CloudWatch

    style CloudFront fill:#FF9900
    style ALB fill:#FF9900
    style ECS fill:#FF9900
    style RDS fill:#527FFF
    style RDSRead fill:#527FFF
    style ElastiCache fill:#E74C3C
    style DynamoDB fill:#527FFF
    style S3 fill:#92C83E
    style SQS fill:#FF9900
    style Kinesis fill:#FF9900
    style Lambda fill:#FF9900
    style CloudWatch fill:#759C3E
    style Route53 fill:#FF9900
```"""

# Terraform template
terraform_template = """### Terraform Infrastructure as Code

```hcl
# Provider configuration
terraform {{
  required_providers {{
    aws = {{
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }}
  }}
}}

provider "aws" {{
  region = var.aws_region

  default_tags {{
    tags = {{
      Environment = var.environment
      Project     = var.project_name
      ManagedBy   = "Terraform"
      CreatedAt   = timestamp()
    }}
  }}
}}

# VPC and Networking
resource "aws_vpc" "main" {{
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {{
    Name = "${{var.project_name}}-vpc"
  }}
}}

resource "aws_subnet" "public" {{
  count                   = length(var.availability_zones)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {{
    Name = "${{var.project_name}}-public-subnet-${{count.index + 1}}"
  }}
}}

resource "aws_subnet" "private" {{
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = var.availability_zones[count.index]

  tags = {{
    Name = "${{var.project_name}}-private-subnet-${{count.index + 1}}"
  }}
}}

# Security Groups
resource "aws_security_group" "alb" {{
  name        = "${{var.project_name}}-alb-sg"
  description = "Security group for ALB"
  vpc_id      = aws_vpc.main.id

  ingress {{
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  ingress {{
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
}}

resource "aws_security_group" "ecs" {{
  name        = "${{var.project_name}}-ecs-sg"
  description = "Security group for ECS tasks"
  vpc_id      = aws_vpc.main.id

  ingress {{
    from_port       = 0
    to_port         = 65535
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }}

  egress {{
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }}
}}

# RDS Database
resource "aws_db_subnet_group" "main" {{
  name       = "${{var.project_name}}-db-subnet"
  subnet_ids = aws_subnet.private[*].id

  tags = {{
    Name = "${{var.project_name}}-db-subnet-group"
  }}
}}

resource "aws_rds_cluster" "main" {{
  cluster_identifier      = "${{var.project_name}}-cluster"
  engine                  = "aurora-postgresql"
  engine_version          = "15.2"
  database_name           = var.db_name
  master_username         = var.db_username
  master_password         = random_password.db_password.result
  db_subnet_group_name    = aws_db_subnet_group.main.name
  vpc_security_group_ids  = [aws_security_group.database.id]
  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  skip_final_snapshot     = false
  final_snapshot_identifier = "${{var.project_name}}-final-snapshot-${{formatdate(\"YYYY-MM-DD-hhmm\", timestamp())}}"
  enabled_cloudwatch_logs_exports = ["postgresql"]

  tags = {{
    Name = "${{var.project_name}}-rds"
  }}
}}

resource "aws_rds_cluster_instance" "main" {{
  count              = var.db_instance_count
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = var.db_instance_class
  engine              = aws_rds_cluster.main.engine
  engine_version      = aws_rds_cluster.main.engine_version
  publicly_accessible = false

  tags = {{
    Name = "${{var.project_name}}-rds-instance-${{count.index + 1}}"
  }}
}}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "main" {{
  name       = "${{var.project_name}}-cache-subnet"
  subnet_ids = aws_subnet.private[*].id
}}

resource "aws_elasticache_cluster" "main" {{
  cluster_id           = "${{var.project_name}}-cache"
  engine               = "redis"
  node_type            = var.cache_node_type
  num_cache_nodes      = var.cache_node_count
  parameter_group_name = aws_elasticache_parameter_group.main.name
  engine_version       = "7.0"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.cache.id]
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  automatic_failover_enabled = true

  tags = {{
    Name = "${{var.project_name}}-redis"
  }}
}}

# ECS Cluster and Service
resource "aws_ecs_cluster" "main" {{
  name = "${{var.project_name}}-cluster"

  setting {{
    name  = "containerInsights"
    value = "enabled"
  }}
}}

resource "aws_ecs_task_definition" "main" {{
  family                   = var.project_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([{{
    name      = var.project_name
    image     = var.docker_image
    essential = true
    portMappings = [{{
      containerPort = var.container_port
      hostPort      = var.container_port
      protocol      = "tcp"
    }}]
    environment = [
      {{
        name  = "DB_HOST"
        value = aws_rds_cluster.main.endpoint
      }},
      {{
        name  = "CACHE_HOST"
        value = aws_elasticache_cluster.main.cache_nodes[0].address
      }},
      {{
        name  = "ENVIRONMENT"
        value = var.environment
      }}
    ]
    secrets = [
      {{
        name      = "DB_PASSWORD"
        valueFrom = aws_secretsmanager_secret_version.db_password.arn
      }}
    ]
    logConfiguration = {{
      logDriver = "awslogs"
      options = {{
        awslogs-group         = aws_cloudwatch_log_group.ecs.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "ecs"
      }}
    }}
  }}])
}}

resource "aws_ecs_service" "main" {{
  name            = "${{var.project_name}}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.main.arn
  desired_count   = var.desired_task_count
  launch_type     = "FARGATE"
  network_configuration {{
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }}
  load_balancer {{
    target_group_arn = aws_lb_target_group.main.arn
    container_name   = var.project_name
    container_port   = var.container_port
  }}

  depends_on = [
    aws_lb_listener.main,
    aws_iam_role_policy.ecs_task_execution_role_policy
  ]

  tags = {{
    Name = "${{var.project_name}}-service"
  }}
}}

# Application Load Balancer
resource "aws_lb" "main" {{
  name               = "${{var.project_name}}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false

  tags = {{
    Name = "${{var.project_name}}-alb"
  }}
}}

resource "aws_lb_target_group" "main" {{
  name        = "${{var.project_name}}-tg"
  port        = var.container_port
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {{
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    interval            = 30
    path                = "/"
    matcher             = "200"
  }}

  tags = {{
    Name = "${{var.project_name}}-tg"
  }}
}}

resource "aws_lb_listener" "main" {{
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  default_action {{
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }}
}}

# CloudWatch Monitoring
resource "aws_cloudwatch_log_group" "ecs" {{
  name              = "/ecs/${{var.project_name}}"
  retention_in_days = 7

  tags = {{
    Name = "${{var.project_name}}-logs"
  }}
}}

# Variables
variable "aws_region" {{
  default = "us-east-1"
}}

variable "project_name" {{
  default = "my-app"
}}

variable "environment" {{
  default = "production"
}}

variable "vpc_cidr" {{
  default = "10.0.0.0/16"
}}

variable "availability_zones" {{
  default = ["us-east-1a", "us-east-1b"]
}}

variable "docker_image" {{
  default = "my-account.dkr.ecr.us-east-1.amazonaws.com/my-app:latest"
}}

variable "container_port" {{
  default = 8080
}}

variable "db_name" {{
  default = "myapp"
}}

variable "db_username" {{
  default = "postgres"
}}

variable "db_instance_class" {{
  default = "db.r6g.large"
}}

variable "db_instance_count" {{
  default = 2
}}

variable "cache_node_type" {{
  default = "cache.r6g.large"
}}

variable "cache_node_count" {{
  default = 2
}}

variable "task_cpu" {{
  default = "1024"
}}

variable "task_memory" {{
  default = "2048"
}}

variable "desired_task_count" {{
  default = 3
}}

# Outputs
output "alb_dns_name" {{
  value = aws_lb.main.dns_name
}}

output "rds_endpoint" {{
  value = aws_rds_cluster.main.endpoint
}}

output "redis_endpoint" {{
  value = aws_elasticache_cluster.main.cache_nodes[0].address
}}
```"""

def add_code_api_aws_terraform(filepath, system_name):
    """Add sample code, API, AWS diagram, and Terraform to system file."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Check if sections already exist
    if "## Sample Code & API Specifications" in content:
        return False

    # Find insertion point
    insertion_point = content.find("## Product Requirements Document")
    if insertion_point == -1:
        insertion_point = content.find("## Architecture & Flow Diagrams")
    if insertion_point == -1:
        return False

    # Build new sections
    new_sections = "\n## Sample Code & API Specifications\n\n"

    if system_name in system_code:
        code_info = system_code[system_name]
        new_sections += "### API Endpoints\n\n"
        for endpoint in code_info["api_endpoints"]:
            new_sections += f"- {endpoint}\n"
        new_sections += f"\n### Rate Limits\n\n{code_info['rate_limits']}\n\n"
        new_sections += f"### Authentication\n\n{code_info['auth']}\n\n"
        new_sections += f"### Sample Request/Response\n\n```\n{code_info['sample_code']}\n```\n"
    else:
        new_sections += """### API Endpoints

[System-specific API endpoints to be documented]

### Rate Limits

[Rate limiting configuration]

### Authentication

[Authentication method]

### Sample Request/Response

[Code examples]
"""

    # Add AWS diagram
    new_sections += f"\n\n## AWS Architecture\n\n{aws_diagram}\n"

    # Add Terraform
    new_sections += f"\n\n## Infrastructure as Code (Terraform)\n\n{terraform_template}\n"

    # Insert new sections
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

    print(f"💻 Adding code, API, AWS diagrams & Terraform to {len(files)} systems...")
    print("=" * 60)

    success_count = 0
    for filepath in files:
        filename = filepath.stem
        parts = filename.split('_', 1)
        if len(parts) < 2:
            continue

        system_name = ' '.join(word.capitalize() for word in parts[1].split('_'))

        try:
            if add_code_api_aws_terraform(filepath, system_name):
                print(f"✅ Added code/API/AWS/Terraform: {system_name}")
                success_count += 1
            else:
                print(f"⏭️  Already has sections: {system_name}")
        except Exception as e:
            print(f"❌ Error in {system_name}: {e}")

    print("=" * 60)
    print(f"✨ Added sections to {success_count} system files!")

if __name__ == '__main__':
    main()
