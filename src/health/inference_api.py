"""
Inference API for Agent Monitoring
Provides REST API endpoints for real-time agent inference data
"""

import asyncio
import json
import logging
from datetime import datetime

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from src.agents.agent_inference_monitor import monitor as inference_monitor

app = FastAPI(
    title="Agent Inference API",
    description="Real-time monitoring API for Claude CLI agent inferences",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

monitoring_task = None


@app.on_event("startup")
async def startup_event():
    """Start inference monitoring on startup"""
    global monitoring_task
    logger.info("[INFERENCE API] Starting inference monitoring...")

    monitoring_task = asyncio.create_task(_start_monitoring())


async def _start_monitoring():
    """Start the inference monitor in background"""
    try:
        await inference_monitor.start_monitoring()
    except Exception as e:
        logger.error(f"Monitor startup error: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop inference monitoring on shutdown"""
    global monitoring_task
    logger.info("[INFERENCE API] Stopping inference monitoring...")

    if monitoring_task:
        monitoring_task.cancel()

    await inference_monitor.stop_monitoring()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Agent Inference API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "inference-api",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/agents")
async def get_all_agents():
    """Get metrics for all agents"""
    try:
        agents_data = {}
        for agent_type in inference_monitor.agent_metrics:
            agents_data[agent_type] = json.loads(
                inference_monitor.get_agent_metrics_json(agent_type)
            )

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "agents": agents_data,
        }
    except Exception as e:
        logger.error(f"Error getting all agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/{agent_type}")
async def get_agent_metrics(agent_type: str):
    """Get metrics for a specific agent"""
    try:
        if agent_type not in inference_monitor.agent_metrics:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_type}' not found")

        metrics_json = inference_monitor.get_agent_metrics_json(agent_type)
        metrics_data = json.loads(metrics_json)

        return {
            "success": True,
            "agent": agent_type,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics_data,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/{agent_type}/inferences")
async def get_agent_inferences(
    agent_type: str,
    limit: int = Query(default=10, ge=1, le=100),
    include_errors: bool = Query(default=False),
):
    """Get recent inferences for a specific agent"""
    try:
        if agent_type not in inference_monitor.agent_metrics:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_type}' not found")

        inferences_json = inference_monitor.get_recent_inferences_json(agent_type, limit)
        inferences_data = json.loads(inferences_json)

        if not include_errors:
            inferences_data = [inf for inf in inferences_data if inf.get("success", True)]

        return {
            "success": True,
            "agent": agent_type,
            "timestamp": datetime.now().isoformat(),
            "inferences": inferences_data,
            "count": len(inferences_data),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting inferences for {agent_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system/summary")
async def get_system_summary():
    """Get system-wide summary"""
    try:
        summary_json = inference_monitor.get_system_summary_json()
        summary_data = json.loads(summary_json)

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "summary": summary_data,
        }
    except Exception as e:
        logger.error(f"Error getting system summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system/health")
async def get_system_health():
    """Get overall system health status"""
    try:
        online_agents = sum(
            1 for m in inference_monitor.agent_metrics.values() if m.status == "online"
        )
        total_agents = len(inference_monitor.agent_metrics)

        health_score = (online_agents / total_agents * 100) if total_agents > 0 else 0

        status = "healthy"
        if health_score < 50:
            status = "unhealthy"
        elif health_score < 80:
            status = "degraded"

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "health_score": round(health_score, 2),
            "online_agents": online_agents,
            "total_agents": total_agents,
            "agents": {
                agent_type: metrics.status
                for agent_type, metrics in inference_monitor.agent_metrics.items()
            },
        }
    except Exception as e:
        logger.error(f"Error getting system health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/{agent_type}/status")
async def get_agent_status(agent_type: str):
    """Get current status of a specific agent"""
    try:
        if agent_type not in inference_monitor.agent_metrics:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_type}' not found")

        metrics = inference_monitor.agent_metrics[agent_type]

        return {
            "success": True,
            "agent": agent_type,
            "timestamp": datetime.now().isoformat(),
            "status": metrics.status,
            "current_task": metrics.current_task,
            "uptime_percentage": round(metrics.uptime_percentage, 2),
            "last_inference": (
                metrics.last_inference.isoformat() if metrics.last_inference else None
            ),
            "total_inferences": metrics.total_inferences,
            "successful_inferences": metrics.successful_inferences,
            "success_rate": (
                round(metrics.successful_inferences / metrics.total_inferences * 100, 2)
                if metrics.total_inferences > 0
                else 0.0
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting status for {agent_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/realtime/metrics")
async def get_realtime_metrics():
    """Get real-time streaming metrics for dashboard"""
    try:
        agents_data = {}

        for agent_type, metrics in inference_monitor.agent_metrics.items():
            agents_data[agent_type] = {
                "status": metrics.status,
                "confidence": round(metrics.average_confidence, 2),
                "response_time": round(metrics.average_processing_time, 2),
                "uptime": round(metrics.uptime_percentage, 2),
                "total_calls": metrics.total_inferences,
                "success_rate": (
                    round(
                        metrics.successful_inferences / metrics.total_inferences * 100,
                        2,
                    )
                    if metrics.total_inferences > 0
                    else 0.0
                ),
                "current_task": metrics.current_task,
                "last_activity": (
                    metrics.last_inference.isoformat() if metrics.last_inference else None
                ),
            }

        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "agents": agents_data,
        }
    except Exception as e:
        logger.error(f"Error getting realtime metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logger.info("[INFERENCE API] Starting Agent Inference API...")

    uvicorn.run("inference_api:app", host="0.0.0.0", port=8004, reload=True, log_level="info")
