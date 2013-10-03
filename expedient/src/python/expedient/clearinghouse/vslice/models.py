'''
Created on Jul 23, 2013

@author: atty
'''
from datetime import datetime, timedelta
from django.db import models
from expedient.clearinghouse.project.models import Project
from expedient.clearinghouse.aggregate.models import Aggregate
from django.contrib.auth.models import User
from expedient.common.permissions.models import ObjectPermission, Permittee
from expedient.clearinghouse.aggregate.utils import get_aggregate_classes
import logging, uuid
from django.db.models import signals
from expedient.common.messaging.models import DatedMessage
import traceback
from expedient.common.utils.mail import send_mail # Wrapper for django.core.mail__send_mail
from django.conf import settings
from expedient.common.timer.models import Job
#from expedient.common.timer.exceptions import JobAlreadyScheduled
from expedient.common.utils.modelfields import LimitedDateTimeField
from expedient.common.middleware import threadlocals
from expedient.common.utils.validators import asciiValidator, descriptionLightValidator
from expedient.clearinghouse.vslice.utils import *

logger = logging.getLogger("vslice.models")

def _get_vslice_max_date():
    return datetime.now() + timedelta(days=settings.MAX_VSLICE_LIFE)

class Vslice(models.Model):
    '''
    Holds information about reservations across aggregates
    @ivar name: The name of the Slice
    @type name: L{str}
    @ivar description: Short description of the slice
    @type description: L{str}
    @ivar project: Project in which this slice belongs
    @type project: L{models.ForeignKey} to L{Project}
    @ivar owner: Original creator of the slice
    @type owner: C{User}
    @ivar started: Has this slice been reserved with the aggregates yet? 
    @type started: C{bool}
    @ivar modified: Has this slice been modified since it was last reserved?
    @type modified: C{bool}
    @ivar expiration_date: Date and time of when the slice is going to
        expire in local time.
    @type expiration_date: L{datetime.datetime} instance
    @ivar aggregates: Read-only property returning all aggregates that can
        be used by the project (i.e. for which the project has the
        "can_use_aggregate" permission).
    @type aggregates: C{QuerySet} of L{Aggregate}s
    '''
    
    name = models.CharField(max_length=200, unique=True, validators=[asciiValidator])
    description = models.TextField(validators=[descriptionLightValidator])
    project = models.ForeignKey(Project)
    owner = models.ForeignKey(User, related_name="owned_vslices")
    started = models.BooleanField(default=False, editable=False)
    modified = models.BooleanField(default=False, editable=False)
    uuid = models.CharField(max_length=200, default = "", unique=True, editable =False)
    expiration_date = LimitedDateTimeField(
        default=datetime.now() + timedelta(days=settings.VSLICE_DEFAULT_EXPIRATION_TIME),
        help_text="Enter a date and time. The date should be in the"
            " following format: 'YYYY-MM-DD'. And for the time: 'HH:MM:SS'."
            " The expiration date cannot be later than %s days from"
            " now." % settings.MAX_VSLICE_LIFE,
        max_date=_get_vslice_max_date,
   )
    
    def __unicode__(self):
        return u"Vslice '%s' in project '%s'" % (self.name, self.project.name)
    
    def start(self, user):
        """
        Should be an idempotent operation on the aggregates.
        """
        # check the expiration date
		# XXX: Expiration mechanism review needed
        #if self.expiration_date <= datetime.now():
        #    raise Exception("Slice expired. Update slice expiration time.")

	from vt_plugin.models.VtPlugin import VtPlugin

        logger.debug("Called start_vslice on %s: %s" % (self, self.name))
        aggs = enumerate(self.aggregates.all())

        started_aggs = list()
        exceptions = list()

        for i, agg in aggs:
            logger.debug("starting vslice on agg %s" % agg.name)
            try:
                agg.as_leaf_class().start_vslice(self)
                started_aggs.append(agg)
            except Exception, e:
                logger.error("Error starting vslice on agg %s" % agg.name)
                # try to stop slice on all previously started aggregates
               
                #Error is in a VT AM, can continue 
                #if isinstance(agg.as_leaf_class(),VtPlugin):
                #    try:
                #        agg.as_leaf_class().stop_slice(self)
                #    except Exception, e2:
                #            # error stopping slice
                #            logger.error(traceback.format_exc())
                #            DatedMessage.objects.post_message_to_user(
                #            msg_text="Error stopping slice %s on "
                #            "aggregate %s" % (self, agg.name),
                #            user=user, msg_type=DatedMessage.TYPE_ERROR)
                #            # raise the original exception raised starting the slice.
                #    exceptions.append(e)
                ##Error is on a OF AM, can not start slice, and should stop all the AMs
                #else:
                for ragg in started_aggs:
                    try:
                        if not isinstance(agg.as_leaf_class(),VtPlugin):
                            ragg.as_leaf_class().stop_vslice(self)
                    except Exception, e2:
                        # error stopping vslice
                        logger.error(traceback.format_exc())
                        DatedMessage.objects.post_message_to_user(
                        msg_text="Error stopping vslice %s on "
                        "aggregate %s" % (self, ragg.name),
                        user=user, msg_type=DatedMessage.TYPE_ERROR)
                # raise the original exception raised starting the slice.
                print e
                raise Exception(parseFVexception(e))
        
        # all is well
        self.started = True
        self.modified = False
        self.save()
        return exceptions


    def stop(self, user):
        """
        Should be an idempotent operation on the aggregates.
        """
        for agg in self.aggregates.all():
            agg.as_leaf_class().stop_vslice(self)
        self.started = False
        self.save()
            
    def _get_aggregates(self):
        """Get all aggregates that can be used by the vslice
        (i.e. for which the vslice has the "can_use_aggregate" permission).
        """
        agg_ids = []
        agg_classes = get_aggregate_classes()
        permittee = Permittee.objects.get_as_permittee(self)
        for agg_class in agg_classes:
            agg_ids.extend(
                ObjectPermission.objects.filter_for_class(
                    agg_class,
                    permission__name="can_use_aggregate",
                    permittees=permittee,
                ).values_list("object_id", flat=True)
            )
        return Aggregate.objects.filter(pk__in=agg_ids)
