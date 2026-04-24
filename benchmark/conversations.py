"""
Knowledge base documents seeded into SemanticMemory, and
10 multi-turn benchmark conversations covering all required test groups.
"""

KNOWLEDGE_BASE = [
    {
        "id": "kb_python_001",
        "content": (
            "Python best practices: Dùng type hints để code rõ ràng hơn. "
            "Sử dụng virtual environment cho mỗi project. Tuân theo PEP 8. "
            "Ưu tiên list comprehension hơn vòng lặp thông thường khi phù hợp."
        ),
        "metadata": {"topic": "python", "category": "best_practices"},
    },
    {
        "id": "kb_docker_001",
        "content": (
            "Docker networking: Khi các container cần giao tiếp trong cùng docker-compose, "
            "dùng service name thay vì localhost. Ví dụ: redis://redis:6379 thay vì "
            "redis://localhost:6379. Tạo custom network để kiểm soát tốt hơn."
        ),
        "metadata": {"topic": "docker", "category": "networking"},
    },
    {
        "id": "kb_docker_002",
        "content": (
            "Docker volumes: Dùng named volumes để persist data. Tránh bind mounts trong "
            "production. Dùng 'docker volume ls' để liệt kê volumes. "
            "Format trong docker-compose: volumes: myvolume:/container/path"
        ),
        "metadata": {"topic": "docker", "category": "volumes"},
    },
    {
        "id": "kb_redis_001",
        "content": (
            "Redis là in-memory database, rất nhanh cho caching và session storage. "
            "TTL (Time To Live) quan trọng để tránh memory leak. "
            "Dùng EXPIRE key seconds để set TTL. Hỗ trợ data structures: string, hash, list, set, sorted set."
        ),
        "metadata": {"topic": "redis", "category": "basics"},
    },
    {
        "id": "kb_langchain_001",
        "content": (
            "LangChain memory types: ConversationBufferMemory lưu toàn bộ history. "
            "ConversationSummaryMemory tóm tắt history cũ để tiết kiệm token. "
            "VectorStoreRetrieverMemory dùng semantic search để lấy context phù hợp nhất."
        ),
        "metadata": {"topic": "langchain", "category": "memory"},
    },
    {
        "id": "kb_vector_db_001",
        "content": (
            "Vector database như ChromaDB và FAISS dùng embedding để tìm kiếm semantic. "
            "Cosine similarity là metric phổ biến nhất. "
            "Khi add document, text được convert thành vector qua embedding model và lưu vào index. "
            "ChromaDB hỗ trợ persistent storage và filter by metadata."
        ),
        "metadata": {"topic": "vector_db", "category": "basics"},
    },
    {
        "id": "kb_privacy_001",
        "content": (
            "PII (Personally Identifiable Information) gồm: tên, địa chỉ, số điện thoại, email, "
            "CCCD, thông tin sức khỏe. GDPR yêu cầu right to erasure (quyền xóa dữ liệu). "
            "Cần user consent trước khi lưu personal data. Áp dụng data minimization principle."
        ),
        "metadata": {"topic": "privacy", "category": "compliance"},
    },
    {
        "id": "kb_git_001",
        "content": (
            "Git best practices: Commit thường xuyên với message rõ ràng theo conventional commits. "
            "Dùng feature branches, không push thẳng vào main. "
            "Rebase trước khi merge để có clean history. Dùng git stash khi cần chuyển nhanh branch."
        ),
        "metadata": {"topic": "git", "category": "best_practices"},
    },
    {
        "id": "kb_llm_001",
        "content": (
            "LLM prompting best practices: Dùng clear và specific instructions. "
            "Cung cấp examples (few-shot) khi cần output format nhất định. "
            "System prompt cho role/persona, user prompt cho task cụ thể. "
            "Temperature=0 cho deterministic output, >0 cho sáng tạo."
        ),
        "metadata": {"topic": "llm", "category": "prompting"},
    },
    {
        "id": "kb_kafka_001",
        "content": (
            "Apache Kafka là distributed streaming platform. Consumer groups cho phép nhiều consumer "
            "cùng đọc từ một topic theo partition. Retention period mặc định 7 ngày. "
            "Dùng exactly-once semantics để tránh duplicate processing."
        ),
        "metadata": {"topic": "kafka", "category": "basics"},
    },
]

