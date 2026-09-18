from typing import Optional
from fastapi import APIRouter, Body
from app.services.demo_orchestrator import demo_orchestrator
from app.schemas.demo import DemoStatusResponse, DemoControlPayload

router = APIRouter(prefix="/demo", tags=["Full System Integration & Demo Mode"])

@router.get("/status", response_model=DemoStatusResponse)
def get_demo_status():
    """
    Returns current stage (1 to 15), telemetry states, physical effect descriptions,
    and system status for SIH Hackathon presentations.
    """
    return demo_orchestrator.get_status()

@router.post("/start", response_model=DemoStatusResponse)
def start_demo(payload: DemoControlPayload = Body(default=DemoControlPayload())):
    """
    Starts or jumps to a specific stage in the 15-stage deterministic flash flood scenario.
    """
    return demo_orchestrator.start_demo(
        auto_play=payload.auto_play,
        seconds_per_stage=payload.seconds_per_stage,
        jump_to_stage=payload.jump_to_stage
    )

@router.post("/stop", response_model=DemoStatusResponse)
def stop_demo():
    """
    Stops the scenario and resets the entire platform to baseline Stage 1.
    """
    return demo_orchestrator.stop_demo()

@router.post("/advance-step", response_model=DemoStatusResponse)
def advance_demo_step():
    """
    Manually advances the demo scenario by +1 stage for controlled presentation delivery.
    """
    return demo_orchestrator.advance_stage(1)
