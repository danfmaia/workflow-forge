from app.database.connection import engine
from app.database.models import Base, Workflow, Agent
import json


def init_db():
    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Import session here to avoid circular imports
    from app.database.connection import SessionLocal
    db = SessionLocal()

    # Check if we already have data
    if db.query(Workflow).first() is None:
        # Add sample workflows
        document_processing = Workflow(
            name="Document Processing Workflow",
            description="Process documents to extract key information and approve or reject based on criteria",
            config=json.dumps({
                "agents": ["researcher", "processor", "approver"],
                "steps": [
                    {"agent": "researcher", "next": "processor"},
                    {"agent": "processor", "next": "approver"},
                    {"agent": "approver", "next": None}
                ]
            })
        )

        customer_support = Workflow(
            name="Customer Support Triage",
            description="Analyze customer support tickets and route to appropriate department",
            config=json.dumps({
                "agents": ["researcher", "processor"],
                "steps": [
                    {"agent": "researcher", "next": "processor"},
                    {"agent": "processor", "next": None}
                ]
            })
        )

        db.add(document_processing)
        db.add(customer_support)

        # Add sample agent types
        researcher = Agent(
            name="Research Agent",
            description="Analyzes input data and extracts relevant information",
            agent_type="researcher",
            config=json.dumps({
                "max_tokens": 1000,
                "temperature": 0.2
            }),
            prompt_template="You are a research agent. Your task is to analyze the following data and extract key information: {input}"
        )

        processor = Agent(
            name="Processing Agent",
            description="Processes extracted information and makes preliminary decisions",
            agent_type="processor",
            config=json.dumps({
                "max_tokens": 800,
                "temperature": 0.1
            }),
            prompt_template="You are a processing agent. Based on the extracted information, process the data and make a preliminary decision: {input}"
        )

        approver = Agent(
            name="Approval Agent",
            description="Makes final decision based on processed information",
            agent_type="approver",
            config=json.dumps({
                "max_tokens": 500,
                "temperature": 0.0
            }),
            prompt_template="You are an approval agent. Review the processed information and make a final decision: {input}"
        )

        optimizer = Agent(
            name="Optimization Agent",
            description="Analyzes workflow performance and suggests improvements",
            agent_type="optimizer",
            config=json.dumps({
                "max_tokens": 1200,
                "temperature": 0.3
            }),
            prompt_template="You are an optimization agent. Review the workflow execution metrics and suggest improvements to agent prompts: {input}"
        )

        db.add(researcher)
        db.add(processor)
        db.add(approver)
        db.add(optimizer)

        db.commit()

    db.close()


if __name__ == "__main__":
    init_db()
