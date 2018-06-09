from django.contrib.staticfiles.storage import CachedFilesMixin, ManifestFilesMixin
from pipeline.storage import PipelineMixin
from storages.backends.s3boto3 import S3Boto3Storage


class S3PipelineManifestStorage(PipelineMixin, ManifestFilesMixin, S3Boto3Storage):
    pass


class S3PipelineCachedStorage(PipelineMixin, CachedFilesMixin, S3Boto3Storage):
    pass
