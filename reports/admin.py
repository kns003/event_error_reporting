from django.contrib import admin
from .models import ErrorReport


# Register your models here.
@admin.register(ErrorReport)
class ErrorReportAdmin(admin.ModelAdmin):
    list_display = ('status', 'path', 'request_method', 'message', 'duration', 'created_at')
    exclude = ('ip_address_info', 'request_headers')
    list_filter = ('code', 'status')
    change_form_template = 'admin/reports/errorreport/change_form.html'

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False