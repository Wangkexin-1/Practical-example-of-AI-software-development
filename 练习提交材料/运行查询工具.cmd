@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0源码"
call "启动查询工具.cmd"