CONVERSATIONS = [
    {
        "id": 1,
        "scenario": "Profile Recall — Name after 4 turns",
        "group": "profile_recall",
        "description": "User giới thiệu tên, sau nhiều turn rồi hỏi agent có nhớ không.",
        "expected_memory_type": "profile",
        "key_check": "Linh",
        "turns": [
            {"role": "user", "content": "Xin chào! Tôi tên là Linh, tôi là sinh viên năm 3 CNTT."},
            {"role": "user", "content": "Bạn có thể giải thích khái niệm machine learning cho tôi không?"},
            {"role": "user", "content": "Cảm ơn! Tôi đang làm đồ án tốt nghiệp về NLP, rất hữu ích."},
            {"role": "user", "content": "Bạn có nhớ tên tôi không?"},
        ],
    },
    {
        "id": 2,
        "scenario": "Conflict Update — Allergy correction",
        "group": "conflict_update",
        "description": "User khai dị ứng sữa bò, sau đó sửa thành dị ứng đậu nành.",
        "expected_memory_type": "profile",
        "key_check": "đậu nành",
        "turns": [
            {"role": "user", "content": "Tôi dị ứng sữa bò, cần tránh hoàn toàn trong chế độ ăn."},
            {"role": "user", "content": "À nhầm, thực ra tôi dị ứng đậu nành chứ không phải sữa bò. Tôi bị nhầm lẫn."},
            {"role": "user", "content": "Gợi ý thực đơn bữa sáng cho tôi đi, nhớ tính đến dị ứng của tôi nhé."},
        ],
    },
    {
        "id": 3,
        "scenario": "Profile Recall — Food preference",
        "group": "profile_recall",
        "description": "User nói không thích đồ ăn cay và ăn chay, sau đó nhờ gợi ý món ăn.",
        "expected_memory_type": "profile",
        "key_check": "chay",
        "turns": [
            {"role": "user", "content": "Tôi không thích đồ ăn cay và tôi ăn chay đã 3 năm nay."},
            {"role": "user", "content": "Hôm nay trời nóng quá, bạn gợi ý đồ uống mát không?"},
            {"role": "user", "content": "Gợi ý cho tôi vài món ăn trưa ngon đi, phù hợp với sở thích của tôi nhé."},
        ],
    },
    {
        "id": 4,
        "scenario": "Episodic Recall — Docker debug session",
        "group": "episodic_recall",
        "description": "User fix bug docker networking, sau đó gặp lỗi tương tự và hỏi lại.",
        "expected_memory_type": "episodic",
        "key_check": "docker",
        "turns": [
            {"role": "user", "content": "Tôi vừa fix xong bug kết nối Redis. Hóa ra phải dùng service name 'redis' thay vì 'localhost' trong docker-compose. Học được bài học quan trọng!"},
            {"role": "user", "content": "Tuyệt, project chạy ổn rồi. Cảm ơn bạn đã hỗ trợ!"},
            {"role": "user", "content": "Ôi, bây giờ service mới của tôi bị lỗi kết nối database tương tự. Hôm trước tôi đã fix vấn đề networking như thế nào nhỉ?"},
        ],
    },
    {
        "id": 5,
        "scenario": "Episodic Recall — Learning vector database",
        "group": "episodic_recall",
        "description": "User học về vector DB, sau đó hỏi lại đã học gì hôm nay.",
        "expected_memory_type": "episodic",
        "key_check": "vector",
        "turns": [
            {"role": "user", "content": "Hôm nay tôi học về vector database và embedding. Hiểu được cách ChromaDB hoạt động rồi, cosine similarity thú vị lắm!"},
            {"role": "user", "content": "Tôi đã hiểu xong phần embedding và đang apply vào project. Học xong cảm thấy rõ hơn nhiều."},
            {"role": "user", "content": "Nhắc lại giúp tôi hôm nay tôi đã học về chủ đề gì?"},
        ],
    },
    {
        "id": 6,
        "scenario": "Semantic FAQ — Docker networking fix",
        "group": "semantic_retrieval",
        "description": "User hỏi cách fix lỗi container không kết nối được, agent retrieve từ KB.",
        "expected_memory_type": "semantic",
        "key_check": "service",
        "turns": [
            {"role": "user", "content": "Tôi là DevOps engineer mới, đang học Docker và docker-compose."},
            {"role": "user", "content": "Tôi bị lỗi: các container trong docker-compose không kết nối được với nhau dù cùng network. Làm thế nào để fix?"},
        ],
    },
    {
        "id": 7,
        "scenario": "Semantic FAQ — LangChain memory types",
        "group": "semantic_retrieval",
        "description": "User hỏi về các loại memory trong LangChain, agent retrieve từ KB.",
        "expected_memory_type": "semantic",
        "key_check": "ConversationBuffer",
        "turns": [
            {"role": "user", "content": "Tôi đang build chatbot với LangChain và cần chọn loại memory phù hợp."},
            {"role": "user", "content": "LangChain có những loại memory nào và nên dùng loại nào cho chatbot cần nhớ cả lịch sử dài?"},
        ],
    },
    {
        "id": 8,
        "scenario": "Token Budget — Long conversation trim",
        "group": "trim_token_budget",
        "description": "Conversation dài 7 turns để test auto-trim context window.",
        "expected_memory_type": "short_term",
        "key_check": "Python",
        "turns": [
            {"role": "user", "content": "Tôi tên là An, là Python developer với 5 năm kinh nghiệm."},
            {"role": "user", "content": "Tôi đang làm data pipeline với Apache Kafka. Scale 1M events/ngày."},
            {"role": "user", "content": "Gần đây tôi học thêm Kubernetes để deploy service cho đỡ đau đầu."},
            {"role": "user", "content": "Tôi cũng đang tìm hiểu MLOps, model serving với FastAPI."},
            {"role": "user", "content": "Dự án hiện tại dùng Airflow để orchestrate các data pipeline."},
            {"role": "user", "content": "Tôi đang migrate từ pandas sang Polars vì performance tốt hơn nhiều."},
            {"role": "user", "content": "Qua nhiều lần nói chuyện, bạn có nhớ tôi là developer của ngôn ngữ gì và tên tôi là gì không?"},
        ],
    },
    {
        "id": 9,
        "scenario": "Multi-fact Profile — Name + location + goal",
        "group": "profile_recall",
        "description": "User chia sẻ nhiều facts, sau đó hỏi agent nhớ được gì về nơi ở và kế hoạch.",
        "expected_memory_type": "profile",
        "key_check": "TP.HCM",
        "turns": [
            {"role": "user", "content": "Tôi tên là Hùng, 28 tuổi, làm backend developer tại Hà Nội. Tôi thích uống cà phê và lập trình Go."},
            {"role": "user", "content": "Tôi đang tìm việc mới ở TP.HCM vì muốn thay đổi môi trường làm việc."},
            {"role": "user", "content": "Bạn có nhớ tôi đang sống ở đâu và muốn chuyển đến đâu không?"},
        ],
    },
    {
        "id": 10,
        "scenario": "Combined Memory — Profile + Episodic + Semantic",
        "group": "combined",
        "description": "Tổng hợp: profile (security engineer) + episodic (học GDPR) + semantic (PII policy).",
        "expected_memory_type": "combined",
        "key_check": "GDPR",
        "turns": [
            {"role": "user", "content": "Tôi tên là Minh, là security engineer với 4 năm kinh nghiệm. Tôi rất quan tâm đến privacy và data protection."},
            {"role": "user", "content": "Hôm qua tôi vừa hoàn thành khóa học về GDPR và data protection. Hiểu sâu hơn về right to erasure rồi."},
            {"role": "user", "content": "Bạn có thể cho tôi biết về quy định PII và cách bảo vệ dữ liệu cá nhân không?"},
            {"role": "user", "content": "Bạn có nhớ nghề nghiệp của tôi là gì và gần đây tôi vừa hoàn thành khóa học về chủ đề gì không?"},
        ],
    },
]
