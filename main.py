import argparse
import asyncio
import json
import random
import re
import time
import os
import sys
from typing import List, Set

import aiohttp
from aiohttp import ClientTimeout
from tqdm.asyncio import tqdm_asyncio
from pystyle import Colors, Colorate, Center, Write

# ───────────────────────────────────────────────────
# Cấu hình mặc định
# ───────────────────────────────────────────────────
DEFAULT_CONFIG = {
    "timeout": 10,
    "retry": 2,
    "max_speed": 5.0,
    "test_site": "https://api.ipify.org",
    "user_agents_file": "user_agents.txt",
    "batch_size": 100,
    "max_concurrent": 50,
    "scrapers_file": "scrapers.json"
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_5) AppleWebKit/605.1.15 Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
]

# ───────────────────────────────────────────────────
# Hàm hiển thị và log
# ───────────────────────────────────────────────────
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def cprint(msg: str):
    Write.Print(f"{msg}\n", Colors.blue_to_green, interval=0.005)

def show_logo():
    clear_screen()
    Write.Print(Center.XCenter("""
████████╗██╗  ██╗ █████╗ ███╗   ██╗ ██████╗ ██╗     ███████╗       
╚══██╔══╝██║  ██║██╔══██╗████╗  ██║██╔════╝ ██║     ██╔════╝       
   ██║   ███████║███████║██╔██╗ ██║██║  ███╗██║     █████╗         
   ██║   ██╔══██║██╔══██║██║╚██╗██║██║   ██║██║     ██╔══╝         
   ██║   ██║  ██║██║  ██║██║ ╚████║╚██████╔╝███████╗███████╗       
   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝╚══════╝       
                                                                   
                    ██████╗ ███████╗██╗   ██╗                      
                    ██╔══██╗██╔════╝██║   ██║                      
                    ██║  ██║█████╗  ██║   ██║                      
                    ██║  ██║██╔══╝  ╚██╗ ██╔╝                      
                    ██████╔╝███████╗ ╚████╔╝                       
                    ╚═════╝ ╚══════╝  ╚═══╝
                    
                    https://me.thangle.io.vn
                  https://github.com/thangledev
"""), Colors.red_to_blue, interval=0.0001)
    time.sleep(2)
    print("\n" * 2)

# ───────────────────────────────────────────────────
# Nhập config từ user
# ───────────────────────────────────────────────────
def get_user_config():
    config = DEFAULT_CONFIG.copy()
    cprint("Nhập cấu hình (Enter để giữ mặc định)")

    try:
        # Timeout
        timeout = input(f"Timeout (giây) [{config['timeout']}]: ").strip()
        config['timeout'] = int(timeout) if timeout else config['timeout']
        if config['timeout'] <= 0:
            raise ValueError("Timeout phải lớn hơn 0")

        # Retry
        retry = input(f"Số lần thử lại [{config['retry']}]: ").strip()
        config['retry'] = int(retry) if retry else config['retry']
        if config['retry'] < 0:
            raise ValueError("Số lần thử lại không được âm")

        # Max speed
        max_speed = input(f"Tốc độ tối đa (giây) [{config['max_speed']}]: ").strip()
        config['max_speed'] = float(max_speed) if max_speed else config['max_speed']
        if config['max_speed'] <= 0:
            raise ValueError("Tốc độ tối đa phải lớn hơn 0")

        # Test site
        test_site = input(f"Site kiểm tra proxy [{config['test_site']}]: ").strip()
        config['test_site'] = test_site if test_site else config['test_site']
        if not config['test_site'].startswith(("http://", "https://")):
            raise ValueError("Site kiểm tra phải bắt đầu bằng http:// hoặc https://")

        # User agents file
        user_agents_file = input(f"File user agents [{config['user_agents_file']}]: ").strip()
        config['user_agents_file'] = user_agents_file if user_agents_file else config['user_agents_file']
        if user_agents_file and not os.path.isfile(user_agents_file):
            raise ValueError(f"File {user_agents_file} không tồn tại")

        # Batch size
        batch_size = input(f"Kích thước batch [{config['batch_size']}]: ").strip()
        config['batch_size'] = int(batch_size) if batch_size else config['batch_size']
        if config['batch_size'] <= 0:
            raise ValueError("Batch size phải lớn hơn 0")

        # Max concurrent
        max_concurrent = input(f"Số kết nối đồng thời [{config['max_concurrent']}]: ").strip()
        config['max_concurrent'] = int(max_concurrent) if max_concurrent else config['max_concurrent']
        if config['max_concurrent'] <= 0:
            raise ValueError("Số kết nối đồng thời phải lớn hơn 0")

        # Scrapers file
        scrapers_file = input(f"File scrapers [{config['scrapers_file']}]: ").strip()
        config['scrapers_file'] = scrapers_file if scrapers_file else config['scrapers_file']
        if not os.path.isfile(config['scrapers_file']):
            raise ValueError(f"File {config['scrapers_file']} không tồn tại")

    except ValueError as e:
        cprint(f"Lỗi: {e}")
        sys.exit(1)

    return config

