from kubernetes import client, config


def load_kubernetes_config():
    try:
        config.load_incluster_config()
    except config.ConfigException:
        config.load_kube_config()


def get_core_v1() -> client.CoreV1Api:
    load_kubernetes_config()
    return client.CoreV1Api()


def get_apps_v1() -> client.AppsV1Api:
    load_kubernetes_config()
    return client.AppsV1Api()


def get_networking_v1() -> client.NetworkingV1Api:
    load_kubernetes_config()
    return client.NetworkingV1Api()


def get_custom_objects_api() -> client.CustomObjectsApi:
    load_kubernetes_config()
    return client.CustomObjectsApi()

def get_api_client():
    load_kubernetes_config()
    return client.ApiClient()
