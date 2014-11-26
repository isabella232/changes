import uuid
import logging

from base64 import b64decode
from cStringIO import StringIO
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.schema import Index
from sqlalchemy.orm import relationship

from changes.config import db
from changes.db.types.enum import Enum as EnumType
from changes.db.types.filestorage import FileStorage, FileData
from changes.db.types.guid import GUID
from changes.db.utils import model_repr

logger = logging.getLogger('models.testartifact')

TESTARTIFACT_STORAGE_OPTIONS = {
    'path': 'test-artifacts',
}


class TestArtifactType(Enum):
    unknown = 0
    text = 1
    image = 2
    html = 3

    def __str__(self):
        return TYPE_LABELS[self]


TYPE_LABELS = {
    TestArtifactType.unknown: 'Unknown',
    TestArtifactType.text: 'Text',
    TestArtifactType.image: 'Image',
    TestArtifactType.html: 'Html',
}


class TestArtifact(db.Model):
    __tablename__ = 'testartifact'
    __tableargs__ = (
        Index('idx_test_id', 'test_id'),
    )

    id = Column(GUID, nullable=False, primary_key=True, default=uuid.uuid4)
    test_id = Column(GUID, ForeignKey('test.id', ondelete="CASCADE"), nullable=False)
    name = Column('name', String(length=256), nullable=False)
    type = Column(EnumType(TestArtifactType),
                  default=TestArtifactType.unknown,
                  nullable=False, server_default='0')
    file = Column(FileStorage(**TESTARTIFACT_STORAGE_OPTIONS))
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)

    test = relationship('TestCase')

    __repr__ = model_repr('name', 'type', 'file')

    def __init__(self, **kwargs):
        super(TestArtifact, self).__init__(**kwargs)
        if self.id is None:
            self.id = uuid.uuid4()
        if self.date_created is None:
            self.date_created = datetime.utcnow()
        if isinstance(self.type, str):
            self.type = TestArtifactType[self.type]
        if self.file is None:
            # TODO(dcramer): this is super hacky but not sure a better way to
            # do it with SQLAlchemy
            self.file = FileData({}, TESTARTIFACT_STORAGE_OPTIONS)

    def save_base64_content(self, base64):
        content = b64decode(base64)
        self.file.save(
            StringIO(content), '{0}/{1}_{2}'.format(
                self.test_id, self.id.hex, self.name
            )
        )
