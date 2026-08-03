from kubernetes import client, config

from app.models.certificate import Certificate


def get_certificates(namespace: str | None = None) -> list[Certificate]:
    try:
        config.load_incluster_config()
    except Exception:
        config.load_kube_config()

    api = client.CustomObjectsApi()

    if namespace:
        certificates = api.list_namespaced_custom_object(
            group="cert-manager.io",
            version="v1",
            namespace=namespace,
            plural="certificates",
        )
    else:
        certificates = api.list_cluster_custom_object(
            group="cert-manager.io",
            version="v1",
            plural="certificates",
        )

    result = []

    for item in certificates.get("items", []):

        status = item.get("status", {})
        conditions = status.get("conditions", [])

        ready = False
        ready_status = "Unknown"

        for condition in conditions:
            if condition.get("type") == "Ready":
                ready = condition.get("status") == "True"
                ready_status = condition.get("message", "Unknown")

        spec = item.get("spec", {})

        result.append(
            Certificate(
                namespace=item["metadata"]["namespace"],
                name=item["metadata"]["name"],
                secret_name=spec.get("secretName"),
                dns_names=spec.get("dnsNames", []),
                issuer=spec.get("issuerRef", {}).get("name"),
                ready=ready,
                status=ready_status,
                not_after=status.get("notAfter"),
                renewal_time=status.get("renewalTime"),
            )
        )

    return result
