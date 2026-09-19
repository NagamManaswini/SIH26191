import sys
import os
from typing import Dict, Any
from fastapi import APIRouter, HTTPException

from app.services.edge_manager import edge_simulation_manager
from app.schemas.edge import (
    EdgeNetworkOverviewResponse,
    EdgeSimulationActionResponse,
    EdgeHazardTriggerResponse
)

router = APIRouter(prefix="/edge", tags=["Edge & LoRaWAN Simulation"])

@router.get("/overview", response_model=EdgeNetworkOverviewResponse)
def get_edge_network_overview():
    """
    Returns current status of all LoRaWAN edge sensor nodes, gateways,
    offline event queues, and local acoustic siren actuation states.
    """
    return edge_simulation_manager.get_overview()

@router.post("/simulate-failure", response_model=EdgeSimulationActionResponse)
def simulate_network_failure():
    """
    Simulates cellular / backhaul network failure.
    Demonstrates that edge sensor nodes continue autonomous local risk calculation
    and local siren actuation while isolated from cloud servers.
    """
    return edge_simulation_manager.simulate_network_failure()

@router.post("/restore-network", response_model=EdgeSimulationActionResponse)
def restore_network():
    """
    Restores backhaul connectivity and triggers automatic replay of queued offline events.
    """
    return edge_simulation_manager.restore_network()

@router.post("/nodes/{node_id}/trigger-hazard", response_model=EdgeHazardTriggerResponse)
def trigger_local_hazard_on_node(node_id: str):
    """
    Simulates severe localized flash flood surge at an edge node.
    Triggers immediate local edge siren without needing cloud connectivity.
    """
    res = edge_simulation_manager.trigger_hazard_on_node(node_id)
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res

@router.post("/nodes/sample-cycle")
def run_sample_cycle():
    """
    Advances physical telemetry simulation loop.
    """
    edge_simulation_manager.sample_all_nodes()
    return {"status": "SAMPLED"}
