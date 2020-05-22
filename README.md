# drone-ecr-retag
A Drone plugin for retagging an existing image on Amazon ECR without using Docker.

This plugin is built to suit only a specific workflow which meets some assumptions:

- There is already images tagged with commit-[commit hash] on ECR.
- Images are pushed only to ECR repositories on your on account.

It supports replication across ECR registries on multiple AWS regions.

## Usage

```
steps:
  - name: 'Promote Docker image to integration'
    image: diegoaltx/drone-ecr-retag
    settings:
      tags:
        - integration
      repo: microservice-example
      region:
        - us-east-1
        - sa-east-1
    when:
      ref:
        - refs/heads/master
  
  - name: 'Promote Docker image to staging'
    image: diegoaltx/drone-ecr-retag
    settings:
      tags:
        - staging
      repo: microservice-example
      region:
        - us-east-1
        - sa-east-1
    when:
      ref:
        - refs/heads/master

  - name: 'Promote Docker image to production'
    image: diegoaltx/drone-ecr-retag
    settings:
      tags:
        - production
      repo: microservice-example
      region:
        - us-east-1
        - sa-east-1
    when:
      ref:
        - refs/heads/master
```

## Settings

| Key                              | Description                                   |
|----------------------------------|-----------------------------------------------|
| **regions** *required*           | ECR registries regions.                       |
| **repo** *optional*              | ECR repo name. Defaults to git repo name.     |
| **tags** *optional*              | Tags to assign to image. Defaults to VCS tag. |
| **access_key_id** *optional*     | AWS access key id.                            |
| **secret_access_key** *optional* | AWS secret access key.                        |
