from kubernetes import client
from app.core.kubernetes import load_kubernetes_config
from app.models.application import KubernetesApplication
from app.services.status import get_application_status

from app.models.application import (
    KubernetesApplication,
    ApplicationDetail,
    DeploymentDetail,
    ServiceDetail,
    IngressDetail,
    PodDetail,
)

def get_applications() -> list[KubernetesApplication]:
    load_kubernetes_config()

    apps_api = client.AppsV1Api()
    core_api = client.CoreV1Api()
    networking_api = client.NetworkingV1Api()

    applications = []

    deployments = apps_api.list_deployment_for_all_namespaces()

    services = core_api.list_service_for_all_namespaces()

    ingresses = networking_api.list_ingress_for_all_namespaces()


    for deployment in deployments.items:
        namespace = deployment.metadata.namespace
        name = deployment.metadata.name

        desired_replicas = (
            deployment.spec.replicas
            if deployment.spec.replicas is not None
            else 1
        )

        ready_replicas = (
            deployment.status.ready_replicas
            if deployment.status.ready_replicas is not None
            else 0
        )

        #
        # Pods liés au Deployment
        #
        pods = []

        selector = deployment.spec.selector.match_labels

        if selector:
            selector_query = ",".join(
                [
                    f"{key}={value}"
                    for key, value in selector.items()
                ]
            )

            pod_list = core_api.list_namespaced_pod(
                namespace=namespace,
                label_selector=selector_query
            )

            pods = [
                pod.metadata.name
                for pod in pod_list.items
            ]


        #
        # Service associé
        #
        service_name = None

        for service in services.items:
            if service.metadata.namespace != namespace:
                continue

            if service.spec.selector == selector:
                service_name = service.metadata.name
                break


        #
        # Ingress associé
        #
        ingress_name = None
        hosts = []

        for ingress in ingresses.items:
            if ingress.metadata.namespace != namespace:
                continue

            for rule in ingress.spec.rules or []:
                for path in rule.http.paths:
                    backend_service = (
                        path.backend
                        .service
                        .name
                    )

                    if backend_service == service_name:
                        ingress_name = ingress.metadata.name

                        if rule.host:
                            hosts.append(rule.host)


        applications.append(
            KubernetesApplication(
                name=name,
                namespace=namespace,
                ingress=ingress_name,
                hosts=hosts,
                service=service_name,
                deployment=name,
                desired_replicas=desired_replicas,
                ready_replicas=ready_replicas,
                pods=pods,
                status=get_application_status(
                    desired_replicas,
                    ready_replicas
                )
            )
        )


    return applications


def get_application_detail(
    namespace: str,
    name: str
) -> ApplicationDetail:

    load_kubernetes_config()

    apps_api = client.AppsV1Api()
    core_api = client.CoreV1Api()
    networking_api = client.NetworkingV1Api()

    deployment = apps_api.read_namespaced_deployment(
        name=name,
        namespace=namespace
    )

    desired = (
        deployment.spec.replicas
        if deployment.spec.replicas is not None
        else 1
    )

    ready = (
        deployment.status.ready_replicas
        if deployment.status.ready_replicas
        else 0
    )


    image = None

    containers = deployment.spec.template.spec.containers

    if containers:
        image = containers[0].image


    deployment_detail = DeploymentDetail(
        name=name,
        desired_replicas=desired,
        ready_replicas=ready,
        image=image
    )


    #
    # Pods
    #

    pods = []

    selector = deployment.spec.selector.match_labels

    if selector:

        selector_query = ",".join(
            [
                f"{k}={v}"
                for k, v in selector.items()
            ]
        )

        pod_list = core_api.list_namespaced_pod(
            namespace=namespace,
            label_selector=selector_query
        )

        for pod in pod_list.items:

            restarts = 0

            if pod.status.container_statuses:
                restarts = sum(
                    c.restart_count
                    for c in pod.status.container_statuses
                )


            pods.append(
                PodDetail(
                    name=pod.metadata.name,
                    status=pod.status.phase,
                    restarts=restarts
                )
            )


    #
    # Service
    #

    service_detail = None

    services = core_api.list_namespaced_service(
        namespace
    )

    for svc in services.items:

        if svc.spec.selector == selector:

            service_detail = ServiceDetail(
                name=svc.metadata.name,
                type=svc.spec.type,
                cluster_ip=svc.spec.cluster_ip
            )

            break


    #
    # Ingress
    #

    ingress_detail = None

    ingresses = networking_api.list_namespaced_ingress(
        namespace
    )

    for ingress in ingresses.items:

        for rule in ingress.spec.rules or []:

            if not rule.http:
                continue

            for path in rule.http.paths:

                if (
                    service_detail
                    and path.backend.service
                    and path.backend.service.name == service_detail.name
                ):

                    ingress_detail = IngressDetail(
                        name=ingress.metadata.name,
                        hosts=[
                            r.host
                            for r in ingress.spec.rules
                            if r.host
                        ],
                        tls=bool(ingress.spec.tls),
                    )


    return ApplicationDetail(
        name=name,
        namespace=namespace,
        status=get_application_status(
            desired,
            ready
        ),
        deployment=deployment_detail,
        service=service_detail,
        ingress=ingress_detail,
        pods=pods
    )
