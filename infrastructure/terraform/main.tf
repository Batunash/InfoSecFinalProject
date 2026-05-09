terraform {
  required_version = ">= 1.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.12"
    }
  }

  backend "s3" {
    bucket         = "devsecops-terraform-state"
    key            = "production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "devsecops-terraform-locks"
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

variable "docker_image" {
  description = "Docker image to deploy"
  type        = string
  default     = "YOUR_USERNAME/devsecops-app:latest"
}

variable "namespace" {
  description = "Kubernetes namespace"
  type        = string
  default     = "production"
}

variable "replicas" {
  description = "Number of replicas"
  type        = number
  default     = 3
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "devsecops-app"
}

resource "kubernetes_namespace" "production" {
  metadata {
    name = var.namespace
    labels = {
      name        = var.namespace
      environment = "production"
      managed-by  = "terraform"
    }
  }
}

resource "kubernetes_deployment" "app" {
  metadata {
    name      = var.app_name
    namespace = var.namespace
    labels = {
      app     = var.app_name
      version = "v1"
    }
  }

  spec {
    replicas = var.replicas

    strategy {
      type = "RollingUpdate"
      rolling_update {
        max_surge       = 1
        max_unavailable = 0
      }
    }

    selector {
      match_labels = {
        app = var.app_name
      }
    }

    template {
      metadata {
        labels = {
          app     = var.app_name
          version = "v1"
        }
        annotations = {
          "prometheus.io/scrape" = "true"
          "prometheus.io/port"   = "5000"
          "prometheus.io/path"   = "/metrics"
        }
      }

      spec {
        service_account_name = "${var.app_name}-sa"

        security_context {
          run_as_non_root = true
          run_as_user    = 1000
          fs_group       = 1000
        }

        container {
          name  = "app"
          image = var.docker_image

          port {
            name           = "http"
            container_port = 5000
            protocol       = "TCP"
          }

          env {
            name  = "FLASK_ENV"
            value = "production"
          }

          env {
            name = "JWT_SECRET_KEY"
            value_from {
              secret_key_ref {
                name = "${var.app_name}-secrets"
                key  = "jwt-secret"
              }
            }
          }

          resources {
            requests = {
              memory = "256Mi"
              cpu    = "250m"
            }
            limits = {
              memory = "512Mi"
              cpu    = "500m"
            }
          }

          security_context {
            allow_privilege_escalation = false
            read_only_root_filesystem = true
            run_as_non_root          = true
            run_as_user             = 1000
            capabilities {
              drop = ["ALL"]
            }
          }

          liveness_probe {
            http_get {
              path = "/health"
              port = "http"
            }
            initial_delay_seconds = 30
            period_seconds        = 10
            timeout_seconds       = 5
            failure_threshold     = 3
          }

          readiness_probe {
            http_get {
              path = "/health"
              port = "http"
            }
            initial_delay_seconds = 10
            period_seconds        = 5
            timeout_seconds       = 3
            failure_threshold     = 3
          }

          volume_mount {
            name       = "tmp"
            mount_path = "/tmp"
          }
        }

        volume {
          name = "tmp"
          empty_dir {}
        }

        affinity {
          pod_anti_affinity {
            preferred_during_scheduling_ignored_during_execution {
              weight = 100
              pod_affinity_term {
                label_selector {
                  match_expressions {
                    key      = "app"
                    operator = "In"
                    values   = [var.app_name]
                  }
                }
                topology_key = "kubernetes.io/hostname"
              }
            }
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "app" {
  metadata {
    name      = "${var.app_name}-service"
    namespace = var.namespace
    labels = {
      app = var.app_name
    }
  }

  spec {
    selector = {
      app = var.app_name
    }

    port {
      name        = "http"
      protocol    = "TCP"
      port        = 80
      target_port = 5000
    }

    type = "LoadBalancer"
  }
}

resource "kubernetes_service_account" "app" {
  metadata {
    name      = "${var.app_name}-sa"
    namespace = var.namespace
  }
}

resource "kubernetes_secret" "app" {
  metadata {
    name      = "${var.app_name}-secrets"
    namespace = var.namespace
  }

  type = "Opaque"

  data = {
    jwt-secret = "CHANGE_THIS_IN_PRODUCTION"
  }
}

resource "kubernetes_horizontal_pod_autoscaler" "app" {
  metadata {
    name      = "${var.app_name}-hpa"
    namespace = var.namespace
  }

  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = var.app_name
    }

    min_replicas = 3
    max_replicas = 10

    metric {
      type = "Resource"
      resource {
        name = "cpu"
        target {
          type                = "Utilization"
          average_utilization = 70
        }
      }
    }

    metric {
      type = "Resource"
      resource {
        name = "memory"
        target {
          type                = "Utilization"
          average_utilization = 80
        }
      }
    }
  }
}

resource "kubernetes_network_policy" "app" {
  metadata {
    name      = "${var.app_name}-netpol"
    namespace = var.namespace
  }

  spec {
    pod_selector {
      match_labels = {
        app = var.app_name
      }
    }

    policy_types = ["Ingress", "Egress"]

    ingress {
      from {
        namespace_selector {
          match_labels = {
            name = "ingress-nginx"
          }
        }
      }
      ports {
        protocol = "TCP"
        port     = 5000
      }
    }

    egress {
      to {
        namespace_selector {}
      }
      ports {
        protocol = "TCP"
        port     = 53
      }
      ports {
        protocol = "UDP"
        port     = 53
      }
    }
  }
}

output "deployment_name" {
  description = "Name of the deployment"
  value       = kubernetes_deployment.app.metadata[0].name
}

output "service_name" {
  description = "Name of the service"
  value       = kubernetes_service.app.metadata[0].name
}

output "namespace" {
  description = "Namespace"
  value       = kubernetes_namespace.production.metadata[0].name
}
