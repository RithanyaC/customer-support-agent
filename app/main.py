from app.graph.workflow import run_customer_support


def cli():
    print("Customer Support CLI")
    print("Type 'exit' to leave.")
    customer_id = input("Customer ID: ").strip()
    if not customer_id:
        customer_id = "CUST001"
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break
        result = run_customer_support(customer_id, user_input)
        print(f"Agent: {result.get('final_response', 'No response.')}")


if __name__ == "__main__":
    cli()
