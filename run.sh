#!/data/data/com.termux/files/usr/bin/bash

REQ=requirements.txt
REQ_HASH=$(sha256sum "$REQ" | awk '{print $1}')
HASH_FILE=".req_hash"

echo "🔍 Kiểm tra requirements..."

if [ ! -f "$HASH_FILE" ] || [ "$REQ_HASH" != "$(cat $HASH_FILE)" ]; then
    echo "📦 Cài đặt dependencies..."
    pip install -r "$REQ"
    echo "$REQ_HASH" > "$HASH_FILE"
else
    echo "✅ Dependencies đã sẵn sàng!"
fi

echo "🚀 Chạy tool proxy.py..."
python main.py

echo "📁 Di chuyển ra /sdcard/Download/ ..."

termux-setup-storage -y 2>/dev/null

mkdir -p /sdcard/Download/proxies
cp proxies.txt /sdcard/Download/proxies/proxies.txt 2>/dev/null
cp proxies.txt.raw /sdcard/Download/proxies/proxies.txt.raw 2>/dev/null

echo "✅ Đã lưu vào: /sdcard/Download/proxies/"
