import boto3
import botocore
import os
import sys

def get_ecr_clients(settings):
  clients = []
  
  for region in settings['regions']:
    clients.append(boto3.client('ecr',
      aws_access_key_id=settings['access_key_id'],
      aws_secret_access_key=settings['secret_access_key'],
      region_name=region
    ))

  return clients

def get_sts_client(settings):
  return boto3.client('sts', 
    aws_access_key_id=settings['access_key_id'],
    aws_secret_access_key=settings['secret_access_key']
  )

def get_aws_account_id(sts_client):
  return sts_client.get_caller_identity().get('Account')

def get_regions(env):
  regions = env.get('PLUGIN_REGION')

  if not regions:
    return None
  
  return regions.split(',')

def get_repo(env):
  return env.get('PLUGIN_REPO', env.get('DRONE_REPO_NAME'))

def get_commit_tags(env):
  commit = env.get('DRONE_COMMIT')
  refs = [commit[0:7]]

  return ['commit-' + ref for ref in refs]

def get_tags(env):
  user_tags = env.get('PLUGIN_TAGS')
  vcs_tag = env.get('DRONE_TAG')
  tags = []

  if vcs_tag:
    tags.append(vcs_tag)

  if user_tags:
    tags.extend(user_tags.split(','))
  
  return tags

def get_settings(env):
  return {
    'access_key_id': env.get('PLUGIN_ACCESS_KEY_ID'),
    'secret_access_key': env.get('PLUGIN_SECRET_ACCESS_KEY'),
    'regions': get_regions(env),
    'repo': get_repo(env),
    'commit': env.get('DRONE_COMMIT'),
    'commit_tags': get_commit_tags(env),
    'tags': get_tags(env)
  }

def get_images(ecr_clients, settings):
  images = []

  for client in ecr_clients:
    response = client.batch_get_image(
      repositoryName=settings['repo'],
      imageIds=[{'imageTag': settings['commit_tags'][0]}]
    )
    image = response['images'][0]
    images.append(image)
  
  return images

def retag_images(ecr_clients, settings, images):
  for index, client in enumerate(ecr_clients):
    for tag in settings['tags']:
      image = images[index]
      try:
        client.put_image(
          repositoryName=settings['repo'],
          imageManifest=image['imageManifest'],
          imageManifestMediaType=image['imageManifestMediaType'],
          imageTag=tag
        )
      except client.exceptions.ImageAlreadyExistsException:
        pass

def exit_with_error(message, *args):
  print('Something went wrong:', message.format(*args), file=sys.stderr)
  sys.exit(1)

def retag():
  settings = get_settings(os.environ)

  ecr_clients = get_ecr_clients(settings)
  
  print('Repo name is', settings['repo'])
  
  print('Regions:')
  for region in settings['regions']:
    print('- ', region)

  print('Fetching images info from ECR across regions...')
  images = get_images(ecr_clients, settings)

  print('Fetched images info. Rettaging images...')
  retag_images(ecr_clients, settings, images)

  print('Retaged images. All done.')

if __name__ == '__main__':
  retag()
