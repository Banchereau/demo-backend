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

    labels = dict(
        pod_obj.metadata.labels or {}
    )

    annotations = dict(
        pod_obj.metadata.annotations or {}
    )

    owner_references = []

    for owner in (
        pod_obj.metadata.owner_references or []
    ):
        owner_references.append(
            {
                "api_version": owner.api_version,
                "kind": owner.kind,
                "name": owner.name,
                "uid": owner.uid,
            }
        )

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
        "service_account": (
            pod_obj.spec.service_account_name
        ),
        "containers": containers,
        "images": images,
        "labels": labels,
        "annotations": annotations,
        "owner_references": owner_references,
    }


def get_pod_restarts(
    namespace: str,
    pod: str,
):
    v1 = get_core_v1()

    pod_obj = v1.read_namespaced_pod(
        name=pod,
        namespace=namespace,
    )

    restarts = []

    for status in (
        pod_obj.status.container_statuses or []
    ):
        if status.restart_count == 0:
            continue

        last_state = status.last_state

        if not last_state:
            continue

        terminated = last_state.terminated

        if not terminated:
            continue

        restarts.append(
            {
                "container": status.name,
                "restart_count": status.restart_count,
                "reason": terminated.reason,
                "exit_code": terminated.exit_code,
                "signal": terminated.signal,
                "started_at": (
                    terminated.started_at.isoformat()
                    if terminated.started_at
                    else None
                ),
                "finished_at": (
                    terminated.finished_at.isoformat()
                    if terminated.finished_at
                    else None
                ),
            }
        )

    restarts.sort(
        key=lambda x: x["finished_at"] or "",
        reverse=True,
    )

    return restarts


def get_deployment_rollouts(
    namespace: str,
    deployment_name: str,
):
    apps_v1 = get_apps_v1()

    deployment = apps_v1.read_namespaced_deployment(
        name=deployment_name,
        namespace=namespace,
    )

    deployment_uid = deployment.metadata.uid

    replica_sets = apps_v1.list_namespaced_replica_set(
        namespace=namespace,
    )

    current_revision = int(
        (
            deployment.metadata.annotations or {}
        ).get(
            "deployment.kubernetes.io/revision",
            "0",
        )
    )

    rollouts = []

    for replica_set in replica_sets.items:
        owner_references = (
            replica_set.metadata.owner_references or []
        )

        owned_by_deployment = any(
            owner.kind == "Deployment"
            and owner.name == deployment_name
            and owner.uid == deployment_uid
            for owner in owner_references
        )

        if not owned_by_deployment:
            continue

        annotations = replica_set.metadata.annotations or {}

        revision_value = annotations.get(
            "deployment.kubernetes.io/revision"
        )

        if not revision_value:
            continue

        try:
            revision = int(revision_value)
        except ValueError:
            continue

        replicas = replica_set.spec.replicas or 0

        ready_replicas = (
            replica_set.status.ready_replicas
            if replica_set.status.ready_replicas is not None
            else 0
        )

        images = []

        for container in (
            replica_set.spec.template.spec.containers or []
        ):
            if container.image:
                images.append(container.image)

        rollouts.append(
            {
                "revision": revision,
                "replicas": replicas,
                "ready_replicas": ready_replicas,
                "image": ",".join(images),
                "created_at": (
                    replica_set.metadata.creation_timestamp
                ),
                "is_current": revision == current_revision,
            }
        )

    rollouts.sort(
        key=lambda rollout: rollout["revision"],
        reverse=True,
    )

    return rollouts
