import os
import re
import socket

import pymongo

import strax


class RunDB(strax.StorageFrontend):
    """Frontend that searches RunDB MongoDB for data.

    Loads appropriate backends ranging from Files to S3.
    """

    def __init__(self,
                 mongo_url,
                 path='.',
                 s3_kwargs={},
                 *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.client = pymongo.MongoClient(mongo_url)
        self.collection = self.client['xenon1t']['runs']

        self.path = path

        # Setup backends for reading.  Don't change order!
        self.backends = [
            strax.S3Backend(**s3_kwargs),
        ]

        # This mess tries to identify the cluster
        self.dali = True if re.match('^dali.*rcc.*', socket.getfqdn()) else False
        if self.dali:
            self.backends.append(strax.FileSytemBackend())

    def _find(self, key: strax.DataKey, write, fuzzy_for, fuzzy_for_options):
        if fuzzy_for or fuzzy_for_options:
            raise NotImplementedError("Can't do fuzzy with RunDB yet.")

        query = {'name': key.run_id,
                 'data.type': key.data_type,
                 '$or': [{'data.host': 'ceph-s3'}]}

        if self.dali:
            query['$or'].append({'data.host': 'dali'})

        doc = self.collection.find_one(query,
                                       {'data': {'$elemMatch': {'type': key.data_type,
                                                                'meta.lineage': key.lineage}}
                                        })

        if (doc is None) or ('data' not in doc) or (len(doc['data']) == 0):
            if write:
                return self.backends[-1].__class__.__name__, os.path.join(self.path, str(key))
            else:
                # If reading and no objects, then problem
                raise strax.DataNotAvailable

        datum = doc['data'][0]

        if write and not self._can_overwrite(key):
            raise strax.DataExistsError(at=datum['protocol'])

        return datum['protocol'], datum['location']

    def remove(self, key):
        raise NotImplementedError()