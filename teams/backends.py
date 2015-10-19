from organizations.backends.defaults import InvitationBackend


class CustomInvitations(InvitationBackend):
    def get_success_url(self):
    	return reverse('index')