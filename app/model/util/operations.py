from google.appengine.ext import db
import logging
from utils.utils import slice_up_list

"""

This should contain all the business logic necessary
for deleting users, links, and topics, or preparing them for deletion.

Incorporate cleanup. 

"""

"""

This should all run in transactions? 

"""






def delete_user(user_key):
  # check in case entity was sent
  if type(user_key).__name__ == "Profile":
    user_key = user_key.key()
  # this will only work with dummy users
  # does not yet get links, etc.
  # best for after messing up and creating a wrong user   
  from model.account import Account
  from model.user import Profile, QuizTaker
  from model.activity import ActivityProfile, UserTopicScores, PostedLink, Scoop, SharedItem
  from model.sponsor import Sponsor, Pledge
  from model.student import Student
  from model.timeline import ProfileTimeline
  
  delete = []    
  p = Profile.get(user_key)
  if p:
    delete.append(p)
  else:
    logging.error('unable to delete user. User key %s not found' % user_key)
    return False
  student = p.student.get()
  if student:
    delete.append(student)
    delete.extend(student.pledges.fetch(50))
  sponsor = p.sponsor.get()
  if sponsor:
    delete.append(sponsor)
    delete.extend(sponsor.pledges.fetch(50))
  key_name = p.key().name()
  failed_links = []
  activity_profiles = p.activity_profiles.fetch(5)
  for a in activity_profiles:
    if a:  
      delete.append(a)
      links = a.links.fetch(1000)
      failed_links.extend(links)
  delete_links(failed_links)
  ts = p.topic_scores.get()
  if ts:
    delete.append(ts)
  ac = Account.get_by_key_name(key_name)
  if ac:
    delete.append(ac)
  shared_items = p.shared_items.fetch(300)
  if shared_items:
    delete.extend(shared_items)
  pt = p.timeline.get()
  if pt:
    delete.append(pt)
  qt = QuizTaker.get_by_key_name(key_name)
  if qt:
    delete.append(qt)
  
  delete.extend(Scoop.all().filter(
    'scooper IN', [a.key() for a in activity_profiles]).fetch(1000))
  delete.extend(Scoop.all().filter(
    'scooped IN', [a.key() for a in activity_profiles]).fetch(1000))                      
  logging.error('deleting %d entities - %s' % (len(delete), str([e.key() for e in delete])))
  db.delete(delete)



# run in transaction!
def delete_links(failed_links, save=True):
  from utils.utils import delete_entities
  from model.util.methods import getRelationalEntityIndexes
  from model.activity import PostedLinkContent, LinkGroup
  _failed_links = failed_links[:]
  link_msg = ('delete_links deleting failed links: %s' 
  % str([link.key().name() for link in failed_links]))
  logging.warning(link_msg)
  print link_msg
  save_links = []
  link_keys = [link.key() for link in failed_links]
  failed_links_content = getRelationalEntityIndexes(link_keys,
                          PostedLinkContent, relationship='link', 
                          sort=None) # not going to be sorted 
  link_msg = ('delete_links deleting failed link content: %s' 
  % str([link.key().name() for link in failed_links_content]))
  logging.warning(link_msg)
  print link_msg
  from model.activity import LinkGroup
  for link_key in link_keys:
    lgs = LinkGroup.all().filter('links', link_key).fetch(500)
    for lg in lgs:
       lg.links.remove(link_key)
       if len(lg.links) == 0:
         failed_links.append(lg)
       else:
         save_links.append(lg)
  failed_links.extend(failed_links_content)
# Get scoops
  from model.activity import Scoop
  # if there are more than 30 failed links, there might be a problem here

  failed_scoops = []
  failed_link_lists = slice_up_list(_failed_links)
  for links in failed_link_lists:
    failed_scoops.extend(Scoop.all().filter(
    'scooper_link IN', links).fetch(1000))
    failed_scoops.extend(Scoop.all().filter(
    'scooped_link IN', links).fetch(1000))
  failed_scoop_msg = 'delete_links deleting %d failed scoops: %s' % (len(failed_scoops), [ scoop.key().name() for scoop in failed_scoops ])
  logging.warning(failed_scoop_msg)
  print failed_scoop_msg
  failed_links.extend(failed_scoops)

  
  if save:
    delete_entities(failed_links)
    db.put(save_links)
  else:
    return failed_links, save_links
    
