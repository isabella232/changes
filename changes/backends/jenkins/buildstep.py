from __future__ import absolute_import

from flask import current_app

from changes.backends.buildstep import BuildStep

from .builder import JenkinsBuilder
from .factory_builder import JenkinsFactoryBuilder


class JenkinsBuildStep(BuildStep):
    def __init__(self, job_name=None):
        self.job_name = job_name

    def get_builder(self, app=current_app):
        return JenkinsBuilder(app=app, job_name=self.job_name)

    def execute(self, job):
        builder = self.get_builder()
        if not job.data:
            builder.create_job(job)
        else:
            builder.sync_job(job)

    def get_label(self):
        return 'Execute job {0} on Jenkins'.format(self.job_name)


class JenkinsFactoryBuildStep(JenkinsBuildStep):
    def __init__(self, job_name=None, downstream_job_names=()):
        self.job_name = job_name
        self.downstream_job_names = downstream_job_names

    def get_builder(self, app=current_app):
        return JenkinsFactoryBuilder(
            app=app,
            job_name=self.job_name,
            downstream_job_names=self.downstream_job_names,
        )
