@echo off
chcp 65001 >nul
title إزالة تعريب لعبة over the hill واستعادة الملفات الأصلية
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Uninstall-Arabic.ps1" %*
if "%1"=="" pause

