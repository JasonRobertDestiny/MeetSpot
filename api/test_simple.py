#!/usr/bin/env python3
"""
极简测试版本 - 不依赖任何复杂模块
"""
from fastapi import FastAPI

app = FastAPI(title="MeetSpot Test")

@app.get("/")
async def root():
    return {"message": "MeetSpot API 测试成功", "status": "working"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "API正常运行"}

@app.post("/api/find_meetspot")
async def find_meetspot():
    return {"message": "推荐功能测试中", "status": "test_mode"}
