from django.db import models
from django.contrib.auth.models import User
from django.db.models import signals

class DatedMessageManager(models.Manager):
    '''
    Add some convenience functions for working with messages.
    '''
    
    def post_message_to_users(self, msg_text, 
                               msg_type='announcement', **kwargs):
        '''
        send a message to users matching the filter arguments in kwargs.
        
        @param msg_text: the text of the message
        @type msg_text: string
        @param msg_type: the message type. One of DatedMessage.TYPE_*
            Defaults to DatedMessage.TYPE_ANNOUNCE
        @type msg_type: One of DatedMessage.TYPE_*
        @param kwargs: filter arguments (e.g. username='dumbuser')
        '''
        
        self.create(
            text=msg_text, type=msg_type,
            users=User.objects.filter(**kwargs))
        
    def delete_messages_for_user(self, msgs, user):
        '''
        Delete messages for a user.
        
        @param msgs: iterable of msgs to delete for user
        @type msgs: iterable
        @param user: user object whose messages to delete
        '''
        
        user.messages.remove(*list(msgs))
        
    def get_messages_for_user(self, user):
        '''
        Get messages for a particular user.
        
        @param user: user object whose messages to get
        '''
        
        return self.filter(users=user)

class DatedMessage(models.Model):
    
    objects = DatedMessageManager()
    
    TYPE_ERROR = 'error'
    TYPE_WARNING = 'warning'
    TYPE_ANNOUNCE = 'announcement'
    
    MSG_TYPE_CHOICES={TYPE_ERROR: 'Error',
                      TYPE_WARNING: 'Warning',
                      TYPE_ANNOUNCE: 'Announcement',
                     }
    type = models.CharField("Message type", max_length=20, choices=MSG_TYPE_CHOICES.items())
    datetime = models.DateTimeField(auto_now=True, auto_now_add=True, editable=False)
    users = models.ManyToManyField(User, related_name="messages", verbose_name="Recipients")
    msg_text = models.CharField("Message", max_length=200)
    
    def format_date(self):
        return self.datetime.strftime("%Y-%m-%d")

    def format_time(self):
        return self.datetime.strftime("%H:%M:%S")
    
    def get_type(self):
        return DatedMessage[self.type]
    
    def __unicode__(self):
        return "%s %s - %s" % (self.format_date(), self.format_time(), self.text)

def clean_messages(sender, **kwargs):
    '''
    If there are no more users for this messages, delete it from
    the database.
    '''
    if kwargs['created'] == False:
        if kwargs['instance'].users.count() == 0:
            kwargs['instance'].delete()

signals.post_save.connect(clean_messages, DatedMessage)
