# BENCHMARK REPORT — Lab #17: Multi-Memory Agent

**Run:** 2026-04-24 12:37:52
**Model:** gpt-4o-mini
**Memory stack:** Short-term buffer · Long-term Profile (JSON/Redis) · Episodic log (JSON) · Semantic (ChromaDB)

---

## Executive Summary

| Metric | No-Memory Agent | With-Memory Agent | Delta |
|--------|-----------------|-------------------|-------|
| Pass rate | — | 10/10 (100%) | +10 wins |
| Avg relevance (0–5) | 1.0 | 5.0 | +4.0 |
| Avg response tokens | 174 | 171 | -4 |
| Context utilization | ~0% | ~100% | — |

---

## 10 Multi-Turn Conversations

| # | Scenario | No-Memory Answer | With-Memory Answer | Score No/With | Pass? |
|---|----------|------------------|--------------------|---------------|-------|
| 1 | Profile Recall — Name after 4 turns | Xin lỗi, nhưng tôi không có khả năng nhớ thông tin cá nhân của bạn. Tôi không lưu trữ dữ l… | Có chứ, Linh! Tên bạn là Linh và bạn đang là sinh viên năm 3 chuyên ngành CNTT. Nếu có điề… | 0/5 | ✅ |
| 2 | Conflict Update — Allergy correction | Tất nhiên rồi! Để tôi có thể gợi ý thực đơn bữa sáng phù hợp, bạn có thể cho tôi biết bạn … | Dưới đây là một số gợi ý thực đơn bữa sáng phù hợp với bạn, chú ý đến việc tránh đậu nành:… | 0/5 | ✅ |
| 3 | Profile Recall — Food preference | Chắc chắn rồi! Để gợi ý cho bạn những món ăn trưa ngon phù hợp với sở thích, bạn có thể cu… | Dưới đây là một số món ăn trưa chay ngon mà bạn có thể thử:  1. **Salad quinoa**: Quinoa n… | 5/5 | ✅ |
| 4 | Episodic Recall — Docker debug session | Để khắc phục vấn đề kết nối database, bạn có thể đã thực hiện một số bước như sau:  1. **K… | Khi gặp lỗi kết nối database trong Docker Compose, bạn cũng nên kiểm tra và sử dụng servic… | 0/5 | ✅ |
| 5 | Episodic Recall — Learning vector database | Xin lỗi, nhưng tôi không có khả năng nhớ lại thông tin cá nhân hoặc các hoạt động mà bạn đ… | Hôm nay, bạn đã học về vector database và embedding. Bạn đã hiểu cách hoạt động của Chroma… | 0/5 | ✅ |
| 6 | Semantic FAQ — Docker networking fix | Khi các container trong Docker Compose không kết nối được với nhau mặc dù chúng nằm trong … | Lỗi này thường xảy ra khi các container không thể giao tiếp với nhau qua tên dịch vụ (serv… | 5/5 | ✅ |
| 7 | Semantic FAQ — LangChain memory types | LangChain cung cấp một số loại memory để giúp các chatbot và ứng dụng AI nhớ thông tin tro… | LangChain cung cấp một số loại memory, mỗi loại có những ưu điểm riêng. Dưới đây là các lo… | 0/5 | ✅ |
| 8 | Token Budget — Long conversation trim | Xin lỗi, nhưng tôi không có khả năng ghi nhớ thông tin cá nhân từ các cuộc trò chuyện trướ… | Có chứ! Bạn tên là An và là một Python developer với 5 năm kinh nghiệm. Bạn đang làm việc … | 0/5 | ✅ |
| 9 | Multi-fact Profile — Name + location + goal | Xin lỗi, nhưng tôi không có khả năng ghi nhớ thông tin cá nhân của người dùng. Nếu bạn cần… | Có, bạn đang sống ở TP.HCM và đang tìm việc mới ở đó để thay đổi môi trường làm việc. Nếu … | 0/5 | ✅ |
| 10 | Combined Memory — Profile + Episodic + Semantic | Xin lỗi, nhưng tôi không có khả năng nhớ thông tin cá nhân của người dùng hoặc các cuộc tr… | Có chứ, Minh! Bạn là một security engineer với 4 năm kinh nghiệm, và gần đây bạn vừa hoàn … | 0/5 | ✅ |

---

## Memory Hit Rate Analysis

| Group | Conversations | Passed | Hit Rate |
|-------|---------------|--------|----------|
| profile_recall | 3 | 3 | 100% |
| conflict_update | 1 | 1 | 100% |
| episodic_recall | 2 | 2 | 100% |
| semantic_retrieval | 2 | 2 | 100% |
| trim_token_budget | 1 | 1 | 100% |
| combined | 1 | 1 | 100% |

---

## Token Budget Breakdown

| Context Component | Token Allocation | Priority Level | Eviction Order |
|-------------------|-----------------|----------------|----------------|
| System Prompt (base) | ~600 tokens | Fixed | Never |
| User Profile (long-term) | up to 600 tokens | Priority 1 | Never |
| Short-term Conversation | up to 1 200 tokens | Priority 2 | Oldest pair first |
| Episodic Memory | up to 400 tokens | Priority 3 | Oldest episode first |
| Semantic Hits | up to 200 tokens | Priority 4 | **Evicted first** |
| Reserved for LLM Response | ~1 000 tokens | Fixed | — |
| **Total context window** | **4 000 tokens** | — | — |

Eviction triggers when estimated context exceeds **2 400 tokens**.
Eviction order: Semantic → Episodic (oldest) → Short-term (oldest pair) → Profile (never).

---

## Detailed Conversation Results

### Conv 1: Profile Recall — Name after 4 turns — ✅ PASS

- **Group:** `profile_recall`
- **Key information checked:** `Linh`
- **Memory type tested:** profile recall

**No-Memory Response (final turn):**
> Xin lỗi, nhưng tôi không có khả năng nhớ thông tin cá nhân của bạn. Tôi không lưu trữ dữ liệu từ những cuộc trò chuyện trước. Bạn có thể cho tôi biết tên của bạn nếu bạn muốn!

**With-Memory Response (final turn):**
> Có chứ, Linh! Tên bạn là Linh và bạn đang là sinh viên năm 3 chuyên ngành CNTT. Nếu có điều gì khác mà bạn muốn chia sẻ hoặc cần hỏi, hãy cho mình biết nhé!

| Metric | No-Memory | With-Memory |
|--------|-----------|-------------|
| Relevance score | 0/5 | 5/5 |
| Response tokens (est.) | 52 | 48 |
| Profile facts stored | — | 4 |
| Episodes stored | — | 1 |
| Semantic docs available | — | 10 |

---

### Conv 2: Conflict Update — Allergy correction — ✅ PASS

- **Group:** `conflict_update`
- **Key information checked:** `đậu nành`
- **Memory type tested:** conflict update

**No-Memory Response (final turn):**
> Tất nhiên rồi! Để tôi có thể gợi ý thực đơn bữa sáng phù hợp, bạn có thể cho tôi biết bạn bị dị ứng với thực phẩm nào không? Điều này sẽ giúp tôi tạo ra một thực đơn an toàn và ngon miệng cho bạn.

**With-Memory Response (final turn):**
> Dưới đây là một số gợi ý thực đơn bữa sáng phù hợp với bạn, chú ý đến việc tránh đậu nành:

1. **Bánh mì nướng với bơ và trái cây**:
   - Bánh mì nguyên cám hoặc bánh mì không chứa đậu nành.
   - Phết bơ (bơ đậu phộng hoặc bơ hạnh nhân) lên bánh.
   - Thêm lát chuối hoặc dâu tây lên trên.

2. **Yến mạch nấu với nước hoặc sữa thực vật**:
   - Yến mạch nấu với nước hoặc sữa hạnh nhân/sữa dừa.
   - Thêm trái cây tươi (như táo, chuối) và một chút mật ong hoặc siro phong nếu thích.

3. **Trứng chiên hoặc trứng bác**:
   - Trứng chiên với rau củ (như ớt chuông, hành tây, hoặc rau bina).
   - Kèm với bánh mì không chứa đậu nành.

4. **Smoothie trái cây**:
   - Xay sinh tố với chuối, dâu tây, và sữa dừa/sữa hạnh nhân.
   - Thêm một chút hạt chia hoặc hạt lanh để tăng dinh dưỡng.

5. **Bánh kếp hoặc bánh ngô**:
   - Làm bánh kếp từ bột mì nguyên cám, nước và trứng (tránh bột có chứa đậu nành).
   - Kèm với siro hoặc trái cây tươi.

Hy vọng rằng những gợi ý này sẽ giúp bạn có một bữa sáng ngon miệng và an toàn! Nếu bạn cần thêm ý tưởng, hãy cho tôi biết nhé!

| Metric | No-Memory | With-Memory |
|--------|-----------|-------------|
| Relevance score | 0/5 | 5/5 |
| Response tokens (est.) | 62 | 298 |
| Profile facts stored | — | 1 |
| Episodes stored | — | 0 |
| Semantic docs available | — | 10 |

---

### Conv 3: Profile Recall — Food preference — ✅ PASS

- **Group:** `profile_recall`
- **Key information checked:** `chay`
- **Memory type tested:** profile recall

**No-Memory Response (final turn):**
> Chắc chắn rồi! Để gợi ý cho bạn những món ăn trưa ngon phù hợp với sở thích, bạn có thể cung cấp cho tôi một số thông tin về khẩu vị của bạn không? Ví dụ: bạn thích món ăn chay hay mặn, món ăn Á hay Âu, hay có nguyên liệu nào bạn thích hoặc không thích không?

**With-Memory Response (final turn):**
> Dưới đây là một số món ăn trưa chay ngon mà bạn có thể thử:

1. **Salad quinoa**: Quinoa nấu chín trộn cùng với rau sống như xà lách, cà chua, dưa chuột và thêm một chút nước sốt chanh hoặc dầu ô liu.

2. **Bánh mì chay**: Bạn có thể làm bánh mì với nhân là đậu hũ chiên, rau sống và một ít sốt mayonnaise chay hoặc sốt tương.

3. **Cơm chiên chay**: Cơm chiên với rau củ như đậu Hà Lan, cà rốt và ngô, thêm một chút nước tương để tăng hương vị.

4. **Mì xào chay**: Mì xào với các loại rau như cải thìa, nấm, và đậu hũ, nêm nếm bằng nước tương và hạt tiêu.

5. **Súp rau củ**: Một tô súp nóng hổi với các loại rau củ như cà rốt, khoai tây, và bông cải, có thể thêm đậu lăng để tăng thêm chất dinh dưỡng.

Hy vọng bạn sẽ tìm thấy món ăn phù hợp để thưởng thức vào bữa trưa!

| Metric | No-Memory | With-Memory |
|--------|-----------|-------------|
| Relevance score | 5/5 | 5/5 |
| Response tokens (est.) | 80 | 228 |
| Profile facts stored | — | 3 |
| Episodes stored | — | 0 |
| Semantic docs available | — | 10 |

---

### Conv 4: Episodic Recall — Docker debug session — ✅ PASS

- **Group:** `episodic_recall`
- **Key information checked:** `docker`
- **Memory type tested:** episodic recall

**No-Memory Response (final turn):**
> Để khắc phục vấn đề kết nối database, bạn có thể đã thực hiện một số bước như sau:

1. **Kiểm tra cấu hình kết nối**: Đảm bảo rằng các thông tin như hostname, port, username, password và tên database là chính xác.

2. **Kiểm tra firewall**: Đảm bảo rằng firewall trên server database cho phép kết nối từ địa chỉ IP của service của bạn. Bạn có thể cần mở cổng mà database đang lắng nghe.

3. **Kiểm tra mạng**: Nếu bạn đang chạy dịch vụ và database trên các máy chủ khác nhau, hãy kiểm tra xem chúng có thể ping lẫn nhau không. Sử dụng lệnh `ping` hoặc `telnet` để kiểm tra kết nối.

4. **Kiểm tra dịch vụ database**: Đảm bảo rằng dịch vụ database đang chạy và không gặp phải sự cố nào. Bạn có thể kiểm tra trạng thái của dịch vụ này.

5. **Kiểm tra logs**: Xem logs của ứng dụng và database để tìm hiểu nguyên nhân cụ thể của lỗi kết nối.

6. **Thử kết nối trực tiếp**: Sử dụng một công cụ như `mysql` cho MySQL, `psql` cho PostgreSQL, hoặc một client tương ứng để thử kết nối trực tiếp tới database và xem có gặp lỗi gì không.

Nếu bạn đã thực hiện những bước này trước đó, bạn có thể xem lại quá trình đó và áp dụng lại. Nếu vấn đề vẫn còn, hãy cung cấp thêm thông tin chi tiết để có thể hỗ trợ tốt hơn.

**With-Memory Response (final turn):**
> Khi gặp lỗi kết nối database trong Docker Compose, bạn cũng nên kiểm tra và sử dụng service name của database thay vì localhost hoặc địa chỉ IP. Đảm bảo rằng bạn đã cấu hình chính xác trong phần định nghĩa service trong file `docker-compose.yml`. Ngoài ra, hãy chắc chắn rằng các container đã được khởi động và có thể giao tiếp với nhau trong cùng một network. 

Nếu bạn đã xác định đúng service name và vẫn gặp vấn đề, hãy kiểm tra các thông tin như port, username, password và xem log của database để tìm hiểu thêm về lỗi. Nếu bạn cần giúp đỡ cụ thể hơn, hãy cho tôi biết thông tin chi tiết về cấu hình của bạn!

| Metric | No-Memory | With-Memory |
|--------|-----------|-------------|
| Relevance score | 0/5 | 5/5 |
| Response tokens (est.) | 334 | 164 |
| Profile facts stored | — | 0 |
| Episodes stored | — | 2 |
| Semantic docs available | — | 10 |

---

### Conv 5: Episodic Recall — Learning vector database — ✅ PASS

- **Group:** `episodic_recall`
- **Key information checked:** `vector`
- **Memory type tested:** episodic recall

**No-Memory Response (final turn):**
> Xin lỗi, nhưng tôi không có khả năng nhớ lại thông tin cá nhân hoặc các hoạt động mà bạn đã thực hiện. Tuy nhiên, nếu bạn cung cấp thêm thông tin về nội dung hoặc chủ đề bạn đã học, tôi sẽ rất vui lòng giúp bạn ôn tập hoặc cung cấp thêm thông tin liên quan!

**With-Memory Response (final turn):**
> Hôm nay, bạn đã học về vector database và embedding. Bạn đã hiểu cách hoạt động của ChromaDB và cảm thấy cosine similarity rất thú vị. Nếu bạn cần thêm thông tin hoặc có câu hỏi nào liên quan, hãy cho tôi biết nhé!

| Metric | No-Memory | With-Memory |
|--------|-----------|-------------|
| Relevance score | 0/5 | 5/5 |
| Response tokens (est.) | 77 | 58 |
| Profile facts stored | — | 0 |
| Episodes stored | — | 3 |
| Semantic docs available | — | 10 |

---

### Conv 6: Semantic FAQ — Docker networking fix — ✅ PASS

- **Group:** `semantic_retrieval`
- **Key information checked:** `service`
- **Memory type tested:** semantic retrieval

**No-Memory Response (final turn):**
> Khi các container trong Docker Compose không kết nối được với nhau mặc dù chúng nằm trong cùng một network, bạn có thể thử một số bước sau để khắc phục vấn đề:

1. **Kiểm tra tên dịch vụ**: Trong Docker Compose, các container có thể kết nối với nhau bằng tên dịch vụ được định nghĩa trong file `docker-compose.yml`. Đảm bảo rằng bạn đang sử dụng đúng tên dịch vụ khi thực hiện kết nối.

   Ví dụ, nếu bạn có một dịch vụ gọi là `web`, bạn có thể kết nối từ dịch vụ khác bằng cách sử dụng `http://web:port` (nếu là ứng dụng web).

2. **Kiểm tra cấu hình network**: Đảm bảo rằng các container thực sự đang ở trong cùng một network. Bạn có thể định nghĩa một network trong file `docker-compose.yml`.

   ```yaml
   version: '3'
   services:
     web:
       image: nginx
       networks:
         - mynetwork
     db:
       image: postgres
       networks:
         - mynetwork

   networks:
     mynetwork:
       driver: bridge
   ```

3. **Kiểm tra trạng thái container**: Sử dụng lệnh `docker-compose ps` để kiểm tra trạng thái của các container. Nếu một container không chạy (Exited), nó có thể gây ra vấn đề kết nối.

4. **Kiểm tra logs**: Sử dụng lệnh `docker-compose logs` để xem log của các container. Điều này sẽ giúp bạn xác định nếu có lỗi gì xảy ra trong quá trình khởi động.

5. **Thử ping giữa các container**: Bạn có thể vào shell của một container và thử ping đến container khác bằng cách sử dụng tên dịch vụ. Ví dụ:

   ```bash
   docker exec -it <tên_container> /bin/sh
   ping <tên_dịch_vụ>
   ```

6. **Kiểm tra cổng và firewall**: Nếu bạn đang sử dụng cổng (ports) để kết nối, hãy đảm bảo rằng các cổng đó được mở và không bị chặn bởi firewall hoặc các quy tắc mạng khác.

7. **Cập nhật Docker và Docker Compose**: Đảm bảo rằng bạn đang sử dụng phiên bản mới nhất của Docker và Docker Compose, vì có thể có các lỗi đã được sửa trong các phiên bản mới.

Nếu bạn đã thử tất cả các bước trên mà vẫn gặp vấn đề, hãy cung cấp thêm thông

**With-Memory Response (final turn):**
> Lỗi này thường xảy ra khi các container không thể giao tiếp với nhau qua tên dịch vụ (service name). Để khắc phục, bạn có thể kiểm tra một số điều sau:

1. **Sử dụng tên dịch vụ**: Khi các container cần giao tiếp với nhau, hãy chắc chắn rằng bạn đang sử dụng tên dịch vụ thay vì `localhost`. Ví dụ, nếu bạn có một dịch vụ Redis trong docker-compose file của bạn, hãy kết nối tới Redis bằng `redis://redis:6379` thay vì `redis://localhost:6379`.

2. **Kiểm tra cấu hình mạng**: Đảm bảo rằng tất cả các dịch vụ bạn muốn kết nối đều nằm trong cùng một mạng. Bạn có thể tạo một mạng tùy chỉnh trong docker-compose file của bạn như sau:

   ```yaml
   version: '3'
   services:
     app:
       image: your_app_image
       networks:
         - my_network
     redis:
       image: redis
       networks:
         - my_network

   networks:
     my_network:
   ```

3. **Kiểm tra trạng thái container**: Sử dụng lệnh `docker-compose ps` để đảm bảo rằng tất cả các container đều đang chạy và không gặp lỗi.

4. **Kiểm tra logs**: Xem logs của các container bằng lệnh `docker-compose logs <service_name>` để xác định xem có thông báo lỗi nào không.

Nếu bạn đã kiểm tra tất cả các điều trên mà vẫn gặp vấn đề, hãy cung cấp thêm thông tin về docker-compose file và mô tả cụ thể về lỗi bạn đang gặp phải để mình có thể giúp bạn tốt hơn!

| Metric | No-Memory | With-Memory |
|--------|-----------|-------------|
| Relevance score | 5/5 | 5/5 |
| Response tokens (est.) | 472 | 313 |
| Profile facts stored | — | 3 |
| Episodes stored | — | 2 |
| Semantic docs available | — | 10 |

---

### Conv 7: Semantic FAQ — LangChain memory types — ✅ PASS

- **Group:** `semantic_retrieval`
- **Key information checked:** `ConversationBuffer`
- **Memory type tested:** semantic retrieval

**No-Memory Response (final turn):**
> LangChain cung cấp một số loại memory để giúp các chatbot và ứng dụng AI nhớ thông tin trong quá trình tương tác. Dưới đây là một số loại memory phổ biến trong LangChain:

1. **Memory ngắn hạn (Short-term Memory)**: Loại memory này chỉ giữ lại thông tin trong thời gian ngắn, thường là cho một phiên làm việc. Đây là loại memory thường được sử dụng cho các nhiệm vụ không cần lưu trữ lâu dài.

2. **Memory dài hạn (Long-term Memory)**: Loại memory này cho phép lưu trữ thông tin trong thời gian dài hơn và có thể được truy xuất trong các phiên tương tác sau. Đây là lựa chọn lý tưởng cho các chatbot cần nhớ thông tin từ nhiều cuộc hội thoại khác nhau.

3. **Memory có cấu trúc (Structured Memory)**: Loại memory này tổ chức thông tin theo cách có cấu trúc, giúp dễ dàng truy cập và quản lý thông tin hơn. Thường được sử dụng cho các ứng dụng cần xử lý thông tin phức tạp.

4. **Memory theo ngữ cảnh (Contextual Memory)**: Loại memory này giữ lại thông tin theo ngữ cảnh, cho phép chatbot phản hồi một cách tự nhiên và mạch lạc hơn dựa trên lịch sử cuộc trò chuyện.

### Đối với chatbot cần nhớ cả lịch sử dài

Nếu bạn cần một chatbot có khả năng nhớ lịch sử dài, bạn nên sử dụng **Memory dài hạn**. Loại memory này cho phép lưu trữ thông tin quan trọng và truy xuất chúng trong các phiên tương tác khác nhau. Điều này giúp chatbot có thể duy trì sự liên tục trong cuộc hội thoại và cung cấp phản hồi phù hợp dựa trên thông tin đã lưu trữ.

Ngoài ra, nếu chatbot của bạn cần phải xử lý thông tin phức tạp hoặc có tính chất đa dạng, bạn cũng có thể xem xét sử dụng **Memory có cấu trúc** để tổ chức thông tin một cách hiệu quả hơn.

**With-Memory Response (final turn):**
> LangChain cung cấp một số loại memory, mỗi loại có những ưu điểm riêng. Dưới đây là các loại memory chính trong LangChain:

1. **ConversationBufferMemory**: Loại memory này lưu trữ toàn bộ lịch sử cuộc trò chuyện. Nó rất hữu ích cho các ứng dụng cần truy cập lại toàn bộ thông tin đã trao đổi trong một phiên trò chuyện, nhưng có thể tiêu tốn nhiều tài nguyên nếu lịch sử dài.

2. **ConversationSummaryMemory**: Memory này tóm tắt lịch sử cuộc trò chuyện cũ để tiết kiệm tài nguyên. Nó cho phép chatbot giữ lại những điểm chính trong cuộc trò chuyện mà không cần lưu trữ toàn bộ chi tiết. Đây là lựa chọn tốt nếu bạn muốn duy trì thông tin quan trọng mà không cần lưu trữ quá nhiều dữ liệu.

3. **VectorStoreRetrieverMemory**: Loại memory này sử dụng tìm kiếm ngữ nghĩa để lấy ngữ cảnh phù hợp nhất từ các thông tin đã lưu. Nó rất hữu ích cho các chatbot cần truy cập vào kiến thức rộng lớn hoặc thông tin có cấu trúc phức tạp.

Nếu bạn cần một chatbot có khả năng nhớ cả lịch sử dài, **ConversationBufferMemory** sẽ là lựa chọn tốt nhất vì nó cho phép lưu trữ toàn bộ lịch sử cuộc trò chuyện. Tuy nhiên, nếu bạn muốn tiết kiệm tài nguyên và chỉ cần giữ lại các điểm chính, bạn có thể cân nhắc sử dụng **ConversationSummaryMemory**. 

Tùy thuộc vào nhu cầu cụ thể và tài nguyên mà bạn có, bạn có thể chọn loại memory phù hợp nhất cho chatbot của mình.

| Metric | No-Memory | With-Memory |
|--------|-----------|-------------|
| Relevance score | 0/5 | 5/5 |
| Response tokens (est.) | 444 | 354 |
| Profile facts stored | — | 0 |
| Episodes stored | — | 0 |
| Semantic docs available | — | 10 |

---

### Conv 8: Token Budget — Long conversation trim — ✅ PASS

- **Group:** `trim_token_budget`
- **Key information checked:** `Python`
- **Memory type tested:** trim token budget

**No-Memory Response (final turn):**
> Xin lỗi, nhưng tôi không có khả năng ghi nhớ thông tin cá nhân từ các cuộc trò chuyện trước. Mỗi lần bạn trò chuyện với tôi, tôi không có thông tin nào từ các lần trò chuyện trước đó. Tuy nhiên, tôi rất vui được hỗ trợ bạn với bất kỳ câu hỏi nào về lập trình hoặc ngôn ngữ mà bạn đang phát triển!

**With-Memory Response (final turn):**
> Có chứ! Bạn tên là An và là một Python developer với 5 năm kinh nghiệm. Bạn đang làm việc với Apache Kafka cho data pipeline, sử dụng Kubernetes để deploy services, và đang tìm hiểu MLOps với FastAPI. Bạn cũng đang chuyển từ Pandas sang Polars để cải thiện hiệu suất. Nếu có thông tin nào khác bạn muốn tôi ghi nhớ hoặc nếu có câu hỏi nào khác, hãy cho tôi biết nhé!

| Metric | No-Memory | With-Memory |
|--------|-----------|-------------|
| Relevance score | 0/5 | 5/5 |
| Response tokens (est.) | 88 | 100 |
| Profile facts stored | — | 3 |
| Episodes stored | — | 2 |
| Semantic docs available | — | 10 |

---

### Conv 9: Multi-fact Profile — Name + location + goal — ✅ PASS

- **Group:** `profile_recall`
- **Key information checked:** `TP.HCM`
- **Memory type tested:** profile recall

**No-Memory Response (final turn):**
> Xin lỗi, nhưng tôi không có khả năng ghi nhớ thông tin cá nhân của người dùng. Nếu bạn cần giúp đỡ về việc chuyển nhà hoặc có câu hỏi liên quan đến địa điểm, hãy cho tôi biết, và tôi sẽ cố gắng giúp bạn!

**With-Memory Response (final turn):**
> Có, bạn đang sống ở TP.HCM và đang tìm việc mới ở đó để thay đổi môi trường làm việc. Nếu bạn cần thêm thông tin hoặc hỗ trợ trong quá trình tìm việc, hãy cho mình biết nhé!

| Metric | No-Memory | With-Memory |
|--------|-----------|-------------|
| Relevance score | 0/5 | 5/5 |
| Response tokens (est.) | 61 | 52 |
| Profile facts stored | — | 7 |
| Episodes stored | — | 0 |
| Semantic docs available | — | 10 |

---

### Conv 10: Combined Memory — Profile + Episodic + Semantic — ✅ PASS

- **Group:** `combined`
- **Key information checked:** `GDPR`
- **Memory type tested:** combined

**No-Memory Response (final turn):**
> Xin lỗi, nhưng tôi không có khả năng nhớ thông tin cá nhân của người dùng hoặc các cuộc trò chuyện trước đây. Tuy nhiên, nếu bạn muốn, bạn có thể chia sẻ về nghề nghiệp của mình và khóa học mà bạn vừa hoàn thành, và tôi sẽ rất vui lòng hỗ trợ bạn!

**With-Memory Response (final turn):**
> Có chứ, Minh! Bạn là một security engineer với 4 năm kinh nghiệm, và gần đây bạn vừa hoàn thành khóa học về GDPR và bảo vệ dữ liệu, trong đó bạn đã hiểu sâu hơn về quyền xóa bỏ (right to erasure). Nếu bạn có bất kỳ câu hỏi nào khác hoặc muốn thảo luận thêm về những kiến thức từ khóa học, hãy cho tôi biết nhé!

| Metric | No-Memory | With-Memory |
|--------|-----------|-------------|
| Relevance score | 0/5 | 5/5 |
| Response tokens (est.) | 73 | 92 |
| Profile facts stored | — | 5 |
| Episodes stored | — | 2 |
| Semantic docs available | — | 10 |

---

## Reflection: Privacy & Limitations

### Which memory helped most?
**Long-term Profile Memory** provides the biggest uplift — the agent instantly knows
user preferences (diet, allergies, job) without re-asking, making every response
feel personalised from the first follow-up turn.

### Which memory is riskiest if retrieved wrong?
**Episodic Memory** — if the agent recalls the wrong past event it can confidently
give incorrect advice (e.g. "you fixed it with X" when actually the user used Y).
**Profile Memory** is dangerous when conflict resolution fails and a stale fact
(e.g. old allergy) overrides the corrected value.

### If the user requests deletion, which backends must be cleared?
| Backend | Deletion method |
|---------|----------------|
| Profile | `profile_mem.delete_all()` → removes `user_profile.json` |
| Episodic | Filter & rewrite `episodic_log.json` removing user episodes |
| Semantic | `collection.delete(ids=[...])` in ChromaDB |
| Short-term | `short_term.clear()` → in-memory, gone on restart anyway |

A unified `forget(user_id)` API is needed for GDPR **Right to Erasure** compliance.

### PII / Privacy risks
- **Sensitive PII** (allergy, health, financial info) is stored in profile with no encryption.
- **No TTL**: profile facts never expire — a medical fact from 2 years ago may still be served.
- **No consent gate**: the agent silently stores facts without explicit user agreement.
- **Namespace isolation missing**: all users share one ChromaDB collection in this implementation.

### Technical limitations of this solution
1. **Keyword-based intent classifier** can miss intent when user phrasing is unexpected.
   Production should replace with LLM-based or fine-tuned classifier.
2. **JSON file storage** is single-process and doesn't scale to multiple users or servers.
   Needs migration to Redis (profile) + PostgreSQL/MongoDB (episodic).
3. **No user-ID partitioning**: all conversations share the same JSON files.
   Multi-user deployment requires a `user_id` dimension across all backends.
4. **ChromaDB local** doesn't support distributed deployment.
   Production: Pinecone, Weaviate, or managed Chroma Cloud.
5. **Episodic recall** relies on keyword overlap, not semantic similarity.
   Embedding-based search would improve recall on paraphrased queries.
