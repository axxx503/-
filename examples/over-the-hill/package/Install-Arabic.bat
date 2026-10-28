@echo off
chcp 65001 >nul
title تثبيت تعريب لعبة over the hill
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-Arabic.ps1" %*
if "%1"=="" pause

