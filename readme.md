# Proxy Scraper

Tool cào và check proxy đa luồng, hỗ trợ nhiều nguồn và giao thức (HTTP, HTTPS, SOCKS4, SOCKS5). Viết bằng Python, sử dụng `aiohttp` cho tốc độ cao và giao diện đẹp mắt với `pystyle`.

## Features

- **Cào proxy** từ nhiều nguồn (SpysMe, ProxyScrape, GeoNode, GitHub, v.v.).
- **Check proxy** với tốc độ tối ưu, hỗ trợ giới hạn số lượng batch.
- **Cấu hình linh hoạt**: timeout, retry, max speed, batch size, số kết nối đồng thời.
- **Giao diện thân thiện**: Logo đẹp, tiến trình rõ ràng với `tqdm`.
- **Lưu kết quả**: Proxy sống được lưu vào file, proxy thô lưu riêng.
- **Hỗ trợ user agents**: Tùy chỉnh danh sách user agents từ file.

## Requirements

- Python 3.8+
- Các thư viện:
  ```bash
  pip install aiohttp tqdm pystyle
  ```

## Installation

1. Clone repo:
   ```bash
   git clone https://github.com/thangledev/proxy-scraper.git
   cd proxy-scraper
   ```
2. Cài đặt dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Chuẩn bị file cấu hình:
   - `user_agents.txt`: Danh sách user agents (mặc định có sẵn 5 user agents).
   - `scrapers.json`: Danh sách nguồn cào proxy (xem mẫu dưới).

## Usage

Chạy tool:

```bash
python main.py
```

- Tool sẽ yêu cầu nhập cấu hình (timeout, retry, test site, v.v.). Nhấn Enter để dùng giá trị mặc định.
- Kết quả:
  - Proxy sống lưu vào `proxies.txt`.
  - Proxy thô lưu vào `proxies.txt.raw`.

### Cấu hình mẫu (`scrapers.json`)

```json
[
  { "type": "SpysMe", "method": "http" },
  { "type": "SpysMe", "method": "socks" },
  {
    "type": "ProxyScrape",
    "method": "http",
    "params": { "timeout": 1000, "country": "All" }
  },
  {
    "type": "ProxyScrape",
    "method": "socks4",
    "params": { "timeout": 1000, "country": "All" }
  },
  {
    "type": "ProxyScrape",
    "method": "socks5",
    "params": { "timeout": 1000, "country": "All" }
  },
  { "type": "GeoNode", "method": "http", "params": { "limit": "500" } },
  { "type": "GeoNode", "method": "socks", "params": { "limit": "500" } },
  {
    "type": "GitHub",
    "method": "http",
    "url": "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt"
  },
  {
    "type": "GitHub",
    "method": "socks5",
    "url": "https://raw.githubusercontent.com/zloi-user/hideip.me/main/socks5.txt"
  }
]
```

## Cấu hình mặc định

- **Timeout**: 10s
- **Retry**: 2 lần
- **Max speed**: 5s
- **Test site**: `https://api.ipify.org`
- **User agents file**: `user_agents.txt`
- **Batch size**: 100 proxy/lần
- **Max concurrent**: 50 kết nối đồng thời
- **Scrapers file**: `scrapers.json`

## Lưu ý

- File `user_agents.txt` phải chứa các user agents hợp lệ (bắt đầu bằng `Mozilla/`).
- File `scrapers.json` phải tồn tại và đúng định dạng.
- Tool giới hạn 20 batch check proxy để tránh quá tải.
- Dùng `Ctrl+C` để dừng chương trình.


# 🛠️ Cách chạy Proxy Scraper trên Termux

🔥 Cài đặt & chạy tool

  1. Cài git và python nếu chưa có
```bash
pkg install git python -y
```
  2. Di chuyển vào thư mục download cho dễ
```bash
cd /sdcard/download/
```
  3. Clone Repo
```bash
git clone https://github.com/thangledev/proxy-scraper.git
cd proxy-scraper
```

  4. Chạy tool
```bash
bash run.sh
```

## Author

- **ThangLeDev**
- Website: [me.thangle.io.vn](https://me.thangle.io.vn)
- GitHub: [thangledev](https://github.com/thangledev)

## License

MIT License
