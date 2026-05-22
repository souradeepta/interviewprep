#!/usr/bin/env python3
"""
Script to add detailed back-of-envelope calculations and PRD sections
to all 36 real-world system design files.
"""

from pathlib import Path

# System-specific calculation and PRD data
system_specs = {
    "Facebook Social Network": {
        "users": "3B+",
        "dau": "2B+",
        "rps": "500K+",
        "avg_posts_per_user_per_day": 0.5,
        "avg_friends": 500,
        "avg_post_size_bytes": 5000,
        "avg_comments_per_post": 10,
        "avg_likes_per_post": 100,
        "feed_size_posts": 1000,
        "functional_requirements": [
            "User registration and authentication with OAuth2",
            "Post creation, editing, and deletion",
            "Feed generation with personalized ranking",
            "Friend request/connection management",
            "Real-time notifications for interactions",
            "Search posts by content, hashtags, users",
            "Comment threads with nested replies",
            "Like/reaction system with counters",
            "Media upload (photos, videos) with CDN delivery",
            "Blocking and privacy controls"
        ],
        "nfr": {
            "latency": "P99 < 500ms for feed",
            "availability": "99.99%",
            "consistency": "Eventual consistency for feeds, strong for critical data",
            "scalability": "Handle 10x growth",
            "throughput": "500K+ RPS peak"
        }
    },
    "WhatsApp Messaging": {
        "users": "2B+",
        "dau": "1.5B+",
        "rps": "1M+",
        "avg_messages_per_user_per_day": 50,
        "avg_message_size_bytes": 200,
        "avg_group_size": 10,
        "message_retention_days": 30,
        "functional_requirements": [
            "User registration with phone number verification",
            "One-to-one messaging with end-to-end encryption",
            "Group messaging with up to 256 members",
            "Message delivery status (sent, delivered, read)",
            "Media sharing (photos, videos, documents)",
            "Voice and video calls (encrypted)",
            "Message search and history",
            "Contact syncing and discovery",
            "Status updates and stories",
            "Call history and backup"
        ],
        "nfr": {
            "latency": "P99 < 100ms message delivery",
            "availability": "99.99%",
            "consistency": "Strong consistency for message order",
            "scalability": "1M+ concurrent messages/sec",
            "throughput": "1B+ messages/day"
        }
    },
    "Slack Team Communication": {
        "users": "750M+",
        "dau": "200M+",
        "rps": "500K+",
        "teams": "50M+",
        "avg_channels_per_team": 50,
        "avg_messages_per_channel_per_day": 100,
        "avg_message_size_bytes": 500,
        "functional_requirements": [
            "Workspace and team creation",
            "Channel management (public, private, archived)",
            "Direct messaging and group DMs",
            "Message search with filters",
            "Thread replies with notifications",
            "File sharing with preview and search",
            "Integration with 2000+ third-party apps",
            "Emoji reactions and mentions",
            "User roles and permissions",
            "Message editing and deletion"
        ],
        "nfr": {
            "latency": "P99 < 200ms message delivery",
            "availability": "99.99%",
            "consistency": "Strong consistency for message order",
            "scalability": "500K+ RPS peak",
            "throughput": "500M+ messages/day"
        }
    },
    "Twitter Feed": {
        "users": "550M+",
        "dau": "350M+",
        "rps": "300K+",
        "avg_tweets_per_user_per_day": 0.3,
        "avg_followers": 100,
        "avg_tweet_size_bytes": 300,
        "avg_retweets_per_tweet": 50,
        "functional_requirements": [
            "Tweet creation with 280 characters",
            "Media attachments (photos, videos, GIFs)",
            "Retweets with optional commentary",
            "Likes and bookmarks",
            "Follow/unfollow users",
            "Timeline generation (home, user, explore)",
            "Hashtag and trend tracking",
            "Search tweets by keyword, user, date",
            "Notifications for interactions",
            "DM support"
        ],
        "nfr": {
            "latency": "P99 < 300ms for timeline",
            "availability": "99.99%",
            "consistency": "Eventual consistency for timeline",
            "scalability": "Billion+ tweets searchable",
            "throughput": "500K+ RPS peak"
        }
    },
    "Discord Gaming Chat": {
        "users": "650M+",
        "dau": "200M+",
        "rps": "400K+",
        "active_voice_sessions": "20M+",
        "servers": "50M+",
        "avg_server_members": 500,
        "functional_requirements": [
            "Server and channel creation",
            "Text messaging with rich formatting",
            "Voice channels with low-latency audio",
            "Video streaming support",
            "Screen sharing",
            "Server roles and permissions",
            "Member moderation tools",
            "Bot integration framework",
            "Reactions and emotes",
            "Message history and search"
        ],
        "nfr": {
            "latency": "P99 < 50ms for voice",
            "availability": "99.99%",
            "consistency": "Strong for voice sessions",
            "scalability": "20M+ concurrent voice sessions",
            "throughput": "400K+ RPS peak"
        }
    },
    "Telegram Secure Messaging": {
        "users": "800M+",
        "dau": "500M+",
        "rps": "600K+",
        "messages_per_second": 600000,
        "avg_message_size_bytes": 300,
        "functional_requirements": [
            "Decentralized cloud storage option",
            "Secret chats with client-side encryption",
            "Group chats up to 200K members",
            "Channels for broadcasting",
            "File sharing up to 4GB per file",
            "Voice and video calls",
            "Bots with custom APIs",
            "Stickers and GIFs",
            "Message self-destruct timer",
            "Encrypted backup"
        ],
        "nfr": {
            "latency": "P99 < 100ms message delivery",
            "availability": "99.99%",
            "consistency": "Strong for message order",
            "scalability": "600K+ messages/sec",
            "throughput": "500M+ DAU"
        }
    },
    "YouTube Video Platform": {
        "users": "2.5B+",
        "dau": "2B+",
        "rps": "1M+",
        "videos_uploaded_per_day": "500K+",
        "avg_video_duration_minutes": 10,
        "avg_bitrate_mbps": 5,
        "daily_watch_hours": "1B+",
        "functional_requirements": [
            "Video upload with multiple formats",
            "Transcoding to 20+ quality levels",
            "Adaptive bitrate streaming",
            "Video search and recommendations",
            "Comments and community features",
            "Playlist creation and sharing",
            "Channel management",
            "Analytics and monetization",
            "Live streaming",
            "Subtitle/caption support"
        ],
        "nfr": {
            "latency": "P99 < 200ms for video start",
            "availability": "99.99%",
            "consistency": "Eventual for recommendations",
            "scalability": "Billion+ video catalog",
            "throughput": "1M+ concurrent streams"
        }
    },
    "Twitch Live Streaming": {
        "users": "140M+",
        "dau": "30M+",
        "rps": "500K+",
        "concurrent_viewers": "3M+",
        "avg_stream_bitrate_mbps": 6,
        "functional_requirements": [
            "Live stream ingestion and distribution",
            "Multiple video quality options",
            "Real-time chat with moderation",
            "Subscriber and donation system",
            "VOD (video on demand) storage",
            "Clips and highlights",
            "Host/raid features",
            "Recommendations engine",
            "Streamer analytics",
            "Two-factor authentication"
        ],
        "nfr": {
            "latency": "P99 < 5000ms (5s) for broadcast",
            "availability": "99.99%",
            "consistency": "Strong for chat order",
            "scalability": "3M+ concurrent viewers",
            "throughput": "500K+ RPS peak"
        }
    },
    "TikTok Short Video": {
        "users": "1.5B+",
        "dau": "1B+",
        "rps": "2M+",
        "videos_watched_per_day": "1T+",
        "avg_video_duration_seconds": 30,
        "avg_video_size_mb": 10,
        "functional_requirements": [
            "Video recording and editing in-app",
            "Sound/music library with millions of tracks",
            "Effects and filters (1000+)",
            "For You Page with ML recommendations",
            "Duets and stitches",
            "Live streaming",
            "Creator fund and monetization",
            "Comment and reply features",
            "Trending hashtags and sounds",
            "Creator analytics"
        ],
        "nfr": {
            "latency": "P99 < 100ms for FYP load",
            "availability": "99.99%",
            "consistency": "Eventual for recommendations",
            "scalability": "1T+ videos watched/day",
            "throughput": "2M+ RPS peak"
        }
    },
    "Spotify Music Streaming": {
        "users": "600M+",
        "dau": "200M+",
        "rps": "500K+",
        "concurrent_listeners": "500K+",
        "songs_in_catalog": "100M+",
        "avg_song_duration_seconds": 210,
        "functional_requirements": [
            "Music streaming with multiple quality levels",
            "Offline sync and download",
            "Personalized playlists",
            "Recommendations based on listening history",
            "Podcast support",
            "Social sharing and collaborative playlists",
            "Cross-device sync",
            "Search and discovery",
            "Artist profiles and albums",
            "Lyrics display"
        ],
        "nfr": {
            "latency": "P99 < 100ms for track switch",
            "availability": "99.99%",
            "consistency": "Eventual for recommendations",
            "scalability": "500K+ concurrent streams",
            "throughput": "100M+ songs searchable"
        }
    },
    "Disney Video Streaming": {
        "users": "300M+",
        "dau": "100M+",
        "rps": "300K+",
        "concurrent_streams": "20M+",
        "content_library": "15K+",
        "functional_requirements": [
            "DRM-protected content delivery",
            "Multi-profile support",
            "Watchlist and continue watching",
            "Personalized recommendations",
            "4K and HDR support",
            "Offline download capability",
            "Multi-device synchronization",
            "Parental controls",
            "Live sports streaming",
            "Premium and standard tiers"
        ],
        "nfr": {
            "latency": "P99 < 500ms for content start",
            "availability": "99.99%",
            "consistency": "Strong for watchlist state",
            "scalability": "20M+ concurrent streams",
            "throughput": "300K+ RPS peak"
        }
    },
    "Dropbox File Sync": {
        "users": "700M+",
        "dau": "200M+",
        "rps": "400K+",
        "storage_managed": "2B+GB",
        "avg_file_size_bytes": 500000,
        "functional_requirements": [
            "File upload and sync across devices",
            "Selective sync capability",
            "Version history and recovery",
            "Sharing with granular permissions",
            "Collaborative editing",
            "Comment and annotation features",
            "LAN sync for bandwidth optimization",
            "Smart sync for space efficiency",
            "File request capability",
            "Password-protected links"
        ],
        "nfr": {
            "latency": "P99 < 1000ms for sync detection",
            "availability": "99.99%",
            "consistency": "Strong eventual consistency",
            "scalability": "Handle 2B+ GB managed",
            "throughput": "400K+ RPS peak"
        }
    },
    "Amazon E-Commerce": {
        "users": "300M+",
        "dau": "100M+",
        "rps": "1M+",
        "product_catalog": "300M+",
        "daily_orders": "5M+",
        "functional_requirements": [
            "Product catalog with search and filtering",
            "Shopping cart and checkout",
            "Payment processing with multiple methods",
            "Order tracking and history",
            "Personalized recommendations",
            "Reviews and ratings",
            "Inventory management",
            "Seller management platform",
            "Returns and refunds",
            "A/B testing framework"
        ],
        "nfr": {
            "latency": "P99 < 200ms for catalog search",
            "availability": "99.99%",
            "consistency": "Strong for inventory",
            "scalability": "1M+ RPS peak",
            "throughput": "300M+ products searchable"
        }
    },
    "eBay Auction System": {
        "users": "180M+",
        "dau": "50M+",
        "rps": "300K+",
        "active_listings": "2B+",
        "daily_transactions": "1M+",
        "functional_requirements": [
            "Auction listing creation and management",
            "Bidding system with auto-bid feature",
            "Real-time bid updates",
            "Payment escrow service",
            "Seller and buyer ratings",
            "Dispute resolution",
            "Inventory management",
            "Bulk listing tools",
            "Search and filtering",
            "Fraud detection"
        ],
        "nfr": {
            "latency": "P99 < 100ms for bid placement",
            "availability": "99.99%",
            "consistency": "Strong for bids and payments",
            "scalability": "1M+ concurrent auctions",
            "throughput": "300K+ RPS peak"
        }
    },
    "Shopify Store Platform": {
        "users": "2M+",
        "dau": "500K+",
        "rps": "400K+",
        "merchants": "2M+",
        "daily_gmv": "20B+",
        "functional_requirements": [
            "Store builder with no-code editor",
            "Product management and inventory",
            "Shopping cart and checkout",
            "Payment gateway integration",
            "Shipping and fulfillment",
            "Analytics and reporting",
            "Marketing and email tools",
            "App ecosystem (10K+)",
            "Multi-channel selling",
            "Customer management"
        ],
        "nfr": {
            "latency": "P99 < 500ms for store load",
            "availability": "99.99%",
            "consistency": "Strong for orders and inventory",
            "scalability": "2M+ merchants",
            "throughput": "400K+ RPS peak"
        }
    },
    "Payment Processing": {
        "users": "billions",
        "dau": "100M+",
        "rps": "2M+",
        "daily_transactions": "500M+",
        "avg_transaction_value_usd": 50,
        "functional_requirements": [
            "Payment authorization and settlement",
            "Card processing (credit, debit, prepaid)",
            "Fraud detection and prevention",
            "PCI-DSS compliance",
            "Chargeback management",
            "Transaction logging and reporting",
            "Currency conversion",
            "Batching and reconciliation",
            "Risk scoring",
            "AML (Anti-Money Laundering)"
        ],
        "nfr": {
            "latency": "P99 < 100ms for authorization",
            "availability": "99.99%",
            "consistency": "Strong for all transactions",
            "scalability": "2M+ RPS peak",
            "throughput": "500M+ daily transactions"
        }
    },
    "Stripe Payment Api": {
        "users": "500K+",
        "dau": "100K+",
        "rps": "1M+",
        "gmv_daily": "50B+",
        "functional_requirements": [
            "RESTful payment APIs",
            "Card tokenization and storage",
            "Subscription management",
            "Invoice generation",
            "Payout management",
            "Webhook notifications",
            "Dashboard for analytics",
            "Fraud detection",
            "3D Secure support",
            "Global payment methods"
        ],
        "nfr": {
            "latency": "P99 < 150ms for API calls",
            "availability": "99.99%",
            "consistency": "Strong for transactions",
            "scalability": "1M+ RPS peak",
            "throughput": "$50B+ daily GMV"
        }
    },
    "Robinhood Trading": {
        "users": "20M+",
        "dau": "5M+",
        "rps": "500K+",
        "daily_trades": "100M+",
        "avg_order_value_usd": 1000,
        "functional_requirements": [
            "Real-time stock quotes",
            "Order placement (market, limit, stop)",
            "Portfolio management",
            "Stock research and analysis",
            "Options trading",
            "Fractional shares",
            "Dividend tracking",
            "Tax documents",
            "Account funding and withdrawal",
            "Regulatory compliance"
        ],
        "nfr": {
            "latency": "P99 < 10ms for order matching",
            "availability": "99.99%",
            "consistency": "Strong for orders and balances",
            "scalability": "100M+ daily trades",
            "throughput": "500K+ RPS peak"
        }
    },
    "Square Pos": {
        "users": "100M+",
        "dau": "30M+",
        "rps": "300K+",
        "daily_transactions": "100M+",
        "functional_requirements": [
            "Point of sale transaction processing",
            "Inventory management",
            "Employee time tracking",
            "Customer database",
            "Marketing campaigns",
            "Real-time analytics",
            "Offline mode capability",
            "Contactless payments",
            "Refunds and exchanges",
            "Multi-location support"
        ],
        "nfr": {
            "latency": "P99 < 100ms for payment",
            "availability": "99.99%",
            "consistency": "Strong for transactions",
            "scalability": "100M+ daily transactions",
            "throughput": "300K+ RPS peak"
        }
    },
    "Paypal Digital Wallet": {
        "users": "430M+",
        "dau": "50M+",
        "rps": "500K+",
        "daily_transactions": "100M+",
        "daily_gmv": "100B+",
        "functional_requirements": [
            "Digital wallet and balance management",
            "Payment sending and receiving",
            "Card and bank account linking",
            "Checkout for merchants",
            "Invoice management",
            "Currency conversion",
            "Dispute resolution",
            "Multi-currency support",
            "Bill payment",
            "Cryptocurrency integration"
        ],
        "nfr": {
            "latency": "P99 < 200ms for payment",
            "availability": "99.99%",
            "consistency": "Strong for transactions",
            "scalability": "500K+ RPS peak",
            "throughput": "$100B+ daily GMV"
        }
    },
    "Google Search": {
        "users": "5B+",
        "dau": "4B+",
        "rps": "5M+",
        "daily_queries": "8B+",
        "functional_requirements": [
            "Index web crawl results",
            "Query processing and ranking",
            "Autocomplete suggestions",
            "Search filters and sorting",
            "Rich snippets and knowledge panels",
            "Image and video search",
            "News search",
            "Shopping results",
            "Safe search filtering",
            "Voice search support"
        ],
        "nfr": {
            "latency": "P99 < 100ms for search results",
            "availability": "99.99%",
            "consistency": "Eventual for index",
            "scalability": "8B+ daily queries",
            "throughput": "5M+ RPS peak"
        }
    },
    "Elastic Search": {
        "users": "100K+",
        "dau": "10K+",
        "rps": "500K+",
        "documents_indexed": "100B+",
        "functional_requirements": [
            "Full-text search indexing",
            "Real-time document indexing",
            "Complex query DSL",
            "Aggregations and analytics",
            "Distributed search",
            "High availability clustering",
            "Backup and recovery",
            "Index lifecycle management",
            "Security and encryption",
            "SQL support"
        ],
        "nfr": {
            "latency": "P99 < 200ms for search",
            "availability": "99.99%",
            "consistency": "Eventual for indexing",
            "scalability": "100B+ documents",
            "throughput": "500K+ RPS peak"
        }
    },
    "Databricks Analytics": {
        "users": "50K+",
        "dau": "10K+",
        "rps": "100K+",
        "daily_data_processed": "1000PB+",
        "functional_requirements": [
            "Distributed SQL queries",
            "ML model training",
            "Data pipeline orchestration",
            "Notebook environment",
            "Delta Lake format support",
            "Job scheduling",
            "Collaboration features",
            "MLflow integration",
            "SQL warehouse",
            "BI tool integration"
        ],
        "nfr": {
            "latency": "P99 < 30sec for query",
            "availability": "99.99%",
            "consistency": "Strong eventual",
            "scalability": "1000PB+ daily",
            "throughput": "Unlimited with auto-scaling"
        }
    },
    "Notion Workspace": {
        "users": "30M+",
        "dau": "10M+",
        "rps": "200K+",
        "documents": "500M+",
        "functional_requirements": [
            "Document creation and editing",
            "Real-time collaboration",
            "Database creation and management",
            "Template library",
            "Integrations (100+)",
            "Block-based page builder",
            "Web clipper",
            "Comments and mentions",
            "Sharing and permissions",
            "Version history"
        ],
        "nfr": {
            "latency": "P99 < 500ms for edits",
            "availability": "99.99%",
            "consistency": "Strong eventual with CRDT",
            "scalability": "10M+ DAU",
            "throughput": "200K+ RPS peak"
        }
    },
    "Figma Design Tool": {
        "users": "30M+",
        "dau": "5M+",
        "rps": "300K+",
        "concurrent_editors": "500K+",
        "functional_requirements": [
            "Vector design and editing",
            "Real-time collaboration",
            "Component library management",
            "Prototyping tools",
            "Design systems",
            "Handoff to developers",
            "Comments and feedback",
            "Version history",
            "Plugin ecosystem",
            "Export options"
        ],
        "nfr": {
            "latency": "P99 < 100ms for edits",
            "availability": "99.99%",
            "consistency": "Strong eventual",
            "scalability": "500K+ concurrent editors",
            "throughput": "300K+ RPS peak"
        }
    },
    "Confluence Wiki": {
        "users": "10M+",
        "dau": "5M+",
        "rps": "200K+",
        "pages": "1B+",
        "functional_requirements": [
            "Page creation and editing",
            "Collaborative spaces",
            "Permission management",
            "Full-text search",
            "Attachment management",
            "Versioning and recovery",
            "Comments and discussions",
            "Macros and extensions",
            "Integration with Jira",
            "Export capabilities"
        ],
        "nfr": {
            "latency": "P99 < 300ms for page load",
            "availability": "99.99%",
            "consistency": "Strong eventual",
            "scalability": "1B+ pages",
            "throughput": "200K+ RPS peak"
        }
    },
    "Doordash Food Delivery": {
        "users": "50M+",
        "dau": "10M+",
        "rps": "200K+",
        "daily_orders": "1M+",
        "restaurants": "1M+",
        "functional_requirements": [
            "Restaurant and menu browsing",
            "Real-time order placement",
            "Live delivery tracking",
            "Driver assignment and routing",
            "Payment processing",
            "Reviews and ratings",
            "Promotions and discounts",
            "Refunds and support",
            "Accessibility features",
            "Notification system"
        ],
        "nfr": {
            "latency": "P99 < 200ms for ordering",
            "availability": "99.99%",
            "consistency": "Strong for orders",
            "scalability": "1M+ daily orders",
            "throughput": "200K+ RPS peak"
        }
    },
    "Booking Travel Marketplace": {
        "users": "300M+",
        "dau": "100M+",
        "rps": "500K+",
        "property_listings": "50M+",
        "daily_bookings": "2M+",
        "functional_requirements": [
            "Property search and filtering",
            "Dynamic pricing",
            "Instant booking capability",
            "Payment processing",
            "Reviews and ratings",
            "Flexible cancellation policies",
            "Traveler protection guarantee",
            "Travel insurance",
            "Group bookings",
            "Package deals"
        ],
        "nfr": {
            "latency": "P99 < 300ms for search",
            "availability": "99.99%",
            "consistency": "Strong for availability",
            "scalability": "50M+ listings",
            "throughput": "500K+ RPS peak"
        }
    },
    "Multiplayer Game Backend": {
        "users": "100M+",
        "dau": "20M+",
        "rps": "1M+",
        "concurrent_players": "5M+",
        "functional_requirements": [
            "Player authentication and account management",
            "Real-time game state synchronization",
            "Network latency compensation",
            "Matchmaking and lobby system",
            "Leaderboard management",
            "In-game messaging and chat",
            "Inventory and item management",
            "Cosmetics and battle pass system",
            "Replay/demo recording",
            "Anti-cheat system"
        ],
        "nfr": {
            "latency": "P99 < 50ms for state update",
            "availability": "99.99%",
            "consistency": "Strong for game state",
            "scalability": "5M+ concurrent players",
            "throughput": "1M+ RPS peak"
        }
    }
}

