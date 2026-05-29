@echo off
chcp 65001 >nul 2>&1
title ASO-DEMO Sync Tool
color 0F

:MENU
cls
echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║          ASO-DEMO  —  Sync Tool                 ║
echo  ╠══════════════════════════════════════════════════╣
echo  ║                                                  ║
echo  ║   [1]  📥  Cap nhat code moi nhat (Pull)        ║
echo  ║                                                  ║
echo  ║   [2]  📤  Luu va day code len (Push)           ║
echo  ║                                                  ║
echo  ║   [3]  📋  Xem trang thai (Status)              ║
echo  ║                                                  ║
echo  ║   [4]  🚀  Cai dat lan dau (First-time Setup)   ║
echo  ║                                                  ║
echo  ║   [0]  ❌  Thoat                                ║
echo  ║                                                  ║
echo  ╚══════════════════════════════════════════════════╝
echo.
set /p choice="  Nhap lua chon (0-4): "

if "%choice%"=="1" goto PULL
if "%choice%"=="2" goto PUSH
if "%choice%"=="3" goto STATUS
if "%choice%"=="4" goto SETUP
if "%choice%"=="0" exit
goto MENU

:PULL
cls
echo.
echo  ────────────────────────────────────────────────
echo   📥  DANG CAP NHAT CODE MOI NHAT...
echo  ────────────────────────────────────────────────
echo.
git pull origin master
if %ERRORLEVEL% EQU 0 (
    echo.
    echo  ✅  Cap nhat thanh cong!
) else (
    echo.
    echo  ⚠️  Co loi xay ra. Vui long lien he nguoi quan ly du an.
    echo     Loi co the do: xung dot file (merge conflict).
)
echo.
pause
goto MENU

:PUSH
cls
echo.
echo  ────────────────────────────────────────────────
echo   📤  LUU VA DAY CODE LEN GITHUB
echo  ────────────────────────────────────────────────
echo.

REM Check if there are changes
git diff --quiet --exit-code HEAD 2>nul
if %ERRORLEVEL% EQU 0 (
    git status --porcelain > "%TEMP%\git_status_check.tmp"
    for %%A in ("%TEMP%\git_status_check.tmp") do (
        if %%~zA==0 (
            echo  ℹ️  Khong co thay doi nao de day len.
            echo.
            pause
            goto MENU
        )
    )
)

echo  Cac file da thay doi:
echo  ────────────────────────────────────────────────
git status --short
echo  ────────────────────────────────────────────────
echo.

set /p msg="  Nhap mo ta thay doi (VD: Cap nhat config AR_Filter): "
if "%msg%"=="" set msg=Update from sync tool

echo.
echo  Dang xu ly...
git add -A
git commit -m "%msg%"
git push origin master

if %ERRORLEVEL% EQU 0 (
    echo.
    echo  ✅  Day code thanh cong!
) else (
    echo.
    echo  ⚠️  Co loi xay ra khi day code.
    echo     Thu chay [1] Cap nhat truoc, roi thu lai.
)
echo.
pause
goto MENU

:STATUS
cls
echo.
echo  ────────────────────────────────────────────────
echo   📋  TRANG THAI HIEN TAI
echo  ────────────────────────────────────────────────
echo.
echo  🔹 Branch hien tai:
git branch --show-current
echo.
echo  🔹 Commit gan nhat:
git log -1 --format="   %%h - %%s (%%cr)"
echo.
echo  🔹 Cac file thay doi:
git status --short
echo.
echo  ────────────────────────────────────────────────
echo.
pause
goto MENU

:SETUP
cls
echo.
echo  ────────────────────────────────────────────────
echo   🚀  HUONG DAN CAI DAT LAN DAU
echo  ────────────────────────────────────────────────
echo.
echo   Buoc 1: Cai dat Git
echo     👉 Tai tai: https://git-scm.com/download/win
echo.
echo   Buoc 2: Cai dat GitHub CLI
echo     👉 Tai tai: https://cli.github.com/
echo.
echo   Buoc 3: Mo PowerShell va chay:
echo     gh auth login --web --git-protocol https
echo     (Lam theo huong dan tren man hinh)
echo.
echo   Buoc 4: Clone du an:
echo     git clone https://github.com/Ytube2403/ASO-MVP.git
echo.
echo   Buoc 5: Cai dat Python packages:
echo     pip install flask openpyxl pandas langdetect
echo.
echo  ────────────────────────────────────────────────
echo.
echo  Ban da cai dat Git va GitHub CLI chua?
set /p ready="  Nhap 'y' de tu dong clone, hoac phim bat ky de quay lai: "
if /i "%ready%"=="y" (
    echo.
    echo  Dang kiem tra dang nhap GitHub...
    gh auth status >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo  Chua dang nhap. Dang mo trang dang nhap...
        gh auth login --web --git-protocol https
    )
    echo.
    echo  ✅  Da dang nhap GitHub!
    echo.
    echo  Nhap thu muc muon luu du an (VD: C:\Users\TenBan\Documents):
    set /p destdir="  Thu muc: "
    echo.
    echo  Dang clone du an...
    git clone https://github.com/Ytube2403/ASO-MVP.git "%destdir%\ASO-DEMO"
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo  ✅  Clone thanh cong! Du an nam tai: %destdir%\ASO-DEMO
    ) else (
        echo.
        echo  ⚠️  Clone that bai. Kiem tra lai duong dan va ket noi mang.
    )
)
echo.
pause
goto MENU
