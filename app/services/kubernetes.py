from datetime import datetime, timezone

from kubernetes import client, config


def get_core_v1_api():
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

    return client.CoreV1Api()


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
        v1 = get_core_v1_api()

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
    v1 = get_core_v1_api()

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