def generate_back_of_envelope(system_name, specs):
    """Generate detailed back-of-envelope calculations."""

    section = f"""## Back-of-Envelope Calculations

### Traffic Metrics

**Daily Activity:**
- DAU: {specs.get('dau', 'N/A')}
- RPS (Peak): {specs.get('rps', 'N/A')}
- Average RPS: {specs.get('rps', 'N/A')} / 3 = {specs.get('rps', 'N/A')} / 3

**Data Volume (Daily):**
"""

    # System-specific calculations
    if "Facebook" in system_name:
        section += f"""- Posts: 2B users × 0.5 posts/day = 1B posts/day
- Post data: 1B posts × 5KB/post = 5PB/day
- Comments: 1B posts × 10 comments × 500B = 5B comments/day
- Comment data: 5B comments × 1KB = 5PB/day
- Likes: 1B posts × 100 likes × 500B users = 50B likes/day
- Total media storage: 5PB + 5PB = 10PB/day
- Monthly growth: 10PB/day × 30 = 300PB/month
"""
    elif "WhatsApp" in system_name:
        section += f"""- Messages: 1.5B DAU × 50 messages/day = 75B messages/day
- Message data: 75B messages × 200B = 15PB/day
- Media messages: 20% of messages have media
- Average media: 500KB per message
- Media volume: 75B × 0.2 × 500KB = 7.5PB/day
- Total: 15PB + 7.5PB = 22.5PB/day
- Monthly: 22.5PB × 30 = 675PB/month
"""
    elif "YouTube" in system_name:
        section += f"""- Views: 2B DAU × 10 videos = 20B views/day
- Uploads: 500K videos/day × 200MB avg = 100PB/day (original)
- After compression: 100PB × 0.2 = 20PB/day (multiple qualities)
- Bandwidth for viewing: 20B views × 5Mbps × 1/8 = 12.5PB/day
- Total storage growth: 20PB/day for originals + encodings
- Monthly: 20PB × 30 = 600PB/month
"""
    elif "TikTok" in system_name:
        section += f"""- Videos watched: 1T videos/day
- Video size: 10MB avg per video
- Bandwidth: 1T × 10MB × 8 = 80EB/day
- Uploads: 1M videos/day × 100MB = 100PB/day
- Storage (1 year): 100PB × 365 = 36.5EB/year
- Replication (3x): 36.5EB × 3 = 110EB/year
"""
    elif "Twitter" in system_name:
        section += f"""- Tweets: 350M DAU × 0.3 tweets = 105M tweets/day
- Tweet data: 105M tweets × 300B = 31.5TB/day
- Media tweets: 40% of tweets have media
- Media size: 105M × 0.4 × 2MB = 84TB/day
- Total: 31.5TB + 84TB = 115.5TB/day
- Monthly: 115.5TB × 30 = 3.5PB/month
"""
    else:
        section += f"""- Baseline calculation using RPS:
- Peak RPS: {specs.get('rps', 'N/A')}
- Average RPS: Peak / 3
- Requests/day: Average RPS × 86400 seconds
- Data/request: varies by system type
"""

    section += f"""
### Storage Calculation

**Database Storage:**
- Current data: Based on daily growth rates
- Indexing overhead: +30% for indexes and metadata
- Backup copies: 3 replicas + daily snapshots
- Total: Current × replication factor

**Cache Layer:**
- Working set size: ~20% of total data
- Hot data: ~1-2% of total data
- Cache nodes needed: Working Set / (Node Capacity)

**CDN/Static Content:**
- Media distribution: Multi-tier caching
- Edge cache: Regional distribution
- Archive storage: Cold data tiered to S3

### Bandwidth Calculation

**Ingress:**
- Peak upload bandwidth: Peak RPS × avg request size
- Peak = 3× average
- Network redundancy: 2+ diverse paths

**Egress:**
- Download bandwidth: Streaming/serving data
- Peak surge: 5-10× during viral events
- CDN reduces origin bandwidth by 80-90%

### Cost Estimation

**Compute:**
- Load balanced instances: Peak RPS / 10K RPS per instance
- Redundancy: 2x for failover
- Reserved capacity: 20% headroom
- Cost: $0.30-0.50 per instance per hour

**Database:**
- Instance cost: $0.50-2.00 per hour
- Primary + replicas: 3-5 instances
- Storage: $0.10 per GB per month

**Networking:**
- Egress: $0.12 per GB
- CDN: $0.085 per GB
- Peak egress bandwidth drives costs

**Total Monthly Cost:**
- Compute: {specs.get('rps', 'N/A')} RPS → Cost scales with traffic
- Database: Depends on data volume
- Networking: Depends on CDN usage
- Typical range: $1M - $10M+ per month

### Latency Budget

**Total P99 latency target: 100-500ms (varies by system)**

Budget breakdown:
- Network round trip: 10-50ms
- API Gateway processing: 5-10ms
- Service processing: 20-50ms
- Database query: 10-50ms
- Cache lookup: 1-5ms
- Response serialization: 5-10ms
- Network return: 10-50ms

### Availability Targets

**99.99% availability:**
- Downtime per year: 52 minutes
- Downtime per month: 4.38 minutes
- Downtime per day: 8.64 seconds

**Implies:**
- No single point of failure
- Multi-region redundancy
- Automated failover < 2 minutes RTO
- RPO < 1 minute for critical data
"""
    return section

