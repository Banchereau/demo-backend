from app.services.kubernetes import get_networking_v1_api


def get_ingresses(namespace=None):

    networking = get_networking_v1_api()

    if namespace:
        ingresses = networking.list_namespaced_ingress(
            namespace=namespace
        )
    else:
        ingresses = networking.list_ingress_for_all_namespaces()

    result = []

    for ingress in ingresses.items:

        hosts = []
        service = None
        tls_secret = None

        if ingress.spec.rules:
            for rule in ingress.spec.rules:

                if rule.host:
                    hosts.append(rule.host)

                if rule.http and rule.http.paths:
                    path = rule.http.paths[0]

                    if path.backend.service:
                        service = path.backend.service.name

        if ingress.spec.tls:
            tls_secret = ingress.spec.tls[0].secret_name

        result.append(
            {
                "namespace": ingress.metadata.namespace,
                "name": ingress.metadata.name,
                "hosts": hosts,
                "service": service,
                "tls_secret": tls_secret,
            }
        )

    return result
