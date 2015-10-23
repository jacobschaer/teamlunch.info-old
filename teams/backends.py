from django.core.urlresolvers import reverse
from django.core.mail import EmailMessage
from django.template import Context, loader
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import Http404
from django.utils.translation import ugettext as _

from organizations.backends.defaults import BaseBackend, InvitationBackend
from organizations.backends.tokens import RegistrationTokenGenerator

from .models import TeamMember

class CustomBaseBackend(BaseBackend):
    def activate_view(self, request, user_id, token):
        """
        View function that activates the given User by setting `is_active` to
        true if the provided information is verified.
        """
        try:
            user = self.user_model.objects.get(id=user_id, is_active=False)
        except self.user_model.DoesNotExist:
            raise Http404(_("Your URL may have expired."))
        if not RegistrationTokenGenerator().check_token(user, token):
            raise Http404(_("Your URL may have expired."))

        teammember = TeamMember.objects.get(user=user)
        team = teammember.organization

        # Did the user post a response?
        form = self.get_form(data=request.POST or None, instance=user)
        if form.is_valid():
            form.instance.is_active = True
            user = form.save()
            user.set_password(form.cleaned_data['password'])
            user.save()
            self.activate_organizations(user)
            user = authenticate(username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'])
            login(request, user)
            return redirect(reverse('teams:detail', kwargs={'team_id' : team.pk}))

        # If the user is logged in, associate the user with the corresponding
        # TeamMember object and move on. They're either already logged in,
        # or they used the social login.
        elif request.user.is_authenticated():
            teammember.user = request.user
            user.delete()
            teammember.save()
            return redirect(reverse('teams:detail', kwargs={'team_id' : team.pk}))

        return render(request, 'teams/accept_invitation.html',
                {'form': form})

    # This could be replaced with a more channel agnostic function, most likely
    # in a custom backend.
    def _send_email(self, user, subject_template, body_template,
            sender=None, **kwargs):
        """Utility method for sending emails to new users"""
        from_email = settings.DEFAULT_FROM_EMAIL
        reply_to = from_email

        headers = {'Reply-To': reply_to}
        kwargs.update({'sender': sender, 'user': user})
        ctx = Context(kwargs, autoescape=False)

        subject_template = loader.get_template(subject_template)
        body_template = loader.get_template(body_template)
        subject = subject_template.render(ctx).strip()  # Remove stray newline characters
        body = body_template.render(ctx)
        return EmailMessage(subject, body, from_email, [user.email],
                headers=headers).send()


class CustomInvitations(CustomBaseBackend, InvitationBackend):
    def get_success_url(self):
        return reverse('index')

