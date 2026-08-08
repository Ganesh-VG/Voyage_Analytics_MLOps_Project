#!/bin/bash

set -e

echo "===================================="
echo "Initializing Minikube for Jenkins"
echo "===================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

KUBE_DIR="$PROJECT_ROOT/jenkins/kube"
KUBECONFIG_FILE="$KUBE_DIR/config"

echo
echo "Project root:"
echo "$PROJECT_ROOT"

echo
echo "Checking Minikube..."

if ! minikube status >/dev/null 2>&1; then
    echo "Minikube is not running."
    echo "Starting Minikube..."

    minikube start --driver=docker
else
    echo "Minikube is already running."
fi

echo
echo "Updating Minikube context..."

minikube update-context

echo
echo "Getting Minikube IP..."

MINIKUBE_IP=$(minikube ip)

echo "Minikube IP: $MINIKUBE_IP"

echo
echo "Creating Jenkins kube directory..."

mkdir -p "$KUBE_DIR"

echo
echo "Creating Jenkins-compatible kubeconfig..."

cat > "$KUBECONFIG_FILE" <<EOF
apiVersion: v1
kind: Config

clusters:
- name: minikube
  cluster:
    certificate-authority: /root/.kube/ca.crt
    server: https://${MINIKUBE_IP}:8443

contexts:
- name: minikube
  context:
    cluster: minikube
    namespace: default
    user: minikube

current-context: minikube

users:
- name: minikube
  user:
    client-certificate: /root/.kube/client.crt
    client-key: /root/.kube/client.key
EOF

echo
echo "Copying required certificates..."

cp "$HOME/.minikube/ca.crt" \
   "$KUBE_DIR/ca.crt"

cp "$HOME/.minikube/profiles/minikube/client.crt" \
   "$KUBE_DIR/client.crt"

cp "$HOME/.minikube/profiles/minikube/client.key" \
   "$KUBE_DIR/client.key"

echo
echo "Kubeconfig created:"
echo "$KUBECONFIG_FILE"

echo
echo "Testing Kubernetes from Jenkins..."

docker exec voyage_jenkins kubectl get nodes

echo
echo "===================================="
echo "Initialization Complete!"
echo "===================================="