from app.services.kubernetes import (
    get_core_v1_api,
)
from app.services.certificates import get_certificates

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


def get_platform_health():

    components = [
        check_kubernetes_api(),
        check_cert_manager(),
        check_flux(),
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
