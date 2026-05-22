#!/usr/bin/env python3
"""Add Python and Java code implementations to system design concept files."""

import os
import re

BASE_DIR = "docs/system_design"

CODE_BLOCKS = {
    "09_decorator_pattern.md": """
## Python Implementation

```python
from abc import ABC, abstractmethod

class Coffee(ABC):
    @abstractmethod
    def cost(self) -> float: pass
    @abstractmethod
    def description(self) -> str: pass

class SimpleCoffee(Coffee):
    def cost(self): return 1.0
    def description(self): return "Simple Coffee"

class CoffeeDecorator(Coffee):
    def __init__(self, coffee: Coffee):
        self._coffee = coffee
    def cost(self): return self._coffee.cost()
    def description(self): return self._coffee.description()

class MilkDecorator(CoffeeDecorator):
    def cost(self): return self._coffee.cost() + 0.5
    def description(self): return self._coffee.description() + ", Milk"

class SugarDecorator(CoffeeDecorator):
    def cost(self): return self._coffee.cost() + 0.25
    def description(self): return self._coffee.description() + ", Sugar"

class WhipDecorator(CoffeeDecorator):
    def cost(self): return self._coffee.cost() + 1.0
    def description(self): return self._coffee.description() + ", Whip"

# Usage
coffee = SimpleCoffee()
coffee = MilkDecorator(coffee)
coffee = SugarDecorator(coffee)
coffee = WhipDecorator(coffee)
print(coffee.description(), "->", coffee.cost())  # Simple Coffee, Milk, Sugar, Whip -> 2.75
```

## Java Implementation

```java
public interface Coffee {
    double cost();
    String description();
}

public class SimpleCoffee implements Coffee {
    public double cost() { return 1.0; }
    public String description() { return "Simple Coffee"; }
}

public abstract class CoffeeDecorator implements Coffee {
    protected Coffee coffee;
    public CoffeeDecorator(Coffee coffee) { this.coffee = coffee; }
    public double cost() { return coffee.cost(); }
    public String description() { return coffee.description(); }
}

public class MilkDecorator extends CoffeeDecorator {
    public MilkDecorator(Coffee coffee) { super(coffee); }
    public double cost() { return coffee.cost() + 0.5; }
    public String description() { return coffee.description() + ", Milk"; }
}

public class WhipDecorator extends CoffeeDecorator {
    public WhipDecorator(Coffee coffee) { super(coffee); }
    public double cost() { return coffee.cost() + 1.0; }
    public String description() { return coffee.description() + ", Whip"; }
}
```
""",

    "10_adapter_pattern.md": """
## Python Implementation

```python
class EuropeanSocket:
    def voltage(self) -> int: return 220
    def live(self) -> int: return 1
    def neutral(self) -> int: return -1

class USASocket:
    def voltage(self) -> int: return 110
    def live(self) -> int: return 1
    def neutral(self) -> int: return -1

class EuropeanToUSAAdapter:
    def __init__(self, socket: EuropeanSocket):
        self._socket = socket

    def voltage(self) -> int:
        return 110  # Convert 220V to 110V

    def live(self) -> int: return self._socket.live()
    def neutral(self) -> int: return self._socket.neutral()

class AmericanDevice:
    def charge(self, socket: USASocket):
        if socket.voltage() == 110:
            print(f"Charging at {socket.voltage()}V")
        else:
            raise ValueError("Incompatible voltage")

# Usage
eu_socket = EuropeanSocket()
adapter = EuropeanToUSAAdapter(eu_socket)
device = AmericanDevice()
device.charge(adapter)  # Charging at 110V
```

## Java Implementation

```java
public interface USSocket {
    int voltage();
    int live();
    int neutral();
}

public class EuropeanSocket {
    public int voltage() { return 220; }
    public int live() { return 1; }
    public int neutral() { return -1; }
}

public class EuropeanToUSAdapter implements USSocket {
    private EuropeanSocket socket;
    public EuropeanToUSAdapter(EuropeanSocket socket) { this.socket = socket; }
    public int voltage() { return 110; }
    public int live() { return socket.live(); }
    public int neutral() { return socket.neutral(); }
}

// Usage
EuropeanSocket eu = new EuropeanSocket();
USSocket adapter = new EuropeanToUSAdapter(eu);
System.out.println("Voltage: " + adapter.voltage()); // 110
```
""",

    "11_pub_sub_system.md": """
## Python Implementation

```python
from collections import defaultdict
from typing import Callable, Any

class EventBroker:
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)

    def subscribe(self, topic: str, handler: Callable[[Any], None]):
        self._subscribers[topic].append(handler)

    def unsubscribe(self, topic: str, handler: Callable):
        self._subscribers[topic].remove(handler)

    def publish(self, topic: str, message: Any):
        for handler in self._subscribers[topic]:
            handler(message)

# Usage
broker = EventBroker()

def email_handler(msg): print(f"Email: {msg}")
def sms_handler(msg): print(f"SMS: {msg}")

broker.subscribe("order.placed", email_handler)
broker.subscribe("order.placed", sms_handler)
broker.publish("order.placed", {"order_id": 42, "total": 99.99})
```

## Java Implementation

```java
import java.util.*;
import java.util.function.Consumer;

public class EventBroker {
    private Map<String, List<Consumer<Object>>> subscribers = new HashMap<>();

    public void subscribe(String topic, Consumer<Object> handler) {
        subscribers.computeIfAbsent(topic, k -> new ArrayList<>()).add(handler);
    }

    public void publish(String topic, Object message) {
        subscribers.getOrDefault(topic, Collections.emptyList())
                   .forEach(h -> h.accept(message));
    }

    public static void main(String[] args) {
        EventBroker broker = new EventBroker();
        broker.subscribe("user.signup", msg -> System.out.println("Email: " + msg));
        broker.subscribe("user.signup", msg -> System.out.println("SMS: " + msg));
        broker.publish("user.signup", "New user joined");
    }
}
```
""",

    "12_thread_pool.md": """
## Python Implementation

```python
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Any
import time

class ThreadPool:
    def __init__(self, max_workers: int = 4):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._futures = []

    def submit(self, fn: Callable, *args, **kwargs):
        future = self._executor.submit(fn, *args, **kwargs)
        self._futures.append(future)
        return future

    def shutdown(self, wait: bool = True):
        self._executor.shutdown(wait=wait)

def task(task_id: int, duration: float):
    time.sleep(duration)
    return f"Task {task_id} done"

# Usage
pool = ThreadPool(max_workers=4)
futures = [pool.submit(task, i, 0.1) for i in range(10)]
results = [f.result() for f in futures]
pool.shutdown()
print(results)
```

## Java Implementation

```java
import java.util.concurrent.*;

public class ThreadPoolExample {
    public static void main(String[] args) throws Exception {
        ExecutorService pool = Executors.newFixedThreadPool(4);
        List<Future<String>> futures = new ArrayList<>();

        for (int i = 0; i < 10; i++) {
            final int taskId = i;
            futures.add(pool.submit(() -> {
                Thread.sleep(100);
                return "Task " + taskId + " done";
            }));
        }

        for (Future<String> f : futures) {
            System.out.println(f.get());
        }
        pool.shutdown();
    }
}
```
""",

    "13_load_balancer.md": """
## Python Implementation

```python
from itertools import cycle
from typing import List

class LoadBalancer:
    def __init__(self, servers: List[str], strategy: str = "round_robin"):
        self._servers = servers
        self._strategy = strategy
        self._cycle = cycle(servers)
        self._weights = {s: 1 for s in servers}
        self._active = set(servers)

    def get_server(self) -> str:
        if self._strategy == "round_robin":
            while True:
                server = next(self._cycle)
                if server in self._active:
                    return server
        return list(self._active)[0]

    def mark_down(self, server: str):
        self._active.discard(server)

    def mark_up(self, server: str):
        self._active.add(server)

# Usage
lb = LoadBalancer(["s1:8080", "s2:8080", "s3:8080"])
for _ in range(6):
    print(lb.get_server())  # s1, s2, s3, s1, s2, s3
lb.mark_down("s2:8080")
print(lb.get_server())  # s1 or s3
```

## Java Implementation

```java
import java.util.*;
import java.util.concurrent.atomic.AtomicInteger;

public class LoadBalancer {
    private List<String> servers;
    private Set<String> active;
    private AtomicInteger index = new AtomicInteger(0);

    public LoadBalancer(List<String> servers) {
        this.servers = new ArrayList<>(servers);
        this.active = new HashSet<>(servers);
    }

    public String getServer() {
        List<String> up = servers.stream()
            .filter(active::contains).toList();
        if (up.isEmpty()) throw new RuntimeException("No servers available");
        return up.get(index.getAndIncrement() % up.size());
    }

    public void markDown(String server) { active.remove(server); }
    public void markUp(String server) { active.add(server); }
}
```
""",

    "14_news_feed.md": """
## Python Implementation

```python
import heapq
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Post:
    post_id: int
    user_id: int
    content: str
    timestamp: int

    def __lt__(self, other):
        return self.timestamp > other.timestamp  # Max-heap by timestamp

class NewsFeedService:
    def __init__(self):
        self.posts: Dict[int, List[Post]] = {}  # user_id -> posts
        self.follows: Dict[int, set] = {}

    def post(self, user_id: int, content: str, timestamp: int):
        post = Post(len(self.posts), user_id, content, timestamp)
        self.posts.setdefault(user_id, []).append(post)

    def follow(self, follower: int, followee: int):
        self.follows.setdefault(follower, set()).add(followee)

    def get_feed(self, user_id: int, limit: int = 10) -> List[Post]:
        followees = self.follows.get(user_id, set()) | {user_id}
        all_posts = []
        for uid in followees:
            for p in self.posts.get(uid, []):
                heapq.heappush(all_posts, p)
        return [heapq.heappop(all_posts) for _ in range(min(limit, len(all_posts)))]

# Usage
feed = NewsFeedService()
feed.follow(1, 2)
feed.post(2, "Hello!", 100)
feed.post(2, "World!", 200)
print([p.content for p in feed.get_feed(1)])  # ['World!', 'Hello!']
```

## Java Implementation

```java
import java.util.*;

public class NewsFeedService {
    private Map<Integer, List<int[]>> posts = new HashMap<>(); // userId -> [time, postId]
    private Map<Integer, Set<Integer>> follows = new HashMap<>();

    public void post(int userId, int timestamp) {
        posts.computeIfAbsent(userId, k -> new ArrayList<>())
             .add(new int[]{timestamp, userId});
    }

    public void follow(int follower, int followee) {
        follows.computeIfAbsent(follower, k -> new HashSet<>()).add(followee);
    }

    public List<int[]> getFeed(int userId) {
        PriorityQueue<int[]> pq = new PriorityQueue<>((a, b) -> b[0] - a[0]);
        Set<Integer> followees = follows.getOrDefault(userId, new HashSet<>());
        followees.add(userId);
        for (int uid : followees)
            pq.addAll(posts.getOrDefault(uid, Collections.emptyList()));
        List<int[]> result = new ArrayList<>();
        while (!pq.isEmpty() && result.size() < 10) result.add(pq.poll());
        return result;
    }
}
```
""",

    "15_ecommerce.md": """
## Python Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"

@dataclass
class Product:
    product_id: str
    name: str
    price: float
    stock: int

@dataclass
class CartItem:
    product: Product
    quantity: int

@dataclass
class Order:
    order_id: str
    user_id: str
    items: List[CartItem]
    status: OrderStatus = OrderStatus.PENDING

    def total(self) -> float:
        return sum(item.product.price * item.quantity for item in self.items)

class EcommerceService:
    def __init__(self):
        self._products: Dict[str, Product] = {}
        self._orders: Dict[str, Order] = {}

    def add_product(self, product: Product):
        self._products[product.product_id] = product

    def place_order(self, user_id: str, cart: List[CartItem]) -> Optional[Order]:
        for item in cart:
            if item.product.stock < item.quantity:
                return None
        for item in cart:
            item.product.stock -= item.quantity
        order_id = f"ORD-{len(self._orders)+1}"
        order = Order(order_id, user_id, cart)
        self._orders[order_id] = order
        return order

# Usage
svc = EcommerceService()
p = Product("P1", "Widget", 9.99, 100)
svc.add_product(p)
order = svc.place_order("user1", [CartItem(p, 2)])
print(order.total(), order.status)  # 19.98 OrderStatus.PENDING
```

## Java Implementation

```java
import java.util.*;

public class EcommerceService {
    record Product(String id, String name, double price, int stock) {}
    record CartItem(Product product, int quantity) {}
    record Order(String orderId, String userId, List<CartItem> items) {
        double total() { return items.stream().mapToDouble(i -> i.product().price() * i.quantity()).sum(); }
    }

    private Map<String, Product> products = new HashMap<>();
    private Map<String, Order> orders = new HashMap<>();

    public void addProduct(Product p) { products.put(p.id(), p); }

    public Optional<Order> placeOrder(String userId, List<CartItem> cart) {
        for (CartItem item : cart)
            if (item.product().stock() < item.quantity()) return Optional.empty();
        String id = "ORD-" + (orders.size() + 1);
        Order order = new Order(id, userId, cart);
        orders.put(id, order);
        return Optional.of(order);
    }
}
```
""",

    "16_ride_sharing.md": """
## Python Implementation

```python
from dataclasses import dataclass
from typing import List, Optional, Tuple
import math

@dataclass
class Location:
    lat: float
    lng: float

    def distance_to(self, other: "Location") -> float:
        return math.sqrt((self.lat - other.lat)**2 + (self.lng - other.lng)**2)

@dataclass
class Driver:
    driver_id: str
    name: str
    location: Location
    available: bool = True

@dataclass
class Ride:
    ride_id: str
    rider_id: str
    driver_id: str
    pickup: Location
    dropoff: Location
    status: str = "requested"

class RideSharingService:
    def __init__(self):
        self._drivers: List[Driver] = []
        self._rides: dict[str, Ride] = {}

    def register_driver(self, driver: Driver):
        self._drivers.append(driver)

    def request_ride(self, rider_id: str, pickup: Location, dropoff: Location) -> Optional[Ride]:
        available = [d for d in self._drivers if d.available]
        if not available:
            return None
        nearest = min(available, key=lambda d: d.location.distance_to(pickup))
        nearest.available = False
        ride_id = f"RIDE-{len(self._rides)+1}"
        ride = Ride(ride_id, rider_id, nearest.driver_id, pickup, dropoff)
        self._rides[ride_id] = ride
        return ride

# Usage
svc = RideSharingService()
svc.register_driver(Driver("D1", "Alice", Location(37.7, -122.4)))
ride = svc.request_ride("R1", Location(37.8, -122.5), Location(37.9, -122.6))
print(ride.ride_id, ride.driver_id)  # RIDE-1 D1
```

## Java Implementation

```java
import java.util.*;

public class RideSharingService {
    record Location(double lat, double lng) {
        double distanceTo(Location o) {
            return Math.sqrt(Math.pow(lat-o.lat, 2) + Math.pow(lng-o.lng, 2));
        }
    }
    static class Driver {
        String id, name; Location loc; boolean available = true;
        Driver(String id, String name, Location loc) { this.id=id; this.name=name; this.loc=loc; }
    }
    record Ride(String id, String riderId, String driverId, Location pickup, Location dropoff) {}

    private List<Driver> drivers = new ArrayList<>();

    public void registerDriver(Driver d) { drivers.add(d); }

    public Optional<Ride> requestRide(String riderId, Location pickup, Location dropoff) {
        return drivers.stream().filter(d -> d.available)
            .min(Comparator.comparingDouble(d -> d.loc.distanceTo(pickup)))
            .map(d -> { d.available = false; return new Ride("R-1", riderId, d.id, pickup, dropoff); });
    }
}
```
""",

    "17_chat_system.md": """
## Python Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime

@dataclass
class Message:
    sender_id: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ChatRoom:
    room_id: str
    members: List[str] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)

class ChatService:
    def __init__(self):
        self._rooms: Dict[str, ChatRoom] = {}
        self._user_rooms: Dict[str, List[str]] = {}

    def create_room(self, room_id: str) -> ChatRoom:
        room = ChatRoom(room_id)
        self._rooms[room_id] = room
        return room

    def join_room(self, user_id: str, room_id: str):
        self._rooms[room_id].members.append(user_id)
        self._user_rooms.setdefault(user_id, []).append(room_id)

    def send_message(self, room_id: str, sender_id: str, content: str) -> Message:
        msg = Message(sender_id, content)
        self._rooms[room_id].messages.append(msg)
        return msg

    def get_history(self, room_id: str, limit: int = 50) -> List[Message]:
        return self._rooms[room_id].messages[-limit:]

# Usage
chat = ChatService()
chat.create_room("room1")
chat.join_room("alice", "room1")
chat.join_room("bob", "room1")
chat.send_message("room1", "alice", "Hello!")
msgs = chat.get_history("room1")
print(msgs[0].content)  # Hello!
```

## Java Implementation

```java
import java.util.*;
import java.time.Instant;

public class ChatService {
    record Message(String senderId, String content, Instant ts) {}
    record Room(String id, List<String> members, List<Message> messages) {}

    private Map<String, Room> rooms = new HashMap<>();

    public Room createRoom(String id) {
        Room room = new Room(id, new ArrayList<>(), new ArrayList<>());
        rooms.put(id, room);
        return room;
    }

    public void joinRoom(String userId, String roomId) {
        rooms.get(roomId).members().add(userId);
    }

    public Message sendMessage(String roomId, String senderId, String content) {
        Message msg = new Message(senderId, content, Instant.now());
        rooms.get(roomId).messages().add(msg);
        return msg;
    }

    public List<Message> getHistory(String roomId, int limit) {
        List<Message> msgs = rooms.get(roomId).messages();
        return msgs.subList(Math.max(0, msgs.size() - limit), msgs.size());
    }
}
```
""",

    "18_video_streaming.md": """
## Python Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum

class VideoQuality(Enum):
    SD = "480p"
    HD = "720p"
    FHD = "1080p"
    UHD = "4K"

@dataclass
class VideoSegment:
    segment_id: int
    quality: VideoQuality
    url: str
    duration_s: float

@dataclass
class Video:
    video_id: str
    title: str
    segments: Dict[VideoQuality, List[VideoSegment]] = field(default_factory=dict)
    thumbnail_url: str = ""

class StreamingService:
    def __init__(self):
        self._videos: Dict[str, Video] = {}
        self._cdn_nodes: List[str] = []

    def upload(self, video: Video):
        self._videos[video.video_id] = video

    def get_manifest(self, video_id: str) -> Dict:
        video = self._videos[video_id]
        return {
            "video_id": video_id,
            "title": video.title,
            "qualities": [q.value for q in video.segments.keys()],
            "thumbnail": video.thumbnail_url,
        }

    def get_segment(self, video_id: str, quality: VideoQuality, segment_id: int) -> Optional[VideoSegment]:
        segs = self._videos[video_id].segments.get(quality, [])
        return segs[segment_id] if segment_id < len(segs) else None

    def adaptive_quality(self, bandwidth_mbps: float) -> VideoQuality:
        if bandwidth_mbps >= 25: return VideoQuality.UHD
        if bandwidth_mbps >= 8: return VideoQuality.FHD
        if bandwidth_mbps >= 5: return VideoQuality.HD
        return VideoQuality.SD

# Usage
svc = StreamingService()
v = Video("v1", "My Video")
svc.upload(v)
quality = svc.adaptive_quality(10)
print(quality)  # VideoQuality.FHD
```

## Java Implementation

```java
import java.util.*;

public class StreamingService {
    enum Quality { SD, HD, FHD, UHD }
    record Segment(int id, Quality quality, String url) {}
    record Video(String id, String title, Map<Quality, List<Segment>> segments) {}

    private Map<String, Video> videos = new HashMap<>();

    public void upload(Video v) { videos.put(v.id(), v); }

    public Quality adaptiveQuality(double bandwidthMbps) {
        if (bandwidthMbps >= 25) return Quality.UHD;
        if (bandwidthMbps >= 8)  return Quality.FHD;
        if (bandwidthMbps >= 5)  return Quality.HD;
        return Quality.SD;
    }

    public Optional<Segment> getSegment(String videoId, Quality q, int idx) {
        List<Segment> segs = videos.get(videoId).segments().getOrDefault(q, List.of());
        return idx < segs.size() ? Optional.of(segs.get(idx)) : Optional.empty();
    }
}
```
""",

    "19_database_sharding.md": """
## Python Implementation

```python
import hashlib
from typing import Any, Dict, List

class Shard:
    def __init__(self, shard_id: int):
        self.shard_id = shard_id
        self._data: Dict[str, Any] = {}

    def get(self, key: str) -> Any:
        return self._data.get(key)

    def put(self, key: str, value: Any):
        self._data[key] = value

class ShardedDatabase:
    def __init__(self, num_shards: int = 4):
        self._shards = [Shard(i) for i in range(num_shards)]
        self._num_shards = num_shards

    def _shard_for(self, key: str) -> Shard:
        hash_val = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return self._shards[hash_val % self._num_shards]

    def get(self, key: str) -> Any:
        return self._shard_for(key).get(key)

    def put(self, key: str, value: Any):
        self._shard_for(key).put(key, value)

# Usage
db = ShardedDatabase(num_shards=4)
db.put("user:1001", {"name": "Alice"})
db.put("user:1002", {"name": "Bob"})
print(db.get("user:1001"))  # {'name': 'Alice'}
```

## Java Implementation

```java
import java.util.*;

public class ShardedDatabase {
    private List<Map<String, Object>> shards;
    private int numShards;

    public ShardedDatabase(int numShards) {
        this.numShards = numShards;
        this.shards = new ArrayList<>();
        for (int i = 0; i < numShards; i++) shards.add(new HashMap<>());
    }

    private int shardFor(String key) {
        return Math.abs(key.hashCode()) % numShards;
    }

    public void put(String key, Object value) {
        shards.get(shardFor(key)).put(key, value);
    }

    public Object get(String key) {
        return shards.get(shardFor(key)).get(key);
    }

    public static void main(String[] args) {
        ShardedDatabase db = new ShardedDatabase(4);
        db.put("user:1", Map.of("name", "Alice"));
        System.out.println(db.get("user:1")); // {name=Alice}
    }
}
```
""",

    "20_message_queue.md": """
## Python Implementation

```python
from collections import deque
from threading import Lock, Condition
from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class Message:
    msg_id: int
    payload: Any
    acknowledged: bool = False

class MessageQueue:
    def __init__(self, max_size: int = 1000):
        self._queue: deque[Message] = deque()
        self._max_size = max_size
        self._lock = Lock()
        self._not_empty = Condition(self._lock)
        self._not_full = Condition(self._lock)
        self._counter = 0

    def send(self, payload: Any, timeout: float = None) -> bool:
        with self._not_full:
            if len(self._queue) >= self._max_size:
                self._not_full.wait(timeout)
                if len(self._queue) >= self._max_size:
                    return False
            self._counter += 1
            self._queue.append(Message(self._counter, payload))
            self._not_empty.notify()
            return True

    def receive(self, timeout: float = None) -> Optional[Message]:
        with self._not_empty:
            if not self._queue:
                self._not_empty.wait(timeout)
                if not self._queue:
                    return None
            msg = self._queue.popleft()
            self._not_full.notify()
            return msg

# Usage
q = MessageQueue(max_size=10)
q.send({"event": "user.signup", "user_id": 42})
msg = q.receive()
print(msg.payload)  # {'event': 'user.signup', 'user_id': 42}
```

## Java Implementation

```java
import java.util.concurrent.*;

public class MessageQueue<T> {
    private final BlockingQueue<T> queue;

    public MessageQueue(int capacity) {
        this.queue = new ArrayBlockingQueue<>(capacity);
    }

    public boolean send(T payload) throws InterruptedException {
        return queue.offer(payload, 100, TimeUnit.MILLISECONDS);
    }

    public T receive() throws InterruptedException {
        return queue.poll(100, TimeUnit.MILLISECONDS);
    }

    public static void main(String[] args) throws Exception {
        MessageQueue<String> q = new MessageQueue<>(100);
        q.send("hello");
        System.out.println(q.receive()); // hello
    }
}
```
""",

    "21_search_engine.md": """
## Python Implementation

```python
from collections import defaultdict
from typing import List, Dict, Set
import math

class SearchEngine:
    def __init__(self):
        self._index: Dict[str, Set[int]] = defaultdict(set)  # term -> doc_ids
        self._docs: Dict[int, str] = {}
        self._tf: Dict[int, Dict[str, float]] = defaultdict(dict)  # doc_id -> term -> tf

    def index(self, doc_id: int, content: str):
        self._docs[doc_id] = content
        terms = content.lower().split()
        term_counts = defaultdict(int)
        for term in terms:
            term_counts[term] += 1
            self._index[term].add(doc_id)
        for term, count in term_counts.items():
            self._tf[doc_id][term] = count / len(terms)

    def search(self, query: str, top_k: int = 10) -> List[int]:
        terms = query.lower().split()
        scores: Dict[int, float] = defaultdict(float)
        N = len(self._docs)
        for term in terms:
            doc_ids = self._index.get(term, set())
            if not doc_ids:
                continue
            idf = math.log(N / len(doc_ids))
            for doc_id in doc_ids:
                tf = self._tf[doc_id].get(term, 0)
                scores[doc_id] += tf * idf
        return sorted(scores, key=scores.get, reverse=True)[:top_k]

# Usage
engine = SearchEngine()
engine.index(1, "python is great for data science")
engine.index(2, "java is great for enterprise apps")
engine.index(3, "python web development with django")
print(engine.search("python"))  # [1, 3] or [3, 1]
```

## Java Implementation

```java
import java.util.*;

public class SearchEngine {
    private Map<String, Set<Integer>> index = new HashMap<>();
    private Map<Integer, String> docs = new HashMap<>();

    public void index(int docId, String content) {
        docs.put(docId, content);
        for (String term : content.toLowerCase().split("\\s+")) {
            index.computeIfAbsent(term, k -> new HashSet<>()).add(docId);
        }
    }

    public List<Integer> search(String query) {
        Set<Integer> result = null;
        for (String term : query.toLowerCase().split("\\s+")) {
            Set<Integer> docs = index.getOrDefault(term, Set.of());
            if (result == null) result = new HashSet<>(docs);
            else result.retainAll(docs);
        }
        return result == null ? List.of() : new ArrayList<>(result);
    }
}
```
""",

    "22_recommendation_engine.md": """
## Python Implementation

```python
from typing import Dict, List, Set
from collections import defaultdict
import math

class RecommendationEngine:
    def __init__(self):
        self._user_items: Dict[int, Set[int]] = defaultdict(set)
        self._item_users: Dict[int, Set[int]] = defaultdict(set)

    def record_interaction(self, user_id: int, item_id: int):
        self._user_items[user_id].add(item_id)
        self._item_users[item_id].add(user_id)

    def _jaccard_similarity(self, user_a: int, user_b: int) -> float:
        a, b = self._user_items[user_a], self._user_items[user_b]
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    def recommend(self, user_id: int, top_k: int = 5) -> List[int]:
        seen = self._user_items[user_id]
        scores: Dict[int, float] = defaultdict(float)
        for other_user, items in self._user_items.items():
            if other_user == user_id:
                continue
            sim = self._jaccard_similarity(user_id, other_user)
            for item in items - seen:
                scores[item] += sim
        return sorted(scores, key=scores.get, reverse=True)[:top_k]

# Usage
engine = RecommendationEngine()
engine.record_interaction(1, 10)
engine.record_interaction(1, 20)
engine.record_interaction(2, 10)
engine.record_interaction(2, 30)
print(engine.recommend(1))  # [30] (item 30 seen by similar user 2)
```

## Java Implementation

```java
import java.util.*;

public class RecommendationEngine {
    private Map<Integer, Set<Integer>> userItems = new HashMap<>();
    private Map<Integer, Set<Integer>> itemUsers = new HashMap<>();

    public void recordInteraction(int userId, int itemId) {
        userItems.computeIfAbsent(userId, k -> new HashSet<>()).add(itemId);
        itemUsers.computeIfAbsent(itemId, k -> new HashSet<>()).add(userId);
    }

    public List<Integer> recommend(int userId, int topK) {
        Set<Integer> seen = userItems.getOrDefault(userId, Set.of());
        Map<Integer, Double> scores = new HashMap<>();
        for (Map.Entry<Integer, Set<Integer>> e : userItems.entrySet()) {
            if (e.getKey() == userId) continue;
            Set<Integer> common = new HashSet<>(seen);
            common.retainAll(e.getValue());
            double sim = (double) common.size() / (seen.size() + e.getValue().size() - common.size());
            for (int item : e.getValue()) {
                if (!seen.contains(item))
                    scores.merge(item, sim, Double::sum);
            }
        }
        return scores.entrySet().stream()
            .sorted(Map.Entry.<Integer, Double>comparingByValue().reversed())
            .limit(topK).map(Map.Entry::getKey).toList();
    }
}
```
""",

    "23_leaderboard.md": """
## Python Implementation

```python
import heapq
from typing import List, Tuple
from sortedcontainers import SortedList

class Leaderboard:
    def __init__(self):
        self._scores: dict[str, int] = {}
        self._sorted: SortedList = SortedList(key=lambda x: -x[0])

    def add_score(self, player_id: str, score: int):
        if player_id in self._scores:
            old_score = self._scores[player_id]
            self._sorted.remove((old_score, player_id))
        self._scores[player_id] = score
        self._sorted.add((score, player_id))

    def top_k(self, k: int) -> List[Tuple[str, int]]:
        return [(pid, s) for s, pid in list(self._sorted)[:k]]

    def rank(self, player_id: str) -> int:
        score = self._scores.get(player_id, 0)
        for i, (s, _) in enumerate(self._sorted):
            if s <= score:
                return i + 1
        return len(self._sorted) + 1

# Simple leaderboard without sortedcontainers
class SimpleLeaderboard:
    def __init__(self):
        self._scores: dict[str, int] = {}

    def add_score(self, player_id: str, score: int):
        self._scores[player_id] = max(self._scores.get(player_id, 0), score)

    def top_k(self, k: int) -> List[Tuple[str, int]]:
        return sorted(self._scores.items(), key=lambda x: -x[1])[:k]

# Usage
lb = SimpleLeaderboard()
lb.add_score("alice", 1500)
lb.add_score("bob", 2000)
lb.add_score("carol", 1800)
print(lb.top_k(3))  # [('bob', 2000), ('carol', 1800), ('alice', 1500)]
```

## Java Implementation

```java
import java.util.*;

public class Leaderboard {
    private Map<String, Integer> scores = new HashMap<>();

    public void addScore(String playerId, int score) {
        scores.merge(playerId, score, Integer::max);
    }

    public List<Map.Entry<String, Integer>> topK(int k) {
        return scores.entrySet().stream()
            .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
            .limit(k).toList();
    }

    public static void main(String[] args) {
        Leaderboard lb = new Leaderboard();
        lb.addScore("alice", 1500);
        lb.addScore("bob", 2000);
        lb.topK(2).forEach(e -> System.out.println(e.getKey() + ": " + e.getValue()));
    }
}
```
""",

    "24_payment_system.md": """
## Python Implementation

```python
from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum
from decimal import Decimal
import uuid

class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

@dataclass
class Payment:
    payment_id: str
    user_id: str
    amount: Decimal
    currency: str
    status: PaymentStatus = PaymentStatus.PENDING

class PaymentService:
    def __init__(self):
        self._payments: Dict[str, Payment] = {}
        self._balances: Dict[str, Decimal] = {}

    def deposit(self, user_id: str, amount: Decimal):
        self._balances[user_id] = self._balances.get(user_id, Decimal(0)) + amount

    def process_payment(self, user_id: str, amount: Decimal, currency: str) -> Payment:
        payment_id = str(uuid.uuid4())[:8]
        payment = Payment(payment_id, user_id, amount, currency)
        balance = self._balances.get(user_id, Decimal(0))
        if balance >= amount:
            self._balances[user_id] = balance - amount
            payment.status = PaymentStatus.COMPLETED
        else:
            payment.status = PaymentStatus.FAILED
        self._payments[payment_id] = payment
        return payment

    def refund(self, payment_id: str) -> bool:
        payment = self._payments.get(payment_id)
        if payment and payment.status == PaymentStatus.COMPLETED:
            self._balances[payment.user_id] = self._balances.get(payment.user_id, Decimal(0)) + payment.amount
            payment.status = PaymentStatus.REFUNDED
            return True
        return False

# Usage
svc = PaymentService()
svc.deposit("user1", Decimal("100.00"))
p = svc.process_payment("user1", Decimal("25.00"), "USD")
print(p.status, p.amount)  # PaymentStatus.COMPLETED 25.00
```

## Java Implementation

```java
import java.math.BigDecimal;
import java.util.*;

public class PaymentService {
    enum Status { PENDING, COMPLETED, FAILED, REFUNDED }
    record Payment(String id, String userId, BigDecimal amount, Status status) {}

    private Map<String, BigDecimal> balances = new HashMap<>();
    private Map<String, Payment> payments = new HashMap<>();

    public void deposit(String userId, BigDecimal amount) {
        balances.merge(userId, amount, BigDecimal::add);
    }

    public Payment processPayment(String userId, BigDecimal amount) {
        String id = UUID.randomUUID().toString().substring(0, 8);
        BigDecimal balance = balances.getOrDefault(userId, BigDecimal.ZERO);
        Status status = balance.compareTo(amount) >= 0 ? Status.COMPLETED : Status.FAILED;
        if (status == Status.COMPLETED)
            balances.put(userId, balance.subtract(amount));
        Payment p = new Payment(id, userId, amount, status);
        payments.put(id, p);
        return p;
    }
}
```
""",

    "25_wallet_system.md": """
## Python Implementation

```python
from dataclasses import dataclass
from typing import Dict, List
from decimal import Decimal
from datetime import datetime
from enum import Enum

class TxnType(Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    TRANSFER = "transfer"

@dataclass
class Transaction:
    txn_id: str
    user_id: str
    amount: Decimal
    txn_type: TxnType
    timestamp: datetime = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()

class WalletService:
    def __init__(self):
        self._balances: Dict[str, Decimal] = {}
        self._history: Dict[str, List[Transaction]] = {}
        self._txn_count = 0

    def _new_txn_id(self) -> str:
        self._txn_count += 1
        return f"TXN-{self._txn_count}"

    def credit(self, user_id: str, amount: Decimal) -> Transaction:
        self._balances[user_id] = self._balances.get(user_id, Decimal(0)) + amount
        txn = Transaction(self._new_txn_id(), user_id, amount, TxnType.CREDIT)
        self._history.setdefault(user_id, []).append(txn)
        return txn

    def transfer(self, from_id: str, to_id: str, amount: Decimal) -> bool:
        if self._balances.get(from_id, Decimal(0)) < amount:
            return False
        self._balances[from_id] -= amount
        self._balances[to_id] = self._balances.get(to_id, Decimal(0)) + amount
        txn = Transaction(self._new_txn_id(), from_id, amount, TxnType.TRANSFER)
        self._history.setdefault(from_id, []).append(txn)
        return True

    def balance(self, user_id: str) -> Decimal:
        return self._balances.get(user_id, Decimal(0))

# Usage
wallet = WalletService()
wallet.credit("alice", Decimal("100"))
wallet.credit("bob", Decimal("50"))
wallet.transfer("alice", "bob", Decimal("30"))
print(wallet.balance("alice"), wallet.balance("bob"))  # 70 80
```

## Java Implementation

```java
import java.math.BigDecimal;
import java.util.*;

public class WalletService {
    private Map<String, BigDecimal> balances = new HashMap<>();
    private int txnCount = 0;

    public void credit(String userId, BigDecimal amount) {
        balances.merge(userId, amount, BigDecimal::add);
    }

    public boolean transfer(String from, String to, BigDecimal amount) {
        BigDecimal fromBal = balances.getOrDefault(from, BigDecimal.ZERO);
        if (fromBal.compareTo(amount) < 0) return false;
        balances.put(from, fromBal.subtract(amount));
        balances.merge(to, amount, BigDecimal::add);
        return true;
    }

    public BigDecimal balance(String userId) {
        return balances.getOrDefault(userId, BigDecimal.ZERO);
    }
}
```
""",

    "26_followers_system.md": """
## Python Implementation

```python
from typing import Dict, Set, List

class FollowersService:
    def __init__(self):
        self._following: Dict[int, Set[int]] = {}  # user_id -> set of followed
        self._followers: Dict[int, Set[int]] = {}  # user_id -> set of followers

    def follow(self, follower_id: int, followee_id: int):
        self._following.setdefault(follower_id, set()).add(followee_id)
        self._followers.setdefault(followee_id, set()).add(follower_id)

    def unfollow(self, follower_id: int, followee_id: int):
        self._following.get(follower_id, set()).discard(followee_id)
        self._followers.get(followee_id, set()).discard(follower_id)

    def get_followers(self, user_id: int) -> List[int]:
        return list(self._followers.get(user_id, set()))

    def get_following(self, user_id: int) -> List[int]:
        return list(self._following.get(user_id, set()))

    def follower_count(self, user_id: int) -> int:
        return len(self._followers.get(user_id, set()))

    def is_following(self, follower_id: int, followee_id: int) -> bool:
        return followee_id in self._following.get(follower_id, set())

    def mutual_follows(self, user_a: int, user_b: int) -> bool:
        return self.is_following(user_a, user_b) and self.is_following(user_b, user_a)

# Usage
svc = FollowersService()
svc.follow(1, 2)
svc.follow(2, 1)
print(svc.follower_count(2))  # 1
print(svc.mutual_follows(1, 2))  # True
```

## Java Implementation

```java
import java.util.*;

public class FollowersService {
    private Map<Integer, Set<Integer>> following = new HashMap<>();
    private Map<Integer, Set<Integer>> followers = new HashMap<>();

    public void follow(int followerId, int followeeId) {
        following.computeIfAbsent(followerId, k -> new HashSet<>()).add(followeeId);
        followers.computeIfAbsent(followeeId, k -> new HashSet<>()).add(followerId);
    }

    public void unfollow(int followerId, int followeeId) {
        following.getOrDefault(followerId, Set.of()).remove(followeeId);
        followers.getOrDefault(followeeId, Set.of()).remove(followerId);
    }

    public int followerCount(int userId) {
        return followers.getOrDefault(userId, Set.of()).size();
    }

    public boolean isFollowing(int follower, int followee) {
        return following.getOrDefault(follower, Set.of()).contains(followee);
    }
}
```
""",

    "27_notifications.md": """
## Python Implementation

```python
from dataclasses import dataclass
from typing import List, Dict, Callable
from enum import Enum
from datetime import datetime
import threading

class NotifChannel(Enum):
    PUSH = "push"
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"

@dataclass
class Notification:
    notif_id: str
    user_id: str
    title: str
    body: str
    channel: NotifChannel
    timestamp: datetime = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()

class NotificationService:
    def __init__(self):
        self._handlers: Dict[NotifChannel, Callable] = {}
        self._unread: Dict[str, List[Notification]] = {}
        self._counter = 0

    def register_handler(self, channel: NotifChannel, handler: Callable):
        self._handlers[channel] = handler

    def send(self, user_id: str, title: str, body: str, channel: NotifChannel):
        self._counter += 1
        notif = Notification(f"N-{self._counter}", user_id, title, body, channel)
        self._unread.setdefault(user_id, []).append(notif)
        handler = self._handlers.get(channel)
        if handler:
            threading.Thread(target=handler, args=(notif,), daemon=True).start()

    def get_unread(self, user_id: str) -> List[Notification]:
        return self._unread.get(user_id, [])

    def mark_read(self, user_id: str):
        self._unread[user_id] = []

# Usage
svc = NotificationService()
svc.register_handler(NotifChannel.IN_APP, lambda n: print(f"[IN-APP] {n.title}"))
svc.send("user1", "New follower", "Alice followed you", NotifChannel.IN_APP)
print(len(svc.get_unread("user1")))  # 1
```

## Java Implementation

```java
import java.util.*;
import java.util.concurrent.*;
import java.util.function.Consumer;

public class NotificationService {
    enum Channel { PUSH, EMAIL, SMS, IN_APP }
    record Notification(String id, String userId, String title, String body, Channel channel) {}

    private Map<Channel, Consumer<Notification>> handlers = new EnumMap<>(Channel.class);
    private Map<String, List<Notification>> unread = new HashMap<>();
    private int counter = 0;
    private ExecutorService executor = Executors.newCachedThreadPool();

    public void registerHandler(Channel ch, Consumer<Notification> handler) {
        handlers.put(ch, handler);
    }

    public void send(String userId, String title, String body, Channel ch) {
        Notification n = new Notification("N-" + (++counter), userId, title, body, ch);
        unread.computeIfAbsent(userId, k -> new ArrayList<>()).add(n);
        Consumer<Notification> h = handlers.get(ch);
        if (h != null) executor.submit(() -> h.accept(n));
    }

    public List<Notification> getUnread(String userId) {
        return unread.getOrDefault(userId, List.of());
    }
}
```
""",

    "28_api_gateway.md": """
## Python Implementation

```python
from dataclasses import dataclass
from typing import Dict, Callable, Optional
from collections import defaultdict
import time

@dataclass
class Request:
    method: str
    path: str
    headers: Dict[str, str]
    body: Optional[str] = None

@dataclass
class Response:
    status_code: int
    body: str
    headers: Dict[str, str] = None

class RateLimiter:
    def __init__(self, max_rps: int):
        self._max_rps = max_rps
        self._counts: Dict[str, list] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()
        self._counts[client_id] = [t for t in self._counts[client_id] if now - t < 1.0]
        if len(self._counts[client_id]) >= self._max_rps:
            return False
        self._counts[client_id].append(now)
        return True

class APIGateway:
    def __init__(self, rate_limit: int = 100):
        self._routes: Dict[str, Callable] = {}
        self._rate_limiter = RateLimiter(rate_limit)
        self._auth_keys: set = set()

    def register_route(self, path: str, handler: Callable):
        self._routes[path] = handler

    def add_api_key(self, key: str):
        self._auth_keys.add(key)

    def handle(self, request: Request, client_id: str) -> Response:
        api_key = request.headers.get("X-API-Key", "")
        if api_key not in self._auth_keys:
            return Response(401, "Unauthorized")
        if not self._rate_limiter.is_allowed(client_id):
            return Response(429, "Too Many Requests")
        handler = self._routes.get(request.path)
        if not handler:
            return Response(404, "Not Found")
        return handler(request)

# Usage
gw = APIGateway(rate_limit=10)
gw.add_api_key("secret-key")
gw.register_route("/users", lambda req: Response(200, '{"users": []}'))
resp = gw.handle(Request("GET", "/users", {"X-API-Key": "secret-key"}), "client1")
print(resp.status_code, resp.body)  # 200 {"users": []}
```

## Java Implementation

```java
import java.util.*;
import java.util.function.Function;

public class APIGateway {
    private Map<String, Function<Map<String, String>, String>> routes = new HashMap<>();
    private Set<String> apiKeys = new HashSet<>();
    private Map<String, List<Long>> rateCounts = new HashMap<>();
    private int maxRps;

    public APIGateway(int maxRps) { this.maxRps = maxRps; }

    public void addRoute(String path, Function<Map<String, String>, String> handler) {
        routes.put(path, handler);
    }

    public void addApiKey(String key) { apiKeys.add(key); }

    public Map<String, Object> handle(String path, Map<String, String> headers, String clientId) {
        if (!apiKeys.contains(headers.getOrDefault("X-API-Key", "")))
            return Map.of("status", 401, "body", "Unauthorized");
        if (!isAllowed(clientId))
            return Map.of("status", 429, "body", "Too Many Requests");
        Function<Map<String, String>, String> handler = routes.get(path);
        if (handler == null)
            return Map.of("status", 404, "body", "Not Found");
        return Map.of("status", 200, "body", handler.apply(headers));
    }

    private boolean isAllowed(String clientId) {
        long now = System.currentTimeMillis();
        List<Long> ts = rateCounts.computeIfAbsent(clientId, k -> new ArrayList<>());
        ts.removeIf(t -> now - t > 1000);
        if (ts.size() >= maxRps) return false;
        ts.add(now);
        return true;
    }
}
```
""",

    "29_websocket_server.md": """
## Python Implementation

```python
from dataclasses import dataclass, field
from typing import Dict, Set, Callable, Any
from collections import defaultdict
import json
import threading

@dataclass
class WebSocketConnection:
    conn_id: str
    user_id: str
    rooms: Set[str] = field(default_factory=set)
    send_fn: Callable = None

class WebSocketServer:
    def __init__(self):
        self._connections: Dict[str, WebSocketConnection] = {}
        self._rooms: Dict[str, Set[str]] = defaultdict(set)
        self._message_handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()

    def connect(self, conn_id: str, user_id: str, send_fn: Callable):
        with self._lock:
            conn = WebSocketConnection(conn_id, user_id, send_fn=send_fn)
            self._connections[conn_id] = conn

    def disconnect(self, conn_id: str):
        with self._lock:
            conn = self._connections.pop(conn_id, None)
            if conn:
                for room in conn.rooms:
                    self._rooms[room].discard(conn_id)

    def join_room(self, conn_id: str, room: str):
        with self._lock:
            self._connections[conn_id].rooms.add(room)
            self._rooms[room].add(conn_id)

    def broadcast(self, room: str, message: Any):
        with self._lock:
            payload = json.dumps(message)
            for conn_id in self._rooms[room]:
                conn = self._connections.get(conn_id)
                if conn and conn.send_fn:
                    conn.send_fn(payload)

    def register_handler(self, event: str, handler: Callable):
        self._message_handlers[event] = handler

    def on_message(self, conn_id: str, raw: str):
        data = json.loads(raw)
        event = data.get("type")
        handler = self._message_handlers.get(event)
        if handler:
            handler(conn_id, data)

# Usage
messages = []
server = WebSocketServer()
server.connect("c1", "alice", lambda msg: messages.append(("c1", msg)))
server.connect("c2", "bob", lambda msg: messages.append(("c2", msg)))
server.join_room("c1", "general")
server.join_room("c2", "general")
server.broadcast("general", {"type": "message", "text": "Hello!"})
print(len(messages))  # 2
```

## Java Implementation

```java
import java.util.*;
import java.util.concurrent.*;
import java.util.function.Consumer;

public class WebSocketServer {
    record Connection(String id, String userId, Set<String> rooms, Consumer<String> send) {}

    private Map<String, Connection> connections = new ConcurrentHashMap<>();
    private Map<String, Set<String>> rooms = new ConcurrentHashMap<>();

    public void connect(String connId, String userId, Consumer<String> send) {
        connections.put(connId, new Connection(connId, userId, new HashSet<>(), send));
    }

    public void disconnect(String connId) {
        Connection conn = connections.remove(connId);
        if (conn != null) conn.rooms().forEach(r -> rooms.getOrDefault(r, Set.of()).remove(connId));
    }

    public void joinRoom(String connId, String room) {
        connections.get(connId).rooms().add(room);
        rooms.computeIfAbsent(room, k -> ConcurrentHashMap.newKeySet()).add(connId);
    }

    public void broadcast(String room, String message) {
        rooms.getOrDefault(room, Set.of()).stream()
            .map(connections::get).filter(Objects::nonNull)
            .forEach(c -> c.send().accept(message));
    }
}
```
""",

    "30_distributed_transaction.md": """
## Python Implementation

```python
from enum import Enum
from typing import List, Callable, Optional

class TxnState(Enum):
    INITIAL = "initial"
    PREPARED = "prepared"
    COMMITTED = "committed"
    ABORTED = "aborted"

class Participant:
    def __init__(self, name: str):
        self.name = name
        self.state = TxnState.INITIAL

    def prepare(self) -> bool:
        # Simulate prepare phase - returns True if ready to commit
        self.state = TxnState.PREPARED
        print(f"[{self.name}] Prepared")
        return True

    def commit(self):
        self.state = TxnState.COMMITTED
        print(f"[{self.name}] Committed")

    def abort(self):
        self.state = TxnState.ABORTED
        print(f"[{self.name}] Aborted")

class TwoPhaseCommit:
    def __init__(self, participants: List[Participant]):
        self._participants = participants

    def execute(self) -> bool:
        # Phase 1: Prepare
        votes = [p.prepare() for p in self._participants]
        if all(votes):
            # Phase 2: Commit
            for p in self._participants:
                p.commit()
            return True
        else:
            # Phase 2: Abort
            for p in self._participants:
                p.abort()
            return False

# Saga Pattern
class SagaStep:
    def __init__(self, action: Callable, compensation: Callable):
        self.action = action
        self.compensation = compensation

class SagaOrchestrator:
    def __init__(self, steps: List[SagaStep]):
        self._steps = steps

    def execute(self):
        completed = []
        for step in self._steps:
            try:
                step.action()
                completed.append(step)
            except Exception as e:
                print(f"Step failed: {e}, compensating...")
                for s in reversed(completed):
                    s.compensation()
                return False
        return True

# Usage
p1, p2, p3 = Participant("DB1"), Participant("DB2"), Participant("DB3")
txn = TwoPhaseCommit([p1, p2, p3])
print("Success:", txn.execute())
```

## Java Implementation

```java
import java.util.*;

public class TwoPhaseCommit {
    interface Participant {
        boolean prepare();
        void commit();
        void abort();
    }

    private List<Participant> participants;

    public TwoPhaseCommit(List<Participant> participants) {
        this.participants = participants;
    }

    public boolean execute() {
        boolean allReady = participants.stream().allMatch(Participant::prepare);
        if (allReady) {
            participants.forEach(Participant::commit);
        } else {
            participants.forEach(Participant::abort);
        }
        return allReady;
    }

    public static void main(String[] args) {
        List<Participant> ps = List.of(
            new Participant() {
                public boolean prepare() { System.out.println("DB1 prepared"); return true; }
                public void commit() { System.out.println("DB1 committed"); }
                public void abort() { System.out.println("DB1 aborted"); }
            }
        );
        System.out.println("Success: " + new TwoPhaseCommit(ps).execute());
    }
}
```
""",

    "31_circuit_breaker.md": """
## Python Implementation

```python
from enum import Enum
from typing import Callable, TypeVar, Any
import time
import functools

T = TypeVar("T")

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0,
                 half_open_max_calls: int = 3):
        self.state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._half_open_max_calls = half_open_max_calls
        self._opened_at: float = 0

    def call(self, fn: Callable[..., T], *args, **kwargs) -> T:
        if self.state == CircuitState.OPEN:
            if time.time() - self._opened_at >= self._recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self._success_count = 0
            else:
                raise Exception("Circuit is OPEN - request rejected")

        try:
            result = fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self._half_open_max_calls:
                self.state = CircuitState.CLOSED
                self._failure_count = 0
        else:
            self._failure_count = 0

    def _on_failure(self):
        self._failure_count += 1
        if self._failure_count >= self._failure_threshold:
            self.state = CircuitState.OPEN
            self._opened_at = time.time()

# Usage
cb = CircuitBreaker(failure_threshold=3)

def unstable_api():
    raise ConnectionError("Service down")

for i in range(5):
    try:
        cb.call(unstable_api)
    except Exception as e:
        print(f"[{cb.state.value}] {e}")
```

## Java Implementation

```java
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.Supplier;

public class CircuitBreaker {
    enum State { CLOSED, OPEN, HALF_OPEN }

    private volatile State state = State.CLOSED;
    private AtomicInteger failures = new AtomicInteger(0);
    private final int threshold;
    private final long recoveryMs;
    private volatile long openedAt;

    public CircuitBreaker(int threshold, long recoveryMs) {
        this.threshold = threshold;
        this.recoveryMs = recoveryMs;
    }

    public <T> T call(Supplier<T> fn) {
        if (state == State.OPEN) {
            if (System.currentTimeMillis() - openedAt >= recoveryMs) {
                state = State.HALF_OPEN;
            } else {
                throw new RuntimeException("Circuit is OPEN");
            }
        }
        try {
            T result = fn.get();
            onSuccess();
            return result;
        } catch (Exception e) {
            onFailure();
            throw e;
        }
    }

    private void onSuccess() {
        failures.set(0);
        state = State.CLOSED;
    }

    private void onFailure() {
        if (failures.incrementAndGet() >= threshold) {
            state = State.OPEN;
            openedAt = System.currentTimeMillis();
        }
    }
}
```
""",

    "32_saga_pattern.md": """
## Python Implementation

```python
from dataclasses import dataclass
from typing import List, Callable, Optional

@dataclass
class SagaStep:
    name: str
    execute: Callable
    compensate: Callable

class SagaResult:
    def __init__(self, success: bool, failed_step: Optional[str] = None):
        self.success = success
        self.failed_step = failed_step

class SagaOrchestrator:
    def __init__(self, steps: List[SagaStep]):
        self._steps = steps

    def run(self) -> SagaResult:
        executed: List[SagaStep] = []
        for step in self._steps:
            try:
                print(f"Executing: {step.name}")
                step.execute()
                executed.append(step)
            except Exception as e:
                print(f"Failed at {step.name}: {e}. Rolling back...")
                for s in reversed(executed):
                    try:
                        s.compensate()
                        print(f"Compensated: {s.name}")
                    except Exception as ce:
                        print(f"Compensation failed for {s.name}: {ce}")
                return SagaResult(False, step.name)
        return SagaResult(True)

# Usage: Order saga
order_id = "ORD-1"
inventory_reserved = False
payment_charged = False

steps = [
    SagaStep(
        "reserve_inventory",
        execute=lambda: globals().update({"inventory_reserved": True}),
        compensate=lambda: globals().update({"inventory_reserved": False})
    ),
    SagaStep(
        "charge_payment",
        execute=lambda: globals().update({"payment_charged": True}),
        compensate=lambda: globals().update({"payment_charged": False})
    ),
    SagaStep(
        "ship_order",
        execute=lambda: (_ for _ in ()).throw(RuntimeError("Shipping failed")),
        compensate=lambda: print("Shipping compensation (no-op)")
    ),
]

result = SagaOrchestrator(steps).run()
print("Success:", result.success, "| inventory:", inventory_reserved)
```

## Java Implementation

```java
import java.util.*;

public class SagaOrchestrator {
    record Step(String name, Runnable execute, Runnable compensate) {}

    private final List<Step> steps;

    public SagaOrchestrator(List<Step> steps) { this.steps = steps; }

    public boolean run() {
        Deque<Step> executed = new ArrayDeque<>();
        for (Step step : steps) {
            try {
                System.out.println("Executing: " + step.name());
                step.execute().run();
                executed.push(step);
            } catch (Exception e) {
                System.out.println("Failed: " + step.name() + " - rolling back");
                executed.forEach(s -> {
                    try { s.compensate().run(); }
                    catch (Exception ce) { System.err.println("Compensation failed: " + s.name()); }
                });
                return false;
            }
        }
        return true;
    }
}
```
""",

    "33_photo_sharing.md": """
## Python Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
import uuid

@dataclass
class Photo:
    photo_id: str
    user_id: str
    url: str
    caption: str
    likes: int = 0
    comments: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

class PhotoSharingService:
    def __init__(self):
        self._photos: Dict[str, Photo] = {}
        self._user_photos: Dict[str, List[str]] = {}
        self._follows: Dict[str, set] = {}

    def upload(self, user_id: str, url: str, caption: str) -> Photo:
        photo = Photo(str(uuid.uuid4())[:8], user_id, url, caption)
        self._photos[photo.photo_id] = photo
        self._user_photos.setdefault(user_id, []).append(photo.photo_id)
        return photo

    def like(self, photo_id: str) -> int:
        self._photos[photo_id].likes += 1
        return self._photos[photo_id].likes

    def comment(self, photo_id: str, text: str):
        self._photos[photo_id].comments.append(text)

    def follow(self, follower_id: str, followee_id: str):
        self._follows.setdefault(follower_id, set()).add(followee_id)

    def get_feed(self, user_id: str, limit: int = 20) -> List[Photo]:
        followees = self._follows.get(user_id, set())
        all_photos = []
        for uid in followees:
            for pid in self._user_photos.get(uid, []):
                all_photos.append(self._photos[pid])
        return sorted(all_photos, key=lambda p: p.created_at, reverse=True)[:limit]

# Usage
svc = PhotoSharingService()
svc.follow("alice", "bob")
p = svc.upload("bob", "https://cdn.example.com/photo.jpg", "Sunset!")
svc.like(p.photo_id)
print(p.likes, p.caption)  # 1 Sunset!
feed = svc.get_feed("alice")
print(len(feed))  # 1
```

## Java Implementation

```java
import java.util.*;

public class PhotoSharingService {
    record Photo(String id, String userId, String url, String caption) {}

    private Map<String, Photo> photos = new HashMap<>();
    private Map<String, List<String>> userPhotos = new HashMap<>();
    private Map<String, Set<String>> follows = new HashMap<>();
    private Map<String, Integer> likes = new HashMap<>();
    private int counter = 0;

    public Photo upload(String userId, String url, String caption) {
        Photo p = new Photo("P-" + (++counter), userId, url, caption);
        photos.put(p.id(), p);
        userPhotos.computeIfAbsent(userId, k -> new ArrayList<>()).add(p.id());
        return p;
    }

    public void follow(String from, String to) {
        follows.computeIfAbsent(from, k -> new HashSet<>()).add(to);
    }

    public int like(String photoId) {
        return likes.merge(photoId, 1, Integer::sum);
    }

    public List<Photo> getFeed(String userId) {
        return follows.getOrDefault(userId, Set.of()).stream()
            .flatMap(uid -> userPhotos.getOrDefault(uid, List.of()).stream())
            .map(photos::get).filter(Objects::nonNull).toList();
    }
}
```
""",

    "34_time_series_db.md": """
## Python Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import bisect

@dataclass
class DataPoint:
    timestamp: int  # Unix ms
    value: float
    tags: Dict[str, str] = field(default_factory=dict)

class TimeSeries:
    def __init__(self, name: str):
        self.name = name
        self._timestamps: List[int] = []
        self._values: List[float] = []

    def write(self, ts: int, value: float):
        idx = bisect.bisect_left(self._timestamps, ts)
        self._timestamps.insert(idx, ts)
        self._values.insert(idx, value)

    def query(self, start: int, end: int) -> List[Tuple[int, float]]:
        lo = bisect.bisect_left(self._timestamps, start)
        hi = bisect.bisect_right(self._timestamps, end)
        return list(zip(self._timestamps[lo:hi], self._values[lo:hi]))

    def aggregate(self, start: int, end: int, fn: str = "avg") -> Optional[float]:
        points = [v for _, v in self.query(start, end)]
        if not points:
            return None
        if fn == "avg": return sum(points) / len(points)
        if fn == "sum": return sum(points)
        if fn == "max": return max(points)
        if fn == "min": return min(points)
        return None

class TimeSeriesDB:
    def __init__(self):
        self._series: Dict[str, TimeSeries] = {}

    def write(self, metric: str, ts: int, value: float):
        if metric not in self._series:
            self._series[metric] = TimeSeries(metric)
        self._series[metric].write(ts, value)

    def query(self, metric: str, start: int, end: int) -> List[Tuple[int, float]]:
        return self._series.get(metric, TimeSeries(metric)).query(start, end)

# Usage
db = TimeSeriesDB()
for i, v in enumerate([12.5, 13.0, 11.8, 14.2]):
    db.write("cpu.usage", 1000 + i * 1000, v)
print(db.query("cpu.usage", 1000, 4000))
```

## Java Implementation

```java
import java.util.*;

public class TimeSeriesDB {
    private Map<String, TreeMap<Long, Double>> series = new HashMap<>();

    public void write(String metric, long timestamp, double value) {
        series.computeIfAbsent(metric, k -> new TreeMap<>()).put(timestamp, value);
    }

    public NavigableMap<Long, Double> query(String metric, long start, long end) {
        TreeMap<Long, Double> ts = series.getOrDefault(metric, new TreeMap<>());
        return ts.subMap(start, true, end, true);
    }

    public OptionalDouble aggregate(String metric, long start, long end, String fn) {
        Collection<Double> values = query(metric, start, end).values();
        return switch (fn) {
            case "avg" -> values.stream().mapToDouble(d -> d).average();
            case "max" -> values.stream().mapToDouble(d -> d).max();
            case "min" -> values.stream().mapToDouble(d -> d).min();
            default -> OptionalDouble.empty();
        };
    }
}
```
""",

    "35_log_aggregation.md": """
## Python Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
from collections import defaultdict
import re

class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

@dataclass
class LogEntry:
    timestamp: datetime
    level: LogLevel
    service: str
    message: str
    trace_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

class LogAggregator:
    def __init__(self):
        self._logs: List[LogEntry] = []
        self._index: Dict[str, List[int]] = defaultdict(list)  # service -> log indices

    def ingest(self, entry: LogEntry):
        idx = len(self._logs)
        self._logs.append(entry)
        self._index[entry.service].append(idx)

    def query(self, service: Optional[str] = None,
              level: Optional[LogLevel] = None,
              start: Optional[datetime] = None,
              end: Optional[datetime] = None,
              pattern: Optional[str] = None,
              limit: int = 100) -> List[LogEntry]:
        candidates = self._logs
        if service:
            candidates = [self._logs[i] for i in self._index.get(service, [])]
        results = []
        for log in candidates:
            if level and log.level.value < level.value:
                continue
            if start and log.timestamp < start:
                continue
            if end and log.timestamp > end:
                continue
            if pattern and not re.search(pattern, log.message):
                continue
            results.append(log)
            if len(results) >= limit:
                break
        return results

    def error_rate(self, service: str, window_s: int = 60) -> float:
        now = datetime.now()
        indices = self._index.get(service, [])
        logs = [self._logs[i] for i in indices]
        recent = [l for l in logs if (now - l.timestamp).total_seconds() <= window_s]
        if not recent:
            return 0.0
        errors = sum(1 for l in recent if l.level.value >= LogLevel.ERROR.value)
        return errors / len(recent)

# Usage
agg = LogAggregator()
agg.ingest(LogEntry(datetime.now(), LogLevel.ERROR, "auth-service", "Login failed", trace_id="t1"))
agg.ingest(LogEntry(datetime.now(), LogLevel.INFO, "auth-service", "User logged in"))
results = agg.query(service="auth-service", level=LogLevel.ERROR)
print(len(results), results[0].message)  # 1 Login failed
```

## Java Implementation

```java
import java.util.*;
import java.time.Instant;

public class LogAggregator {
    enum Level { DEBUG, INFO, WARNING, ERROR, CRITICAL }
    record LogEntry(Instant ts, Level level, String service, String message) {}

    private List<LogEntry> logs = new ArrayList<>();
    private Map<String, List<Integer>> index = new HashMap<>();

    public void ingest(LogEntry entry) {
        int idx = logs.size();
        logs.add(entry);
        index.computeIfAbsent(entry.service(), k -> new ArrayList<>()).add(idx);
    }

    public List<LogEntry> query(String service, Level minLevel, int limit) {
        List<Integer> indices = index.getOrDefault(service, List.of());
        return indices.stream()
            .map(logs::get)
            .filter(l -> l.level().ordinal() >= minLevel.ordinal())
            .limit(limit).toList();
    }
}
```
""",

    "36_like_comment_system.md": """
## Python Implementation

```python
from dataclasses import dataclass, field
from typing import Dict, Set, List, Optional
from datetime import datetime

@dataclass
class Comment:
    comment_id: str
    user_id: str
    content_id: str
    text: str
    created_at: datetime = field(default_factory=datetime.now)
    parent_id: Optional[str] = None  # For replies

class LikeCommentService:
    def __init__(self):
        self._likes: Dict[str, Set[str]] = {}          # content_id -> set of user_ids
        self._comments: Dict[str, Comment] = {}         # comment_id -> comment
        self._content_comments: Dict[str, List[str]] = {}  # content_id -> comment_ids
        self._counter = 0

    def like(self, user_id: str, content_id: str) -> int:
        self._likes.setdefault(content_id, set()).add(user_id)
        return len(self._likes[content_id])

    def unlike(self, user_id: str, content_id: str) -> int:
        self._likes.get(content_id, set()).discard(user_id)
        return len(self._likes.get(content_id, set()))

    def like_count(self, content_id: str) -> int:
        return len(self._likes.get(content_id, set()))

    def has_liked(self, user_id: str, content_id: str) -> bool:
        return user_id in self._likes.get(content_id, set())

    def comment(self, user_id: str, content_id: str, text: str,
                parent_id: Optional[str] = None) -> Comment:
        self._counter += 1
        c = Comment(f"C-{self._counter}", user_id, content_id, text, parent_id=parent_id)
        self._comments[c.comment_id] = c
        self._content_comments.setdefault(content_id, []).append(c.comment_id)
        return c

    def get_comments(self, content_id: str) -> List[Comment]:
        ids = self._content_comments.get(content_id, [])
        return [self._comments[i] for i in ids]

# Usage
svc = LikeCommentService()
svc.like("alice", "post1")
svc.like("bob", "post1")
print(svc.like_count("post1"))  # 2
c = svc.comment("alice", "post1", "Great post!")
print(c.text, svc.get_comments("post1")[0].text)  # Great post! Great post!
```

## Java Implementation

```java
import java.util.*;

public class LikeCommentService {
    record Comment(String id, String userId, String contentId, String text) {}

    private Map<String, Set<String>> likes = new HashMap<>();
    private Map<String, List<Comment>> comments = new HashMap<>();
    private int counter = 0;

    public int like(String userId, String contentId) {
        return likes.computeIfAbsent(contentId, k -> new HashSet<>()).size();
    }

    public void unlike(String userId, String contentId) {
        likes.getOrDefault(contentId, Set.of()).remove(userId);
    }

    public int likeCount(String contentId) {
        return likes.getOrDefault(contentId, Set.of()).size();
    }

    public Comment comment(String userId, String contentId, String text) {
        Comment c = new Comment("C-" + (++counter), userId, contentId, text);
        comments.computeIfAbsent(contentId, k -> new ArrayList<>()).add(c);
        return c;
    }

    public List<Comment> getComments(String contentId) {
        return comments.getOrDefault(contentId, List.of());
    }
}
```
""",

    "38_transaction_ledger.md": """
## Python Implementation

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime
from enum import Enum
import uuid

class EntryType(Enum):
    DEBIT = "debit"
    CREDIT = "credit"

@dataclass
class LedgerEntry:
    entry_id: str
    account_id: str
    entry_type: EntryType
    amount: Decimal
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    reference_id: Optional[str] = None

class TransactionLedger:
    def __init__(self):
        self._entries: List[LedgerEntry] = []
        self._account_entries: Dict[str, List[int]] = {}
        self._balances: Dict[str, Decimal] = {}

    def _add_entry(self, account_id: str, entry_type: EntryType,
                   amount: Decimal, description: str, ref_id: Optional[str] = None) -> LedgerEntry:
        entry = LedgerEntry(str(uuid.uuid4())[:8], account_id, entry_type, amount, description, reference_id=ref_id)
        idx = len(self._entries)
        self._entries.append(entry)
        self._account_entries.setdefault(account_id, []).append(idx)
        if entry_type == EntryType.CREDIT:
            self._balances[account_id] = self._balances.get(account_id, Decimal(0)) + amount
        else:
            self._balances[account_id] = self._balances.get(account_id, Decimal(0)) - amount
        return entry

    def transfer(self, from_account: str, to_account: str, amount: Decimal, description: str) -> str:
        txn_id = str(uuid.uuid4())[:8]
        self._add_entry(from_account, EntryType.DEBIT, amount, description, txn_id)
        self._add_entry(to_account, EntryType.CREDIT, amount, description, txn_id)
        return txn_id

    def balance(self, account_id: str) -> Decimal:
        return self._balances.get(account_id, Decimal(0))

    def history(self, account_id: str) -> List[LedgerEntry]:
        indices = self._account_entries.get(account_id, [])
        return [self._entries[i] for i in indices]

# Usage
ledger = TransactionLedger()
ledger._add_entry("acc1", EntryType.CREDIT, Decimal("1000"), "Initial deposit")
txn = ledger.transfer("acc1", "acc2", Decimal("250"), "Payment")
print(ledger.balance("acc1"), ledger.balance("acc2"))  # 750 250
```

## Java Implementation

```java
import java.math.BigDecimal;
import java.util.*;

public class TransactionLedger {
    enum EntryType { DEBIT, CREDIT }
    record Entry(String id, String accountId, EntryType type, BigDecimal amount, String desc) {}

    private List<Entry> entries = new ArrayList<>();
    private Map<String, BigDecimal> balances = new HashMap<>();

    public void addEntry(String accountId, EntryType type, BigDecimal amount, String desc) {
        entries.add(new Entry(UUID.randomUUID().toString().substring(0, 8), accountId, type, amount, desc));
        BigDecimal sign = type == EntryType.CREDIT ? amount : amount.negate();
        balances.merge(accountId, sign, BigDecimal::add);
    }

    public void transfer(String from, String to, BigDecimal amount, String desc) {
        addEntry(from, EntryType.DEBIT, amount, desc);
        addEntry(to, EntryType.CREDIT, amount, desc);
    }

    public BigDecimal balance(String accountId) {
        return balances.getOrDefault(accountId, BigDecimal.ZERO);
    }
}
```
""",

    "39_consensus_algorithm.md": """
## Python Implementation

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from enum import Enum
import random

class NodeRole(Enum):
    FOLLOWER = "follower"
    CANDIDATE = "candidate"
    LEADER = "leader"

@dataclass
class LogEntry:
    term: int
    command: str
    index: int

class RaftNode:
    def __init__(self, node_id: str, peers: List[str]):
        self.node_id = node_id
        self.peers = peers
        self.role = NodeRole.FOLLOWER
        self.current_term = 0
        self.voted_for: Optional[str] = None
        self.log: List[LogEntry] = []
        self.commit_index = 0
        self.leader_id: Optional[str] = None
        self._votes_received: Set[str] = set()

    def start_election(self):
        self.current_term += 1
        self.role = NodeRole.CANDIDATE
        self.voted_for = self.node_id
        self._votes_received = {self.node_id}
        print(f"[{self.node_id}] Starting election for term {self.current_term}")

    def request_vote(self, candidate_id: str, term: int) -> bool:
        if term < self.current_term:
            return False
        if term > self.current_term:
            self.current_term = term
            self.role = NodeRole.FOLLOWER
            self.voted_for = None
        if self.voted_for is None or self.voted_for == candidate_id:
            self.voted_for = candidate_id
            return True
        return False

    def receive_vote(self, voter_id: str, granted: bool):
        if granted and self.role == NodeRole.CANDIDATE:
            self._votes_received.add(voter_id)
            majority = (len(self.peers) + 1) // 2 + 1
            if len(self._votes_received) >= majority:
                self.role = NodeRole.LEADER
                self.leader_id = self.node_id
                print(f"[{self.node_id}] Became LEADER for term {self.current_term}")

    def append_entry(self, term: int, command: str) -> bool:
        if term < self.current_term:
            return False
        self.current_term = term
        self.role = NodeRole.FOLLOWER
        entry = LogEntry(term, command, len(self.log))
        self.log.append(entry)
        return True

# Simple majority vote simulation
def simulate_election(nodes: List[RaftNode]):
    candidate = nodes[0]
    candidate.start_election()
    for node in nodes[1:]:
        granted = node.request_vote(candidate.node_id, candidate.current_term)
        candidate.receive_vote(node.node_id, granted)
    return candidate

# Usage
nodes = [RaftNode(f"N{i}", [f"N{j}" for j in range(5) if j != i]) for i in range(5)]
leader = simulate_election(nodes)
print(f"Leader: {leader.node_id}, Role: {leader.role}")
```

## Java Implementation

```java
import java.util.*;

public class RaftNode {
    enum Role { FOLLOWER, CANDIDATE, LEADER }

    private String id;
    private List<String> peers;
    private Role role = Role.FOLLOWER;
    private int term = 0;
    private String votedFor = null;
    private Set<String> votes = new HashSet<>();

    public RaftNode(String id, List<String> peers) {
        this.id = id;
        this.peers = peers;
    }

    public void startElection() {
        term++;
        role = Role.CANDIDATE;
        votedFor = id;
        votes.clear();
        votes.add(id);
        System.out.println(id + " starting election for term " + term);
    }

    public boolean requestVote(String candidateId, int candidateTerm) {
        if (candidateTerm < term) return false;
        if (candidateTerm > term) { term = candidateTerm; role = Role.FOLLOWER; votedFor = null; }
        if (votedFor == null || votedFor.equals(candidateId)) {
            votedFor = candidateId;
            return true;
        }
        return false;
    }

    public void receiveVote(String voterId, boolean granted) {
        if (granted && role == Role.CANDIDATE) {
            votes.add(voterId);
            if (votes.size() > (peers.size() + 1) / 2) {
                role = Role.LEADER;
                System.out.println(id + " became LEADER for term " + term);
            }
        }
    }
}
```
""",
}


def append_code_to_file(filepath: str, code: str):
    with open(filepath, "a", encoding="utf-8") as f:
        f.write("\n" + code.strip() + "\n")
    print(f"✓ {filepath}")


def main():
    updated = 0
    for filename, code in CODE_BLOCKS.items():
        # Find the file
        found = False
        for root, dirs, files in os.walk(BASE_DIR):
            if filename in files:
                full_path = os.path.join(root, filename)
                # Check if already has python code
                with open(full_path, encoding="utf-8") as f:
                    content = f.read()
                if "```python" in content:
                    print(f"  skip (has code): {filename}")
                    found = True
                    break
                append_code_to_file(full_path, code)
                updated += 1
                found = True
                break
        if not found:
            print(f"  NOT FOUND: {filename}")

    print(f"\n✅ Added code to {updated} files")


if __name__ == "__main__":
    main()
