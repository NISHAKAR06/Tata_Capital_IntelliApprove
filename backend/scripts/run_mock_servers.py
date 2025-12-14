from multiprocessing import Process

import uvicorn


def run_crm() -> None:
    # CRM mock server on port 8001
    uvicorn.run("mock_servers.crm_server:app", host="0.0.0.0", port=8001)


def run_credit_bureau() -> None:
    # Credit Bureau mock server on port 8002
    uvicorn.run("mock_servers.credit_bureau_server:app", host="0.0.0.0", port=8002)


def run_offer_mart() -> None:
    # Offer Mart mock server on port 8003
    uvicorn.run("mock_servers.offer_mart_server:app", host="0.0.0.0", port=8003)


def run_email_sms() -> None:
    # Email/SMS mock server on port 8004
    uvicorn.run("mock_servers.email_sms_server:app", host="0.0.0.0", port=8004)


if __name__ == "__main__":
    # Run all three mock services in parallel processes so they are all
    # available at once for local development.
    processes = [
        Process(target=run_crm, daemon=True),
        Process(target=run_credit_bureau, daemon=True),
        Process(target=run_offer_mart, daemon=True),
        Process(target=run_email_sms, daemon=True),
    ]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
