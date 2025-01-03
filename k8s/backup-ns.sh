#!/bin/bash

# Check if namespace argument is provided
if [ -z "$1" ]; then
    echo "Please provide a namespace name"
    echo "Usage: $0 <Namespace>"
    exit 1
fi

NAMESPACE=$1
BACKUP_DIR="k8s_backup_${NAMESPACE}_$(date +%Y%m%d_%H%M%S)"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "Starting backup of namespace: $NAMESPACE"

# List of resources to backup
RESOURCES=(
    "configmap"
    "secret"
    "deployment"
    "statefulset"
    "service"
    "ingress"
    "horizontalpodautoscaler"
    "persistentvolumeclaim"
    "cronjob"
    "job"
    "daemonset"
    "serviceaccount"
    "role"
    "rolebinding"
    "networkpolicy"
)

# Backup each resource type
for RESOURCE in "${RESOURCES[@]}"; do
    echo "Backing up $RESOURCE..."
    # Get resource list
    kubectl get "$RESOURCE" -n "$NAMESPACE" -o name > "$BACKUP_DIR/${RESOURCE}_list.txt" 2>/dev/null
    
    if [ -s "$BACKUP_DIR/${RESOURCE}_list.txt" ]; then
        # Create resource backup directory
        mkdir -p "$BACKUP_DIR/$RESOURCE"
        
        # Backup each resource
        while IFS= read -r ITEM; do
            NAME=$(basename "$ITEM")
            echo "- Backing up $RESOURCE/$NAME"
            kubectl get "$RESOURCE" "$NAME" -n "$NAMESPACE" -o yaml > "$BACKUP_DIR/$RESOURCE/$NAME.yaml" 2>/dev/null
        done < "$BACKUP_DIR/${RESOURCE}_list.txt"
    else
        echo "No $RESOURCE found in namespace $NAMESPACE"
        rm "$BACKUP_DIR/${RESOURCE}_list.txt"
    fi
done

# Backup namespace metadata
echo "Backing up namespace metadata..."
kubectl get namespace "$NAMESPACE" -o yaml > "$BACKUP_DIR/namespace.yaml" 2>/dev/null

# Create a tarball of the backup
#tar -czf "${BACKUP_DIR}.tar.gz" "$BACKUP_DIR"

echo "Backup completed! Files are stored in ${BACKUP_DIR}.tar.gz"
echo "Please verify the backup contents before deleting the namespace"

# Optional: Remove the uncompressed backup directory
#rm -rf "$BACKUP_DIR"
