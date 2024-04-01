terraform {
  required_version = ">= 1.5"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "2.27.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "2.12.1"
    }
  }
}

provider "kubernetes" {
  config_context = var.kubernetes_context
  config_path    = var.kubernetes_config_path
}

provider "helm" {
  kubernetes {
    config_context = var.kubernetes_context
    config_path    = var.kubernetes_config_path
  }
}

locals {
  argo_namespace                                   = "argo"
  argo_manifests                                   = split("---", file("${path.module}/k8s/argo.yaml"))
  argo_events_manifests                            = split("---", file("${path.module}/k8s/argo-events.yaml"))
  argo_events_install_validating_webhook_manifests = split("---", file("${path.module}/k8s/argo-events-install-validating-webhook.yaml"))
}

resource "kubernetes_namespace" "argo" {
  metadata {
    name = local.argo_namespace
  }
}

resource "kubernetes_namespace" "argo_events" {
  metadata {
    name = "argo-events"
  }
}

resource "kubernetes_manifest" "argo_install" {
  depends_on = [kubernetes_namespace.argo]

  count    = length(local.argo_manifests)
  manifest = yamldecode(local.argo_manifests[count.index])

  field_manager {
    force_conflicts = true
  }
}

resource "kubernetes_role" "argo_api_role" {
  metadata {
    name      = "argo-api"
    namespace = local.argo_namespace
  }

  rule {
    api_groups = [
      ""
    ]
    resources = [
      "workflows.argoproj.io"
    ]
    verbs = [
      "list",
      "patch"
    ]
  }
}

resource "kubernetes_service_account" "argo_api" {
  metadata {
    name      = "argo-api"
    namespace = local.argo_namespace
  }
}

resource "kubernetes_secret" "argo_api_token" {
  metadata {
    name        = "argo-api-token"
    namespace   = local.argo_namespace
    annotations = {
      "kubernetes.io/service-account.name" : kubernetes_service_account.argo_api.metadata[0].name
    }
  }
  type = "kubernetes.io/service-account-token"
}

resource "kubernetes_role_binding" "argo_api" {
  metadata {
    name = "argo-api"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.argo_api_role.metadata[0].name
  }
  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.argo_api.metadata[0].name
    namespace = local.argo_namespace
  }
}

resource "kubernetes_manifest" "argo_events_install" {
  depends_on = [kubernetes_namespace.argo_events]

  count    = length(local.argo_events_manifests)
  manifest = yamldecode(local.argo_events_manifests[count.index])

  field_manager {
    force_conflicts = true
  }
}

resource "kubernetes_manifest" "argo_events_install_validating_webhook_manifests_install" {
  depends_on = [kubernetes_manifest.argo_events_install]

  count    = length(local.argo_events_install_validating_webhook_manifests)
  manifest = yamldecode(local.argo_events_install_validating_webhook_manifests[count.index])

  field_manager {
    force_conflicts = true
  }
}

resource "helm_release" "minio" {
  chart = "${path.module}/charts/minio"

  name             = "minio"
  namespace        = "minio"
  create_namespace = true
}

output "argo_api_token" {
  value = nonsensitive(kubernetes_secret.argo_api_token.data.token)
}
