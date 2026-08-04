def get_application_status(
    desired_replicas: int,
    ready_replicas: int
) -> str:
    if desired_replicas == ready_replicas:
        return "healthy"

    return "degraded"
