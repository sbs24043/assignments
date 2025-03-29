#!/bin/bash
# ./build.sh clientapp v0.0.1-custom

APP_TYPE=$1  # First argument. Options: serverapp, clientapp

# Variables
IMAGE_NAME="leeloodub/flwr_$APP_TYPE"
VERSION=$2  # Second argument. Example: v1.0.0-custom
PLATFORMS="linux/amd64,linux/arm64/v8"
DOCKERFILE="$APP_TYPE.Dockerfile"

# Enable Docker Buildx
#echo "Enabling Docker Buildx..."
#docker buildx create --use --name multiarch-builder || docker buildx use multiarch-builder

# Build the multi-architecture image
echo "Building multi-architecture image for $IMAGE_NAME:$VERSION..."
docker buildx build \
  --platform $PLATFORMS \
  -f $DOCKERFILE \
  -t $IMAGE_NAME:$VERSION \
  --push .

# Verify the image on Docker Hub
echo "Image $IMAGE_NAME:$VERSION has been pushed to Docker Hub."