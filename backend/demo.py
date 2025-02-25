#!/usr/bin/env python
"""
WorkflowForge Demo Script

This script demonstrates the core functionality of WorkflowForge,
including workflow execution and self-reflection capabilities.
"""

import asyncio
import json
import uuid
import logging
from datetime import datetime

from app.workflow.orchestrator import WorkflowOrchestrator
from app.database import init_db, get_db
from app.config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.logging.level),
    format=config.logging.format
)
logger = logging.getLogger(__name__)


async def run_demo():
    """Run the WorkflowForge demonstration."""
    print("\n" + "=" * 80)
    print("WorkflowForge Demonstration".center(80))
    print("=" * 80 + "\n")
    print(f"Environment: {config.environment}\n")

    # Initialize the database
    print("Initializing database...")
    await init_db()
    print("Database initialized.\n")

    # Create workflow orchestrator
    print("Creating workflow orchestrator...")
    orchestrator = WorkflowOrchestrator(use_mock=config.workflow.use_mock)
    print(
        f"Workflow orchestrator created (using {'mock' if orchestrator.use_mock else 'LangGraph'} execution).\n")

    # Define a sample workflow
    workflow_id = str(uuid.uuid4())
    workflow_name = "Customer Feedback Analysis"
    workflow_description = "Analyze customer feedback to identify trends and sentiment"

    print(f"Workflow ID: {workflow_id}")
    print(f"Name: {workflow_name}")
    print(f"Description: {workflow_description}\n")

    # Define input data
    input_data = {
        "query": "Analyze customer feedback trends",
        "context": "E-commerce customer reviews dataset",
        "constraints": {
            "time_period": "last_month",
            "min_confidence": 0.8
        }
    }

    print("Input data:")
    print(json.dumps(input_data, indent=2))
    print()

    # Execute workflow
    print("Executing workflow...")
    start_time = datetime.now()
    result = await orchestrator.execute_workflow(workflow_id, input_data)
    end_time = datetime.now()
    execution_time = (end_time - start_time).total_seconds()
    print(f"Workflow executed in {execution_time:.2f} seconds.\n")

    # Print the raw result for debugging
    print("Raw workflow result:")
    print(json.dumps(result, indent=2))
    print()

    # Store workflow in database
    print("Storing workflow results...")
    async with get_db() as db:
        await db.execute(
            """
            INSERT INTO workflows (id, name, description, status, result)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                workflow_id,
                workflow_name,
                workflow_description,
                result.get("status", "unknown"),
                json.dumps(result.get("result", {}))
            )
        )

        # Store execution metrics
        await db.execute(
            """
            INSERT INTO workflow_executions (workflow_id, execution_time, status)
            VALUES (?, ?, ?)
            """,
            (
                workflow_id,
                execution_time,
                result.get("status", "unknown")
            )
        )
    print("Workflow results stored in database.\n")

    # Display results
    print("Workflow Results:")
    print("-" * 80)
    print(f"Status: {result.get('status', 'unknown')}")
    print("\nResult Data:")
    result_data = result.get("result", {})
    if result_data:
        print(json.dumps(result_data, indent=2))
    else:
        print("No result data available")

    print("\nExecution History:")
    for step in result.get("history", []):
        print(f"- {step}")
    print("-" * 80 + "\n")

    # Demonstrate self-reflection
    print("Self-Reflection Analysis:")
    print("-" * 80)

    # Get the optimizer agent from the orchestrator
    optimizer = orchestrator.optimizer

    # Run optimization analysis
    optimization_input = {
        "workflow_results": result,
        "performance_metrics": {
            "execution_time": execution_time,
            "success_rate": 1.0 if result.get("status") == "completed" else 0.0
        },
        "optimization_goals": {
            "reduce_execution_time": True,
            "improve_accuracy": True
        }
    }

    print("Running optimization analysis...")
    try:
        optimization_result = await optimizer.process(optimization_input)
        print("\nOptimization Suggestions:")
        print(json.dumps(optimization_result, indent=2))
    except Exception as e:
        logger.error(f"Error during optimization: {str(e)}")
        print(f"\nOptimization failed: {str(e)}")

    print("-" * 80 + "\n")

    print("Demonstration complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_demo())
