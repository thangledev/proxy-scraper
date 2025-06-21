@echo off
set REQUIREMENTS=requirements.txt

pip freeze > current.txt
findstr /V /G:current.txt %REQUIREMENTS% > diff.txt

if exist diff.txt (
    echo Cài thiếu thư viện, đang install...
    pip install -r %REQUIREMENTS%
) else (
    echo Đã đủ requirements rồi!
)

echo.
echo === Chạy tool ===
python proxy.py

pause