def generate_prd(system_name, specs):
    """Generate detailed PRD section."""

    functional_reqs = "\n".join([f"- {req}" for req in specs.get('functional_requirements', [])])
    nfr = specs.get('nfr', {})

    section = f"""## Product Requirements Document (PRD)

### Overview

{system_name} is a mission-critical system serving {specs.get('users', 'N/A')} users globally.
This PRD defines requirements for scaling, reliability, and performance at this unprecedented scale.

### Functional Requirements

{functional_reqs}

### Non-Functional Requirements

**Performance:**
- Latency: {nfr.get('latency', 'N/A')}
- Throughput: {nfr.get('throughput', 'N/A')}
- Concurrent users: {specs.get('dau', 'N/A')} DAU, {specs.get('rps', 'N/A')} RPS peak

**Reliability:**
- Availability: {nfr.get('availability', 'N/A')}
- Data durability: 99.999999% (8 nines)
- RTO (Recovery Time Objective): < 2 minutes
- RPO (Recovery Point Objective): < 1 minute

**Scalability:**
- {nfr.get('scalability', 'N/A')}
- Horizontal scaling for all tiers
- Auto-scaling based on metrics
- Handle 10x load spikes gracefully

**Consistency:**
- Model: {nfr.get('consistency', 'N/A')}
- Critical data: Strong ACID guarantees
- Non-critical data: Eventual consistency acceptable

### User Roles & Personas

**End Users:**
- Need: Fast, reliable access to services
- Pain point: Downtime, slow response times
- Success metric: P99 latency < target, 99.99% uptime

**Business Stakeholders:**
- Need: Revenue generation, market expansion
- Pain point: Scale limitations, operational costs
- Success metric: Supports 10x growth, cost per user decreases

**Operations/SRE:**
- Need: System visibility and control
- Pain point: Complex failure modes, unclear blame
- Success metric: MTTR < 5 minutes, clear root causes

**Developers:**
- Need: Simple APIs, good documentation
- Pain point: Operational complexity, debugging
- Success metric: Easy to understand, debug, and extend

### Success Metrics

**Technical Metrics:**
- P50 latency: < 50ms
- P99 latency: {nfr.get('latency', 'P99 < 100ms')}
- P99.9 latency: < 1s
- Availability: {nfr.get('availability', '> 99.99%')}
- Error rate: < 0.1%
- Cache hit ratio: > 95%
- Database replication lag: < 1 second

**Business Metrics:**
- Daily active users: {specs.get('dau', 'N/A')}
- Monthly active users: {specs.get('users', 'N/A')}
- Request success rate: > 99.9%
- Customer satisfaction: > 4.5/5

**Operational Metrics:**
- Mean time to resolution: < 30 minutes
- Deployment frequency: Daily
- Change failure rate: < 5%
- Incident response time: < 15 minutes

### Constraints & Assumptions

**Constraints:**
- Global latency: Can't reduce network physics
- Data center failover: 30-60s detection + 1-2min failover
- Budget: Must optimize cost per request
- Compliance: GDPR, SOC2, PCI-DSS requirements

**Assumptions:**
- Team has Kubernetes expertise
- Access to managed database services
- Multi-region deployment possible
- Cloud budget is flexible for auto-scaling

### Out of Scope (Phase 1)

- Blockchain/crypto integration
- Quantum-resistant encryption
- Machine learning model training (covered separately)
- Mobile app optimization (covered separately)

### Success Criteria

1. System operates at scale: {specs.get('users', 'N/A')} users
2. Maintains SLOs: {nfr.get('latency', 'N/A')} latency, {nfr.get('availability', '99.99%')} availability
3. Cost per request: $0.0001 or lower
4. Team can troubleshoot issues < 30 minutes
5. Can scale 10x in < 1 week
6. Zero data loss in any failure scenario
"""
    return section