# ───────────────────────────────────────────────────
# Class Scraper cơ sở và các Class con
# ───────────────────────────────────────────────────
class Scraper:
    def __init__(self, method: str, url_template: str, auth: tuple = None):
        self.method = method
        self.url_template = url_template
        self.auth = auth

    def get_url(self, **kwargs) -> str:
        return self.url_template.format(**kwargs, method=self.method)

    async def fetch(self, session: aiohttp.ClientSession, config: dict) -> str:
        url = self.get_url()
        for attempt in range(config["retry"] + 1):
            try:
                async with session.get(url, auth=self.auth, timeout=config["timeout"]) as resp:
                    resp.raise_for_status()
                    return await resp.text()
            except Exception:
                if attempt == config["retry"]:
                    return ""
                await asyncio.sleep(0.5 * (attempt + 1))
        return ""

    async def scrape(self, session: aiohttp.ClientSession, config: dict) -> List[str]:
        raw = await self.fetch(session, config)
        return re.findall(r"\d{1,3}(?:\.\d{1,3}){3}:\d{1,5}", raw)

class SpysMeScraper(Scraper):
    def __init__(self, method: str):
        super().__init__(method, "https://spys.me/{mode}.txt")

    def get_url(self, **kwargs) -> str:
        mode = "proxy" if self.method == "http" else "socks"
        return super().get_url(mode=mode)

class ProxyScrapeScraper(Scraper):
    def __init__(self, method: str, timeout: int = 1000, country: str = "All"):
        super().__init__(
            method,
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol={method}&timeout={timeout}&country={country}"
        )
        self.params = {"timeout": timeout, "country": country}

    def get_url(self, **kwargs) -> str:
        return super().get_url(**self.params)

class GeoNodeScraper(Scraper):
    def __init__(self, method: str, limit: str = "500"):
        super().__init__(
            method,
            "https://proxylist.geonode.com/api/proxy-list?limit={limit}&page=1&sort_by=lastChecked&sort_type=desc"
        )
        self.params = {"limit": limit}

    def get_url(self, **kwargs) -> str:
        return super().get_url(**self.params)

class GitHubScraper(Scraper):
    async def scrape(self, session: aiohttp.ClientSession, config: dict) -> List[str]:
        raw = await self.fetch(session, config)
        proxies = [
            line.split("//")[-1].strip()
            for line in raw.splitlines()
            if re.match(r"\d+\.\d+\.\d+\.\d+:\d+", line)
        ]
        if self.method.startswith("socks"):
            return [p for p in proxies if self.method in line.lower()]
        return proxies

def load_scrapers(config_file: str) -> List[Scraper]:
    try:
        with open(config_file, "r") as f:
            configs = json.load(f)
        scrapers = []
        for cfg in configs:
            if cfg["type"] == "SpysMe":
                scrapers.append(SpysMeScraper(cfg["method"]))
            elif cfg["type"] == "ProxyScrape":
                scrapers.append(ProxyScrapeScraper(cfg["method"], **cfg.get("params", {})))
            elif cfg["type"] == "GeoNode":
                scrapers.append(GeoNodeScraper(cfg["method"], **cfg.get("params", {})))
            elif cfg["type"] == "GitHub":
                scrapers.append(GitHubScraper(cfg["method"], cfg["url"]))
            elif cfg["type"] == "Generic":
                scrapers.append(Scraper(cfg["method"], cfg["url"]))
        return scrapers
    except Exception as e:
        cprint(f"Lỗi load scrapers: {e}")
        sys.exit(1)

# ───────────────────────────────────────────────────
# Cào và Check proxy
# ───────────────────────────────────────────────────
async def gather_proxies(method: str, config: dict) -> Set[str]:
    methods = {"socks4", "socks5", "socks"} if method == "socks" else {method}
    targets = [s for s in load_scrapers(config["scrapers_file"]) if s.method in methods]
    proxies = set()

    async with aiohttp.ClientSession(timeout=ClientTimeout(total=config["timeout"])) as session:
        async def scrape_task(scraper):
            try:
                res = await scraper.scrape(session, config)
                proxies.update(res)
            except Exception:
                pass

        await tqdm_asyncio.gather(
            *[scrape_task(s) for s in targets], desc="Cào proxy", unit="nguồn", total=len(targets), ncols=100
        )
    return proxies

async def check_proxy(
    session: aiohttp.ClientSession,
    proxy: str,
    method: str,
    site: str,
    timeout: int,
    max_speed: float,
    semaphore: asyncio.Semaphore
) -> tuple[bool, float]:
    async with semaphore:
        proxy_url = f"{method}://{proxy}"
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        try:
            start = time.time()
            async with session.get(
                site, proxy=proxy_url, headers=headers, timeout=timeout
            ) as resp:
                if resp.status == 200:
                    delay = time.time() - start
                    if delay <= max_speed:
                        cprint(f"Proxy hoạt động: {proxy} • {delay:.2f}s")
                        return True, delay
        except Exception:
            pass
        return False, 0.0

