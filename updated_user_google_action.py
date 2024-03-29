#!/usr/bin/python2.4
#
# Copyright 2006 Google, Inc.
# All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License")
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Default action for users who've been updated

  UpdatedUserGoogleAction: the class implementing the default action
"""


import google_action
import logging
import userdb
from google.appsforyourdomain import provisioning
from google.appsforyourdomain import provisioning_errs


class UpdatedUserGoogleAction(google_action.GoogleAction):

  """ The default "GoogleAction" for users whose LDAP records have been
  updated.  This is NOT called if the usernames have been changed; for
  that handler, look at RenamedUserGoogleAcion.
  This object
  does an UpdateAccount on the user and queues its results on the
  GoogleResultQueue
  """
  def __init__(self, api, result_queue, thread_stats, **moreargs):
    """ Constructor
    Args:
      api: a google.appsforyourdomain.provisioning.API object
      result_queue:  a google_result_queue.GoogleResultQueue object,
        for writing results back to a status handler
    """
    super(UpdatedUserGoogleAction, self).__init__(api=api,
        result_queue=result_queue, thread_stats=thread_stats, **moreargs)
    self._api = api
    self._result_queue = result_queue

  def Handle(self, dn, attrs):
    """ Override of superclass.Handle() method
    Args:
      dn: distinguished name of the user
      attrs: dictionary of all the user's attributes
    """
    self.dn = dn
    self.attrs = attrs
    try:
      Update(self._api, attrs)

      # report success
      logging.debug('updated %s' % self.attrs['GoogleUsername'])
      self._thread_stats.IncrementStat('updates', 1)
      self._result_queue.PutResult(self.dn, 'updated', None, attrs)

    except provisioning_errs.ProvisioningApiError, e:
      # report failure
      logging.error('error: %s' % str(e))
      self._thread_stats.IncrementStat('update_fails', 1)
      self._result_queue.PutResult(self.dn, 'updated', str(e))

    except Exception, e:
      logging.error('error during update: %s' % str(e)) 
      self._thread_stats.IncrementStat('update_fails', 1)
      self._result_queue.PutResult(self.dn, 'added', str(e))

def Update(api, attrs):
  """ Update the Google Account given by dn with attrs.
  Args:
    attrs: dictionary of all the user's attributes
  """
  mapping_for_updates = {'firstName': 'GoogleFirstName', 
                         'lastName': 'GoogleLastName',
                         'password': 'GooglePassword'}
  fields = {}
  for (key, google_key) in mapping_for_updates.iteritems():
    if google_key in attrs and attrs[google_key]:
      if key == 'password':
        fields[key] = attrs[google_key]
      else:
        fields[key] = userdb.toUnicode(attrs[google_key])
  logging.debug('about to UpdateAccount for %s' % attrs['GoogleUsername'])
  api.UpdateAccount(attrs['GoogleUsername'], fields)

if __name__ == '__main__':
  pass
