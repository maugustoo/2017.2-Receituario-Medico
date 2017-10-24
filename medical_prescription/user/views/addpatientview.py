# standard library
import hashlib
import datetime
import random

# Django
from django.views.generic import FormView
from django.core.mail import send_mail
from django.shortcuts import redirect, render

# Local Django
from user.forms import AddPatientForm
from user.models import User, AssociatedHealthProfessionalAndPatient, Patient, HealthProfessional
from user.models import SendInvitationProfile


class AddPatientView(FormView):
    form_class = AddPatientForm
    template_name = 'add_patient.html'

    def get(self, request, *args, **kwargs):
        form = self.form_class(initial=self.initial)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            email = form.cleaned_data.get('email')
            email_from_database = Patient.objects.filter(email=email, is_active=True)

            if email_from_database.exists():
                patient_profile = Patient.objects.get(email=email)
                AddPatientView.create_link_patient_health_professional(request.user, patient_profile)
                AddPatientView.activate_link_patient_health_professional(patient_profile.email)
            else:
                patient_profile = AddPatientView.create_send_invitation_profile(email)
                AddPatientView.send_invitation_email(email, patient_profile)

        else:
            # Nothing to do.
            pass

        return redirect('http://0.0.0.0:8000/dashboard_health_professional/health_professional/')

    def create_send_invitation_profile(email):
        # Prepare the information needed to send the account verification
        # email.
        salt = hashlib.sha1(str(random.random()).
                            encode('utf-8')).hexdigest()[:5]
        activation_key = hashlib.sha1(str(salt+email).
                                      encode('utf‌​-8')).hexdigest()
        key_expires = datetime.datetime.today() + datetime.timedelta(2)

        patient = Patient.objects.create_user(email=email, is_active=False)

        # Creating the temporary user.
        new_profile = SendInvitationProfile(patient=patient, activation_key=activation_key,
                                            key_expires=key_expires)
        new_profile.save()

        return new_profile

    # Sending email for account activation.
    def send_invitation_email(email, SendInvitationProfile):
        email_subject = 'Convite para Cadastro no Sistema'
        email_body = """
                     Para se cadastrar, clique neste link:
                     http://localhost:8000/user/register_patient/%s
                     """

        send_mail(email_subject, email_body % SendInvitationProfile.activation_key,
                  'medicalprescriptionapp@gmail.com', [email], fail_silently=False)

    def create_link_patient_health_professional(HealthProfessional, Patient):
        link = AssociatedHealthProfessionalAndPatient(associated_health_professional=HealthProfessional,
                                                      associated_patient=Patient, is_active=False)
        link.save()

    def activate_link_patient_health_professional(email):
        patient_profile = Patient.objects.get(email=email)
        AssociatedHealthProfessionalAndPatient.objects.filter(associated_patient=patient_profile,
                                                              is_active=False).update(is_active=True)