def add_sections_to_file(filepath, system_name):
    """Add back-of-envelope calculations and PRD to file."""
    with open(filepath, 'r') as f:
        content = f.read()

    # Check if sections already exist
    if "## Back-of-Envelope Calculations" in content and "## Product Requirements Document" in content:
        return False

    # Find insertion point (before Architecture & Flow Diagrams or Capacity Planning)
    insertion_point = content.find("## Architecture & Flow Diagrams")
    if insertion_point == -1:
        insertion_point = content.find("## Capacity Planning")
    if insertion_point == -1:
        return False

    # Get system specs
    specs = system_specs.get(system_name, {})

    # Generate sections
    boe_section = generate_back_of_envelope(system_name, specs)
    prd_section = generate_prd(system_name, specs)

    # Combine sections
    new_sections = boe_section + "\n" + prd_section + "\n"

    # Insert before diagrams
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

    print(f"📊 Adding BoE calculations & PRD to {len(files)} system files...")
    print("=" * 60)

    success_count = 0
    for filepath in files:
        filename = filepath.stem
        # Extract system name: remove leading number and underscore
        parts = filename.split('_', 1)
        if len(parts) < 2:
            print(f"⏭️  Skipping {filename} (invalid format)")
            continue

        system_name = ' '.join(word.capitalize() for word in parts[1].split('_'))

        try:
            if add_sections_to_file(filepath, system_name):
                print(f"✅ Added BoE & PRD: {system_name}")
                success_count += 1
            else:
                print(f"⏭️  Already has sections: {system_name}")
        except Exception as e:
            import traceback
            print(f"❌ Error in {system_name}: {e}")
            traceback.print_exc()

    print("=" * 60)
    print(f"✨ Added sections to {success_count} system files!")

if __name__ == '__main__':
    main()
