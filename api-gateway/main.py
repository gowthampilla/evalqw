from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import asyncpg

app = FastAPI()

# 1. THE ENTERPRISE SCHEMA
class StructuredAction(BaseModel):
    intent: str
    target_system: str
    requested_write: str
    scope: str
    confidence: float

holding_cell = {}
history_log = []

@app.post("/v1/proxy")
async def intercept_ai_action(action: StructuredAction):
    action_id = str(uuid.uuid4())[:8]
    print(f"\n🛡️ GOVERNOR INTERCEPT: {action.intent}")

    # --- PHASE 1: DETERMINISTIC POLICY ENGINE (Stateless Rules) ---
    if action.confidence < 0.85:
        return {"status": "BLOCKED", "reason": "Confidence below 85% threshold."}

    risk_score = 10
    if action.scope == "mass_delete": risk_score = 100
    elif action.scope == "mass_update": risk_score = 75

    # --- PHASE 2: THE SYNTHETIC EVALUATOR (The Reality Check) ---
    print("🔬 Running Synthetic Evaluation...")
    impact_msg = "Unknown"
    rows_affected = 0
    evaluation_status = "PASSED"
    
    try:
        conn = await asyncpg.connect('postgresql://admin:secretpassword@localhost:5432/fake_client_prod')
        tr = conn.transaction()
        await tr.start()
        try:
            # 1. Run the simulation
            result = await conn.execute(action.requested_write) # Returns e.g., "DELETE 4"
            
            # 2. Extract the blast radius (number of rows)
            if " " in result:
                rows_affected = int(result.split(" ")[-1])
            impact_msg = f"Would modify {rows_affected} rows."
            
            # 3. VERIFICATION LOGIC: Does the code match the JSON claim?
            if action.scope == "single_record" and rows_affected > 1:
                evaluation_status = "FAILED_HALLUCINATION"
                risk_score = 1000 # Absolute ban
                print(f"❌ EVALUATION FAILED: AI claimed 'single_record' but query impacts {rows_affected} rows!")
                
            elif action.scope == "mass_delete" and rows_affected == 0:
                evaluation_status = "FAILED_NO_TARGET"
                print("⚠️ EVALUATION WARNING: AI tried a mass delete, but 0 rows matched.")

            else:
                print(f"✅ EVALUATION PASSED: Query safely impacts {rows_affected} rows.")

        finally:
            await tr.rollback() # Destroy the simulation
            await conn.close()
            
    except Exception as e:
        evaluation_status = "FAILED_SYNTAX_ERROR"
        impact_msg = f"Broken SQL: {str(e)[:50]}"
        risk_score = 1000
        print(f"❌ EVALUATION FAILED: The AI wrote invalid SQL.")

    # If the Evaluator catches a hallucination, kill it instantly.
    if "FAILED" in evaluation_status and risk_score == 1000:
        return {"status": "KILLED_BY_EVALUATOR", "reason": evaluation_status, "impact": impact_msg}

    # --- PHASE 3: THE PROMOTION GATE (Holding Cell) ---
    holding_cell[action_id] = {
        "agent": "Qwen-Enterprise",
        "intent": action.intent,
        "query": action.requested_write,
        "eval_status": evaluation_status, # We now track the evaluation score!
        "status": "AWAITING_APPROVAL",
        "risk_score": risk_score,
        "impact": impact_msg
    }
    
    print(f"⚠️ QUARANTINED: Risk {risk_score}. Awaiting Human Promotion.")
    return {"status": "PAUSED", "action_id": action_id, "evaluation": evaluation_status}