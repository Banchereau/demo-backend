from datetime import datetime, timezone

from kubernetes import client, config

from app.core.kubernetes import (
    get_apps_v1,
    get_core_v1,
    get_networking_v1,
)


def format_age(created_at):
    if created_at is None:
        return "Unknown"

    delta = datetime.now(timezone.utc) - created_at

    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    if days > 0:
        return f"{days}d"

    if hours > 0:
        return f"{hours}h"

    return f"{minutes}m"


def get_cluster_status():
    try:
        v1 = get_core_v1()

        nodes = v1.list_node()
        pods = v1.list_pod_for_all_namespaces()
        services = v1.list_service_for_all_namespaces()
        namespaces = v1.list_namespace()

        return {
            "nodes": len(nodes.items),
            "pods": len(pods.items),
            "services": len(services.items),
            "namespaces": len(namespaces.items),
            "health": "healthy",
        }

    except Exception as e:
        return {
            "health": "unhealthy",
            "error": str(e),
        }


def get_pods():
    v1 = get_core_v1()

    pods = []

    for pod in v1.list_pod_for_all_namespaces().items:
        restarts = sum(
            status.restart_count
            for status in (pod.status.container_statuses or [])
        )

        pods.append(
            {
                "name": pod.metadata.name,
                "namespace": pod.metadata.namespace,
                "status": pod.status.phase,
                "restarts": restarts,
                "node": pod.spec.node_name,
                "age": format_age(
                    pod.metadata.creation_timestamp
                ),
            }
        )

    return pods


def get_services():
    v1 = get_core_v1()

    services = []

    for service in v1.list_service_for_all_namespaces().items:
        ports = []

        if service.spec.ports:
            for port in service.spec.ports:
                ports.append(
                    str(port.port)
                )

        services.append(
            {
                "name": service.metadata.name,
                "namespace": service.metadata.namespace,
                "type": service.spec.type,
                "cluster_ip": service.spec.cluster_ip,
                "ports": ",".join(ports),
            }
        )

    return services


def get_deployments():
    apps_v1 = get_apps_v1()

    deployments = []

    for deployment in apps_v1.list_deployment_for_all_namespaces().items:

        replicas = deployment.spec.replicas or 0

        ready_replicas = (
            deployment.status.ready_replicas
            if deployment.status.ready_replicas
            else 0
        )

        available_replicas = (
            deployment.status.available_replicas
            if deployment.status.available_replicas
            else 0
        )

        strategy = (
            deployment.spec.strategy.type
            if deployment.spec.strategy
            else "Unknown"
        )

        images = []

        for container in deployment.spec.template.spec.containers:
            images.append(container.image)

        deployments.append(
            {
                "name": deployment.metadata.name,
                "namespace": deployment.metadata.namespace,
                "replicas": replicas,
                "ready_replicas": ready_replicas,
                "available_replicas": available_replicas,
                "strategy": strategy,
                "images": ",".join(images),
            }
        )

    return deployments


def get_namespaces():
    try:
        v1 = get_core_v1()

        namespaces = v1.list_namespace()

        result = []

        for ns in namespaces.items:
            result.append(
                {
                    "name": ns.metadata.name,
                    "status": ns.status.phase,
                }
            )

        return result

    except Exception as e:
        raise RuntimeError(
            f"Unable to retrieve Kubernetes namespaces: {e}"
        )


def get_events(
    limit: int = 50,
    namespace: str | None = None,
    event_type: str | None = None,
):
    v1 = get_core_v1()

    if namespace:
        kubernetes_events = v1.list_namespaced_event(
            namespace=namespace
        )
    else:
        kubernetes_events = v1.list_event_for_all_namespaces()

    events = []

    for event in kubernetes_events.items:

        if event_type and event.type != event_type:
            continue

        involved_object = None

        if event.involved_object:
            involved_object = (
                f"{event.involved_object.kind}/"
                f"{event.involved_object.name}"
            )

        timestamp = (
            event.last_timestamp
            or event.event_time
            or event.first_timestamp
        )

        events.append(
            {
                "namespace": event.metadata.namespace,
                "name": event.metadata.name,
                "type": event.type,
                "reason": event.reason,
                "message": event.message,
                "involved_object": involved_object,
                "timestamp": (
                    timestamp.isoformat()
                    if timestamp
                    else None
                ),
            }
        )

    events.sort(
        key=lambda x: x["timestamp"] or "",
        reverse=True,
    )

    return events[:limit]


def get_pod_events(
    namespace: str,
    pod: str,
    limit: int = 50,
):
    v1 = get_core_v1()

    kubernetes_events = v1.list_namespaced_event(
        namespace=namespace
    )

    events = []

    for event in kubernetes_events.items:

        if not event.involved_object:
            continue

        if event.involved_object.kind != "Pod":
            continue

        if event.involved_object.name != pod:
            continue

        timestamp = (
            event.last_timestamp
            or event.event_time
            or event.first_timestamp
        )

        events.append(
            {
                "namespace": event.metadata.namespace,
                "name": event.metadata.name,
                "type": event.type,
                "reason": event.reason,
                "message": event.message,
                "involved_object": (
                    f"{event.involved_object.kind}/"
                    f"{event.involved_object.name}"
                ),
                "timestamp": (
                    timestamp.isoformat()
                    if timestamp
                    else None
                ),
            }
        )

    events.sort(
        key=lambda x: x["timestamp"] or "",
        reverse=True,
    )

    return events[:limit]


def get_pod_detail(
    namespace: str,
    pod: str,
):
    v1 = get_core_v1()

    pod_obj = v1.read_namespaced_pod(
        name=pod,
        namespace=namespace,
    )

    restarts = sum(
        status.restart_count
        for status in (pod_obj.status.container_statuses or [])
    )

    containers = []
    images = []

    for container in pod_obj.spec.containers or []:
        containers.append(container.name)
        images.append(container.image)

    return {
        "name": pod_obj.metadata.name,
        "namespace": pod_obj.metadata.namespace,
        "status": pod_obj.status.phase,
        "restarts": restarts,
        "node": pod_obj.spec.node_name,
        "age": format_age(
            pod_obj.metadata.creation_timestamp
        ),
        "pod_ip": pod_obj.status.pod_ip,
        "host_ip": pod_obj.status.host_ip,
        "service_account": pod_obj.spec.service_account_name,
        "containers": containers,
        "images": images,
    }