async def validate_proxies(
    proxies: List[str],
    method: str,
    config: dict,
    output_file: str
) -> int:
    valid_proxies = [p for p in proxies if re.match(r"^\d{1,3}(?:\.\d{1,3}){3}:\d{1,5}$", p)]
    connector = aiohttp.TCPConnector(ssl=False, limit=config["max_concurrent"])
    semaphore = asyncio.Semaphore(config["max_concurrent"])
    file_lock = asyncio.Lock()
    proxy_count = 0
    total_batches = 20  # Giới hạn 20 batch
    processed_proxies = 0

    # Xóa file output cũ nếu có
    try:
        with open(output_file, "w") as f:
            pass
    except Exception as e:
        cprint(f"Không tạo được file {output_file}: {e}")
        sys.exit(1)

    async with aiohttp.ClientSession(
        connector=connector, timeout=aiohttp.ClientTimeout(total=config["timeout"])
    ) as session:
        cprint(f"Bắt đầu check proxy, tổng {len(valid_proxies)} proxy, chia thành {total_batches} lần check")
        for i in range(0, len(valid_proxies), config["batch_size"]):
            batch_idx = i // config["batch_size"] + 1
            if batch_idx > total_batches:
                cprint(f"Đã check đủ {total_batches} lần!")
                break

            batch = valid_proxies[i:i + config["batch_size"]]
            processed_proxies += len(batch)
            cprint(f"Đang check lần thứ {batch_idx}/{total_batches} - {len(batch)} proxy")

            tasks = [
                check_proxy(session, p, method, config["test_site"], config["timeout"], config["max_speed"], semaphore)
                for p in batch
            ]
            results = await tqdm_asyncio.gather(
                *tasks, desc=f"Lần {batch_idx}", unit="proxy", total=len(batch), ncols=100
            )
            batch_valid = [p for (p, (valid, _)) in zip(batch, results) if valid]

            # Lưu proxy hợp lệ của batch vào file
            if batch_valid:
                async with file_lock:
                    try:
                        with open(output_file, "a") as f:
                            f.write("\n".join(batch_valid) + "\n")
                        proxy_count += len(batch_valid)
                        cprint(f"Lần thứ {batch_idx} có {len(batch_valid)} proxy sống, đã lưu vào file!")
                    except Exception as e:
                        cprint(f"Không ghi được file {output_file}: {e}")
                        sys.exit(1)

        cprint(f"Check xong {batch_idx-1}/{total_batches} lần, tổng {proxy_count} proxy sống, xử lý {processed_proxies} proxy")

    return proxy_count

# ───────────────────────────────────────────────────
# Thực thi chính
# ───────────────────────────────────────────────────
async def run(config):
    start_time = time.time()
    args = argparse.Namespace(
        proxy="http",
        output="output/proxies.txt"
    )

    # Validate đầu vào
    valid_protocols = ["http", "https", "socks", "socks4", "socks5"]
    if args.proxy not in valid_protocols:
        cprint(f"Loại proxy {args.proxy} không hợp lệ! Chọn: {valid_protocols}")
        sys.exit(1)
    try:
        with open(args.output, "a") as f:
            pass
    except Exception as e:
        cprint(f"Không thể ghi file {args.output}: {e}")
        sys.exit(1)

    # Cào proxy
    cprint("Đang cào proxy...")
    proxies = await gather_proxies(args.proxy, config)
    cprint(f"Cào được {len(proxies)} proxy")

    # Lưu danh sách proxy thô
    raw_file = f"{args.output}.raw"
    try:
        with open(raw_file, "w") as f:
            f.write("\n".join(proxies))
    except Exception as e:
        cprint(f"Lỗi lưu file thô {raw_file}: {e}")

    # Check proxy
    cprint("Đang check proxy...")
    proxy_count = await validate_proxies(
        list(proxies), args.proxy, config, args.output
    )

    cprint(f"Hoàn tất: {proxy_count} proxy hoạt động, thời gian: {time.time() - start_time:.2f}s")

# ───────────────────────────────────────────────────
# Main
# ───────────────────────────────────────────────────
def main():
    show_logo()

    # Load user agents
    config = get_user_config()
    try:
        with open(config["user_agents_file"], "r") as f:
            USER_AGENTS.extend(line.strip() for line in f if line.strip() and line.strip().startswith("Mozilla/"))
        if not USER_AGENTS:
            cprint("File user_agents.txt rỗng hoặc không hợp lệ!")
            sys.exit(1)
    except FileNotFoundError:
        pass

    try:
        asyncio.run(run(config))
    except KeyboardInterrupt:
        cprint("Chương trình bị dừng!")
    except Exception as e:
        cprint(f"Lỗi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
