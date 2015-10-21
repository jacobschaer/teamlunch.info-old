from django.shortcuts import render
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
            return redirect(reverse('detail', team_id=team.pk))

        # If the user is logged in, associate the user with the corresponding
        # TeamMember object and move on. They're either already logged in,
        # or they used the social login.
        elif request.user.is_authenticated():
            teammember.user = request.user
            user.delete()
            teammember.save()
            return redirect(reverse('detail', team_id=team.pk))

        return render(request, 'teams/accept_invitation.html',
                {'form': form})


class CustomInvitations(CustomBaseBackend, InvitationBackend):
    def get_success_url(self):
        return reverse('index')

