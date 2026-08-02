from datetime import datetime, timezone

from kubernetes import client, config


def get_core_v1_api():
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

    return client.CoreV1Api()


def get_apps_v1_api():
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()

    return client.AppsV1Api()


def get_kubernetes_client():
    try:
        config.load_incluster_config()
    except Exception:
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


def get_services():
    v1 = get_core_v1_api()

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
    apps_v1 = get_apps_v1_api()

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

        containers = (
            deployment.spec.template.spec.containers
            if deployment.spec.template.spec.containers
            else []
        )

        for container in containers:
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

def get_deployments():
    apps_v1 = get_apps_v1_api()

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
        v1 = get_kubernetes_client()

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