#        return Aggregate.objects
    aggregates=property(_get_aggregates)
    
    @classmethod
    @models.permalink
    def get_create_url(cls, proj_id):
        "Returns the URL to create vslices"
        return ("vslice_create", (), {"proj_id": proj_id})
    
    @models.permalink
    def get_update_url(self):
        "Returns the URL to update vslice info"
        return ("vslice_update", (), {"vslice_id": self.id})

    @models.permalink
    def get_detail_url(self):
        "Returns the URL for the vslice detail page"
        return ("vslice_detail", (), {"vslice_id": self.id})
    
    @models.permalink
    def get_delete_url(self):
        "Returns the URL to delete a vslice"
        return ("vslice_delete", (), {"vslice_id": self.id})
    
    @models.permalink
    def get_start_url(self):
        "Returns the URL to start the vslice"
        return ("vslice_start", (), {"vslice_id": self.id})
    
    @models.permalink
    def get_stop_url(self):
        "Returns the URL to stop the vslice"
        return ("vslice_stop", (), {"vslice_id": self.id})    
    
    @models.permalink
    def get_agg_add_url(self):
        "Returns the URL to add an aggregate to a vslice"
        return ("vslice_add_agg", (), {"vslice_id": self.id})

    @models.permalink
    def get_agg_update_url(self, aggregate):
        "Returns URL to update an aggregate's info related to the vslice"
        return ("vslice_update_agg", (), {
            "vslice_id": self.id,
            "agg_id": aggregate.id})
    
    @models.permalink
    def get_agg_remove_url(self, aggregate):
        "Returns URL to remove aggregate from vslice"
        return ("vslice_remove_agg", (), {
            "vslice_id": self.id,
            "agg_id": aggregate.id})
    
    @models.permalink
    def get_rsc_management_url(self):
        "Returns the URL at which to select a UI plugin."
        return ("vslice_manage_resources", (), {"vslice_id": self.id})
    
    
def stop_vslice_before_delete(sender, **kwargs):
    """Before deleting a vslice, make sure it is stopped"""
    try:
        kwargs["instance"].stop()
    except:
        pass
signals.pre_delete.connect(stop_vslice_before_delete, Vslice)

# Deal with expired vslices ##################################################

def stop_expired_vslices():
    """Find expired vslices and stop them, sending an email to the owner."""
    
    expired_vslices = Vslice.objects.filter(
        expiration_date__lte=datetime.now(), started=True)
    
    for vslice in expired_vslices:
        threadlocals.push_frame(user=vslice.owner)
        try:
            vslice.stop(vslice.owner)
        except:
            logger.error(
                "Error stopping expired vslice"
                " %s: %s" % (vslice, traceback.format_exc()))
        threadlocals.pop_frame()
        try:
            send_mail(
                "Your vslice %s expired." % vslice,
                "Your vslice %s has been stopped because it expired on %s."
                "Before you restart your vslice, you will need to update the "
                "vslice's expiration date." % (vslice, vslice.expiration_date),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[vslice.owner.email],
            )
        except:
            logger.error(
                "Error sending expired vslice "
                "email to user: %s" % traceback.format_exc())
    
def notify_vslice_expirations():
    """Notify owners that their vslices will expire soon."""

    expiration_time = datetime.now() + timedelta(
        seconds=settings.VSLICE_EXPIRATION_NOTIFICATION_TIME)
    
    almost_expired_vslices = Vslice.objects.filter(
        expiration_date__lte=expiration_time, started=True)

    for vslice in almost_expired_vslices:
        try:
            send_mail(
                "Your vslice %s is almost expired." % vslice,
                "Your vslice %s is almost expired. If you don't do anything, "
                "it will expired on %s. "
                "To renew your vslice, you will need to update the "
                "vslice's expiration date." % (vslice, vslice.expiration_date),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[vslice.owner.email],
            )
        except:
            logger.error(
                "Error sending almost expired vslice "
                "email to user: %s" % traceback.format_exc())
    
# schedule jobs
# XXX: Expiration mechanism review needed
#try:
#    Job.objects.schedule_post_syncdb(settings.VSLICE_EXPIRATION_CHECK_INTERVAL, stop_expired_vslices)
#except JobAlreadyScheduled:
#    pass
#
#try:
#    Job.objects.schedule_post_syncdb(settings.VSLICE_EXPIRATION_NOTIFICATION_TIME, notify_vslice_expirations)
#except JobAlreadyScheduled:
#    pass
