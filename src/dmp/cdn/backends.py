from storages.backends.s3boto3 import S3Boto3Storage, SpooledTemporaryFile
import os
from abc import ABC
from tempfile import SpooledTemporaryFile

class StaticRootS3Boto3Storage(S3Boto3Storage, ABC):
    bucket_name = 'plannit-spaces'
    location = 'static'

    def _save(self, name, content):
        """
        We create a clone of the content file as when this is passed to
        boto3 it wrongly closes the file upon upload where as the storage
        backend expects it to still be open
        """
        # Seek our content back to the start
        content.seek(0, os.SEEK_SET)

        # Create a temporary file that will write to disk after a specified
        # size. This file will be automatically deleted when closed by
        # boto3 or after exiting the `with` statement if the boto3 is fixed
        with SpooledTemporaryFile() as content_autoclose:

            # Write our original content into our copy that will be closed by boto3
            content_autoclose.write(content.read())

            # Upload the object which will auto close the
            # content_autoclose instance
            return super(StaticRootS3Boto3Storage, self)._save(name, content_autoclose)


class MediaRootS3Boto3Storage(S3Boto3Storage, ABC):
    bucket_name = 'plannit-spaces'
    location = 'static/media' 

    def _save(self, name, content):
        """
        We create a clone of the content file as when this is passed to
        boto3 it wrongly closes the file upon upload where as the storage
        backend expects it to still be open
        """
        # Seek our content back to the start
        content.seek(0, os.SEEK_SET)

        # Create a temporary file that will write to disk after a specified
        # size. This file will be automatically deleted when closed by
        # boto3 or after exiting the `with` statement if the boto3 is fixed
        with SpooledTemporaryFile() as content_autoclose:

            # Write our original content into our copy that will be closed by boto3
            content_autoclose.write(content.read())

            # Upload the object which will auto close the
            # content_autoclose instance
            return super(MediaRootS3Boto3Storage, self)._save(name, content_autoclose)