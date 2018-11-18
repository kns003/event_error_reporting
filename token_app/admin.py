import json
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin, UserAdmin as BaseUserAdmin
from django.core.exceptions import FieldDoesNotExist
from django.contrib.admin.exceptions import DisallowedModelAdminToField
from django.core.exceptions import PermissionDenied
from django.contrib.admin.utils import unquote, flatten_fieldsets
from django.contrib.admin import helpers
from django.forms.formsets import all_valid
from django.utils.translation import gettext as _
from django.utils.translation import ngettext, override as translation_override
from django.contrib.admin.options import get_content_type_for_model
from event_error_reporting.middleware import get_client_ip
from token_app.models import CustomLogEntry, TestApp

EMPTY_VALUE_LIST = ['', None, {}, []]
TO_FIELD_VAR = '_to_field'
IS_POPUP_VAR = '_popup'

admin.site.unregister(Group)
admin.site.unregister(User)

# Register your models here.
class LogCustomModelAdmin(admin.ModelAdmin):

    def log_addition(self, request, object, message, data):
        """
        Log that an object has been successfully added.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import LogEntry, ADDITION
        log_obj = CustomLogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=str(object),
            action_flag=ADDITION,
            change_message=message,
        )
        log_obj.changed_data = data
        log_obj.request_meta = str(request.META)
        log_obj.ip_address = get_client_ip(request)
        log_obj.save()

    def log_change(self, request, object, message, data):
        """
        Log that an object has been successfully changed.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import LogEntry, CHANGE
        log_obj = CustomLogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=str(object),
            action_flag=CHANGE,
            change_message=message,
        )
        log_obj.changed_data = data
        log_obj.request_meta = str(request.META)
        log_obj.ip_address = get_client_ip(request)
        log_obj.save()

    def log_deletion(self, request, object, object_repr):
        """
        Log that an object will be deleted. Note that this method must be
        called before the deletion.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import LogEntry, DELETION
        return CustomLogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=object_repr,
            action_flag=DELETION,
        )
        log_obj.changed_data = data
        log_obj.request_meta = str(request.META)
        log_obj.ip_address = get_client_ip(request)
        log_obj.save()



    def _changeform_view(self, request, object_id, form_url, extra_context):
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)

        model = self.model
        opts = model._meta

        if request.method == 'POST' and '_saveasnew' in request.POST:
            object_id = None

        add = object_id is None

        if add:
            if not self.has_add_permission(request):
                raise PermissionDenied
            obj = None

        else:
            obj = self.get_object(request, unquote(object_id), to_field)

            if not self.has_view_or_change_permission(request, obj):
                raise PermissionDenied

            if obj is None:
                return self._get_obj_does_not_exist_redirect(request, opts, object_id)

        ModelForm = self.get_form(request, obj, change=not add)
        if request.method == 'POST':
            form = ModelForm(request.POST, request.FILES, instance=obj)
            form_validated = form.is_valid()
            if form_validated:
                new_object = self.save_form(request, form, change=not add)
            else:
                new_object = form.instance
            formsets, inline_instances = self._create_formsets(request, new_object, change=not add)
            if all_valid(formsets) and form_validated:
                self.save_model(request, new_object, form, not add)
                self.save_related(request, form, formsets, not add)
                change_message, data = self.construct_change_message(request, form, formsets, add)
                if add:
                    self.log_addition(request, new_object, change_message, data)
                    return self.response_add(request, new_object)
                else:
                    self.log_change(request, new_object, change_message, data)
                    return self.response_change(request, new_object)
            else:
                form_validated = False
        else:
            if add:
                initial = self.get_changeform_initial_data(request)
                form = ModelForm(initial=initial)
                formsets, inline_instances = self._create_formsets(request, form.instance, change=False)
            else:
                form = ModelForm(instance=obj)
                formsets, inline_instances = self._create_formsets(request, obj, change=True)

        if not add and not self.has_change_permission(request, obj):
            readonly_fields = flatten_fieldsets(self.get_fieldsets(request, obj))
        else:
            readonly_fields = self.get_readonly_fields(request, obj)
        adminForm = helpers.AdminForm(
            form,
            list(self.get_fieldsets(request, obj)),
            self.get_prepopulated_fields(request, obj),
            readonly_fields,
            model_admin=self)
        media = self.media + adminForm.media

        inline_formsets = self.get_inline_formsets(request, formsets, inline_instances, obj)
        for inline_formset in inline_formsets:
            media = media + inline_formset.media

        if add:
            title = _('Add %s')
        elif self.has_change_permission(request, obj):
            title = _('Change %s')
        else:
            title = _('View %s')
        context = {
            **self.admin_site.each_context(request),
            'title': title % opts.verbose_name,
            'adminform': adminForm,
            'object_id': object_id,
            'original': obj,
            'is_popup': IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET,
            'to_field': to_field,
            'media': media,
            'inline_admin_formsets': inline_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'preserved_filters': self.get_preserved_filters(request),
        }

        # Hide the "Save" and "Save and continue" buttons if "Save as New" was
        # previously chosen to prevent the interface from getting confusing.
        if request.method == 'POST' and not form_validated and "_saveasnew" in request.POST:
            context['show_save'] = False
            context['show_save_and_continue'] = False
            # Use the change template instead of the add template.
            add = False

        context.update(extra_context or {})

        return self.render_change_form(request, context, add=add, change=not add, obj=obj, form_url=form_url)

    def construct_change_message(self, request, form, formsets, add=False):
        """
        Construct a JSON structure describing changes from a changed object.
        """
        return construct_change_message(form, formsets, add)


def log_entry_data(form):
    change_list = form.changed_data
    initial_dict = form.initial
    changed_dict = form.cleaned_data
    instance = form.instance
    field_structure = []
    for value in change_list:
        tmp_dict = {}
        if changed_dict[value] in EMPTY_VALUE_LIST:
            continue
        tmp_dict['initial_value'] = get_value_names_based_on_field(value,
                                                                   initial_dict.get(value, ''),
                                                                   form.instance)
        tmp_dict['final_value'] = get_value_names_based_on_field(value,
                                                                 changed_dict.get(value, ''),
                                                                 form.instance)
        try:
            tmp_dict['field_name'] = str(instance._meta.get_field(value).verbose_name)
        except FieldDoesNotExist:
            if '_' in value:
                value = value.replace('_', ' ')
            tmp_dict['field_name'] = str(value)

        field_structure.append(tmp_dict)
    return field_structure

def get_value_names_based_on_field(key_name, value, obj):
    """
    Get the name of the key field
    :param key_name:
    :param obj:
    :return:
    """
    try:
        if obj._meta.get_field(key_name).get_internal_type() == 'ForeignKey':
            return obj._meta.get_field(key_name).related_model.objects.get(id=value).__str__()

        if obj._meta.get_field(key_name).get_internal_type() == 'CharField' and \
                obj._meta.get_field(key_name).choices != []:
            return dict(obj._meta.get_field(key_name).choices)[str(value)]

        return str(value)
    except Exception as e:
        return str(value)

def construct_change_message(form, formsets, add):
    """
    Construct a JSON structure describing changes from a changed object.
    Translations are deactivated so that strings are stored untranslated.
    Translation happens later on LogEntry access.
    """
    change_message = []
    if add:
        change_message.append({'added': {}})

    elif form.changed_data:
        change_message.append({'changed': {'fields': form.changed_data}})

    data = log_entry_data(form)
    if formsets:
        with translation_override(None):
            for formset in formsets:
                for added_object in formset.new_objects:
                    change_message.append({
                        'added': {
                            'name': str(added_object._meta.verbose_name),
                            'object': str(added_object),
                        }
                    })
                for changed_object, changed_fields in formset.changed_objects:
                    change_message.append({
                        'changed': {
                            'name': str(changed_object._meta.verbose_name),
                            'object': str(changed_object),
                            'fields': changed_fields,
                        }
                    })
                for deleted_object in formset.deleted_objects:
                    change_message.append({
                        'deleted': {
                            'name': str(deleted_object._meta.verbose_name),
                            'object': str(deleted_object),
                        }
                    })
    return change_message, data

@admin.register(CustomLogEntry)
class CustomLogEntryAdmin(admin.ModelAdmin):
    list_display = ('get_content_type', 'get_action_flag', 'changed_by', 'change_message')
    exclude = ('changed_data', 'request_meta', 'ipaddress')

    change_form_template = 'admin/token_app/customlogentry/change_form.html'
    def get_content_type(self, obj):
        return obj.content_type.model.title()
    get_content_type.short_description = 'Model name'

    def get_action_flag(self, obj):
        if obj.action_flag == 2:
            return 'CHANGED'
        elif obj.action_flag == 1:
            return 'ADDED'
        else:
            return 'DELETED'
    get_action_flag.allow_tags = True
    get_action_flag.short_description = 'Status'

    def changed_by(self, obj):
        return obj.user.get_full_name()

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Group)
class GroupAdmin(LogCustomModelAdmin):
    list_display = ('id', 'name', 'permissions_list')

    def permissions_list(self, obj):
        permissions = [x.name for x in obj.permissions.all()]
        return ', '.join(permissions)


@admin.register(User)
class UserAdmin(LogCustomModelAdmin):

    list_display = (
        'id', 'first_name', 'last_name', 'email', 'is_superuser', 'is_staff', 'is_active')

@admin.register(TestApp)
class TestAppAdmin(LogCustomModelAdmin):
    list_display = ('name', 'email', 'phone_number', 'address')
