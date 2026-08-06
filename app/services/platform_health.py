from app.services.kubernetes import (
    get_core_v1_api,
    get_apps_v1_api,
)
from app.services.certificates import get_certificates
from app.services.applications import get_applications

def check_kubernetes_api():

    try:
        v1 = get_core_v1_api()

        v1.list_namespace(
            limit=1
        )

        return {
            "name": "Kubernetes API",
            "status": "healthy",
            "message": "API reachable",
        }

    except Exception as e:
        return {
            "name": "Kubernetes API",
            "status": "unhealthy",
            "message": str(e),
        }


def check_cert_manager():

    try:
        certificates = get_certificates()

        total = len(certificates)

        ready = sum(
            1
            for certificate in certificates
            if certificate.ready
        )

        if total == 0:
            return {
                "name": "cert-manager",
                "status": "degraded",
                "message": "No certificates found",
            }

        if ready == total:
            return {
                "name": "cert-manager",
                "status": "healthy",
                "message": f"{ready}/{total} certificates ready",
            }

        return {
            "name": "cert-manager",
            "status": "degraded",
            "message": f"{ready}/{total} certificates ready",
        }

    except Exception as e:
        return {
            "name": "cert-manager",
            "status": "unhealthy",
            "message": str(e),
        }


def check_flux():

    try:
        v1 = get_core_v1_api()

        pods = v1.list_namespaced_pod(
            namespace="flux-system"
        )

        running = [
            pod
            for pod in pods.items
            if pod.status.phase == "Running"
        ]

        if running:
            return {
                "name": "FluxCD",
                "status": "healthy",
                "message": f"{len(running)} controllers running",
            }

        return {
            "name": "FluxCD",
            "status": "unhealthy",
            "message": "No running controllers",
        }

    except Exception as e:
        return {
            "name": "FluxCD",
            "status": "unknown",
            "message": str(e),
        }


def check_ingress_controller():

    try:
        apps = get_apps_v1_api()

        deployment = apps.read_namespaced_deployment(
            name="ingress-nginx-controller",
            namespace="ingress-nginx",
        )

        replicas = deployment.spec.replicas or 0
        ready = deployment.status.ready_replicas or 0

        if ready == replicas:
            return {
                "name": "Ingress Controller",
                "status": "healthy",
                "message": (
                    "1 controller running"
                    if ready == 1
                    else f"{ready} controllers running"
                ),
            }

        return {
            "name": "Ingress Controller",
            "status": "degraded",
            "message": f"{ready}/{replicas} controllers ready",
        }

    except Exception as e:
        return {
            "name": "Ingress Controller",
            "status": "unhealthy",
            "message": str(e),
        }


def check_applications():

    try:
        applications = get_applications()

        total = len(applications)

        healthy = sum(
            1
            for application in applications
            if application.status == "healthy"
        )

        if total == 0:
            return {
                "name": "Applications",
                "status": "degraded",
                "message": "No applications found",
            }

        if healthy == total:
            return {
                "name": "Applications",
                "status": "healthy",
                "message": f"{healthy}/{total} applications healthy",
            }

        return {
            "name": "Applications",
            "status": "degraded",
            "message": f"{healthy}/{total} applications healthy",
        }

    except Exception as e:
        return {
            "name": "Applications",
            "status": "unhealthy",
            "message": str(e),
        }


def check_monitoring():

    try:
        apps = get_apps_v1_api()

        checks = {
            "Grafana": False,
            "Alertmanager": False,
            "kube-state-metrics": False,
            "Prometheus Operator": False,
        }

        deployments = apps.list_namespaced_deployment(
            namespace="monitoring"
        )

        for deployment in deployments.items:

            name = deployment.metadata.name

            ready = (
                deployment.status.ready_replicas
                or 0
            )

            if (
                "grafana" in name
                and ready > 0
            ):
                checks["Grafana"] = True

            if (
                "kube-state-metrics" in name
                and ready > 0
            ):
                checks["kube-state-metrics"] = True

            if (
                "operator" in name
                and ready > 0
            ):
                checks["Prometheus Operator"] = True


        statefulsets = apps.list_namespaced_stateful_set(
            namespace="monitoring"
        )

        for statefulset in statefulsets.items:

            name = statefulset.metadata.name

            ready = (
                statefulset.status.ready_replicas
                or 0
            )

            if (
                "alertmanager" in name
                and ready > 0
            ):
                checks["Alertmanager"] = True


        running = sum(
            checks.values()
        )

        expected = len(checks)


        if running == expected:
            return {
                "name": "Monitoring",
                "status": "healthy",
                "message": (
                    "Grafana, Alertmanager, "
                    "kube-state-metrics and "
                    "Prometheus Operator running"
                ),
            }


        return {
            "name": "Monitoring",
            "status": "degraded",
            "message": (
                f"{running}/{expected} "
                "monitoring components running"
            ),
        }


    except Exception as e:
        return {
            "name": "Monitoring",
            "status": "unhealthy",
            "message": str(e),
        }


def check_network():

    try:
        v1 = get_core_v1_api()

        checks = {
            "Cilium": False,
            "MetalLB Controller": False,
            "MetalLB Speaker": False,
            "MetalLB FRR": False,
        }


        cilium = v1.list_namespaced_pod(
            namespace="kube-system",
            label_selector="k8s-app=cilium",
        )

        checks["Cilium"] = any(
            pod.status.phase == "Running"
            for pod in cilium.items
        )


        metallb = v1.list_namespaced_pod(
            namespace="metallb-system",
        )


        for pod in metallb.items:

            if pod.status.phase != "Running":
                continue

            labels = pod.metadata.labels or {}

            component = labels.get(
                "app.kubernetes.io/component"
            )

            if component == "controller":
                checks["MetalLB Controller"] = True

            elif component == "speaker":
                checks["MetalLB Speaker"] = True

            elif component == "frr-k8s":
                checks["MetalLB FRR"] = True


        running = sum(checks.values())
        expected = len(checks)


        if running == expected:
            return {
                "name": "Network",
                "status": "healthy",
                "message": (
                    "Cilium and MetalLB running"
                ),
            }


        return {
            "name": "Network",
            "status": "degraded",
            "message": (
                f"{running}/{expected} "
                "network components running"
            ),
        }


    except Exception as e:
        return {
            "name": "Network",
            "status": "unhealthy",
            "message": str(e),
        }

def get_platform_health():

    components = [
        check_kubernetes_api(),
        check_cert_manager(),
        check_flux(),
        check_ingress_controller(),
        check_applications(),
        check_monitoring(),
        check_network(),
    ]

    status = (
        "healthy"
        if all(
            component["status"] == "healthy"
            for component in components
        )
        else "degraded"
    )

    return {
        "status": status,
        "components": components,
    }
