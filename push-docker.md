# Docker Build and Push

Make sure you're logged in to DockerHub first:

```bash
docker login
```

To build and push multi-platform image to DockerHub:

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t boedegoat/ctf-instance-runner:latest --push .
```

This command:

-   Builds for both AMD64 and ARM64 platforms
-   Tags the image as `boedegoat/ctf-instance-runner:latest`
-   Automatically pushes to DockerHub
