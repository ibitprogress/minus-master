from models import VocalContest, VocalContestCategory, VocalContestParticipant, RealVocalContestParticipant, RealVocalContestGuest
from django.contrib import admin


class VocalContestCategoryInline(admin.StackedInline):
    model = VocalContestCategory

class VocalContestAdmin(admin.ModelAdmin):
    inlines = [VocalContestCategoryInline,]

class VocalContestParticipantAdmin(admin.ModelAdmin):
    exclude = ('user',)
    list_filter = ('category',)
    search_fields = ('title',)

class RealVocalContestPersonAdmin(admin.ModelAdmin):
    readonly_fields = ('user',)
    list_filter = ('contest', 'is_payed')
    list_display = ('user','places','is_payed')
    

admin.site.register(VocalContest, VocalContestAdmin)
admin.site.register(VocalContestCategory)
admin.site.register(VocalContestParticipant, VocalContestParticipantAdmin)
admin.site.register(RealVocalContestGuest, RealVocalContestPersonAdmin)
admin.site.register(RealVocalContestParticipant, RealVocalContestPersonAdmin)

