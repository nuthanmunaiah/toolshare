from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import FormView, TemplateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import HttpResponseRedirect
import operator
from app.forms.shed import *
from app.views.edit import FormsetView


class RegisterShedView(FormsetView):
    template_name = 'shed/register.html'
    form_class = RegisterShedForm
    formset_class = RegisterShedAddressFormSet
    http_method_names = ['get', 'post']
    success_url = reverse_lazy('shed:index')
    success_message = '<strong>%(shed_name)s</strong> was successfully registered.'

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        formset_class = self.get_formset_class()
        formset = formset_class(instance=request.user.address)
        return self.render_to_response(self.get_context_data(form=form, formset=formset))

    def form_valid(self, request, form, formset):
        shed_address = formset.save()
        shed = form.save(owner=self.request.user, address=shed_address)

        messages.success(request, self.success_message % {'shed_name': shed.name}, extra_tags='safe')
        return super(RegisterShedView, self).form_valid(request, form, formset)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(RegisterShedView, self).dispatch(request, *args, **kwargs)


class IndexShedView(TemplateView):
    template_name = 'shed/index.html'

    def get(self, request, *args, **kwargs):
        sheds = Shed.objects.filter(address__zip__startswith = request.user.share_zone)
        return self.render_to_response(self.get_context_data(sheds=sheds))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(IndexShedView, self).dispatch(request, *args, **kwargs)


class ShedDetailView(TemplateView):
    template_name = 'shed/detail.html'

    def get(self, request, *args, **kwargs):
        shed = Shed.objects.get(pk=kwargs['shed_id'])
        temptools = shed.tool_set.all()
        toolavailability = dict()

        for tool in temptools:
           toolavailability[tool] = tool.get_days_until_available()

        sortedTools = sorted(toolavailability.items(), key=operator.itemgetter(1))

        paginator = Paginator(sortedTools, 12, 1)
        page = request.GET.get('page', 1)

        try:
            tools = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            tools = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            tools = paginator.page(paginator.num_pages)

        return self.render_to_response(self.get_context_data(shed=shed, tools=tools))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ShedDetailView, self).dispatch(request, *args, **kwargs)


class UpdateShedView(FormsetView):
    template_name = 'shed/update.html'
    form_class = UpdateShedForm
    formset_class = UpdateShedAddressFormSet
    http_method_names = ['get', 'post']
    success_message = '<strong>%(shed_name)s</strong> was successfully updated.'
    perm_denied_message = 'You are <strong>not authorized</strong> to update the details of a community shed that ' \
                          'you do not own.'

    def get(self, request, *args, **kwargs):
        shed = Shed.objects.get(pk=kwargs['shed_id'])

        if shed.owner != request.user:
            messages.error(request, self.perm_denied_message, extra_tags='safe')
            perm_denied_url = reverse_lazy('shed:detail', kwargs={'shed_id': shed.pk})
            return HttpResponseRedirect(perm_denied_url)

        form_class = self.get_form_class()
        form = form_class(instance=shed)
        formset_class = self.get_formset_class()
        formset = formset_class(instance=shed.address)
        return self.render_to_response(self.get_context_data(form=form, formset=formset, shed=shed, user=request.user))

    def post(self, request, *args, **kwargs):
        shed = Shed.objects.get(pk=kwargs['shed_id'])
        form_class = self.get_form_class()
        form = form_class(request.POST, instance=shed)
        formset_class = self.get_formset_class()
        formset = formset_class(request.POST, instance=shed.address)

        if form.is_valid() and formset.is_valid():
            return self.form_valid(request, form, formset)
        else:
            return self.form_invalid(request, form, formset)

    def form_valid(self, request, form, formset):
        address = formset.save()
        shed = form.save()
        messages.success(request, self.success_message % {'shed_name': shed.name}, extra_tags='safe')
        self.success_url = reverse_lazy('shed:detail', kwargs={'shed_id': shed.pk})
        return super(UpdateShedView, self).form_valid(request, form, formset)

    def form_invalid(self, request, form, formset):
        shed = form.instance
        return self.render_to_response(self.get_context_data(form=form, formset=formset, shed=shed))

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(UpdateShedView, self).dispatch(request, *args, **kwargs)


class DeleteShedView(DeleteView):
    model = Shed
    pk_url_kwarg = 'shed_id'
    http_method_names = ['post']
    success_message = '<strong>%(shed_name)s</strong> was successfully deleted.'
    success_url = reverse_lazy('shed:index')

    def post(self, request, *args, **kwargs):
        shed = self.get_object()
        messages.success(request, self.success_message % {'shed_name': shed.name}, extra_tags='safe')
        return super(DeleteShedView, self).post(request, *args, **kwargs)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(DeleteShedView, self).dispatch(request, *args, **kwargs)