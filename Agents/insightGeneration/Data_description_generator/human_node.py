from langgraph.types import interrupt,Command
def human_input(state):
    """
    Interrupts graph execution for capturing human feedback and stores it in the state for the description
    node to process.
    """
    if not isinstance(state, dict) or "description" not in state:
        raise ValueError("Invalid state: missing description")

    description = state["description"]
    current_feedback = state.get("human_feedback", [])

    user_feedback = interrupt(
        {"description": description, "report": state.get("report", "")},)

    if user_feedback[-1].lower() == "done":
          return Command(update={"human_node": state["human_feedback"] + ["Finalized"]}, goto="qugen_node")
    
    return Command(
        update={"human_feedback": current_feedback + [user_feedback]},
        goto="data_description"
    )

def take_human_feedback(state):
    if state.get("num_iterations")==0 :
        print("taking human feedback,num_iterations:", state.get("num_iterations"))
        return "human_node"
    else:
        print("skipping human feedback,num_iterations:", state.get("num_iterations"))
        return "qugen_node"